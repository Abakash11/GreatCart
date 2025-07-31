from django.shortcuts import render,redirect
from .models import Cart, CartItem
from store.models import Product
from django.http import HttpResponse 
from django.contrib.auth.decorators import login_required
# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create() 
    return cart

def add_to_cart(request,product_id):
    user=request.user
    product=Product.objects.get(id=product_id)
    if user.is_authenticated:
        try:
            if request.POST:
                colour=request.POST['radio_color']
                size=request.POST['radio_size']
                
            cart_item=CartItem.objects.get(
                product=product,
                user=user,
                colour=colour,
                size=size
            )
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist :
            if request.POST:
                colour=request.POST['radio_color']
                size=request.POST['radio_size']
            cart_item=CartItem.objects.create(
                product=product,
                quantity=1,
                user=user,
                colour=colour,
                size=size
            )
            cart_item.save()
        
        return redirect('cart')
    
    #with out login 
    else:
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart=Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()
        try:
            if request.POST:
                colour=request.POST['radio_color']
                size=request.POST['radio_size']
            cart_item=CartItem.objects.get(
                product=product,
                cart=cart,
                colour=colour,
                size=size
            )
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            if request.POST:
                colour=request.POST['radio_color']
                size=request.POST['radio_size']
            cart_item=CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
                colour=colour,
                size=size
            )
            cart_item.save()
        return redirect('cart')


def add_item_to_cart(request,product_id,colour,size):
    user=request.user
    if user.is_authenticated:
        product=Product.objects.get(id=product_id)
        cart_item=CartItem.objects.get(product=product,user=user,colour=colour,size=size)
        cart_item.quantity += 1
        cart_item.save()
        return redirect('cart')
    else:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        product=Product.objects.get(id=product_id)
        cart_item=CartItem.objects.get(product=product,cart=cart,colour=colour,size=size)
        cart_item.quantity += 1
        cart_item.save()
        return redirect('cart')

def remove_cart(request,product_id,colour,size):
    user=request.user
    if user.is_authenticated:
        product=Product.objects.get(id=product_id)  
        cart_item=CartItem.objects.get(product=product,user=user,colour=colour,size=size)
        if cart_item.quantity>1:
            cart_item.quantity-=1
            cart_item.save()
        else:
            cart_item.delete()
        return redirect('cart')
    else:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        product=Product.objects.get(id=product_id)  
        cart_item=CartItem.objects.get(product=product,cart=cart,colour=colour,size=size)
        if cart_item.quantity>1:
            cart_item.quantity-=1
            cart_item.save()
        else:
            cart_item.delete()
        return redirect('cart')
def car_item_delete(request,product_id,colour,size):
    user=request.user
    if user.is_authenticated:
        product=Product.objects.get(id=product_id)
        cart_item=CartItem.objects.get(product=product,user=user,colour=colour,size=size)
        cart_item.delete()
        return redirect('cart')
    else:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        product=Product.objects.get(id=product_id)
        cart_item=CartItem.objects.get(product=product,cart=cart,colour=colour,size=size)
        cart_item.delete()
        return redirect('cart')


def cart(request,total=0,quantity=0):
    cart_items=None
    tax=None
    grand_total=None
    try:
        
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax=int((5*total)/100)
        grand_total=int(total + tax)
    except Cart.DoesNotExist:
        cart=None
    data={
        'cart_items':cart_items,
        'total':total,
        'tax':tax,
        'grand_total':grand_total,
        'quantity':quantity,
    }

    return render(request,'store/cart.html',data)

@login_required(login_url='login')
def check_out(request,total=0,quantity=0):
    cart_items=None
    tax=None
    grand_total=None
    try:
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax=int((5*total)/100)
        grand_total=int(total + tax)
    except Cart.DoesNotExist:
        cart=None
    data={
        'cart_items':cart_items,
        'total':total,
        'tax':tax,
        'grand_total':grand_total,
        'quantity':quantity,
    }
    return render (request,'store/check_out.html',data)