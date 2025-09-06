"""
Views for Rentz application.
These functions handle HTTP requests and return responses.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import uuid

from .models import Product, UserProfile, Rental, Payment
from .forms import SignUpForm, ProductForm, RentalForm

def home(request):
    """
    Home page view - Shows featured products and welcome message.
    Available to all users (authenticated and anonymous).
    """
    # Get featured products (latest 6 available products)
    featured_products = Product.objects.filter(availability='available')[:6]
    
    context = {
        'featured_products': featured_products,
        'total_products': Product.objects.filter(availability='available').count(),
        'categories': Product.PRODUCT_CATEGORIES,
    }
    return render(request, 'home.html', context)

def signup_view(request):
    """
    User registration view.
    Handles both GET (show form) and POST (process form) requests.
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Save new user and automatically log them in
            user = form.save()
            login(request, user)
            
            # Show success message
            messages.success(request, f'Welcome to Rentz, {user.first_name}! Your account has been created.')
            
            # Redirect based on user type
            user_profile = UserProfile.objects.get(user=user)
            if user_profile.user_type == 'owner':
                return redirect('owner_dashboard')
            else:
                return redirect('renter_dashboard')
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})

def about_view(request):
    """About Us page - Information about Rentz platform"""
    return render(request, 'about.html')

def contact_view(request):
    """Contact Us page - Contact information and form"""
    if request.method == 'POST':
        # In a real app, you'd handle contact form submission here
        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        return redirect('contact')
    
    return render(request, 'contact.html')

@login_required
def owner_dashboard(request):
    """
    Owner dashboard - Shows owner's products, earnings, and statistics.
    Only accessible to users with owner profile.
    """
    # Check if user is an owner
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.user_type != 'owner':
            messages.error(request, 'Access denied. Owner account required.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profile not found. Please contact support.')
        return redirect('home')
    
    # Get owner's products
    products = Product.objects.filter(owner=request.user)
    
    # Calculate total earnings from completed rentals
    total_earnings = Rental.objects.filter(
        product__owner=request.user,
        payment_status='Completed'
    ).aggregate(Sum('total_cost'))['total_cost__sum'] or 0
    
    # Get recent rentals for owner's products
    recent_rentals = Rental.objects.filter(
        product__owner=request.user
    ).order_by('-created_at')[:5]
    
    context = {
        'products': products,
        'total_products': products.count(),
        'available_products': products.filter(availability='available').count(),
        'rented_products': products.filter(availability='rented').count(),
        'total_earnings': total_earnings,
        'recent_rentals': recent_rentals,
    }
    
    return render(request, 'owner_dashboard.html', context)

@login_required
def renter_dashboard(request):
    """
    Renter dashboard - Shows available products and rental history.
    Only accessible to users with renter profile.
    """
    # Check if user is a renter
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.user_type != 'owner':  # Renters can access this
            pass
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profile not found. Please contact support.')
        return redirect('home')
    
    # Get available products
    products = Product.objects.filter(availability='available')
    
    # Filter by category if requested
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category=category_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Get user's rental history
    user_rentals = Rental.objects.filter(renter=request.user).order_by('-created_at')[:5]
    
    # Calculate total spent
    total_spent = Rental.objects.filter(
        renter=request.user,
        payment_status='Completed'
    ).aggregate(Sum('total_cost'))['total_cost__sum'] or 0
    
    context = {
        'products': products,
        'categories': Product.PRODUCT_CATEGORIES,
        'selected_category': category_filter,
        'search_query': search_query,
        'user_rentals': user_rentals,
        'total_spent': total_spent,
    }
    
    return render(request, 'renter_dashboard.html', context)

@login_required
def add_product(request):
    """
    Add new product view - Only for owners.
    Allows owners to list new items for rent.
    """
    # Check if user is an owner
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.user_type != 'owner':
            messages.error(request, 'Only owners can add products.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            # Save product with current user as owner
            product = form.save(commit=False)
            product.owner = request.user
            product.save()
            
            messages.success(request, f'Product "{product.name}" has been added successfully!')
            return redirect('owner_dashboard')
    else:
        form = ProductForm()
    
    return render(request, 'add_product.html', {'form': form})

@login_required
def delete_product(request, product_id):
    """
    Delete product view - Only owners can delete their own products.
    """
    product = get_object_or_404(Product, id=product_id, owner=request.user)
    
    # Check if product has active rentals
    active_rentals = Rental.objects.filter(product=product, status='active')
    if active_rentals.exists():
        messages.error(request, 'Cannot delete product with active rentals.')
        return redirect('owner_dashboard')
    
    product_name = product.name
    product.delete()
    messages.success(request, f'Product "{product_name}" has been deleted.')
    
    return redirect('owner_dashboard')

@login_required
def rent_product(request, product_id):
    """
    Rent product view - Process rental requests from renters.
    """
    product = get_object_or_404(Product, id=product_id, availability='available')
    
    # Check if user is trying to rent their own product
    if product.owner == request.user:
        messages.error(request, 'You cannot rent your own product.')
        return redirect('renter_dashboard')
    
    if request.method == 'POST':
        form = RentalForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            days = form.cleaned_data['days']
            
            # Validate start date
            if start_date < timezone.now().date():
                messages.error(request, 'Start date cannot be in the past.')
                return render(request, 'rent_product.html', {'form': form, 'product': product})
            
            # Calculate end date and total cost
            end_date = start_date + timedelta(days=days)
            total_cost = product.price_per_day * days
            
            # Create rental record
            rental = Rental.objects.create(
                renter=request.user,
                product=product,
                start_date=start_date,
                end_date=end_date,
                days_rented=days,
                total_cost=total_cost,
                payment_method='Online Payment',
                payment_status='Completed'
            )
            
            # Create payment record
            Payment.objects.create(
                rental=rental,
                amount=total_cost,
                payment_method='Credit Card',
                transaction_id=f'TXN{uuid.uuid4().hex[:10].upper()}'
            )
            
            # Update product availability
            product.availability = 'rented'
            product.save()
            
            messages.success(request, f'Successfully rented {product.name} for {days} days. Total cost: ₹{total_cost}')
            return redirect('renter_dashboard')
    else:
        form = RentalForm()
    
    context = {
        'form': form,
        'product': product,
    }
    
    return render(request, 'rent_product.html', context)

@login_required
def rental_history(request):
    """
    View rental history - Shows user's past and current rentals.
    """
    rentals = Rental.objects.filter(renter=request.user).order_by('-created_at')
    
    context = {
        'rentals': rentals,
    }
    
    return render(request, 'rental_history.html', context)
