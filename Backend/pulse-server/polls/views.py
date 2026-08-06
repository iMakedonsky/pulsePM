from django.http import HttpResponse
from dotenv import dotenv_values

ENV = dotenv_values()

def home(req):
    return HttpResponse("<h1>home page</h1>")

def index(req):
    return HttpResponse(f'Hello {ENV["NAME"]}!')