from django import forms
from django.db import models
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
from django.forms.widgets import Widget
from .models import Address

class CheckoutForm(forms.Form):
    first_name = forms.CharField(required=False, max_length=50)
    last_name = forms.CharField(required=False, max_length=50)

    shipping_address_title = forms.CharField(required=False, max_length=40)
    country = forms.CharField(required=False, max_length=100)
    province = forms.CharField(required=False, max_length=100)
    zip = forms.CharField(required=False, max_length=50)
    address_detail = forms.CharField(required=False, max_length=600)

    same_billing_address = forms.BooleanField(required=False)

    billing_address_title = forms.CharField(required=False, max_length=40)

    billing_country = forms.CharField(required=False, max_length=100)
    billing_province = forms.CharField(required=False, max_length=100)
    billing_zip = forms.CharField(required=False, max_length=50)
    billing_address_detail = forms.CharField(required=False, max_length=600)


class CouponForm(forms.Form):
    promo_code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code'
    }))
