from django.shortcuts import render, redirect
from .forms import NewUserForm
from django.contrib.auth import login
from django.contrib import messages
from django.http import HttpResponse


def index(request):
    return render(request, 'index.html', {})


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Successfully Registered.")
            return redirect('/login/')
        messages.error(request, "Unsuccessful Registration")
    form = NewUserForm
    return render(request=request, template_name="main\\register.html", context={"register_form": form})


def sample_render(request):
    messages.success(request, "Succesful Load")
    return redirect('/')
    # return HttpResponse("Good Load")
