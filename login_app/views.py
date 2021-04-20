from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import LoginForm, NewApplicationForm, RequestForm
from django.contrib import messages
from django.http import HttpResponse
# from login_app.models import Faculty, activeleaveentries
from main.models import Faculty, Active_Leave_Entries, Previous_Request_Record, Decision_Record, Previous_Cross_Cutting
# Comments, Previous_Record
from datetime import datetime
from django.db import connections
# Create your views here.

departments = {'EE': 'Electrical',
               'ME': 'Mechanical', 'CSE': 'Computer Science'}

levels = ['Faculty', 'Head of Department', 'Dean Faculty Affairs', 'Director']
datetime_format = '%Y-%m-%dT%H:%M:%S'


def clean_comments(input_comment):
    length = len(input_comment)
    outp = ""
    for i in range(length):
        char = input_comment[i]
        outp += char
        if char == '\'':
            size = 0
            while i < length-1:
                if input_comment[i] == '\'':
                    i += 1
                    size += 1
                else:
                    break

            for j in range(size):
                outp += '\''

    return outp


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def get_active_leaves(user_id):
    check_querr = f'SELECT * FROM "main_active_leave_entries" where "FacultyID" = {user_id}'
    check_res = Active_Leave_Entries.objects.raw(check_querr)
    return (len(check_res), check_res)


def exec_querry(querry, val=False):
    outp = {}
    with connections['default'].cursor() as cursors:
        cursors.execute(querry)
        if val:
            outp = dictfetchall(cursors)
    return outp


def clean_date(date):
    return datetime.strptime(date[:-6], datetime_format)


def index(request):
    # print(request.user)
    if request.user.is_anonymous:
        return redirect('/login')

    return redirect('/profile')


def login_req(request):
    if request.user.is_anonymous:
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                print(request.POST)
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']

                # if form.cleaned_data['is_cross'] == True:
                #     # Special Permissions Processing
                #     print("Super")

                user = authenticate(username=username, password=password)

                if user is not None:
                    messages.success(
                        request, f"Welcome back, {user.first_name}!!")
                    login(request, user)
                    return redirect("/profile")

                else:
                    messages.error(
                        request, "Failed Login!! :'( Please Check Username/Password")

            else:
                print(form.errors)
                messages.error(
                    request, "Unexpected Error!! Try Refreshing the page")
    else:
        return redirect('/profile')

    return render(request=request, template_name="loginpage.html")


def logoutuser(request):
    logout(request)
    return redirect("/login")


def profile(request):
    if request.user.is_anonymous:
        return redirect('/login')
    user = request.user
    fullname = user.first_name + " " + user.last_name

    querry = f'SELECT * FROM main_faculty WHERE \"FacultyID\" ={user.id}'
    context_dict = {'email': user.email,
                    'name': fullname, 'uname': user.username, 'has_perm': False}
    res = Faculty.objects.raw(querry)
    for faculty_details in res:
        context_dict['dept'] = departments[faculty_details.dept] + \
            " Department"
        context_dict['rem_leave'] = faculty_details.leaves_remaining
        context_dict['perm'] = levels[faculty_details.permission_level]
        context_dict['has_permission'] = faculty_details.permission_level

    return render(request=request, template_name="profile.html", context=context_dict)


def requests(request):
    if request.method == "POST":
        req_form = RequestForm(request.POST)
        if req_form.is_valid():
            print(req_form.cleaned_data)
        else:
            print(req_form.errors)

    if request.user.is_anonymous:
        return redirect('/login')
    perm = False
    user = request.user
    querry = f'SELECT * FROM main_faculty WHERE \"FacultyID\" ={user.id}'
    res = Faculty.objects.raw(querry)
    for faculty_details in res:
        perm_level = faculty_details.permission_level
        perm = bool(faculty_details.permission_level)
    # perm_level = perm_level-1 -------------------------------------------------------------------------- CHECK
    if perm_level < 1:
        messages.warning("Error!: You are not authorised for the action.")
        return redirect('/profile')
    querry = f'select * from get_active_requests({perm_level});'
    cursor = connections['default'].cursor()
    cursor.execute(querry)
    cur = cursor.fetchall()
    cursor.close()
    entries = []
    for obj in cur:
        obj = obj[0]
        obj['app_date'] = clean_date(obj['app_date'])
        facul_id = obj['fac_id']
        active = get_active_leaves(facul_id)
        for val in active[1]:
            obj['comms'] = get_comments_by_entryID(val.id, facul_id)
        entries.append(obj.copy())

    return render(request=request, template_name="requests.html", context={'details': entries, 'has_permission': perm})


def application(request):
    perm = False
    leave_cnt = 0
    if request.user.is_anonymous:
        return redirect('/login')
    with connections['default'].cursor() as cursors:
        cursors.execute(
            f"select * from get_personal_id({request.user.id})")
        res = cursors.fetchone()
        res = res[0]
        perm = res['permission_level']
        user_id = res['FacultyID']
        leave_cnt = res['leaves_remaining']

    if request.method == 'POST':
        form = NewApplicationForm(request.POST)
        if form.is_valid():
            st_date = form.cleaned_data['startdate']
            end_date = form.cleaned_data['enddate']
            desc = clean_comments(form.cleaned_data['description'])

            check_res = get_active_leaves(user_id)

            if check_res[0] > 0:
                messages.error(
                    request, f"Error: You Already Have an Active Leave Entry with id = {check_res[1][0].id}")

            else:
                now = datetime.today().strftime('%Y-%m-%d')
                insert_querry = f'INSERT INTO "main_active_leave_entries"("FacultyID", application_date, starting_date, num_leaves, curr_status) VALUES({request.user.id}, \'{now}\', \'{st_date}\', {(end_date - st_date).days}, 1)'
                exec_querry(insert_querry)

                check_res = get_active_leaves(user_id)
                insert_record = f"INSERT INTO main_decision_record(\"EntryID\", timecreated, body, verdict, \"DecisionMakerID\", is_active) VALUES({check_res[1][0].id}, '{now}', '{desc}', -1, '{request.user.id}', True)"
                exec_querry(insert_record)

                messages.success(
                    request, f"Succesfully Submitted new request with id = {check_res[1][0].id}. Check Status in Active Entries")

        else:
            print(form.error)

    return render(request=request, template_name="application.html", context={'has_permission': perm, 'max_leaves': leave_cnt})


def get_faculty_details(FacID):
    querry = f'SELECT * FROM main_faculty WHERE \"FacultyID\" ={FacID}'
    return Faculty.objects.raw(querry)


def get_comments_by_entryID(entryID, user_id):
    querry = f'SELECT * FROM "main_decision_record" WHERE "EntryID" = {entryID} ORDER BY timecreated'
    comm = Decision_Record.objects.raw(querry)
    curr_com = []
    for com_entry in comm:
        com = {}
        com['body'] = com_entry.body
        if int(com_entry.DecisionMakerID) == int(user_id):
            com['from'] = 'Me'
        else:
            res = get_faculty_details(com_entry.DecisionMakerID)
            for details in res:
                from_post = levels[details.permission_level]
                if details.permission_level == 0:
                    return "-1"
                if details.permission_level == 1:
                    from_post += " " + departments[details.dept]
                com['from'] = from_post
        curr_com.append(com)

    return curr_com


def status(request):
    perm = False
    with connections['default'].cursor() as cursors:
        cursors.execute(
            f"select * from get_personal_id({request.user.id})")
        res = cursors.fetchone()
        res = res[0]
        perm = res['permission_level']

    user_id = request.user.id
    active = []
    prev = -1
    with connections['default'].cursor() as cursors:
        cursors.execute(f"Select * from get_active_records({user_id})")
        result = cursors.fetchall()

    for val in result:
        val = val[0]
        if val['EntryID'] != prev:
            new_val = {}
            new_val['id'] = val['EntryID']
            new_val['application_date'] = clean_date(val['application_date'])
            new_val['start_date'] = val['starting_date']
            new_val['num'] = val['num_leaves']
            new_val['curr_status'] = val['curr_status']
            new_val['comms'] = []
            prev = val['EntryID']
            active.append(new_val.copy())

        comment_details = {}
        deciderID, deciderName = (0, "")
        with connections['default'].cursor() as cursors:
            cursors.execute(
                f"select * from get_personal_id({val['DecisionMakerID']})")
            res = cursors.fetchone()
            res = res[0]
            deciderID = res['FacultyID']
            deciderName = res['first_name'] + " " + res['last_name']
            comment_details['from'] = deciderName

        if deciderID == val['FacultyID'] or val['DecisionMakerID'] == val['FacultyID']:
            comment_details['from'] = 'Me'
        else:
            comment_details['from'] = deciderName
        comment_details['body'] = val['body']

        comment_details['createdon'] = clean_date(val['timecreated'])
        active[-1]['comms'].append(comment_details.copy())

    # print(active)

    previous_entries = []

    with connections['default'].cursor() as cursors:
        cursors.execute(f"Select * from get_past_records({user_id})")
        result = cursors.fetchall()

    prev = -1
    for val in result:
        val = val[0]
        # print(val)
        if val['EntryID'] != prev:
            new_val = {}
            new_val['id'] = val['EntryID']
            new_val['comms'] = []
            new_val['start_date'] = val['starting_date']
            new_val['decision_date'] = val['timecreated']
            # new_val['was_approved'] = bool(val['verdict']/2)
            new_val['num'] = val['num_leaves']
            new_val['application_date'] = datetime.strptime(
                val['timecreated'][:-6], datetime_format)

            prev = val['EntryID']
            previous_entries.append(new_val.copy())

        previous_entries[-1]['decision_date'] = val['timecreated']
        previous_entries[-1]['verdict'] = val['verdict']
        comment_details = {}
        deciderID, deciderName = (0, "")
        with connections['default'].cursor() as cursors:
            cursors.execute(
                f"select * from get_personal_id({val['DecisionMakerID']})")
            res = cursors.fetchone()
            res = res[0]
            deciderID = res['FacultyID']
            deciderName = res['first_name'] + " " + res['last_name']
            comment_details['from'] = deciderName

        if deciderID == val['ApplicantID'] or val['DecisionMakerID'] == val['ApplicantID']:
            comment_details['from'] = 'Me'
        else:
            comment_details['body'] = val['body']

        comment_details['createdon'] = datetime.strptime(
            val['timecreated'][:-6], datetime_format)
        comment_details['body'] = val['body']
        previous_entries[-1]['comms'].append(comment_details.copy())

    print(previous_entries, active)

    return render(request=request, template_name="status.html", context={'atv': active, 'act_cnt': len(active), 'past': previous_entries, 'past_cnt': len(previous_entries), 'has_permission': perm})
