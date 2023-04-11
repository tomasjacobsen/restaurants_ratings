from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='smiley')
def smiley(rating):
    if rating in [0, 1]:
        icon = "<i class='bi bi-emoji-smile text-success'></i>"
    elif rating == 2:
        icon = "<i class='bi bi-emoji-neutral text-warning'></i>"
    elif rating == 3:
        icon = "<i class='bi bi-emoji-frown text-danger'></i>"
    else:
        icon = ""

    return mark_safe(icon)