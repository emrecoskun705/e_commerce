from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.text import slugify
from django.conf import settings

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

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Product, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return self.slug

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
        return f'{self.quantity} x {self.product.title}'

    def get_total_item_price(self):
        return self.quantity * self.product.price

    def get_total_discount_item_price(self):
        return self.quantity * self.product.discount_price

    def get_final_price(self):
        if self.product.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderProduct)
    timestamp = models.DateTimeField(auto_now_add=True)
    order_date = models.DateTimeField()
    is_ordered = models.BooleanField(default=False)
    ####
    #### ADD ADDRESS METHOD
    ###
    is_refund_requested = models.BooleanField(default=False)
    is_refund_granted = models.BooleanField(default=False)

    is_delivered = models.BooleanField(default=False)
    is_received = models.BooleanField(default=False)


    # order name is username
    def __str__(self):
        return self.user.username
    