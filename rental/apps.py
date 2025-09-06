"""
Rental App Configuration for Rentz
"""

from django.apps import AppConfig


class RentalConfig(AppConfig):
    """
    App configuration for the rental functionality.
    Handles products, rentals, and user management.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rental'
    verbose_name = 'Rentz Rental System'
