from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_home, name='home'),
    path('category/', views.get_category, name='shop'),
    path('category/product/<slug>/', views.get_product, name='product'),
    path('category/<slug>/', views.get_category, name='category'),
    path('order-summary/', views.get_ordersum, name='order-summary'),
    
    path('add-to-cart/<slug>/', views.add_to_cart, name='add-to-cart'),
    path('checkout/', views.get_checkout, name='checkout'),
    path('remove-from-cart/<slug>/', views.remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', views.remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('refund/', views.get_refund, name='request-refund'),
    path('post_refund/', views.post_refund, name='post-refund'),
    path('add_coupon/', views.add_coupon, name='add_coupon'),
    path('get_coupon/', views.get_coupon, name='get_coupon'),
    


    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('login/', views.log_in, name='login'),
    path('register/', views.signup, name='register'),
    path('logout/', views.log_out, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile_edit/', views.profile_edit, name='profile_edit'),
    path('login/forget_password/', views.forget_password, name='forget_password'),
    path('login/forget_password/new_password/', views.new_password, name='new_password'),
    path('login/forget_password/otp_confirmation/', views.otp_confirmation, name="otp_confirmation"),
 


]


