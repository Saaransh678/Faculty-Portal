from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import LoginForm, NewApplicationForm, RequestForm, ResponseForm, AppointmentForm, NewCourseForm, NewPublicationForm, bgform, PublicationForm, CoursesForm
from django.contrib import messages
from django.http import HttpResponse
# from login_app.models import Faculty, activeleaveentries
from main.models import Faculty, Active_Leave_Entries, Previous_Request_Record, Decision_Record, Previous_Cross_Cutting
# Comments, Previous_Record
from datetime import datetime
from django.db import connections
from pymongo import MongoClient
# Create your views here.

departments = {'EE': 'Electrical',
               'ME': 'Mechanical', 'CSE': 'Computer Science'}

levels = ['Faculty', 'Head of Department', 'Dean Faculty Affairs', 'Director']
posi = ["Director", "Dean Faculty Affairs", "HOD-cse", "HOD-ee", "HOD-me"]
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
    date = date[:-6]
    date = date.split('.')[0]
    return datetime.strptime(date, datetime_format)


def getBaseDetails(user_id):
    querry = f'SELECT * FROM get_personal_id({user_id})'
    cursor = connections['default'].cursor()
    cursor.execute(querry)
    res = cursor.fetchone()
    cursor.close()
    return res[0]


def mongoconnect():
    client = MongoClient(
        'mongodb+srv://admin_0:pass1234@cluster0.2449b.mongodb.net/dbms?retryWrites=true&w=majority')
    return (client, client.dbms.Data)


def index(request):
    # print(request.user)
    if request.user.is_anonymous:
        return redirect('/login')

    return redirect(f'/profile/id={request.user.id}')


def login_req(request):
    if request.user.is_anonymous:
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                print(request.POST)
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']

                user = authenticate(username=username, password=password)

                if user is not None:
                    messages.success(
                        request, f"Welcome back, {user.first_name}!!")
                    login(request, user)
                    return redirect(f'/profile/id={request.user.id}')

                else:
                    messages.error(
                        request, "Failed Login!! :'( Please Check Username/Password")

            else:
                print(form.errors)
                messages.error(
                    request, "Unexpected Error!! Try Refreshing the page")
    else:
        return redirect(f'/profile/id={request.user.id}')

    return render(request=request, template_name="loginpage.html")


def logoutuser(request):
    logout(request)
    return redirect("/login")


def profile(request, req_id, loc="home"):
    # print(loc)
    params = {'home': 0, 'background': 1, 'publications': 2, 'courses': 3}
    param_id = params[loc]
    (conn, collection) = mongoconnect()

    if request.user.is_anonymous:
        requester_id = -1
    else:
        requester_id = getBaseDetails(request.user.id)["FacultyID"]

    faculty_details = getBaseDetails(req_id)
    fullname = faculty_details['first_name'] + \
        " " + faculty_details['last_name']
    user_id = faculty_details["FacultyID"]

    context_dict = {}
    context_dict['email'] = faculty_details['email']
    context_dict['name'] = fullname
    context_dict['uname'] = faculty_details['username']
    context_dict['dept'] = departments[faculty_details['dept']] + \
        " Department"
    context_dict['rem_leave'] = faculty_details['leaves_remaining']
    context_dict['perm'] = levels[faculty_details['permission_level']]
    context_dict['has_permission'] = faculty_details['permission_level']

    context_dict['editor'] = (requester_id == user_id)

    if request.method == "POST":
        updates = {}
        new_course_form = NewCourseForm(request.POST)
        if new_course_form.is_valid():
            param_id = 3
            res = collection.find_one({'fac_id': user_id, 'courses': {
                                      '$elemMatch': {'code': new_course_form.cleaned_data['course_code']}
                                      }})

            if res == None:
                updates["$push"] = {}
                updates["$push"]['courses'] = {
                    "id": datetime.now().timestamp(),
                    'code': new_course_form.cleaned_data['course_code'],
                    'name': new_course_form.cleaned_data['course_name']
                }

            else:
                messages.error(
                    request, f"You already have an course with Course Code: {new_course_form.cleaned_data['course_code']}")
                print(res)

        pub_form = NewPublicationForm(request.POST)
        if pub_form.is_valid():
            param_id = 2
            res = collection.find_one({'fac_id': user_id, 'publications': {
                                      '$elemMatch': {'name': pub_form.cleaned_data['journal_name']}
                                      }})
            if res == None:
                if "$push" not in updates:
                    updates["$push"] = {}

                updates["$push"]['publications'] = {
                    "id": datetime.now().timestamp(),
                    'name': pub_form.cleaned_data['journal_name'],
                    'authors': pub_form.cleaned_data['authors'],
                    'year': pub_form.cleaned_data['year']
                }

            else:
                messages.error(
                    request, f"You already have a publication with Title {pub_form.cleaned_data['journal_name']}")

        backgrnd = bgform(request.POST)
        if backgrnd.is_valid():
            param_id = 1
            updates['$set'] = {'background': backgrnd.cleaned_data['desc']}

        pub_edit = PublicationForm(request.POST)
        if pub_edit.is_valid():
            param_id = 2
            if pub_edit.cleaned_data['is_delete']:
                if "$pull" not in updates:
                    updates["$pull"] = {}
                updates["$pull"]["publications"] = {
                    "id": pub_edit.cleaned_data['pub_id']}
            else:
                collection.update(
                    {'fac_id': user_id,
                        'publications.id': pub_edit.cleaned_data['pub_id']},
                    {"$set": {
                        "publications.$.name": pub_edit.cleaned_data['journ_name'],
                        "publications.$.year": pub_edit.cleaned_data['year'],
                        "publications.$.authors": pub_edit.cleaned_data['authors'],
                    }}
                )

        course_form = CoursesForm(request.POST)
        if course_form.is_valid():
            param_id = 3
            if course_form.cleaned_data['is_delete']:
                print(course_form.cleaned_data)
                if "$pull" not in updates:
                    updates["$pull"] = {}
                updates["$pull"]["courses"] = {
                    "id": course_form.cleaned_data['c_id']}
            else:
                collection.update(
                    {'fac_id': user_id,
                        'courses.id': course_form.cleaned_data['c_id']},
                    {"$set": {
                        "courses.$.name": course_form.cleaned_data['c_name'],
                        "courses.$.code": course_form.cleaned_data['c_code'],
                    }}
                )
        else:
            print(course_form.errors)

        if(bool(updates)):
            collection.update(
                {'fac_id': user_id},
                updates,
                upsert=True
            )

    profile_data = collection.find_one({'fac_id': user_id})

    if profile_data == None:
        context_dict['background'] = context_dict['publications'] = context_dict['courses'] = None
    else:
        fields = ['background', 'publications', 'courses']
        for val in fields:
            if val in profile_data:
                context_dict[val] = profile_data[val]
                if val != 'background':
                    for i in range(1, len(context_dict[val])+1):
                        context_dict[val][i-1]['num'] = i
            else:
                context_dict[val] = None

    context_dict['loc'] = param_id
    conn.close
    return render(request=request, template_name="profile.html", context=context_dict)


def requests(request):
    if request.user.is_anonymous:
        return redirect('/login')

    perm = 0
    user = request.user
    faculty_details = getBaseDetails(user.id)

    perm_level = faculty_details["permission_level"]
    department = faculty_details["dept"]
    user_id = faculty_details["FacultyID"]

    # perm_level = perm_level-1 -------------------------------------------------------------------------- CHECK
    if perm_level < 1:
        messages.warning(
            request, "Error!: You are not authorised for the action.")
        return redirect(f'/profile?id={user_id}')

    exec_querry("SELECT clean_db()")
    if request.method == "POST":
        req_form = RequestForm(request.POST)
        if req_form.is_valid():
            print(req_form.cleaned_data['faculty_id'])
            Comment = clean_comments(req_form.cleaned_data['comments'])
            Facultyid = getBaseDetails(req_form.cleaned_data['faculty_id'])['FacultyID']  # perm_level = perm_level-1 -------------------------------------------------------------------------- CHECK# perm_level = perm_level-1 -------------------------------------------------------------------------- CHECK# perm_level = perm_level-1 -------------------------------------------------------------------------- CHECK# perm_level = perm_level-1 -------------------------------------------------------------------------- CHECK# perm_level = perm_level-1 -------------------------------------------------------------------------- CHECK# perm_level = perm_level-1 -------------------------------------------------------------------------- CHECK
            verdict = req_form.cleaned_data['verdict']
            now = datetime.now()
            insert_record = ""
            insert_record1 = ""
            delete_record = ""
            update_record = ""
            update_record1 = ""
            update_leaves = ""
            querry = f"select * from main_active_leave_entries where \"FacultyID\" ={Facultyid}"
            res = Active_Leave_Entries.objects.raw(querry)
            for faculty_details in res:
                entryid = faculty_details.id
                current_status = faculty_details.curr_status
                appli_date = faculty_details.application_date
                start_date = faculty_details.starting_date
                leaves = faculty_details.num_leaves

            if verdict == '2':
                res = getBaseDetails(Facultyid)
                perm = res['permission_level']
                leave_cnt = res['leaves_remaining']

                if perm == 0:
                    if datetime.date(appli_date) > start_date:
                        if current_status == 3:
                            update_leaves = f"UPDATE main_faculty SET leaves_remaining = {leave_cnt - leaves} where \"FacultyID\" = {Facultyid}"
                            insert_record = f"INSERT INTO main_decision_record(\"EntryID\", timecreated, body, verdict, \"DecisionMakerID\", is_active) VALUES({entryid}, '{now}', '{Comment}', 2, '{request.user.id}', False)"
                            insert_record1 = f"INSERT INTO main_previous_request_record(\"EntryID\", \"ApplicantID\", starting_date, num_leaves, was_approved) VALUES({entryid}, '{Facultyid}',\'{start_date}\','{leaves}' , True)"
                            update_record1 = f"UPDATE main_decision_record SET is_active = false where \"EntryID\" = {entryid}"
                            delete_record = f"DELETE FROM main_active_leave_entries WHERE id={entryid}"

                        else:
                            insert_record = f"INSERT INTO main_decision_record(\"EntryID\", timecreated, body, verdict, \"DecisionMakerID\", is_active) VALUES({entryid}, '{now}', '{Comment}', 2, '{request.user.id}', True)"
                            update_record = f"UPDATE  main_active_leave_entries SET curr_status={current_status+1} WHERE id={entryid} "
                    else:
                        if current_status == 2:
                            update_leaves = f"UPDATE main_faculty SET leaves_remaining = {leave_cnt - leaves} where \"FacultyID\"= {Facultyid}"
                            insert_record = f"INSERT INTO main_decision_record(\"EntryID\", timecreated, body, verdict, \"DecisionMakerID\", is_active) VALUES({entryid}, '{now}', '{Comment}', 2, '{request.user.id}', False)"
                            insert_record1 = f"INSERT INTO main_previous_request_record(\"EntryID\", \"ApplicantID\", starting_date, num_leaves, was_approved) VALUES({entryid}, '{Facultyid}',\'{start_date}\','{leaves}' , True)"
                            update_record1 = f"UPDATE main_decision_record SET is_active = false where \"EntryID\" = {entryid}"
                            delete_record = f"DELETE FROM main_active_leave_entries WHERE id={entryid}"
                        else:
                            insert_record = f"INSERT INTO main_decision_record(\"EntryID\", timecreated, body, verdict, \"DecisionMakerID\", is_active) VALUES({entryid}, '{now}', '{Comment}', 2, '{request.user.id}', True)"
                            update_record = f"UPDATE  main_active_leave_entries SET curr_status={current_status+1} WHERE id={entryid} "

                elif perm == 1 or perm == 2:
                    update_leaves = f"UPDATE main_faculty SET leaves_remaining = {leave_cnt - leaves} where \"FacultyID\"= {Facultyid}"
                    insert_record = f"INSERT INTO main_decision_record(\"EntryID\", timecreated, body, verdict, \"DecisionMakerID\", is_active) VALUES({entryid}, '{now}', '{Comment}', 2, '{request.user.id}', False)"
                    insert_record1 = f"INSERT INTO main_previous_request_record(\"EntryID\", \"ApplicantID\", starting_date, num_leaves, was_approved) VALUES({entryid}, '{Facultyid}',\'{start_date}\','{leaves}' , True)"
                    update_record1 = f"UPDATE main_decision_record SET is_active = false where \"EntryID\" = {entryid}"
                    delete_record = f"DELETE FROM main_active_leave_entries WHERE id={entryid}"

            elif verdict == '1':
                insert_record = f"INSERT INTO main_decision_record(\"EntryID\", timecreated, body, verdict, \"DecisionMakerID\", is_active) VALUES({entryid}, '{now}', '{Comment}', 1, '{request.user.id}', True)"
                update_record = f"UPDATE  main_active_leave_entries SET curr_status={0} WHERE id={entryid} "

            elif verdict == '0':
                insert_record = f"INSERT INTO main_decision_record(\"EntryID\", timecreated, body, verdict, \"DecisionMakerID\", is_active) VALUES({entryid}, '{now}', '{Comment}', 0, '{request.user.id}', False)"
                insert_record1 = f"INSERT INTO main_previous_request_record(\"EntryID\", \"ApplicantID\", starting_date, num_leaves, was_approved) VALUES({entryid}, '{Facultyid}',\'{start_date}\','{leaves}' , False)"
                delete_record = f"DELETE FROM main_active_leave_entries WHERE id={entryid}"
                update_record1 = f"UPDATE main_decision_record SET is_active = false where \"EntryID\" = {entryid}"

            if(len(insert_record) != 0):
                exec_querry(insert_record)
            if(len(insert_record1) != 0):
                exec_querry(insert_record1)
            if(len(delete_record) != 0):
                exec_querry(delete_record)
            if(len(update_record) != 0):
                exec_querry(update_record)
            if(len(update_record1) != 0):
                exec_querry(update_record1)
            if(len(update_leaves) != 0):
                exec_querry(update_leaves)
        else:
            print(req_form.errors)

    querry = f'select * from get_active_requests({perm_level}, \'{department}\');'
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
            obj['comms'] = get_comments_by_entryID(
                val.id, facul_id, True, True, user_id)
        entries.append(obj.copy())

    return render(request=request, template_name="requests.html", context={'details': entries, 'has_permission': perm_level})


def application(request):
    perm = False
    leave_cnt = 0
    if request.user.is_anonymous:
        return redirect('/login')

    exec_querry("SELECT clean_db()")

    res = getBaseDetails(request.user.id)
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
                insert_querry = f'INSERT INTO "main_active_leave_entries"("FacultyID", application_date, starting_date, num_leaves, curr_status) VALUES({user_id}, \'{datetime.today()}\', \'{st_date}\', {(end_date - st_date).days}, {1 if perm==0 else 3})'
                exec_querry(insert_querry)

                check_res = get_active_leaves(user_id)
                insert_record = f"INSERT INTO main_decision_record(\"EntryID\", timecreated, body, verdict, \"DecisionMakerID\", is_active) VALUES({check_res[1][0].id}, '{datetime.now()}', '{desc}', -1, '{user_id}', True)"
                exec_querry(insert_record)

                messages.success(
                    request, f"Succesfully Submitted new request with id = {check_res[1][0].id}. Check Status in Active Entries")

        else:
            print(form.error)

    return render(request=request, template_name="application.html", context={'has_permission': perm, 'max_leaves': leave_cnt})


def get_faculty_details(FacID):
    querry = f'SELECT * FROM main_faculty WHERE \"FacultyID\" ={FacID}'
    return Faculty.objects.raw(querry)


def get_comments_by_entryID(entryID, user_id, is_act=False, is_third_party=False, third_id=-1):
    comp_id = -1
    if is_third_party:
        comp_id = third_id
    else:
        comp_id = user_id
    querry = f'SELECT * FROM "main_decision_record" WHERE "EntryID" = {entryID} and is_active = {is_act} ORDER BY timecreated'
    comm = Decision_Record.objects.raw(querry)
    curr_com = []
    for com_entry in comm:
        com = {}
        com['body'] = com_entry.body
        com['verdict'] = com_entry.verdict
        com['DecisionMakerID'] = com_entry.DecisionMakerID

        if int(com_entry.DecisionMakerID) == int(comp_id):
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
    if(request.user.is_anonymous):
        return redirect('/login')
    perm = 0
    exec_querry("SELECT clean_db()")

    res = getBaseDetails(request.user.id)
    user_id = res['FacultyID']
    perm = res['permission_level']

    if request.method == "POST":
        form = ResponseForm(request.POST)
        if form.is_valid():
            comm = clean_comments(form.cleaned_data['comments'])
            entryid = form.cleaned_data['entryid']

            dec_record = get_comments_by_entryID(entryid, user_id, True)
            prev_id = dec_record[-1]['DecisionMakerID']
            updated_level = get_faculty_details(prev_id)[0].permission_level

            dec_rec = f'INSERT INTO main_decision_record("EntryID", timecreated, body, "DecisionMakerID", verdict, is_active) VALUES({entryid}, \'{datetime.now()}\', \'{comm}\', {user_id}, -1,  True)'
            update_record = f"UPDATE  main_active_leave_entries SET curr_status={updated_level} WHERE id={entryid}"
            exec_querry(dec_rec)
            exec_querry(update_record)

        else:
            print(form.errors)

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
        res = getBaseDetails(val['DecisionMakerID'])
        deciderID = res['FacultyID']
        deciderName = res['first_name'] + " " + \
            res['last_name'] + f" ({levels[res['permission_level']]})"
        comment_details['from'] = deciderName

        if deciderID == val['FacultyID'] or val['DecisionMakerID'] == val['FacultyID']:
            comment_details['from'] = 'Me'
        else:
            comment_details['from'] = deciderName
        comment_details['body'] = val['body']

        print(clean_date(val['timecreated']))
        comment_details['createdon'] = clean_date(val['timecreated'])
        active[-1]['comms'].append(comment_details.copy())

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
            new_val['num'] = val['num_leaves']
            new_val['application_date'] = clean_date(val['timecreated'])

            prev = val['EntryID']
            previous_entries.append(new_val.copy())

        previous_entries[-1]['decision_date'] = clean_date(val['timecreated'])
        previous_entries[-1]['was_approved'] = bool(val['verdict'])
        comment_details = {}
        deciderID, deciderName = (0, "")

        if val['DecisionMakerID'] == -1:
            comment_details['from'] = 'Default'
        else:
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
                comment_details['from'] = deciderName

        previous_entries[-1]['decisionBy'] = comment_details['from']
        comment_details['body'] = val['body']

        comment_details['createdon'] = clean_date(val['timecreated'])
        comment_details['body'] = val['body']
        comment_details['succ'] = bool(val['verdict'] == 2)
        comment_details['prim'] = bool(val['verdict'] == 1)
        comment_details['dang'] = bool(val['verdict'] == 0)
        previous_entries[-1]['comms'].append(comment_details.copy())

    # print(previous_entries, active)

    return render(request=request, template_name="status.html", context={'atv': active, 'act_cnt': len(active), 'past': previous_entries, 'past_cnt': len(previous_entries), 'has_permission': perm})


def appointment(request):
    if request.user.is_anonymous:
        return redirect('/login')
    exec_querry("SELECT clean_db()")
    user_id = request.user.id
    perm = -1
    with connections['default'].cursor() as cursors:
        cursors.execute(
            f"select * from get_personal_id({user_id})")
        res = cursors.fetchone()
        res = res[0]
        perm = res['permission_level']
        user_id = res['FacultyID']

    if perm < 1:
        messages.warning(
            request, "Error: You don't have permission for that action")
        return redirect(f'/profile?id={user_id}')
    # -------------------------------------------------________________________________________________________________________________________---------------------------------------------------------------------------------
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            posts = [2, 1, 1, 1]
            perm_level = posts[form.cleaned_data['post_id']]
            with connections['default'].cursor() as cursors:
                cursors.execute(
                    f"select * from get_personal_id({form.cleaned_data['post_id']+2})")
                res = cursors.fetchone()
                res = res[0]
                date_joined = res['date_joined']
                facultyid = res['FacultyID']
            with connections['default'].cursor() as cursors:
                cursors.execute(
                    f"select * from get_personal_id({form.cleaned_data['new_fac_id']})")
                res = cursors.fetchone()
                res = res[0]
                first_name = res['first_name']
                last_name = res['last_name']
            update1 = f"UPDATE auth_user SET first_name='{first_name}' , last_name='{last_name}', date_joined='{datetime.now()}' WHERE id= {form.cleaned_data['post_id']+2}"
            update2 = f"UPDATE main_faculty SET permission_level=0 WHERE  \"FacultyID\"={facultyid}"
            update3 = f"UPDATE main_faculty SET permission_level={perm_level} WHERE  \"FacultyID\"={form.cleaned_data['new_fac_id']}"
            insert1 = f"INSERT INTO main_previous_cross_cutting( \"FacultyID\", timebegin , timeend , permission_level) VALUES({facultyid}, \'{date_joined}\',\'{datetime.now()}\', {perm_level})"
            exec_querry(update1)
            exec_querry(update2)
            exec_querry(update3)
            exec_querry(insert1)
            print(form.cleaned_data)

        else:
            print(form.errors)
    # ----------------------------------------------________________##########################_####################------------------------------------------------------------------------------------
    with connections['default'].cursor() as cursors:
        cursors.execute(
            f"select * from get_personal_id({2})")
        res = cursors.fetchone()
        res = res[0]
        deaninfo = {}
        deaninfo['position'] = posi[1]
        deaninfo['user_id'] = 2
        deaninfo['name'] = res['first_name']+" "+res['last_name']
    with connections['default'].cursor() as cursors:
        cursors.execute(
            f"select * from get_personal_id({3})")
        res = cursors.fetchone()
        res = res[0]
        hodcseinfo = {}
        hodcseinfo['position'] = posi[2]
        hodcseinfo['user_id'] = 3
        hodcseinfo['name'] = res['first_name']+" "+res['last_name']

    with connections['default'].cursor() as cursors:
        cursors.execute(
            f"select * from get_personal_id({4})")
        res = cursors.fetchone()
        res = res[0]
        hodeeinfo = {}
        hodeeinfo['position'] = posi[3]
        hodeeinfo['user_id'] = 4
        hodeeinfo['name'] = res['first_name']+" "+res['last_name']

    with connections['default'].cursor() as cursors:
        cursors.execute(
            f"select * from get_personal_id({5})")
        res = cursors.fetchone()
        res = res[0]
        hodmeinfo = {}
        hodmeinfo['position'] = posi[4]
        hodmeinfo['user_id'] = 5
        hodmeinfo['name'] = res['first_name']+" "+res['last_name']

    mech = []
    with connections['default'].cursor() as cursors:
        cursors.execute(f"Select * from get_department_data('ME')")
        result = cursors.fetchall()

    dean = []
    for val in result:
        val = val[0]
        new_val = {}
        new_val['facultyid'] = val['FacultyID']
        new_val['name'] = val['first_name']+" "+val['last_name']
        new_val['dept'] = 'ME'
        mech.append(new_val.copy())
        dean.append(new_val.copy())

    elec = []
    with connections['default'].cursor() as cursors:
        cursors.execute(f"Select * from get_department_data('EE')")
        result = cursors.fetchall()

    for val in result:
        val = val[0]
        new_val = {}
        new_val['facultyid'] = val['FacultyID']
        new_val['name'] = val['first_name']+" "+val['last_name']
        new_val['dept'] = 'EE'
        elec.append(new_val.copy())
        dean.append(new_val.copy())

    cse = []
    with connections['default'].cursor() as cursors:
        cursors.execute(f"Select * from get_department_data('CSE')")
        result = cursors.fetchall()

    for val in result:
        val = val[0]
        new_val = {}
        new_val['facultyid'] = val['FacultyID']
        new_val['name'] = val['first_name']+" "+val['last_name']
        new_val['dept'] = 'CSE'
        cse.append(new_val.copy())
        dean.append(new_val.copy())

    return render(request=request, template_name="appointment.html", context={'deaninfo': deaninfo, 'hodcseinfo': hodcseinfo, 'hodeeinfo': hodeeinfo, 'hodmeinfo': hodmeinfo, 'Mechanical': mech, 'Electrical': elec, 'computer': cse, 'Dean': dean, 'has_permission': perm})


def faculty(request):
    if request.method == "POST":

        form = AppointmentForm(request.POST)
        if form.is_valid():
            fac_id = form.cleaned_data['new_fac_id']
            return redirect(f'/profile/id={fac_id}')
    with connections['default'].cursor() as cursors:
        cursors.execute(
            f"select * from get_personal_id({1})")
        res = cursors.fetchone()
        res = res[0]
        dirinfo = {}
        dirinfo['position'] = posi[0]
        dirinfo['user_id'] = 1
        dirinfo['name'] = res['first_name']+" "+res['last_name']
    with connections['default'].cursor() as cursors:
        cursors.execute(
            f"select * from get_personal_id({2})")
        res = cursors.fetchone()
        res = res[0]
        deaninfo = {}
        deaninfo['position'] = posi[1]
        deaninfo['user_id'] = 2
        deaninfo['name'] = res['first_name']+" "+res['last_name']
    with connections['default'].cursor() as cursors:
        cursors.execute(
            f"select * from get_personal_id({3})")
        res = cursors.fetchone()
        res = res[0]
        hodcseinfo = {}
        hodcseinfo['position'] = posi[2]
        hodcseinfo['user_id'] = 3
        hodcseinfo['name'] = res['first_name']+" "+res['last_name']

    with connections['default'].cursor() as cursors:
        cursors.execute(
            f"select * from get_personal_id({4})")
        res = cursors.fetchone()
        res = res[0]
        hodeeinfo = {}
        hodeeinfo['position'] = posi[3]
        hodeeinfo['user_id'] = 4
        hodeeinfo['name'] = res['first_name']+" "+res['last_name']

    with connections['default'].cursor() as cursors:
        cursors.execute(
            f"select * from get_personal_id({5})")
        res = cursors.fetchone()
        res = res[0]
        hodmeinfo = {}
        hodmeinfo['position'] = posi[4]
        hodmeinfo['user_id'] = 5
        hodmeinfo['name'] = res['first_name']+" "+res['last_name']

    mech = []
    with connections['default'].cursor() as cursors:
        cursors.execute(f"Select * from get_department_data('ME')")
        result = cursors.fetchall()

    dean = []
    for val in result:
        val = val[0]
        new_val = {}
        new_val['facultyid'] = val['FacultyID']
        new_val['name'] = val['first_name']+" "+val['last_name']
        new_val['dept'] = 'ME'
        mech.append(new_val.copy())
        dean.append(new_val.copy())

    elec = []
    with connections['default'].cursor() as cursors:
        cursors.execute(f"Select * from get_department_data('EE')")
        result = cursors.fetchall()

    for val in result:
        val = val[0]
        new_val = {}
        new_val['facultyid'] = val['FacultyID']
        new_val['name'] = val['first_name']+" "+val['last_name']
        new_val['dept'] = 'EE'
        elec.append(new_val.copy())
        dean.append(new_val.copy())

    cse = []
    with connections['default'].cursor() as cursors:
        cursors.execute(f"Select * from get_department_data('CSE')")
        result = cursors.fetchall()

    for val in result:
        val = val[0]
        new_val = {}
        new_val['facultyid'] = val['FacultyID']
        new_val['name'] = val['first_name']+" "+val['last_name']
        new_val['dept'] = 'CSE'
        cse.append(new_val.copy())
        dean.append(new_val.copy())
    return render(request=request, template_name="faculties.html", context={'deaninfo': deaninfo,'dirinfo': dirinfo, 'hodcseinfo': hodcseinfo, 'hodeeinfo': hodeeinfo, 'hodmeinfo': hodmeinfo, 'Mechanical': mech, 'Electrical': elec, 'computer': cse, 'Dean': dean})
