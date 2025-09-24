
from django.contrib import admin
from django.urls import path
from ecom import views
from django.contrib.auth.views import LoginView,LogoutView
from django.views.generic import TemplateView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home_view,name=''),
    path('afterlogin', views.afterlogin_view,name='afterlogin'),
    path('logout/', LogoutView.as_view(template_name='ecom/logout.html'), name='logout'),
    #path('logout/', LogoutView.as_view(template_name='/'), name='logout'),

    path('aboutus', views.aboutus_view),
    path('contactus', views.contactus_view,name='contactus'),
    path('search', views.search_view,name='search'),
    path('send-feedback', views.send_feedback_view,name='send-feedback'),
    path('view-feedback', views.view_feedback_view,name='view-feedback'),

    path('adminclick', views.adminclick_view),
    path('adminlogin', LoginView.as_view(template_name='ecom/adminlogin.html'),name='adminlogin'),
    path('admin-dashboard', views.admin_dashboard_view,name='admin-dashboard'),

    path('view-customer', views.view_customer_view,name='view-customer'),
    path('delete-customer/<int:pk>', views.delete_customer_view,name='delete-customer'),
    path('update-customer/<int:pk>', views.update_customer_view,name='update-customer'),

    path('admin-products', views.admin_products_view,name='admin-products'),
    path('admin-add-product', views.admin_add_product_view,name='admin-add-product'),
    path('delete-product/<int:pk>', views.delete_product_view,name='delete-product'),
    path('update-product/<int:pk>', views.update_product_view,name='update-product'),

    path('admin-view-booking', views.admin_view_booking_view,name='admin-view-booking'),
    path('delete-order/<int:pk>', views.delete_order_view,name='delete-order'),
    path('update-order/<int:pk>', views.update_order_view,name='update-order'),


    path('customersignup', views.customer_signup_view),
    #path('customerlogin', LoginView.as_view(template_name='ecom/customerlogin.html'),name='customerlogin'),
    path('customerlogin', views.customerlogin_view, name='customerlogin'),
    path('customer-home', views.customer_home_view,name='customer-home'),
    path('my-order', views.my_order_view,name='my-order'),
    # path('my-order', views.my_order_view2,name='my-order'),
    path('my-profile', views.my_profile_view,name='my-profile'),
    path('edit-profile', views.edit_profile_view,name='edit-profile'),
    path('download-invoice/<int:orderID>/<int:productID>', views.download_invoice_view,name='download-invoice'),


    path('add-to-cart/<int:pk>', views.add_to_cart_view,name='add-to-cart'),
    path("add-to-cart-ajax/", views.add_to_cart_ajax, name="add-to-cart-ajax"),
    path('update-cart-ajax/', views.update_cart_ajax, name='update-cart-ajax'),
    path('toggle-wishlist-ajax/', views.toggle_wishlist_ajax, name='toggle-wishlist-ajax'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart', views.cart_view,name='cart'),
    path('increase-cart-item/<int:pk>/', views.increase_cart_item_view, name='increase-cart-item'),
    path('decrease-cart-item/<int:pk>/', views.decrease_cart_item_view, name='decrease-cart-item'),
    path('remove-from-cart/<int:pk>', views.remove_from_cart_view,name='remove-from-cart'),
    path('customer-address', views.customer_address_view,name='customer-address'),
    path('payment-success', views.payment_success_view,name='payment-success'),

    path('test-logout-form/', TemplateView.as_view(template_name='ecom/test_logout.html')),

    #path("initiate/<int:order_id>/", views.initiate_payment, name="mpesa_initiate"),
    path("mpesa/initiate/", views.initiate_payment, name="mpesa_initiate"),
    path("mpesa/callback/", views.mpesa_callback, name="mpesa_callback"),
    # Add to urls.py
    path('check-payment-status/', views.check_payment_status, name='check-payment-status'),

]
