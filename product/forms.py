from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import OrderFormInfo

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control mb-4",
            "placeholder": "Username",
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control mb-4",
            "placeholder": "Password",
        })
    )


class SignupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"})
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm Password"})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

        widgets = {
            'username': forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Username"
            }),
            'email': forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Email"
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already in use!")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        validate_password(password)  # Uses Django’s built-in strength validation
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password and confirm and password != confirm:
            self.add_error('confirm_password', "Passwords do not match")

        return cleaned_data
    

class OrderForm(forms.ModelForm):
    class Meta:
        model = OrderFormInfo
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address1', 'address2', 'city', 'state', 'country', 'note'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'address1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 1'}),
            'address2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 2'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country', 'value': 'India'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Order Note', 'rows': 3}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return phone
