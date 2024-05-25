
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.core.mail import EmailMessage, send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from Sales_website import settings
from django.utils import timezone 
import json
from django.db.models import F, FloatField, ExpressionWrapper


from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, View
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from . tokens import generate_token
import mysql.connector
import datetime
from  .models import *
from .forms import CheckoutForm, CouponForm, RefundForm
from .add_data import add_data,create_categories
import random
import string


############################
# create_categories()
# add_data()
#############################

from django.http import JsonResponse
def search_suggestions(request):
    query = request.GET.get('query', '')
    if query:
        products = Item.objects.filter(title__icontains=query)[:4]
        suggestions = []
        for product in products:
            suggestions.append({
                'name': product.title,
                'price': product.price,
                'url': product.get_absolute_url(),  # Assuming you have this method
                'image_url': product.image.url if product.image else None  # Adjust based on your model
            })
        return JsonResponse({'suggestions': suggestions})
    return JsonResponse({'suggestions': []})

# # chay tren docker 
mydb = mysql.connector.connect(
    host='db',
    user='your_username',
    password='your_password',
    database = 'sale_website'
)
################ chạy trên local
# mydb = mysql.connector.connect(
#     host='localhost',
#     user='root',
#     password='',
#     database = 'sales_website'
# )

# Create your views here.
def get_home(request) :

    return render(request, 'index.html')

def get_ordersum(request):
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        context = {
                'object': order
        }
        return render(request, 'order_summary.html', context)
    except ObjectDoesNotExist:
        messages.error(request, "Bạn chưa có đơn hàng nào")
        return redirect("/")

def get_ordered(request):
    try:
        order = Order.objects.filter(user=request.user, ordered=True)
        context = {
                'objects': order
        }
        if request.method == 'POST':
            if 'received' in request.POST:
                code = request.POST['received']
                order = Order.objects.get(user=request.user, ordered=True,ref_code=code)
                order.received = True
                order.save()
                return redirect('ordered')

        return render(request, 'ordered.html', context)
    except ObjectDoesNotExist:
        messages.error(request, "Bạn chưa có đơn hàng nào")
        return redirect("/")
    
def add_feedback(request,titles):
    if request.method == 'POST':
        title = request.POST['item_feed']
        start = request.POST['rate']
        content = request.POST['content']
        item = Item.objects.get(title=title)
        
        feedback = FeedBack.objects.create(
                    user = request.user,
                    items = item,
                    content = content,
                    start = start
                )
        item.feedback.add(feedback)
        return redirect('ordered')
    try:
        feedback = FeedBack.objects.get(user=request.user,items=titles)
        return redirect('ordered')
    except ObjectDoesNotExist:
        item = Item.objects.get(title = titles)
        return render(request, 'feedback.html',{'title':titles,'item':item})
    
def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        email = request.POST["email"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]

        if User.objects.filter(username=username):
            return render(request,'register.html', {'username_error': 'Username already exist! Please try some other username.'})

        if User.objects.filter(email=email).exists():
            # messages.error(request, "Email Already Registered!!")
            return render(request,'register.html',{'email_error':'Email Already Registered!!'})

        if len(username) > 20:
            return render(request,'register.html',{'username_error': 'Username must be under 20 charcters!!'})

        if pass1 != pass2:
            return render(request,'register.html',{'password_error':"Passwords didn't matched!!"})

        if not username.isalnum():
            # messages.error(request, "Username must be Alpha-Numeric!!")
            return render(request,'register.html',{'username_error': 'Username must be Alpha-Numeric!!'})

        myuser = User.objects.create_user(username, email, pass1)
        InfoUser.objects.create(
            user=myuser,
            birth_date= timezone.now()
        )
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()
        Order.objects.create(
            user=myuser, ordered_date=timezone.now(),ref_code=random.randint(10000,99999)  )
        ShipAddress.objects.create(user = myuser)
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
            return render(request, 'otp_confirmation.html', {'msg': 'Incorrect OTP. Please try again.'})
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
        return render(request, 'index.html')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:

                ShipAddress.objects.create(user = request.user)

                return redirect('admin:index')
            else:
                return redirect('home')
        else:
            msg = 'Error Login'
            form = AuthenticationForm(request.POST)
            return render(request, 'login.html',{'msg':msg})
    else:
        form = AuthenticationForm()
        return render(request, 'login.html')
    


from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import random
from .models import Item, Order, RecentlyViewedItems
from .recommendations import get_recommendations

from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import random
from .models import Item, Order, RecentlyViewedItems
from .recommendations import get_recommendations, get_knn_recommendations

def get_product(request, slug):
    product = Item.objects.get(slug=slug)
    template_name = "product-detail.html"

    # Track recently viewed items
    if request.user.is_authenticated:
        RecentlyViewedItems.objects.create(user=request.user, item=product, date=timezone.now())

    # Content-Based Recommendations
    content_recommendations = get_recommendations(product.title)
    content_recommendation_items = Item.objects.filter(title__in=content_recommendations)

    # Collaborative Filtering Recommendations
    # collaborative_recommendations = get_knn_recommendations(product.id)
    # collaborative_recommendation_items = Item.objects.filter(id__in=collaborative_recommendations)

    context = {
        'object': product,
        'content_recommendation_items': content_recommendation_items,
        # 'collaborative_recommendation_items': collaborative_recommendation_items
    }

    if request.user.is_authenticated:
        try:
            order = Order.objects.get(user=request.user, ordered=False)
        except ObjectDoesNotExist:
            order = Order.objects.create(user=request.user, ordered_date=timezone.now(), ref_code=random.randint(10000, 99999))
            context['order'] = order

    return render(request, template_name, context)




def add_to_cart(request, slug):
    if request.user.is_authenticated :
        item = Item.objects.get(slug=slug)
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False
        )
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.items.filter(item__slug=item.slug).exists():
                order_item.quantity += 1
                order_item.save()
                messages.info(request, "Item qty was updated.")
                return redirect("order-summary")
            else:
                order.items.add(order_item)
                messages.info(request, "Thêm thành công sảm phẩm vào giỏ hàng.")
                return redirect("order-summary")
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=request.user, ordered_date=ordered_date,ref_code=random.randint(10000,99999) )
            order.items.add(order_item)
            messages.info(request, "Thêm thành công sảm phẩm vào giỏ hàng.")
        return redirect("order-summary")
    else:
        messages.success(request, "Vui lòng đăng nhập để thêm vào giỏi hàng!")
        return redirect('login')


def get_category(request, slug=None):
    sorting = request.GET.get('sorting')
    search = request.GET.get('search-product')
    if search == None:
        search = ''
    if slug:
        category = Category.objects.get(slug=slug)
        items = Item.objects.filter(category=category, is_active=True) 
        if search != '':
            items = Item.objects.filter(title__icontains=search, is_active=True)
            # return redirect(f'category/?search-product={search}')

    else:
        items = Item.objects.all()
        if search != '':
            items = Item.objects.filter(title__icontains=search, is_active=True)
            # return redirect(f'category/?search-product={search}')
            
    if sorting == 'deepest_discount':
        items = items.filter(discount_price__isnull=False).annotate(
            discount_ratio=ExpressionWrapper(F('discount_price') / F('price'), output_field=FloatField())
        ).order_by('discount_ratio')
    elif sorting == 'price_asc':
        items = items.order_by('price')
    elif sorting == 'price_desc':
        items = items.order_by('-price')
    context = {
            'object_list': items,
            'category_title': category.title if slug else None,
            'category_description': category.description if slug else None,
            'category_image': category.image if slug else None,
            'search_pro':search
        }
    if search != '':
         context = {
            'object_list': items,
            'category_title': 'Tìm kiếm sảm phẩm',
            'category_description':  None,
            'category_image':  None,
            'search_pro': search
        }
    return render(request, "category.html", context)



def get_checkout(request):
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            ship = ShipAddress.objects.get(user=request.user)
            if request.method == 'POST':
                method = request.POST['method']
                address_detail = request.POST['address']
                address_detail2 = request.POST['address2']
                city = request.POST['city'] 
                district = request.POST['district'] 
                xa = request.POST['xa'] 
                phone = request.POST['telphone'] 
                if 'save_address' in request.POST:
                    ship = ShipAddress.objects.get(user=request.user)
                    ship.address_detail = address_detail
                    ship.address_detail2 = address_detail2
                    ship.phone = phone
                    ship.district = district
                    ship.xa = xa
                    ship.city = city
                    ship.save()
                if method == 'tt':
                    order.ordered = True
                    order.save()
                    return redirect('complete')

            context = {
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True,
                'add_ship': ship  
            }

            return render(request, "checkout.html", context)

        except ObjectDoesNotExist:
            ShipAddress.objects.create(user = request.user)
            messages.info(request, "Bạn chưa có đơn hàng nào")
            return redirect("home")    


def remove_from_cart(request, slug): 
    item = Item.objects.get(slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.quantity = 1
            order_item.save()
            messages.info(request, "Item was removed from your cart.")
            return redirect("order-summary")
        else:
            # add a message saying the user dosent have an order
            messages.info(request, "Item was not in your cart.")
            return redirect("product", slug=slug)
    else:
        # add a message saying the user dosent have an order
        messages.info(request, "u don't have an active order.")
        return redirect("product", slug=slug)


def remove_single_item_from_cart(request, slug):
    item = Item.objects.get(slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item qty was updated.")
            return redirect("order-summary")
        else:
            # add a message saying the user dosent have an order
            messages.info(request, "Item was not in your cart.")
            return redirect("product", slug=slug)
    else:
        # add a message saying the user dosent have an order
        messages.info(request, "u don't have an active order.")
        return redirect("product", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return None

def order_complete(request):
    return render(request,'complete_order.html')


def add_coupon(request):
    form = CouponForm(request.POST or None)
    if form.is_valid():
        try:
            code = form.cleaned_data.get('code')
            order = Order.objects.get(user=request.user, ordered=False)
            coupon = get_coupon(request, code)
            if coupon:
                order.coupon = coupon
                order.save()
                messages.success(request, "Successfully added coupon")
                return redirect("checkout")
            else:
                messages.info(request, "This coupon does not exist")
                return redirect("checkout")

        except ObjectDoesNotExist:
            messages.info(request, "Bạn chưa có đơn hàng nào")
            return redirect("checkout")





def get_refund(request):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(request, "request_refund.html", context)

def post_refund(request):
        form = RefundForm(request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(request, "Your request was received")
                return redirect("request-refund")

            except ObjectDoesNotExist:
                messages.info(request, "This order does not exist")
                return redirect("request-refund")

def profile(request):
    if request.user.is_superuser is True:
        return redirect('/logout')
    else:
        user_info = InfoUser.objects.get(user = request.user)
        view_list = RecentlyViewedItems.objects.filter(user=request.user).order_by('-date')[:3]
        return render(request, 'profile.html',{'User_info': user_info,'view_list':view_list})
    

def profile_edit(request):
    user_info = InfoUser.objects.get(user = request.user)

    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        birth_date = request.POST['birthday']
        gender = request.POST['gender']
        phone = request.POST['phone']
        address = request.POST['address']
        city = request.POST['city']
        district = request.POST['district']
        image = request.FILES['avatar']

        my_user = request.user
        my_user.last_name = last_name
        my_user.first_name = first_name

        my_info = InfoUser.objects.get(user = request.user)
        my_info.birth_date = birth_date
        my_info.gender = gender
        my_info.phone = phone
        my_info.address = address
        my_info.city = city
        my_info.district = district
        my_info.image = image

        my_info.save()
        my_user.save()
        return redirect('/profile')

    return render(request, 'profile_edit.html',{'User_info': user_info})

