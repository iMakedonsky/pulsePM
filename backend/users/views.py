from typing import Any

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic.base import View

from .forms import RegistrationForm


class LoginView(View):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return render(request, 'pulse/auth.html', {'login_form': AuthenticationForm()})

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('/')
        return render(request, 'pulse/auth.html', {'login_form': form})


class RegistrationView(View):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return render(request, 'pulse/sign-up.html', {'registration_form': RegistrationForm()})

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            try:
                get_user_model().objects.create_user(
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                )
            except IntegrityError:
                return HttpResponse(status=409, content='User already exists')
            return redirect('/auth/login')
        return render(request, 'pulse/sign-up.html', {'registration_form': form})


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect(to='login')
