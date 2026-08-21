from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render

from .forms import RegisterForm
from .models import LoyaltySettings, Member


def register(request):
    if request.user.is_authenticated:
        return redirect('products:product_list')

    next_url = request.POST.get('next') or request.GET.get('next') or ''

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(
                request,
                user,
                backend='django.contrib.auth.backends.ModelBackend',
            )
            return redirect(next_url or 'products:product_list')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form, 'next': next_url})


@login_required
def profile(request):
    from orders.models import Order

    loyalty = LoyaltySettings.get_solo()
    member = request.user

    total_spent = Order.objects.filter(
        member=member, status=Order.Status.COMPLETED
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    if member.tier == Member.Tier.GOLD:
        next_tier_label = None
        amount_to_next_tier = None
    elif member.tier == Member.Tier.SILVER:
        next_tier_label = '金卡會員'
        amount_to_next_tier = max(loyalty.gold_threshold - total_spent, 0)
    else:
        next_tier_label = '銀卡會員'
        amount_to_next_tier = max(loyalty.silver_threshold - total_spent, 0)

    context = {
        'member': member,
        'total_spent': total_spent,
        'next_tier_label': next_tier_label,
        'amount_to_next_tier': amount_to_next_tier,
    }
    return render(request, 'accounts/profile.html', context)
