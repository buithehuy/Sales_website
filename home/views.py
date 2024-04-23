from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.core.mail import EmailMessage, send_mail
from django.contrib import messages
from Sales_website import settings
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.shortcuts import HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from . tokens import generate_token
import mysql.connector
import random
import string


mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database = 'sales_website'
)
# Create your views here.
def get_home(request) :
    return render(request, 'home.html')

# def register(request) :
#     if request.user.is_authenticated:
#         return redirect('/')
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password1')
#             user = authenticate(username=username, password=password)
#             login(request, user)
#             return redirect('/')
#         else:
#             return render(request, 'register.html', {'form': form})
#     else:
#         form = UserCreationForm()
#         return render(request, 'register.html', {'form': form})
def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        email = request.POST["email"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('register')

        if len(username) > 20:
            messages.error(request, "Username must be under 20 charcters!!")
            return redirect('register')

        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('register')

        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('register')
        myuser = User.objects.create_user(username, email, pass1)
        myuser.fname = fname
        myuser.lname = lname
        # myuser.is_active = False
        myuser.is_active = False
        myuser.save()
        messages.success(request,
                         "Your Account has been created succesfully!! Please check your email to confirm your email address in order to activate your account.")

        # Welcome Email
        subject = "Welcome to ThreeBoys"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to ThreeBoys!! \nThank you for visiting our website\n. We have also sent you a confirmation email, please confirm your email address. \n\nThanking You\nShovit Nepal"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # Email Address Confirmation Email
        current_site = get_current_site(request)
        email_subject = "Confirm your Email !"
        message2 = render_to_string('email_confirmation.html', {
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        send_mail(email_subject, message2, from_email, to_list, fail_silently=True)
        return redirect('login')

    return render(request, "register.html")
def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('login')
    else:
        return render(request,'activation_failed.html')
def log_out(request) :
    logout (request)
    return redirect('/')
list = []

def generate_otp():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def forget_password(request):
    if request.method == 'POST':
        username_f = request.POST["username"]
        email_f = request.POST['email']
        sql = f'SELECT * FROM auth_user ' \
              f'WHERE username =\'{username_f}\' ' \
              f'AND email = \'{email_f}\' '

        mycursor = mydb.cursor()
        mycursor.execute(sql)
        auth = mycursor.fetchall()

        if len(auth) == 0:
            return render(request, 'forget_password.html', {'msg': 'Tên người dùng hoặc email không chính xác'})
        else:
            otp = generate_otp()
            # Save the OTP in the server's memory or database
            request.session['otp'] = otp
            request.session['email'] = email_f

            # Send OTP to the user's email
            subject = "Password Reset OTP"
            message = f"Your OTP for password reset is: {otp}"
            from_email = settings.EMAIL_HOST_USER
            to_list = [email_f]
            send_mail(subject, message, from_email, to_list)

            return redirect('otp_confirmation')

    return render(request, 'forget_password.html')

def otp_confirmation(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        if otp_entered == request.session.get('otp'):
            # OTP is correct, proceed to new password confirmation
            return redirect('new_password')
        else:
            return render(request, 'otp_confirmation.html', {'msg': 'Invalid OTP. Please try again.'})
    return render(request, 'otp_confirmation.html')


def new_password(request):
    if request.method == 'POST':
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        if pass1 == pass2:
            current_user = User.objects.get(email=request.session.get('email'))
            current_user.set_password(pass1)
            current_user.save()
            messages.success(request, "Password changed successfully")
            del request.session['otp']
            del request.session['email']
            return redirect('login')
        else:
            return render(request, 'new_password.html', {'msg': 'Passwords do not match'})
    return render(request, 'new_password.html')

def log_in(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/profile') 
        else:
            msg = 'Error Login'
            form = AuthenticationForm(request.POST)
            return render(request, 'login.html',{'msg':msg})
    else:
        form = AuthenticationForm()
        return render(request, 'login.html')
    
def profile(request) :
    return render(request, 'profile.html')



