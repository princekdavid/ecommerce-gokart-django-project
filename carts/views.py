from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

# Create your views here.
def _cart_id(request):                            #  Private function to get cart id from session
    cart = request.session.session_key            #  get Cart id from session 
    if not cart:
        cart = request.session.create()           #  create cart_id if not available 
    return cart

def add_cart(request, product_id):
    current_user = request.user
    product= Product.objects.get(id=product_id)                       #   Get product using product_id
    if current_user.is_authenticated:
        product_variation = []
        if request.method =='POST':
            # color = request.POST['color']                 We want our program to check the variations
            # size = request.POST['size']
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.object.get(product = product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

            # add more Item in cart
        is_cart_item_exist = CartItem.objects.filter(product = product, user = current_user).exists()
        if is_cart_item_exist:
            cart_item = CartItem.objects.filter(product=product, user = current_user)

            existing_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                existing_variation_list.append(list(existing_variation))
                id.append(item.id)

            # check if current variation exist or not
            if product_variation in existing_variation_list:

                # increase cart item quantity
                index = existing_variation_list.index(product_variation)
                item_id = id[index]
                cart_item = CartItem.objects.get(product = product, id = item_id)
                cart_item.quantity += 1
                cart_item.save()
            else:
                cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
            )
                if len(product_variation) > 0:
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation)
                cart_item.save()

        else :
            
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()  

        return redirect('cart')
    
    else:
        product_variation = []
        if request.method =='POST':
            # color = request.POST['color']                 We want our program to check the variations
            # size = request.POST['size']
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.object.get(product = product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
        
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))             #  Get Cart_id from Private Function _cart_id
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

            # add more Item in cart
        is_cart_item_exist = CartItem.objects.filter(product = product, cart = cart).exists()
        if is_cart_item_exist:
            cart_item = CartItem.objects.filter(product=product, cart = cart)
            # check for Existing Variation  => database
            # check for current Variation   => product_variation
            # item id is required   =>  database
            existing_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                existing_variation_list.append(list(existing_variation))
                id.append(item.id)
            # check if current variation exist or not
            if product_variation in existing_variation_list:
                # increase cart item quantity
                index = existing_variation_list.index(product_variation)
                item_id = id[index]
                cart_item = CartItem.objects.get(product = product, id = item_id)
                cart_item.quantity += 1
                cart_item.save()
            else:
                cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
                if len(product_variation) > 0:
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation)
                cart_item.save()

        else :
            
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()  

        return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    product =  get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product,user=request.user,id=cart_item_id)

        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass

    return redirect('cart')

def remove_cart_item(request,product_id,cart_item_id):
    product = get_object_or_404(Product,id=product_id)
    if request.user:
        cart_item = CartItem.objects.get(product=product,user=request.user, id=cart_item_id)
    else:   
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(product=product,cart=cart, id=cart_item_id)
    cart_item.delete()
    
    return redirect('cart')


def cart(request, total = 0, quantity = 0, cart_items = None):
    tax = 0
    grand_total = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.product_price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2 * total)/100
        grand_total = tax + total
    except ObjectDoesNotExist:
        pass   #Just Ignore

    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' :grand_total,
    }
        
    return render(request,'store/cart.html',context)

@login_required(login_url= 'login')
def checkout(request, total = 0, quantity = 0, cart_items = None):
    tax = 0
    grand_total = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.product_price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2 * total)/100
        grand_total = tax + total
    except ObjectDoesNotExist:
        pass   #Just Ignore

    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' :grand_total,
    }
    return render(request, 'store/checkout.html', context)