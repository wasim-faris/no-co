from django import template

register = template.Library()

@register.filter
def split(value, arg):
    return value.split(arg)

@register.filter
def filter_status(queryset, status_name):
    """Filters the status history queryset for a specific status."""
    if not queryset:
        return None
    return queryset.filter(status=status_name).first()
