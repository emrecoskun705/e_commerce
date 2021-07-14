from django import template

register = template.Library()

@register.simple_tag
def handle_width(image, height, *args, **kwargs):
    """Handle image resizing with same aspect ratio according to height parameter"""
    return height/int(image.height)*int(image.width)