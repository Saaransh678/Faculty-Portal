from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import LoginForm, NewApplicationForm
from django.contrib import messages
from django.http import HttpResponse
from login_app.models import Faculty, activeleaveentries
from main.models import Faculty, Active_Leave_Entries, Comments, Previous_Record
from datetime import datetime
from django.db import connections
# Create your views here.

departments = {'EE': 'Electrical',
               'ME': 'Mechanical', 'CSE': 'Computer Science'}

levels = ['Faculty', 'Head of Department', 'Dean Faculty Affairs', 'Director']


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


def get_active_leaves(user_id):
    check_querr = f'SELECT * FROM "main_active_leave_entries" where "FacultyID" = {user_id}'
    check_res = Active_Leave_Entries.objects.raw(check_querr)
    return (len(check_res), check_res)


def exec_querry(querry):
    cursor = connections['default'].cursor()
    cursor.execute(querry)


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
        redirect('/profile')

    return render(request=request, template_name="loginpage.html")


def logoutuser(request):
    logout(request)
    return redirect("/login")


def profile(request):
    user = request.user
    fullname = user.first_name + " " + user.last_name

    querry = f'SELECT * FROM main_faculty WHERE \"FacultyID\" ={user.id}'
    context_dict = {'email': user.email,
                    'name': fullname, 'uname': user.username}
    res = Faculty.objects.raw(querry)
    for faculty_details in res:
        context_dict['dept'] = departments[faculty_details.dept] + \
            " Department"
        context_dict['rem_leave'] = faculty_details.leaves_remaining
        context_dict['perm'] = levels[faculty_details.permission_level]

    return render(request=request, template_name="profile.html", context=context_dict)


def application(request):
    if request.method == 'POST':
        form = NewApplicationForm(request.POST)
        if form.is_valid():
            st_date = form.cleaned_data['startdate']
            end_date = form.cleaned_data['enddate']
            desc = clean_comments(form.cleaned_data['description'])

            check_res = get_active_leaves(request.user.id)

            if check_res[0] > 0:
                messages.error(
                    request, f"Error: You Already Have an Active Leave Entry with id = {check_res[1][0].id}")

            else:
                now = datetime.today().strftime('%Y-%m-%d')
                insert_querry = f'INSERT INTO "main_active_leave_entries"("FacultyID", application_date, starting_date, num_leaves, curr_status) VALUES({request.user.id}, \'{now}\', \'{st_date}\', {(end_date- st_date).days}, 0)'
                exec_querry(insert_querry)
                check_res = get_active_leaves(request.user.id)

                insert_comments = f"INSERT INTO main_Comments(\"EntryID\", timecreated, body, \"FromFacultyID\") VALUES({check_res[1][0].id}, '{now}', '{desc}', '{request.user.id}')"
                exec_querry(insert_comments)

                messages.success(
                    request, f"Succesfully Submitted new request with id = {check_res[1][0].id}. Check Status in Active Entries")

        else:
            print(form.error)

    return render(request=request, template_name="application.html")


def get_faculty_details(FacID):
    querry = f'SELECT * FROM main_faculty WHERE \"FacultyID\" ={FacID}'
    return Faculty.objects.raw(querry)


def get_comments_by_entryID(entryID, user_id):
    querry = f'SELECT * FROM "main_comments" WHERE "EntryID" = {entryID} ORDER BY timecreated'
    comm = Comments.objects.raw(querry)
    curr_com = []
    for com_entry in comm:
        com = {}
        com['body'] = com_entry.body
        if int(com_entry.FromFacultyID) == int(user_id):
            com['from'] = 'Me'
        else:
            res = get_faculty_details(com_entry.FromFacultyID)
            for details in res:
                from_post = levels[details.permission_level]
                if details.permission_level == 1:
                    from_post += " " + departments[details.dept]
                com['from'] = from_post
        curr_com.append(com)

    return curr_com


def status(request):
    user_id = request.user.id
    active = get_active_leaves(user_id)

    previous = Previous_Record.objects.raw(
        f'SELECT * FROM "main_previous_record" where "ApplicantID" = {user_id}')

    active_entries = []
    previous_entries = []

    for val in active[1]:
        curr = {}
        curr['id'] = val.id
        curr['application_date'] = val.application_date
        curr['start_date'] = val.starting_date
        curr['num'] = val.num_leaves
        curr['curr_status'] = levels[val.curr_status]
        curr['comms'] = get_comments_by_entryID(val.EntryID, user_id)
        active_entries.append(curr.copy())

    for val in previous:
        curr = {}
        curr['id'] = val.EntryID
        curr['application_date'] = val.starting_date
        curr['decision_date'] = val.decisiondate
        curr['num'] = val.num_leaves
        try:
            user = User.objects.get(id=val.DecisionMakerID)
        except User.DoesNotExist:
            messages.error("Unexpected Error Occured: Invalid From ID")
        curr['decisionBy'] = user.first_name + " " + user.last_name
        curr['was_approved'] = val.was_approved
        curr['comms'] = get_comments_by_entryID(val.EntryID, user_id)
        previous_entries.append(curr.copy())

    print(previous_entries)
    return render(request=request, template_name="status.html", context={'atv': active_entries, 'act_cnt': len(active_entries), 'past': previous_entries, 'past_cnt': len(previous_entries)})
