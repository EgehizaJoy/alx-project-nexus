from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Customer(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/CustomerProfilePic/',null=True,blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return self.user.first_name


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Bottles', 'Bottles'),
        ('Clothing', 'Clothing'),
        ('Home', 'Home'),
        ('Gallery', 'Books'),
        ('Other', 'Other'),
    ]
    name=models.CharField(max_length=40)
    product_image= models.ImageField(upload_to='product_image/',null=True,blank=True)
    price = models.PositiveIntegerField()
    # description=models.CharField(max_length=40)
    description = models.TextField()  # ✅ allows long text
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    # Add these new fields for inventory management
    is_available = models.BooleanField(default=True, verbose_name="Available for purchase")
    stock_count = models.PositiveIntegerField(default=0, verbose_name="Quantity in stock")
    low_stock_threshold = models.PositiveIntegerField(
        default=10, 
        verbose_name="Low stock alert threshold"
    )
     # You might also want to add these fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        """Check if product is running low on stock"""
        return self.stock_count <= self.low_stock_threshold
    
    @property
    def is_out_of_stock(self):
        """Check if product is out of stock"""
        return self.stock_count == 0

class Orders(models.Model):
    STATUS =(
        ('Pending','Pending'),
        ('Order Confirmed','Order Confirmed'),
        ('Out for Delivery','Out for Delivery'),
        ('Delivered','Delivered'),
    )
    customer=models.ForeignKey('Customer', on_delete=models.CASCADE,null=True)
    product=models.ForeignKey('Product',on_delete=models.CASCADE,null=True)
    email = models.CharField(max_length=50,null=True)
    address = models.CharField(max_length=500,null=True)
    mobile = models.CharField(max_length=20,null=True)
    order_date= models.DateField(auto_now_add=True,null=True)
    status=models.CharField(max_length=50,null=True,choices=STATUS)


class Feedback(models.Model):
    name=models.CharField(max_length=40)
    feedback=models.CharField(max_length=500)
    date= models.DateField(auto_now_add=True,null=True)
    def __str__(self):
        return self.name
