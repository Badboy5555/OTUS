from builtins import super

from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpResponseRedirect


# Create your views here.
class IndexView(TemplateView):
    template_name = 'Index.html'

class MaiView(TemplateView):
    template_name = 'main.html'

    def get(self, request):
        if request.user.is_authenticated:
            context= {'x': 'Здесь будет список друзей, вся инфа о пользователе.'}
            return render(request, self.template_name, context)
        else:
            context = {'x': 'Здесь какая-то информация главной страницы, вроде новостей и т.п.'}
            return render(request, self.template_name, context)

class RegisterFormView(FormView):
    form_class = UserCreationForm
    success_url = '/main/'
    template_name = 'register.html'

    def form_valid(self, form):
        form.save()
        return super(RegisterFormView, self).form_valid(form)
    
    def form_invalid(self, form):
        return super(RegisterFormView, self).form_invalid(form)

class LoginFormView(FormView):
    form_class = AuthenticationForm
    success_url = '/'
    template_name = 'login.html'

    def form_valid(self, form):
        self.user = form.get_user()

        login(self.request, self.user)
        return super(LoginFormView, self).form_valid(form)

    def form_invalid(self, form):
        return super(LoginFormView, self).form_invalid(form)

class LogoutView(TemplateView):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/')

