"""
Forms for Rentz application.
These forms handle user input and validation.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Product

class SignUpForm(UserCreationForm):
    """
    Custom signup form with additional fields.
    Extends Django's built-in UserCreationForm.
    """
    USER_TYPES = (
        ('owner', 'I want to rent out my items'),
        ('renter', 'I want to rent items from others'),
    )
    
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Enter your email'
    }))
    
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'First Name'
    }))
    
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Last Name'
    }))
    
    user_type = forms.ChoiceField(choices=USER_TYPES, widget=forms.RadioSelect(attrs={
        'class': 'user-type-radio'
    }))
    
    phone_number = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Phone Number (Optional)'
    }))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Choose a username'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-input',
                'placeholder': 'Password'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-input',
                'placeholder': 'Confirm Password'
            }),
        }
    
    def save(self, commit=True):
        """Save user and create associated UserProfile"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Create UserProfile
            UserProfile.objects.create(
                user=user,
                user_type=self.cleaned_data['user_type'],
                phone_number=self.cleaned_data.get('phone_number', '')
            )
        return user

class ProductForm(forms.ModelForm):
    """
    Form for adding/editing products.
    Used by owners to list their items for rent.
    """
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price_per_day', 'image', 'availability']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter product name'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Describe your product...',
                'rows': 4
            }),
            'price_per_day': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Price per day (₹)'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-file-input',
                'accept': 'image/*'
            }),
            'availability': forms.Select(attrs={
                'class': 'form-select'
            })
        }

class RentalForm(forms.Form):
    """
    Form for renting products.
    Used by renters to specify rental duration.
    """
    start_date = forms.DateField(widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-input'
    }))
    
    days = forms.IntegerField(min_value=1, max_value=365, widget=forms.NumberInput(attrs={
        'class': 'form-input',
        'placeholder': 'Number of days',
        'min': '1',
        'max': '365'
    }))
