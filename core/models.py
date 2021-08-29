from django.db import models
from django.db.models import Q, CheckConstraint
from django.db.models.aggregates import Min
from django.db.models.fields.files import ImageField
from django.db.models.fields.related import ForeignKey, ManyToManyField, OneToOneField
from django.db.models.signals import post_save
from django.http import request
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.text import slugify
from django.conf import Settings, settings
from django.urls import reverse

from django.core.validators import MaxValueValidator, MinValueValidator

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    address_title = models.CharField(max_length=50)
    country = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    zip = models.CharField(max_length=50)
    detail = models.CharField(max_length=600)

    def __str__(self):
        return self.address_title
    
    class Meta:
        verbose_name_plural = 'Addresses'
    


class ProductRate(models.Model):
    product = OneToOneField('Product', on_delete=models.CASCADE)
    user_rates = ManyToManyField('Rate')


class Rate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rate = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])

    class Meta:
        constraints = (
            CheckConstraint(
                check=Q(rate__gte=0.0) & Q(rate__lte=5.0),
                name='star_rate_range'
            ),
        )

class SpecialProduct(models.Model):
    title = models.CharField(max_length=120) # trend, most bougth, etc.
    products = models.ManyToManyField('Product')

class FavouriteProduct(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField('Product')

class Product(models.Model):
    """
     Product model
    """
    title = models.CharField(max_length=120)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    slug = models.SlugField(null=True)
    description = models.TextField(max_length=1000)
    image = models.ImageField(upload_to='images/')
    stock = models.IntegerField()

    category = models.ForeignKey(
        'Category',
        related_name='products',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Product, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Gets absolute url for product, for example
        .../product/slugname/
        """
        return reverse("core:product-detail", kwargs={
            'slug': self.slug
        })

    def get_product_cart_url(self):
        return reverse('core:add-to-cart', kwargs={
            'slug': self.slug
        })
    
    def get_remove_one_product_url(self):
        return reverse('core:remove-one-product', kwargs={
            'slug': self.slug
        })

    def get_remove_product_cart_url(self):
        return reverse('core:remove-product', kwargs={
            'slug': self.slug
        })

class Category(MPTTModel):
    """
       MPTT is a technique for storing hierarchical data in a database. 
       The aim is to make retrieval operations very efficient. 
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    #Parent and child relation 
    parent = TreeForeignKey(
        'self',
        blank=True,
        null=True,
        related_name='child',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('slug', 'parent')
        verbose_name_plural = 'categories'
    
    
    def __str__(self):
        return self.name
        """ full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1]) """

    def get_name(self):
        return self.name


class ProductImage(models.Model):
    """
        Add multiple images for one product
    """
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')

class OrderProduct(models.Model):
    """
     Order product model,
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    is_ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{str(self.quantity)} x {self.product.title}"

    def get_total_item_price(self):
        return self.quantity * self.product.price

    def get_total_discount_item_price(self):
        return self.quantity * self.product.discount_price

    def get_final_price(self):
        if self.product.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

class Coupon(models.Model):
    key = models.CharField(max_length=16)
    #percantage
    amount = models.FloatField()

    def __str__(self):
        return self.key

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderProduct)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    order_date = models.DateTimeField(blank=True, null=True)
    is_ordered = models.BooleanField(default=False)
    
    shipping_address = models.ForeignKey(Address, related_name='shipping_address', on_delete=models.SET_NULL,
        blank=True, null=True)
    billing_address = models.ForeignKey(Address, related_name='billing_address', on_delete=models.SET_NULL,
        blank=True, null=True)

    is_refund_requested = models.BooleanField(default=False)
    is_refund_granted = models.BooleanField(default=False)

    is_delivered = models.BooleanField(default=False)
    is_received = models.BooleanField(default=False)

    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)

    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True)

    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)

    # order name is username
    def __str__(self):
        return self.user.username

    def get_total_order_price_without_coupon(self):
        sum = 0
        for item in self.items.all():
            sum += item.get_final_price()

        return sum
    def get_total_order_price(self):
        sum = 0
        for item in self.items.all():
            sum += item.get_final_price()
        if self.coupon:
            return sum -  (sum * (self.coupon.amount/100))
        return sum

class MobileCarousel(models.Model):
    image = models.ImageField(upload_to='images/')

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Payment(models.Model):
    stripe_payment_intent = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    email = models.EmailField()
    accepted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order.user.username

def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)

"""
This receiver will create Userprofile for user when a new user is created
"""
post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)