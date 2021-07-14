from django import template

register = template.Library()

@register.filter
def handle_width(image):
    """Handle image resizing with same aspect ratio according to image height 200px"""
    return 200/int(image.height)*int(image.width)