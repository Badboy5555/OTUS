from django.urls import path, include
from . import views

urlpatterns = [

    path('register/', views.RegisterFormView.as_view()),
    path('login/', views.LoginFormView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('mypage/', views.MyPageView.as_view()),
    path('friends/', views.FriendsView.as_view()),
    path('incomefriends/', views.IncomeFriendsView.as_view()),
    path('outcomefriends/', views.OutcomeFriendsView.as_view()),
    path('search/', views.SearchView.as_view()),
    path('anyuser/', views.AnyUserView.as_view()),
    path('', views.MainView.as_view()),
]
