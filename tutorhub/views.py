from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Tutor Hub in progress</h1>")