"""
Database models for Rentz application.
These models define the structure of our database tables.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    """
    Extended user profile to store additional information.
    Links to Django's built-in User model.
    """
    USER_TYPES = (
        ('owner', 'Owner'),     # Users who rent out items
        ('renter', 'Renter'),   # Users who rent items
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.user_type})"

class Product(models.Model):
    """
    Model for rental products/items.
    Each product belongs to an owner and can be rented by renters.
    """
    PRODUCT_CATEGORIES = (
        ('vehicle', 'Vehicle'),
        ('furniture', 'Furniture'),
        ('electronics', 'Electronics'),
        ('gadgets', 'Gadgets'),
        ('sports', 'Sports & Outdoor'),
        ('books', 'Books'),
        ('clothing', 'Clothing'),
        ('tools', 'Tools'),
        ('others', 'Others'),
    )
    
    AVAILABILITY_STATUS = (
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'Under Maintenance'),
    )
    
    # Basic product information
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=PRODUCT_CATEGORIES)
    description = models.TextField()
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Ownership and availability
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    availability = models.CharField(max_length=20, choices=AVAILABILITY_STATUS, default='available')
    
    # Media and timestamps
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - ₹{self.price_per_day}/day"
    
    def days_listed(self):
        """Calculate how many days this product has been listed"""
        return (timezone.now() - self.created_at).days
    
    class Meta:
        ordering = ['-created_at']  # Show newest products first

class Rental(models.Model):
    """
    Model to track rental transactions.
    Links renters, products, and rental details.
    """
    RENTAL_STATUS = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    # Rental relationship
    renter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rentals')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='rentals')
    
    # Rental details
    start_date = models.DateField()
    end_date = models.DateField()
    days_rented = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=RENTAL_STATUS, default='active')
    
    # Payment information
    payment_method = models.CharField(max_length=50, default='Online Payment')
    payment_status = models.CharField(max_length=20, default='Completed')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.renter.username} rented {self.product.name}"
    
    class Meta:
        ordering = ['-created_at']

class Payment(models.Model):
    """
    Model to track payment history.
    Links to rental transactions.
    """
    rental = models.OneToOneField(Rental, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment ₹{self.amount} for {self.rental.product.name}"
