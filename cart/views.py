from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem
from store.models import Product, Variation
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
# Create your views here.


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


# @login_required(login_url='login')
def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)     # get the product
    product_variation = []

    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(
                    product=product, variation__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass

    try:
        # get the cart using the cart id present in the session
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    is_cart_item_exists = CartItem.objects.filter(
        product=product, cart=cart).exists()

    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(
            product=product, cart=cart)
        # existing variation -> database
        # current variation -> product_variation
        # item-id -> database
        ex_var_list = []
        id = []
        for item in cart_item:
            existing_variation = item.variation.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)

        if product_variation in ex_var_list:
            index = ex_var_list.index(product_variation)
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()

        else:
            item = CartItem.objects.create(
                product=product, quantity=1, cart=cart)
            if len(product_variation) > 0:
                item.variation.clear()
                item.variation.add(*product_variation)
            item.save()
    else:
        cart_item = CartItem.objects.create(
            product=product, quantity=1, cart=cart)
        if len(product_variation) > 0:
            cart_item.variation.clear()
            cart_item.variation.add(*product_variation)
        cart_item.save()

    return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(
            product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass

    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(
        product=product, cart=cart, id=cart_item_id)
    cart_item.delete()

    return redirect('cart')


# @login_required(login_url='login')
def cart(request, total=0, quantity=0, tax=0, delivery=0, grand_total=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            quantity += cart_item.quantity
            total += (cart_item.product.price * cart_item.quantity)

        tax = (4 * total)/100  # for 4% tax ... could be any amount tho
        delivery = (1 * total)/100  # random delivery fee
        grand_total = total + (tax + delivery)

    except ObjectDoesNotExist:
        pass

    context = {
        'quantity': quantity,
        'total': total,
        'tax': tax,
        'delivery': delivery,
        'grand_total': grand_total,
        'cart_items': cart_items,
    }

    return render(request, 'pages/cart.html', context)


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, tax=0, delivery=0, grand_total=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            quantity += cart_item.quantity
            total += (cart_item.product.price * cart_item.quantity)

        tax = (4 * total)/100  # for 4% tax ... could be any amount tho
        delivery = (1 * total)/100  # random delivery fee
        grand_total = total + (tax + delivery)

    except ObjectDoesNotExist:
        pass

    context = {
        'quantity': quantity,
        'total': total,
        'tax': tax,
        'delivery': delivery,
        'grand_total': grand_total,
        'cart_items': cart_items,
    }
    return render(request, 'pages/checkout.html', context)
