from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Hale is stimky butt</h1>")