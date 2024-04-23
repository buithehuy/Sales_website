from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_home, name='home'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('login/', views.log_in, name='login'),
    path('register/', views.signup, name='register'),
    path('logout/', views.log_out, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('login/forget_password/', views.forget_password, name='forget_password'),
    path('login/forget_password/new_password/', views.new_password, name='new_password'),
    path('login/forget_password/otp_confirmation/', views.otp_confirmation, name="otp_confirmation"),

]


