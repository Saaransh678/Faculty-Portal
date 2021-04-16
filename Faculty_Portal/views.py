from django.http import HttpResponse


def base_page(request):
    return HttpResponse("Index Page")
