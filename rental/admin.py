"""
Django Admin Configuration for Rentz Rental Application
Provides a comprehensive admin interface for managing users, products, rentals, and payments.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta

from .models import UserProfile, Product, Rental, Payment


# ========================================
# INLINE ADMIN CLASSES
# ========================================

class UserProfileInline(admin.StackedInline):
    """
    Inline admin for UserProfile to show user profile info in User admin
    """
    model = UserProfile
    can_delete = False
    verbose_name = "User Profile"
    verbose_name_plural = "User Profile"
    
    fieldsets = (
        ('Profile Information', {
            'fields': ('user_type', 'phone_number', 'address')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)


class RentalInline(admin.TabularInline):
    """
    Inline admin for Rentals to show in Product admin
    """
    model = Rental
    extra = 0
    readonly_fields = ('created_at', 'total_cost', 'payment_status')
    fields = ('renter', 'start_date', 'end_date', 'days_rented', 'total_cost', 'status', 'payment_status')
    
    def has_add_permission(self, request, obj=None):
        return False  # Prevent adding rentals from product admin


class PaymentInline(admin.StackedInline):
    """
    Inline admin for Payment to show in Rental admin
    """
    model = Payment
    extra = 0
    readonly_fields = ('payment_date', 'transaction_id')
    fields = ('amount', 'payment_method', 'transaction_id', 'payment_date')


# ========================================
# CUSTOM USER ADMIN
# ========================================

class UserAdmin(BaseUserAdmin):
    """
    Extended User admin with UserProfile inline
    """
    inlines = (UserProfileInline,)
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_user_type', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined', 'userprofile__user_type')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'userprofile__phone_number')
    
    def get_user_type(self, obj):
        """Display user type from profile"""
        try:
            return obj.userprofile.get_user_type_display()
        except UserProfile.DoesNotExist:
            return "No Profile"
    get_user_type.short_description = "User Type"
    get_user_type.admin_order_field = 'userprofile__user_type'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('userprofile')


# ========================================
# USER PROFILE ADMIN
# ========================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for UserProfile model
    """
    list_display = ('user', 'user_type', 'phone_number', 'get_products_count', 'get_rentals_count', 'created_at')
    list_filter = ('user_type', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone_number')
    readonly_fields = ('created_at', 'get_user_info', 'get_activity_summary')
    
    fieldsets = (
        ('User Information', {
            'fields': ('get_user_info', 'user', 'user_type')
        }),
        ('Contact Details', {
            'fields': ('phone_number', 'address')
        }),
        ('Activity Summary', {
            'fields': ('get_activity_summary',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_info(self, obj):
        """Display formatted user information"""
        if obj.user:
            return format_html(
                '<strong>{}</strong><br>'
                'Email: {}<br>'
                'Joined: {}',
                obj.user.get_full_name() or obj.user.username,
                obj.user.email,
                obj.user.date_joined.strftime('%B %d, %Y')
            )
        return "No user associated"
    get_user_info.short_description = "User Details"
    
    def get_products_count(self, obj):
        """Display number of products owned"""
        if obj.user_type == 'owner':
            count = obj.user.products.count()
            return format_html('<span style="color: #2e7d32;">{}</span>', count)
        return "N/A"
    get_products_count.short_description = "Products"
    
    def get_rentals_count(self, obj):
        """Display number of rentals made"""
        count = obj.user.rentals.count()
        return format_html('<span style="color: #1976d2;">{}</span>', count)
    get_rentals_count.short_description = "Rentals"
    
    def get_activity_summary(self, obj):
        """Display comprehensive activity summary"""
        if obj.user_type == 'owner':
            products_count = obj.user.products.count()
            total_earnings = obj.user.products.aggregate(
                total=Sum('rentals__total_cost')
            )['total'] or 0
            
            return format_html(
                '<div style="background: #f5f5f5; padding: 10px; border-radius: 5px;">'
                '<strong>Owner Statistics:</strong><br>'
                '📦 Products Listed: {}<br>'
                '💰 Total Earnings: ₹{}<br>'
                '</div>',
                products_count,
                total_earnings
            )
        else:
            rentals_count = obj.user.rentals.count()
            total_spent = obj.user.rentals.aggregate(
                total=Sum('total_cost')
            )['total'] or 0
            
            return format_html(
                '<div style="background: #f5f5f5; padding: 10px; border-radius: 5px;">'
                '<strong>Renter Statistics:</strong><br>'
                '🛒 Total Rentals: {}<br>'
                '💳 Total Spent: ₹{}<br>'
                '</div>',
                rentals_count,
                total_spent
            )
    get_activity_summary.short_description = "Activity Summary"


# ========================================
# PRODUCT ADMIN
# ========================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin interface for Product model
    """
    list_display = ('name', 'category', 'owner', 'price_per_day', 'availability', 'get_image_preview', 'get_rental_count', 'created_at')
    list_filter = ('category', 'availability', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'owner__username', 'owner__email')
    readonly_fields = ('created_at', 'updated_at', 'get_image_preview', 'get_rental_history', 'get_earnings_summary')
    inlines = (RentalInline,)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description')
        }),
        ('Pricing & Availability', {
            'fields': ('price_per_day', 'availability')
        }),
        ('Ownership', {
            'fields': ('owner',)
        }),
        ('Media', {
            'fields': ('image', 'get_image_preview')
        }),
        ('Statistics', {
            'fields': ('get_rental_history', 'get_earnings_summary'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_image_preview(self, obj):
        """Display image preview in admin"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return "No image uploaded"
    get_image_preview.short_description = "Image Preview"
    
    def get_rental_count(self, obj):
        """Display rental count with color coding"""
        count = obj.rentals.count()
        if count > 5:
            color = "#2e7d32"  # Green
        elif count > 0:
            color = "#f57c00"  # Orange
        else:
            color = "#757575"  # Gray
        
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, count)
    get_rental_count.short_description = "Rentals"
    
    def get_rental_history(self, obj):
        """Display detailed rental history"""
        rentals = obj.rentals.order_by('-created_at')[:5]
        if not rentals:
            return "No rentals yet"
        
        rental_list = []
        for rental in rentals:
            rental_list.append(
                f"• {rental.renter.username} ({rental.start_date} - {rental.end_date}) - ₹{rental.total_cost}"
            )
        
        more_count = obj.rentals.count() - 5
        if more_count > 0:
            rental_list.append(f"... and {more_count} more")
        
        return format_html(
            '<div style="background: #f5f5f5; padding: 10px; border-radius: 5px;">'
            '<strong>Recent Rentals:</strong><br>'
            '{}'
            '</div>',
            '<br>'.join(rental_list)
        )
    get_rental_history.short_description = "Recent Rentals"
    
    def get_earnings_summary(self, obj):
        """Display earnings summary"""
        total_earnings = obj.rentals.aggregate(total=Sum('total_cost'))['total'] or 0
        total_days = obj.rentals.aggregate(total=Sum('days_rented'))['total'] or 0
        
        return format_html(
            '<div style="background: #e8f5e8; padding: 10px; border-radius: 5px;">'
            '<strong>Earnings Summary:</strong><br>'
            '💰 Total Earnings: ₹{}<br>'
            '📅 Total Days Rented: {} days<br>'
            '📊 Average per Day: ₹{}<br>'
            '</div>',
            total_earnings,
            total_days,
            round(total_earnings / total_days, 2) if total_days > 0 else 0
        )
    get_earnings_summary.short_description = "Earnings"
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('owner').prefetch_related('rentals')


# ========================================
# RENTAL ADMIN
# ========================================

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    """
    Admin interface for Rental model
    """
    list_display = ('get_product_name', 'renter', 'start_date', 'end_date', 'days_rented', 'total_cost', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at', 'start_date')
    search_fields = ('product__name', 'renter__username', 'renter__email', 'product__owner__username')
    readonly_fields = ('created_at', 'updated_at', 'get_rental_details', 'get_duration_info')
    inlines = (PaymentInline,)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Rental Information', {
            'fields': ('product', 'renter', 'get_rental_details')
        }),
        ('Duration & Pricing', {
            'fields': ('start_date', 'end_date', 'days_rented', 'total_cost', 'get_duration_info')
        }),
        ('Status & Payment', {
            'fields': ('status', 'payment_method', 'payment_status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_product_name(self, obj):
        """Display product name with link"""
        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            reverse('admin:rental_product_change', args=[obj.product.id]),
            obj.product.name
        )
    get_product_name.short_description = "Product"
    get_product_name.admin_order_field = 'product__name'
    
    def get_rental_details(self, obj):
        """Display comprehensive rental details"""
        return format_html(
            '<div style="background: #f5f5f5; padding: 10px; border-radius: 5px;">'
            '<strong>Rental Details:</strong><br>'
            '📦 Product: {}<br>'
            '👤 Owner: {}<br>'
            '🏷️ Category: {}<br>'
            '💰 Daily Rate: ₹{}<br>'
            '</div>',
            obj.product.name,
            obj.product.owner.get_full_name() or obj.product.owner.username,
            obj.product.get_category_display(),
            obj.product.price_per_day
        )
    get_rental_details.short_description = "Details"
    
    def get_duration_info(self, obj):
        """Display duration calculation details"""
        days_elapsed = (timezone.now().date() - obj.start_date).days
        days_remaining = (obj.end_date - timezone.now().date()).days
        
        status_color = "#2e7d32" if days_remaining > 0 else "#d32f2f"
        
        return format_html(
            '<div style="background: #e3f2fd; padding: 10px; border-radius: 5px;">'
            '<strong>Duration Analysis:</strong><br>'
            '📅 Total Duration: {} days<br>'
            '⏱️ Days Elapsed: {} days<br>'
            '<span style="color: {};">📍 Days Remaining: {} days</span><br>'
            '💵 Cost per Day: ₹{}<br>'
            '</div>',
            obj.days_rented,
            max(0, days_elapsed),
            status_color,
            max(0, days_remaining),
            round(obj.total_cost / obj.days_rented, 2) if obj.days_rented > 0 else 0
        )
    get_duration_info.short_description = "Duration Info"
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('product', 'product__owner', 'renter')


# ========================================
# PAYMENT ADMIN
# ========================================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Admin interface for Payment model
    """
    list_display = ('transaction_id', 'get_rental_info', 'amount', 'payment_method', 'payment_date')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('transaction_id', 'rental__product__name', 'rental__renter__username')
    readonly_fields = ('payment_date', 'get_payment_details', 'get_rental_summary')
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('rental', 'amount', 'payment_method', 'transaction_id')
        }),
        ('Details', {
            'fields': ('get_payment_details', 'get_rental_summary'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('payment_date',),
            'classes': ('collapse',)
        }),
    )
    
    def get_rental_info(self, obj):
        """Display rental information"""
        return format_html(
            '{} → {}',
            obj.rental.product.name,
            obj.rental.renter.username
        )
    get_rental_info.short_description = "Rental"
    get_rental_info.admin_order_field = 'rental__product__name'
    
    def get_payment_details(self, obj):
        """Display payment details"""
        return format_html(
            '<div style="background: #f5f5f5; padding: 10px; border-radius: 5px;">'
            '<strong>Payment Details:</strong><br>'
            '🆔 Transaction ID: {}<br>'
            '💳 Method: {}<br>'
            '💰 Amount: ₹{}<br>'
            '📅 Date: {}<br>'
            '</div>',
            obj.transaction_id,
            obj.payment_method,
            obj.amount,
            obj.payment_date.strftime('%B %d, %Y at %I:%M %p')
        )
    get_payment_details.short_description = "Payment Details"
    
    def get_rental_summary(self, obj):
        """Display rental summary"""
        rental = obj.rental
        return format_html(
            '<div style="background: #e8f5e8; padding: 10px; border-radius: 5px;">'
            '<strong>Associated Rental:</strong><br>'
            '📦 Product: {}<br>'
            '👤 Renter: {}<br>'
            '📅 Duration: {} days<br>'
            '🔄 Status: {}<br>'
            '</div>',
            rental.product.name,
            rental.renter.get_full_name() or rental.renter.username,
            rental.days_rented,
            rental.get_status_display()
        )
    get_rental_summary.short_description = "Rental Summary"
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('rental', 'rental__product', 'rental__renter')


# ========================================
# ADMIN SITE CUSTOMIZATION
# ========================================

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Customize admin site headers
admin.site.site_header = "Rentz Administration"
admin.site.site_title = "Rentz Admin"
admin.site.index_title = "Welcome to Rentz Administration Panel"

# Add custom CSS to admin
def get_admin_media():
    """Add custom CSS for better admin interface"""
    return {
        'css': {
            'all': ('admin/css/custom_admin.css',)
        }
    }

# Custom admin actions
def mark_products_available(modeladmin, request, queryset):
    """Mark selected products as available"""
    updated = queryset.update(availability='available')
    modeladmin.message_user(request, f'{updated} products marked as available.')
mark_products_available.short_description = "Mark selected products as available"

def mark_rentals_completed(modeladmin, request, queryset):
    """Mark selected rentals as completed"""
    updated = queryset.update(status='completed')
    modeladmin.message_user(request, f'{updated} rentals marked as completed.')
mark_rentals_completed.short_description = "Mark selected rentals as completed"

# Add actions to respective admin classes
ProductAdmin.actions = [mark_products_available]
RentalAdmin.actions = [mark_rentals_completed]

# Custom admin dashboard stats (would require additional setup)
def admin_dashboard_stats():
    """Generate dashboard statistics"""
    from django.db.models import Count, Sum
    
    stats = {
        'total_users': User.objects.count(),
        'total_products': Product.objects.count(),
        'total_rentals': Rental.objects.count(),
        'total_revenue': Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0,
        'active_rentals': Rental.objects.filter(status='active').count(),
        'new_users_this_week': User.objects.filter(
            date_joined__gte=timezone.now() - timedelta(days=7)
        ).count(),
    }
    
    return stats

# Add to admin site context (would require custom admin template)
# admin.site.each_context = lambda request: admin_dashboard_stats()
