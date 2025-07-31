from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponseRedirect
from .models import Product,ReviewRating,ProductGallery
from order.models import Order_product
from .forms import ReviewForm
from category.models import Category
from carts.models import Cart,CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.db.models import Q
from django.contrib import messages


# Create your views here.
def store(request,catagory_slug=None):
    catagores=None
    products=None
    page=1
    if catagory_slug!=None:
        catagores=get_object_or_404(Category,slug=catagory_slug)
        products=Product.objects.filter(category=catagores,is_available=True).order_by('id')
        paginator=Paginator(products,3)
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
        product_count=products.count()
    else:
        products=Product.objects.all().filter(is_available=True).order_by('id')
        paginator=Paginator(products,1)
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
        product_count=products.count()
        
    context={
        'products':paged_products,
        'product_count':product_count,
        
    }
    return render(request,'store/store.html',context)





def product_detail(request,catagory_slug,product_slug):
    try:
        #for this catagory slug and product slug
        single_product=Product.objects.get(category__slug=catagory_slug,slug=product_slug)
        in_cart=CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
    except Exception as e:
        raise e
    try:
        if request.user.is_authenticated:
            is_orderd=Order_product.objects.filter(user=request.user,product_id=single_product.id).exists()
        else:
            is_orderd=False
    except Order_product.DoesNotExist:
        is_orderd=None
    reviews=ReviewRating.objects.filter(product_id=single_product.id,status=True)
    producr_gallery=ProductGallery.objects.filter(product_id=single_product.id)
    context={
        'single_product':single_product,
        'in_cart':in_cart,
        'colour':single_product.colors.split(','),
        'size':single_product.sizes.split(','),
        'is_orderd':is_orderd,
        'reviews':reviews,
        'product_gallery':producr_gallery,
        
    }
    return render(request,'store/product_detail.html',context)

def search(request):
    
    if 'keyword' in request.GET:
        keyword=request.GET['keyword']
        if keyword:
            products=Product.objects.filter(Q(descriptions__icontains=keyword) | Q(product_name__icontains=keyword) ).order_by('create_at')
            product_count=products.count()
            context={
                'products':products,
                'product_count':product_count,
                'keyword':keyword,     
            }
            return render(request,'store/store.html',context)

    return render(request,'store/store.html')

def submitreview(request,product_id):
    url =request.META.get('HTTP_REFERER')
    if request.method=='POST':
        try:
            reviews=ReviewRating.objects.get(user__id=request.user.id,product__id=product_id)
            form=ReviewForm(request.POST,instance=reviews)
            form.save()
            messages.success(request, 'Your review has been submitted updated!')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form=ReviewForm(request.POST)
            if form.is_valid():
                data=ReviewRating()
                data.subject=form.cleaned_data['subject']
                data.rating=form.cleaned_data['rating']
                data.review=form.cleaned_data['review']
                data.ip=request.META.get('REMOTE_ADDR')
                data.product_id=product_id
                data.user=request.user
                data.status=True
                data.save()
                messages.success(request, 'Your Review has been submitted successfully!')
                return redirect(url)
