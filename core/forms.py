from random import choices
from django import forms
from django.db import models
from django.db.models.query import QuerySet
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
from django.forms.widgets import Textarea, Widget
from .models import Address

class CheckoutForm(forms.Form):
    first_name = forms.CharField(required=False, max_length=50)
    last_name = forms.CharField(required=False, max_length=50)

    shipping_address = forms.ChoiceField(widget=forms.Select(attrs={
        'class': 'custom-select d-block w-100'
    }), required=False)

    billing_address = forms.ChoiceField(widget=forms.Select(attrs={
        'class': 'custom-select d-block w-100'
    }), required=False)

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

    def __init__(self, user, *args, **kwargs):
        super(CheckoutForm, self).__init__(*args, **kwargs)
        # This part defines the choice of addres per user
        self.fields['shipping_address'].choices = [("None",'-------')]
        self.fields['shipping_address'].choices += ((str(addr.pk), f"{addr.address_title}") for addr in Address.objects.filter(user=user))
        
        self.fields['billing_address'].choices = [("None",'-------')]
        self.fields['billing_address'].choices += ((str(addr.pk), f"{addr.address_title}") for addr in Address.objects.filter(user=user))

class CouponForm(forms.Form):
    promo_code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code'
    }))

class RefundForm(forms.Form):
    reason = forms.CharField(widget=Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()

class SearchForm(forms.Form):
    search = forms.CharField()
