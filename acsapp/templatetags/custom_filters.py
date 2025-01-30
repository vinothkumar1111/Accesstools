# acsapp/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def length_is(value, length):
    return len(value) == length



@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)
from django import template

register = template.Library()


@register.filter
def is_image(file_field):
    """Check if the file is an image based on its extension."""
    if not file_field:
        return False
    file_name = file_field.name if hasattr(file_field, 'name') else str(file_field)
    return file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))

