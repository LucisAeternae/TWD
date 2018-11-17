from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    context_dict = {'boldmessage': "Crunchy, creamy, cookie, candy, cupcake!"}
    return render(request, 'rango\index.html', context=context_dict)
def about(request):
    return HttpResponse('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title> </title></head><body><p>Rango says here about page.</p><br><a href="/rango">main page</a></body></html>')
