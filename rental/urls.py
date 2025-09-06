"""
URL patterns for the rental app.
Maps URLs to view functions.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home and static pages
    path('', views.home, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup_view, name='signup'),
    
    # Dashboard URLs
    path('owner-dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('renter-dashboard/', views.renter_dashboard, name='renter_dashboard'),
    
    # Product management URLs
    path('add-product/', views.add_product, name='add_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    
    # Rental URLs
    path('rent/<int:product_id>/', views.rent_product, name='rent_product'),
    path('rental-history/', views.rental_history, name='rental_history'),
]
