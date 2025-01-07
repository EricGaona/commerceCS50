from django.shortcuts import render
import os
from dotenv import load_dotenv, dotenv_values


from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required



# Create your views here.
VONAGE_API_KEY = os.getenv('VONAGE_API_KEY') 
VONAGE_API_SECRET = os.getenv('VONAGE_API_SECRET')

def index(request):
    print("------- 1 -------")
    print(VONAGE_API_KEY)
    print(VONAGE_API_SECRET)
    # user = User.objects.get(username=request.user.username)  DA ERROR SI NO ESTA LOGUEADO
    # users = User.objects.all()
    # print(f"SOY user ---QuerySet--- >>> {users}")
    # print(" ----- 1 -------------- ")
    # users_json = User.objects.all().values()
    # print(f"SOY user_json ----- >>> {users_json}")
    # print(" ----- 2 -------------- ")
    return render(request, "auctions/index.html")