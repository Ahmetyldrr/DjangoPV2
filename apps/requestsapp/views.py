from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from .models import UserRequest
from .forms import UserRequestForm


class UserRequestCreateView(CreateView):
    model = UserRequest
    form_class = UserRequestForm
    template_name = 'requestsapp/request_create.html'
    success_url = reverse_lazy('requestsapp:success')


class UserRequestSuccessView(TemplateView):
    template_name = 'requestsapp/request_success.html'
