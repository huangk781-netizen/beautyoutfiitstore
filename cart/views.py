from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from products.models import ProductVariant

from .cart import Cart


def cart_detail(request):
    return render(request, 'cart/detail.html', {'cart': Cart(request)})


@require_POST
def cart_add(request):
    variant = get_object_or_404(ProductVariant, id=request.POST.get('variant_id'))

    if not request.user.is_authenticated:
        messages.info(request, '請先登入會員才能加入購物車')
        next_url = reverse('products:product_detail', kwargs={'pk': variant.product_id})
        return redirect(f"{reverse('accounts:login')}?next={next_url}")

    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1
    quantity = max(quantity, 1)

    cart = Cart(request)
    before = cart.get_quantity(variant)
    cart.add(variant, quantity=quantity)
    after = cart.get_quantity(variant)

    if after > before:
        added = after - before
        messages.success(
            request,
            f'已加入購物車：{variant.product.name}（{variant.get_size_display()} / {variant.color}）x {added}',
        )
    else:
        messages.warning(request, '已達庫存上限，無法再加入')

    return redirect('products:product_detail', pk=variant.product_id)


@require_POST
def cart_increase(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    cart = Cart(request)
    cart.set_quantity(variant, cart.get_quantity(variant) + 1)
    return redirect('cart:cart_detail')


@require_POST
def cart_decrease(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    cart = Cart(request)
    cart.set_quantity(variant, cart.get_quantity(variant) - 1)
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    Cart(request).remove(variant)
    return redirect('cart:cart_detail')
