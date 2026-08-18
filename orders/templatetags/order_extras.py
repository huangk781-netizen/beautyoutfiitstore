from django import template

register = template.Library()

STATUS_BADGE_CLASSES = {
    'pending_payment': 'bg-orange-100 text-orange-700',
    'paid': 'bg-sky-100 text-sky-700',
    'preparing': 'bg-purple-100 text-purple-700',
    'shipped': 'bg-blue-100 text-blue-700',
    'completed': 'bg-green-100 text-green-700',
    'returning': 'bg-red-100 text-red-700',
    'returned': 'bg-gray-200 text-gray-600',
}


@register.filter
def status_badge_class(status):
    return STATUS_BADGE_CLASSES.get(status, 'bg-secondary/60 text-neutral')
