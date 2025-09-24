from django.shortcuts import render,redirect,reverse,get_object_or_404  
from .context_processors import product_count_in_cart
from . import forms,models
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect,HttpResponse
from django.core.mail import send_mail
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.conf import settings
from django.views.decorators.http import require_POST
from .models import Product
from django.http import JsonResponse
import json
import hashlib
import hmac
import time
from django.http import JsonResponse
from .mpesa import stk_push_request

def home_view(request):
    products=models.Product.objects.all()
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'ecom/index.html',{'products':products,'product_count_in_cart':product_count_in_cart})
    


#for showing login button for admin(by sumit)
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


def customer_signup_view(request):
    userForm=forms.CustomerUserForm()
    customerForm=forms.CustomerForm()
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST)
        customerForm=forms.CustomerForm(request.POST,request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customer=customerForm.save(commit=False)
            customer.user=user
            customer.save()
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)
        return HttpResponseRedirect('customerlogin')
    return render(request,'ecom/customersignup.html',context=mydict)

#-----------for checking user iscustomer
def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()


#------------------customer login view
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User

def customerlogin_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        print(f"Username: {username}, Password: {password}")  # Debug

        user = authenticate(request, username=username, password=password)
        print(f"Authenticated User: {user}")  # Debug

        if user is not None:
            login(request, user)
            print(f"User logged in. Groups: {user.groups.all()}")  # Debug
            return redirect('afterlogin')
        else:
            print("Auth failed. Users in DB:", User.objects.values_list('username', flat=True))  # Debug
            messages.error(request, "Invalid credentials")
            return redirect('customerlogin')
    
    return render(request, 'ecom/customerlogin.html')  # make sure the path is correct

    
#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,CUSTOMER
def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('customer-home')
    else:
        return redirect('admin-dashboard')

#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    # for cards on dashboard
    customercount=models.Customer.objects.all().count()
    productcount=models.Product.objects.all().count()
    ordercount=models.Orders.objects.all().count()

    # for recent order tables
    orders=models.Orders.objects.all()
    ordered_products=[]
    ordered_bys=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_by=models.Customer.objects.all().filter(id = order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)

    mydict={
    'customercount':customercount,
    'productcount':productcount,
    'ordercount':ordercount,
    'data':zip(ordered_products,ordered_bys,orders),
    }
    return render(request,'ecom/admin_dashboard.html',context=mydict)


# admin view customer table
@login_required(login_url='adminlogin')
def view_customer_view(request):
    customers=models.Customer.objects.all()
    return render(request,'ecom/view_customer.html',{'customers':customers})

# admin delete customer
@login_required(login_url='adminlogin')
def delete_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return redirect('view-customer')


@login_required(login_url='adminlogin')
def update_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect('view-customer')
    return render(request,'ecom/admin_update_customer.html',context=mydict)

# admin view the product
@login_required(login_url='adminlogin')
def admin_products_view(request):
    products=models.Product.objects.all()
    return render(request,'ecom/admin_products.html',{'products':products})


# admin add product by clicking on floating button
@login_required(login_url='adminlogin')
def admin_add_product_view(request):
    productForm=forms.ProductForm()
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST, request.FILES)
        if productForm.is_valid():
            productForm.save()
        return HttpResponseRedirect('admin-products')
    return render(request,'ecom/admin_add_products.html',{'productForm':productForm})


@login_required(login_url='adminlogin')
def delete_product_view(request,pk):
    product=models.Product.objects.get(id=pk)
    product.delete()
    return redirect('admin-products')


@login_required(login_url='adminlogin')
def update_product_view(request,pk):
    product=models.Product.objects.get(id=pk)
    productForm=forms.ProductForm(instance=product)
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST,request.FILES,instance=product)
        if productForm.is_valid():
            productForm.save()
            return redirect('admin-products')
    return render(request,'ecom/admin_update_product.html',{'productForm':productForm})


@login_required(login_url='adminlogin')
def admin_view_booking_view(request):
    orders=models.Orders.objects.all()
    ordered_products=[]
    ordered_bys=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_by=models.Customer.objects.all().filter(id = order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)
    return render(request,'ecom/admin_view_booking.html',{'data':zip(ordered_products,ordered_bys,orders)})


@login_required(login_url='adminlogin')
def delete_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    order.delete()
    return redirect('admin-view-booking')

# for changing status of order (pending,delivered...)
@login_required(login_url='adminlogin')
def update_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    orderForm=forms.OrderForm(instance=order)
    if request.method=='POST':
        orderForm=forms.OrderForm(request.POST,instance=order)
        if orderForm.is_valid():
            orderForm.save()
            return redirect('admin-view-booking')
    return render(request,'ecom/update_order.html',{'orderForm':orderForm})


# admin view the feedback
@login_required(login_url='adminlogin')
def view_feedback_view(request):
    feedbacks=models.Feedback.objects.all().order_by('-id')
    return render(request,'ecom/view_feedback.html',{'feedbacks':feedbacks})



#---------------------------------------------------------------------------------
#------------------------ PUBLIC CUSTOMER RELATED VIEWS START ---------------------
#---------------------------------------------------------------------------------
def search_view(request):
    # whatever user write in search box we get in query
    query = request.GET['query']
    products=models.Product.objects.all().filter(name__icontains=query)
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    # word variable will be shown in html when user click on search button
    word="Searched Result :"

    if request.user.is_authenticated:
        return render(request,'ecom/customer_home.html',{'products':products,'word':word,'product_count_in_cart':product_count_in_cart})
    return render(request,'ecom/index.html',{'products':products,'word':word,'product_count_in_cart':product_count_in_cart})

#adding to cart no redirect
def add_to_cart_ajax(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        # Get current cart data from cookie
        cart_data = {}
        if 'cart_data' in request.COOKIES:
            try:
                cart_data = json.loads(request.COOKIES['cart_data'])
            except json.JSONDecodeError:
                cart_data = {}
        
        # Update quantity for the product
        if product_id in cart_data:
            cart_data[product_id] += quantity
        else:
            cart_data[product_id] = quantity
        
        # Calculate total items in cart
        total_items = sum(cart_data.values())
        
        response = JsonResponse({
            'success': True, 
            'message': 'Product added to cart successfully', 
            'cart_count': total_items
        })
        
        # Set the cookie with updated cart data
        response.set_cookie('cart_data', json.dumps(cart_data), max_age=30*24*60*60)  # 30 days
        
        return response
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})
    
# any one can add product to cart, no need of signin
def add_to_cart_view(request,pk):
    products=models.Product.objects.all()

    #for cart counter, fetching products ids added by customer from cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=1

    response = render(request, 'ecom/index.html',{'products':products,'product_count_in_cart':product_count_in_cart})

    #adding product id to cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids=="":
            product_ids=str(pk)
        else:
            product_ids=product_ids+"|"+str(pk)
        response.set_cookie('product_ids', product_ids)
    else:
        response.set_cookie('product_ids', pk)

    product=models.Product.objects.get(id=pk)
    messages.info(request, product.name + ' added to cart successfully!')

    return response
    

#product details view
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Safely get related products
    try:
        # Try to get products from the same category
        related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    except AttributeError:
        # Fallback to random products if category doesn't exist
        related_products = Product.objects.exclude(id=product.id).order_by('?')[:4]
    
    return render(request, 'ecom/product_details.html', {
        'product': product,
        'related_products': related_products
    })

# for checkout of cart
# views.py (cart_view update)
def cart_view(request):
    # For cart counter - now counting total items including quantities
    total_items = 0
    cart_data = {}
    
    # Check for both old and new cookie formats
    if 'cart_data' in request.COOKIES:
        try:
            cart_data = json.loads(request.COOKIES['cart_data'])
            # Calculate total items in cart (sum of all quantities)
            total_items = sum(int(qty) for qty in cart_data.values())
        except (json.JSONDecodeError, ValueError):
            cart_data = {}
            total_items = 0
    # Fallback to old format for backward compatibility
    # elif 'product_ids' in request.COOKIES:
    #   product_ids = request.COOKIES['product_ids']
    #    if product_ids:
            # Convert old format to new format
    #       counter = product_ids.split('|')
    #       for pid in counter:
    #          cart_data[pid] = cart_data.get(pid, 0) + 1
    #       total_items = len(counter)
    
    # Fetch product details from db whose id is present in cart_data
    products = None
    total = 0
    cart_items = []
    
    if cart_data:
        product_ids = list(cart_data.keys())
        try:
            products = models.Product.objects.filter(id__in=product_ids)
           # products = models.Product.objects.filter(id__in=product_ids, active=True)
           # Prepare cart items with product details and quantities
            for p in products:
                quantity = int(cart_data.get(str(p.id), 1))
                item_total = p.price * quantity
                total += item_total
                cart_items.append({
                    'product': p,
                    'quantity': quantity,
                    'item_total': item_total
                })
        except (ValueError, TypeError):
            # Handle case where product IDs are invalid
            cart_items = []
            total = 0
    
    return render(request, 'ecom/cart.html', {
        'cart_items': cart_items, 
        'total': total,
        'product_count_in_cart': total_items
    })
def update_cart_ajax(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        # Get current cart data from cookie
        cart_data = {}
        if 'cart_data' in request.COOKIES:
            try:
                cart_data = json.loads(request.COOKIES['cart_data'])
            except json.JSONDecodeError:
                cart_data = {}
        
        # Update quantity for the product
        if quantity > 0:
            cart_data[product_id] = quantity
        else:
            # Remove product if quantity is 0
            if product_id in cart_data:
                del cart_data[product_id]
        
        # Calculate total items in cart
        total_items = sum(cart_data.values())
        
        response = JsonResponse({
            'success': True, 
            'cart_count': total_items,
            'message': 'Cart updated successfully'
        })
        
        # Set updated cart data in cookie
        response.set_cookie('cart_data', json.dumps(cart_data), max_age=30*24*60*60)
        return response
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})
    
def toggle_wishlist_ajax(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        
        # Get current wishlist from cookie or session
        wishlist = request.session.get('wishlist', [])
        
        if product_id in wishlist:
            # Remove from wishlist
            wishlist.remove(product_id)
            added = False
        else:
            # Add to wishlist
            wishlist.append(product_id)
            added = True
        
        # Save wishlist in session
        request.session['wishlist'] = wishlist
        
        return JsonResponse({
            'success': True, 
            'added': added,
            'message': 'Wishlist updated successfully'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})    

# Add these utility functions at the top of views.py
def create_cart_signature(cart_data):
    """Create HMAC signature for cart data with timestamp to prevent replay attacks"""
    timestamp = str(int(time.time()))
    data_to_sign = f"{cart_data}|{timestamp}"
    return hmac.new(
        key=settings.SECRET_KEY.encode(),
        msg=data_to_sign.encode(),
        digestmod=hashlib.sha256
    ).hexdigest(), timestamp

def verify_cart_signature(cart_data, signature, timestamp, max_age=3600):
    """Verify the HMAC signature of cart data with timestamp check"""
    # Check if timestamp is recent to prevent replay attacks
    try:
        if int(time.time()) - int(timestamp) > max_age:
            return False
    except (ValueError, TypeError):
        return False
        
    expected_signature = hmac.new(
        key=settings.SECRET_KEY.encode(),
        msg=f"{cart_data}|{timestamp}".encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)

#remove items from cart
import logging
logger = logging.getLogger(__name__)
def remove_from_cart_view(request, pk):
    logger.debug(f"Attempting to remove product {pk} from cart")
    logger.debug(f"Current cart data: {request.COOKIES.get('cart_data')}")
    # Use the same cookie key as your other views
    cart_data_str = request.COOKIES.get('cart_data', '{}')
    
    try:
        cart_data = json.loads(cart_data_str)
    except json.JSONDecodeError:
        cart_data = {}
    
    # Remove the product from cart
    product_id = str(pk)
    product_was_in_cart = product_id in cart_data
    
    if product_was_in_cart:
        del cart_data[product_id]
        message = "Product removed from cart successfully!"
    else:
        message = "Product not found in cart!"
    
    # For AJAX requests (from your cart.html)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Calculate updated cart total
        total = 0
        cart_count = 0
        
        # Only calculate if we have items
        if cart_data:
            product_ids = list(cart_data.keys())
            products = models.Product.objects.filter(id__in=product_ids)
           # product_ids = list(cart_data.keys())
            #products = models.Product.objects.filter(id__in=product_ids, active=True)
            
            for p in products:
                quantity = int(cart_data.get(str(p.id), 0))
                total += p.price * quantity
                cart_count += quantity
        
        response = JsonResponse({
            'success': product_was_in_cart,
            'cart_total': total,
            'cart_count': cart_count,
            'message': message
        })
    else:
        # For non-AJAX requests
        if product_was_in_cart:
            messages.success(request, message)
        else:
            messages.error(request, message)
        
        response = HttpResponseRedirect(reverse('cart'))
    
    # Set the updated cart data in cookie with proper settings
    response.set_cookie(
        'cart_data', 
        json.dumps(cart_data), 
        max_age=30*24*60*60,  # 30 days
        httponly=True,
        samesite='Lax'
    )
    
    return response

 
#increase cart items# views.py
def increase_cart_item_view(request, pk):
    # Get cart data from cookie
    cart_data = request.COOKIES.get('cart', '{}')
    try:
        cart = json.loads(cart_data)
    except json.JSONDecodeError:
        cart = {}
    
    # Increase quantity
    product_id = str(pk)
    cart[product_id] = cart.get(product_id, 0) + 1
    messages.success(request, "Item quantity increased!")
    
    # Create response
    response = HttpResponseRedirect(reverse('cart'))
    response.set_cookie('cart', json.dumps(cart))
    return response

def decrease_cart_item_view(request, pk):
    # Get cart data from cookie
    cart_data = request.COOKIES.get('cart', '{}')
    try:
        cart = json.loads(cart_data)
    except json.JSONDecodeError:
        cart = {}
    
    # Decrease quantity or remove if 1
    product_id = str(pk)
    if product_id in cart:
        if cart[product_id] > 1:
            cart[product_id] -= 1
            messages.success(request, "Item quantity decreased!")
        else:
            del cart[product_id]
            messages.success(request, "Product removed from cart!")
    
    # Create response
    response = HttpResponseRedirect(reverse('cart'))
    response.set_cookie('cart', json.dumps(cart))
    return response
def send_feedback_view(request):
    feedbackForm=forms.FeedbackForm()
    if request.method == 'POST':
        feedbackForm = forms.FeedbackForm(request.POST)
        if feedbackForm.is_valid():
            feedbackForm.save()
            return render(request, 'ecom/feedback_sent.html')
    return render(request, 'ecom/send_feedback.html', {'feedbackForm':feedbackForm})


#---------------------------------------------------------------------------------
#------------------------ CUSTOMER RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_home_view(request):
    products=models.Product.objects.all()
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0
    return render(request,'ecom/customer_home.html',{'products':products,'product_count_in_cart':product_count_in_cart})



# shipment address before placing order
@login_required(login_url='customerlogin')
def customer_address_view(request):
    # Check for products in cart using the new format
    product_in_cart = False
    product_count_in_cart = 0
    total = 0
    
    # Check for new cookie format first
    if 'cart_data' in request.COOKIES:
        try:
            cart_data = json.loads(request.COOKIES['cart_data'])
            if cart_data:  # If cart is not empty
                product_in_cart = True
                product_count_in_cart = len(cart_data)  # Number of distinct products
                
                # Calculate total price for payment page
                product_ids = list(cart_data.keys())
                products = models.Product.objects.filter(id__in=product_ids)
                for p in products:
                    quantity = int(cart_data.get(str(p.id), 1))
                    total += p.price * quantity
        except json.JSONDecodeError:
            pass

    addressForm = forms.AddressForm()
    if request.method == 'POST':    #this triggers when the submit button is clicked
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            email = addressForm.cleaned_data['Email']
            mobile = addressForm.cleaned_data['Mobile']
            address = addressForm.cleaned_data['Address']
            
            response = render(request, 'ecom/payment.html', {'total': total})
            response.set_cookie('email', email)
            response.set_cookie('mobile', mobile)
            response.set_cookie('address', address)
            return response
            
    return render(request, 'ecom/customer_address.html', {
        'addressForm': addressForm,
        'product_in_cart': product_in_cart,
        'product_count_in_cart': product_count_in_cart
    })


# here we are just directing to this view...actually we have to check whther payment is successful or not
#then only this view should be accessed
@login_required(login_url='customerlogin')
def payment_success_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    email = request.COOKIES.get('email')
    mobile = request.COOKIES.get('mobile')
    address = request.COOKIES.get('address')

    products = None
    cart_data = {}

    # ✅ Use new cart_data cookie instead of product_ids
    if 'cart_data' in request.COOKIES:
        try:
            cart_data = json.loads(request.COOKIES['cart_data'])
            if cart_data:
                product_ids = list(cart_data.keys())
                products = models.Product.objects.filter(id__in=product_ids)
        except (json.JSONDecodeError, ValueError):
            products = None

    # ✅ Create orders based on cart_data quantities
    if products:
        for product in products:
            quantity = int(cart_data.get(str(product.id), 1))
            for _ in range(quantity):  # one row per item (like before)
                models.Orders.objects.create(
                    customer=customer,
                    product=product,
                    status='Pending',
                    email=email,
                    mobile=mobile,
                    address=address
                )

    # ✅ Render success page and clear cookies
    response = render(request, 'ecom/payment_success.html')
    response.delete_cookie('cart_data')
    response.delete_cookie('email')
    response.delete_cookie('mobile')
    response.delete_cookie('address')
    return response


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_order_view(request):
    
    customer=models.Customer.objects.get(user_id=request.user.id)
    orders=models.Orders.objects.all().filter(customer_id = customer)
    ordered_products=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_products.append(ordered_product)

    return render(request,'ecom/my_order.html',{'data':zip(ordered_products,orders)})
 



# @login_required(login_url='customerlogin')
# @user_passes_test(is_customer)
# def my_order_view2(request):

#     products=models.Product.objects.all()
#     if 'product_ids' in request.COOKIES:
#         product_ids = request.COOKIES['product_ids']
#         counter=product_ids.split('|')
#         product_count_in_cart=len(set(counter))
#     else:
#         product_count_in_cart=0
#     return render(request,'ecom/my_order.html',{'products':products,'product_count_in_cart':product_count_in_cart})    



#--------------for discharge patient bill (pdf) download and printing
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def download_invoice_view(request,orderID,productID):
    order=models.Orders.objects.get(id=orderID)
    product=models.Product.objects.get(id=productID)
    mydict={
        'orderDate':order.order_date,
        'customerName':request.user,
        'customerEmail':order.email,
        'customerMobile':order.mobile,
        'shipmentAddress':order.address,
        'orderStatus':order.status,

        'productName':product.name,
        'productImage':product.product_image,
        'productPrice':product.price,
        'productDescription':product.description,


    }
    return render_to_pdf('ecom/download_invoice.html',mydict)






@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    return render(request,'ecom/my_profile.html',{'customer':customer})


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def edit_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return HttpResponseRedirect('my-profile')
    return render(request,'ecom/edit_profile.html',context=mydict)



#---------------------------------------------------------------------------------
#------------------------ ABOUT US AND CONTACT US VIEWS START --------------------
#---------------------------------------------------------------------------------
def aboutus_view(request):
    return render(request,'ecom/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message, settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'ecom/contactussuccess.html')
    return render(request, 'ecom/contactus.html', {'form':sub})

def initiate_payment(request):
    phone = request.GET.get("phone")
    phone = normalize_phone(phone)
    amount = request.GET.get("amount")

    response = stk_push_request(phone, int(amount), "TEMP")
    print("STK Response:", response)  # 👈 see server logs
    return JsonResponse(response)

def normalize_phone(phone: str) -> str:
    phone = phone.strip()
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    elif phone.startswith("7"):
        phone = "254" + phone
    elif phone.startswith("+254"):
        phone = phone[1:]  # remove the +
    return phone
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

@csrf_exempt
def mpesa_callback(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        result_code = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')

        response = JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

        if result_code == 0:
            # ✅ set cookie flag (accessible to polling view)
            response.set_cookie('payment_success', '1', max_age=300)  # 5 min expiry
        else:
            response.set_cookie('payment_success', '0', max_age=300)

        return response
    except Exception as e:
        print(f"Error processing callback: {e}")
        return JsonResponse({"ResultCode": 1, "ResultDesc": "Failed"})

     
def check_payment_status(request):
    if request.COOKIES.get('payment_success') == '1':
        return JsonResponse({'status': 'completed'})
    elif request.COOKIES.get('payment_success') == '0':
        return JsonResponse({'status': 'failed'})
    else:
        return JsonResponse({'status': 'pending'})
        