from builtins import super, print, str, type

from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, ProcessFormView
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpResponseRedirect
from django.db import connection


# Create your views here.
class MainView(TemplateView):
    template_name = 'main.html'

    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect('mypage/')
        else:
            context = {'x': 'Здесь какая-то информация главной страницы, вроде новостей и т.п.'}
            return render(request, self.template_name, context)

class RegisterFormView(FormView):
    form_class = UserCreationForm
    success_url = '/'
    template_name = 'register.html'

    def form_valid(self, form):
        form.save()

        with connection.cursor() as c:
            c.execute("select max(id) from auth_user")
            id = c.fetchone()[0]
        name = form.data['name']
        surname = form.data['surname']
        age = form.data['age']
        sex = form.data['sex']
        city = form.data['city']
        interests = form.data['interests']

        with connection.cursor() as c:
            c.execute("insert into user_info (id, name, surname, age, sex, city, interests)"
                      " values (%s, %s, %s, %s, %s, %s, %s)", [id, name, surname, age, sex, city, interests])
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

class MyPageView(TemplateView):
    template_name = 'mypage.html'

    def get(self, request):
        if request.user.is_authenticated:
            with connection.cursor() as c:
                c.execute("select id from auth_user where username = %s", [self.request.user.username])
                id = c.fetchone()[0]
                c.execute("select name, surname, age, sex, city, interests from user_info "
                          "where id = %s", [id])
                name, surname, age, sex, city, interests = c.fetchall()[0]
                context = {'name': name, 'surname':surname, 'age': age, 'sex': sex, 'city': city, 'interests':interests}
            return render(request, self.template_name, context)
        else:
            return HttpResponseRedirect('main/')

class FriendsView(TemplateView):
    template_name = 'friends.html'

    def get(self, request):
        if request.user.is_authenticated:
            with connection.cursor() as c:
                c.execute("select id from auth_user where username = %s", [self.request.user.username])
                id = c.fetchone()[0]

                ''' Удалить из друзей '''
                user2_id = self.request.GET.get('user2_id')
                if user2_id:
                    if user2_id[-3:] == 'del':
                        pending = 0
                        user2_id = user2_id[:-3]
                        c.execute("delete from user_friends "
                                  "where pending = %s and user1_id = %s and user2_id = %s", [pending, id, user2_id])
                        c.execute("delete from user_friends "
                                  "where pending = %s and user1_id = %s and user2_id = %s", [pending, user2_id, id])
                ''' Удалить из друзей '''

                pending = 0
                c.execute("select user2_id from user_friends "
                          "where user1_id = %s and pending = %s", [id, pending])

                friends = c.fetchall()
                if friends:
                    c.execute("select id, name, surname, age, city from user_info "
                          "where id in %s", [friends])
                    context_data = c.fetchall()
                    context = {'context_data': context_data}
                    return render(request, self.template_name, context)
                else:
                    context = {'context_data': 'Ничего не найдено'}
                    return render(request, self.template_name, context)

class IncomeFriendsView(TemplateView):
    template_name = 'incomefriends.html'

    def get(self, request):
        if request.user.is_authenticated:
            with connection.cursor() as c:
                c.execute("select id from auth_user where username = %s", [self.request.user.username])
                id = c.fetchone()[0]

                ''' Подтверждение входящей заявки на дружбу '''
                user1_id = self.request.GET.get('user1_id')
                if user1_id:
                    if user1_id[-2:] == 'ok':
                        user1_id = user1_id[:-2]
                        pending = 1
                        c.execute("update user_friends set pending = 0  "
                                  "where pending = %s and user1_id = %s and user2_id = %s", [pending, user1_id, id])
                        pending = 0
                        c.execute("insert into user_friends (pending, user1_id, user2_id)"
                                  "values (%s, %s, %s)", [pending, id, user1_id])
                        # print(connection.queries, sep='\n')
                    elif user1_id[-2:] == 'no':
                        pending = 1
                        user1_id = user1_id[:-2]
                        c.execute("delete from user_friends "
                                  "where pending = %s and user1_id = %s and user2_id = %s", [pending, user1_id, id])
                ''' Подтверждение входящей заявки на дружбу '''


                pending = 1
                c.execute("select user1_id from user_friends "
                          "where user2_id = %s and pending = %s", [id, pending])

                friends = c.fetchall()
                if friends:
                    c.execute("select id, name, surname, age, city from user_info "
                          "where id in %s", [friends])
                    context_data = c.fetchall()
                    context = {'context_data': context_data}
                    return render(request, self.template_name, context)
                else:
                    context = {'context_data': 'Ничего не найдено'}
                    return render(request, self.template_name, context)

class OutcomeFriendsView(TemplateView):
    template_name = 'Outcomefriends.html'

    def get(self, request):
        if request.user.is_authenticated:
            with connection.cursor() as c:
                c.execute("select id from auth_user where username = %s", [self.request.user.username])
                id = c.fetchone()[0]

                ''' Отозвать заявку на дружбу '''
                user2_id = self.request.GET.get('user2_id')
                if user2_id:
                    if user2_id[-2:] == 'no':
                        pending = 1
                        user2_id = user2_id[:-2]
                        c.execute("delete from user_friends "
                                  "where pending = %s and user1_id = %s and user2_id = %s", [pending,id, user2_id])
                ''' Отозвать заявку на дружбу '''

                pending = 1
                c.execute("select user2_id from user_friends "
                          "where user1_id = %s and pending = %s", [id, pending])

                friends = c.fetchall()
                if friends:
                    c.execute("select id, name, surname, age, city from user_info "
                          "where id in %s", [friends])
                    context_data = c.fetchall()
                    context = {'context_data': context_data}
                    return render(request, self.template_name, context)
                else:
                    context = {'context_data': 'Ничего не найдено'}
                    return render(request, self.template_name, context)

class SearchView(FormView):
    form_class = ProcessFormView
    template_name = 'search.html'
    success_url = '/search/'

    def post(self, request):
        with connection.cursor() as c:
            form = self.get_form()

            form_name = form.data['name']
            form_name = f'%{form_name}%'

            form_surname = form.data['surname']
            form_surname = f'%{form_surname}%'

            if form_name == '%%' and form_surname == '%%':
                context = {'context_data': 'Нужно ввести данные'}
                return render(request, self.template_name, context)
            else:
                c.execute("select id from auth_user where username = %s", [self.request.user.username])
                id = c.fetchone()[0]
                c.execute("select id, name, surname, age, city from user_info "
                          "where name like %s and surname like %s and id != %s",
                                            [form_name, form_surname, id])

                # print(connection.queries, sep='\n')

                check = c.fetchall()
                if check:
                    context = {'context_data': check}
                    return render(request, self.template_name, context)
                else:
                    context = {'context_data': 'Ничего не найдено'}
                    return render(request, self.template_name, context)

class AnyUserView(TemplateView):
    template_name = 'anyuser.html'

    def get(self, request):
        if request.user.is_authenticated:
            with connection.cursor() as c:
                id = self.request.GET.get('id')
                c.execute("select name, surname, age, sex, city, interests from user_info "
                          "where id = %s", [id])
                name, surname, age, sex, city, interests = c.fetchall()[0]
                context = {'id': id, 'name': name, 'surname': surname, 'age': age, 'sex': sex, 'city': city,
                           'interests': interests}

                ''' Подружиться '''
                user1_id = self.request.GET.get('user1_id')
                if user1_id:
                    pending = 1
                    c.execute("insert into user_friends (pending, user1_id, user2_id) "
                              "values (%s, %s, %s)", [pending, user1_id, id])
                ''' Подружиться '''

                ''' Проверка на дружбу '''
                c.execute("select id from auth_user where username = %s", [self.request.user.username])
                user1_id = c.fetchone()[0]
                c.execute("select pending from user_friends "
                          "where user1_id = %s and user2_id = %s", [user1_id, id])
                pending = c.fetchone()
                print(pending)
                context['pending'] = pending
                context['user1_id'] = user1_id

            return render(request, self.template_name, context)
        else:
            return HttpResponseRedirect('main/')



