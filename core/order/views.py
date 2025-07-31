from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,JsonResponse
from carts.models import CartItem,Product,Cart
from .models import Order,Order_product,Payment
from datetime import datetime
from carts.views import check_out
import json
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
# Create your views here.
def payments(request):
    body=json.loads(request.body)
    print(body)
    payment=Payment.objects.create(
        user=request.user,
        payment_id=body['transction_id'],
        payment_method=body['payment_methods'],
        amount_paid=body['grand_value'],
        status=body['status']
    )
    payment.save()
    order = Order.objects.get(user=request.user, is_orderd=False, order_number=body['orderID'])
    order.payment = payment
    order.is_orderd = True
    order.save()

    # move cart item to order product table 
    cart_items=CartItem.objects.filter(user = request.user)
    print(cart_items)
    for item in cart_items:
        orderdProduct = Order_product.objects.create(
            order = order,
            payment=payment,
            user=request.user,
            product= item.product,
            colour=item.colour,
            size=item.size,
            quantity=item.quantity,
            product_price=item.product.price,
            orderd=True,
        )
        print(orderdProduct)
        orderdProduct.save()
        # reduce the quantity of sold product 
        product=Product.objects.get(id=item.product.id)
        product.stock -= item.quantity
        product.save()
    # clear Cart 
    CartItem.objects.filter(user=request.user).delete()
    # send mail for successful compleate the order 
    mail_subject='Thank You for Bye Products From us'
    message=render_to_string('orders/order_reseve_email.html',{
        'user':request.user,
        'order':order
    })
    to_email=request.user.email
    send_email=EmailMessage(mail_subject,message,to=[to_email ])
    send_email.send()

    context={
        'order_number':order.order_number,
        'transID':payment.payment_id
    }
    return JsonResponse(context)


def place_order(request,total=0,quantity=0):
    curren_user=request.user
    cart_item=CartItem.objects.filter(user=curren_user)
    
    for item in cart_item:
        total += (item.product.price * item.quantity)
        quantity += item.quantity
    tax=(2*total)/100
    grand_total=total + tax

    if request.method == 'POST':
        full_name=request.POST['full_name']
        if len(full_name.split(' ')) == 3:
            first_name=full_name.split(' ')[0]
            last_name=full_name.split(' ')[2]
        else:
            first_name=full_name.split(' ')[0]
            last_name=full_name.split(' ')[1]
        ph_num=request.POST['ph_num']
        address=request.POST['address1']
        pin=request.POST['pin']
        order_note=request.POST['order_note']

        order=Order.objects.create(
            user=curren_user,
            first_name=first_name,
            last_name=last_name,
            phone=ph_num,
            email=curren_user.email,
            adress_1=address,
            oredr_note=order_note,
            order_value=grand_total,
            tax=tax,
            pin=pin,
            ip=request.META.get('REMOTE_ADDR')
        )
        date = format(datetime.now().strftime("%Y%m%d"))
        order_id=date +str(order.id)
        order.order_number= order_id
        order.save()
        order_context=Order.objects.get(user=curren_user,is_orderd=False,order_number=order_id,)
        context={
            'order':order_context,
            'cart_items':cart_item,
            'total':total,
            'tax':tax,
            'grand_total':grand_total
        }
        return render(request,'orders/payments.html',context)
    return redirect(check_out)

def order_complite(request):
    order_number=request.GET.get('order_number')
    transID=request.GET.get('payment_id')
    try:
        order=Order.objects.get(order_number=order_number,is_orderd=True)
        ordered_product=Order_product.objects.filter(order=order)
       
        subtotal = sum(item.product_price * item.quantity for item in ordered_product)
        context={
            'order':order,
            'ordered_product':ordered_product,
            'subtotal':subtotal,
            'tax':order.tax, 
        }
    except (Payment.DoesNotExist,Order.DoesNotExist):
        payment = Payment.objects.filter(payment_id=transID).first()
        return HttpResponse(payment)
    return render(request,'orders/order_complite.html',context)
