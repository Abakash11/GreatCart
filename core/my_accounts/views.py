from django.shortcuts import render,redirect
from .models import Accounts,UserProfile
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from carts.views import _cart_id
from carts.models import Cart,CartItem
from order.models import Order,Order_product
from django.contrib import messages

# for sending mail 
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from core.settings import EMAIL_HOST_USER
import random
# Create your views here.
def register(request):
    if request.method == 'POST':
        f_name=request.POST['f_name']
        l_name=request.POST['l_name']
        email=request.POST['email']
        ph_number=request.POST['ph_number']
        password=request.POST['password']
        c_password=request.POST['c_password']
        username=email.split('@')[0]
        if Accounts.objects.filter(email=email).exists():
            return render(request,'my_accounts/register.html',{'message':'Email already exists','success':False,'message_des':'The email you entered is already registered. Please enter a different email or try logging in.'})       
        if f_name and l_name and email and password and c_password:
            if password==c_password:
                user=Accounts.objects.create_user(first_name=f_name,last_name=l_name,username=username,email=email,password=password)
                user.phone_number=ph_number
                user.save()
                print('Account created successfully')
                #activate user
                email_message=f'Welcome to Great Cart , Hellow {user.first_name } '
                otp=int(random.randint(1000,9999))
                send_mail(email_message,f'Your OTP is: {otp}',EMAIL_HOST_USER,[email],fail_silently=True)
                
                request.session['uid']=urlsafe_base64_encode(force_bytes(user.pk))
                request.session['token']=default_token_generator.make_token(user)
                return redirect (f'verify/?otp={otp}')
            else:
                return render(request,'my_accounts/register.html',{'message':'Password does not match','success':False,'message_des':'Please enter the same password in both fields'})
        
    return render(request,'my_accounts/register.html')

def verify(request):
    otp=request.GET['otp']
    uidb64=request.session.get('uid')
    token=request.session.get('token')
    if request.method == 'POST':
        otp_input = request.POST.get('otp_input')
        if otp_input == otp:
            try:
                uid=urlsafe_base64_decode(uidb64).decode()
                user=Accounts._default_manager.get(pk=uid)
            except(ValueError,TypeError,OverflowError,Accounts.DoesNotExist):
                user=None
            if user is not None and default_token_generator.check_token(user,token):
                user.is_active=True
                user.save()
                return redirect(login)
            else:
                return redirect(register)
        else:
            render(request,'my_accounts/verify.html',{'message':'Your OTP Dose Not Match'})            
    return render(request,'my_accounts/verify.html')

def login(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        user=auth.authenticate(request,email=email,password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                if CartItem.objects.filter(cart=cart).exists():
                    cart_items = CartItem.objects.filter(cart=cart)
                    user_cart_items = CartItem.objects.filter(user=user)

                    for item in cart_items:
                        existing_item = user_cart_items.filter(
                            product=item.product,
                            colour=item.colour,
                            size=item.size
                        ).first()
                        if existing_item:
                            existing_item.quantity += item.quantity
                            existing_item.save()
                            item.delete()
                        else:
                            item.user = user
                            item.save()
            except:
                print('somthing wrong in log views')    
            auth.login(request,user)
            return redirect('index') 
    return render(request,'my_accounts/login.html')



@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')
def activate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Accounts._default_manager.get(pk=uid)
    except(ValueError,TypeError,OverflowError,Accounts.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        return redirect(login)
    else:
        return redirect(register)

@login_required(login_url='login')
def dashbord(request):
    order=Order.objects.filter(user=request.user,is_orderd=True).order_by('-create_at')
    user_profile = UserProfile.objects.get_or_create(user=request.user)
    order_count= order.count()
    context={
        'order_count':order_count,
        'user_profile':user_profile,
    }
    return render(request,'my_accounts/dashbord.html',context)


def forgotPassword(request):
    if request.method == 'POST':
        email=request.POST['email']
        if Accounts.objects.filter(email=email).exists():
            user=Accounts.objects.get(email=email)

            # send Email 
            current_site=get_current_site(request)
            mail_subject='Reset Your Account'
            message=render_to_string('my_accounts/rest_password_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user)
            })
            to_email=email
            send_email=EmailMessage(mail_subject,message,to=[to_email ])
            send_email.send()
            render(request,'my_accounts/forgotPassword.html',{'message':'Check Your Mail'})

        else:
            render(request,'my_accounts/forgotPassword.html',{'message':'User Dose not Exist'})
            
    return render(request,'my_accounts/forgotPassword.html')

def reset_password_validate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Accounts._default_manager.get(pk=uid)
    except(ValueError,TypeError,OverflowError,Accounts.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid']=uid
        return redirect('resetPassword')
    else:
        return redirect(forgotPassword)  
    return HttpResponse(f"Something went wrong {user} {token}",)

def resetPassword(request):
    if request.method == 'POST':
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']
        
        if pass1 == pass2:
            uid =request.session.get('uid')
            user= Accounts.objects.get(pk=uid)
            user.set_password(pass1)
            user.save()
            return redirect(login)
        else:
            return redirect(forgotPassword)
    return render(request,'my_accounts/resetPassword.html')

def my_orders(request):
    orders=Order.objects.filter(user=request.user,is_orderd=True).order_by('-create_at')
    context={
        'orders':orders,
    }
    return render(request,'my_accounts/my_orders.html',context)
def edit_profile(request):
        
    user_profile,created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user_profile.profile_picture = request.FILES.get('profile_picture', user_profile.profile_picture)
        user_profile.cover_picture = request.FILES.get('cover_picture', user_profile.cover_picture)
        user_profile.bio = request.POST.get('bio', user_profile.bio)
        user_profile.location = request.POST.get('location', user_profile.location)
        user_profile.website = request.POST.get('website', user_profile.website)
        user_profile.save()
        messages.success(request,'Profile updated Success')
        return redirect('edit_profile')  # Replace with your URL name
    return render(request, 'my_accounts/edit_profile.html', {'user_profile': user_profile})

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['Current_pass']
        new_password = request.POST['New_pass']
        confirm_password = request.POST['Confirm_pass']
        user = Accounts.objects.get(username__exact=request.user.username)
        success=user.check_password(current_password)
        if success:
            if new_password == confirm_password :
                if new_password != current_password:
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'Password changed successfully')
                else:
                    messages.error(request, 'New password cannot be the same as the current password')
            else:
                messages.error(request, 'New password and confirm password do not match')
        else:
            messages.error(request, 'Current password is incorrect')
    return render(request,'my_accounts/change_password.html')

@login_required(login_url='login')
def order_detail(request,order_id):
    order_detail=Order_product.objects.filter(order__order_number=order_id)
    order=Order.objects.get(order_number=order_id)
    subtotal=0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    context={
        'order_details':order_detail,
        'order':order,
        'subtotal':subtotal,
    }
    return render(request,'my_accounts/order_detail.html',context)