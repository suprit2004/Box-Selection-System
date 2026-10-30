from django import forms
from fulfillment.models import Product, ShippingBox


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['sku', 'name', 'length', 'width', 'height', 'weight', 'is_active']
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. PROD-BOOK-01'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Product Name'}),
            'length': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0.01', 'placeholder': 'cm'}),
            'width': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0.01', 'placeholder': 'cm'}),
            'height': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0.01', 'placeholder': 'cm'}),
            'weight': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.001', 'min': '0.001', 'placeholder': 'kg'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class ShippingBoxForm(forms.ModelForm):
    class Meta:
        model = ShippingBox
        fields = ['code', 'name', 'internal_length', 'internal_width', 'internal_height', 'max_weight', 'cost', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. BOX-S'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Box Name'}),
            'internal_length': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0.01', 'placeholder': 'cm'}),
            'internal_width': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0.01', 'placeholder': 'cm'}),
            'internal_height': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0.01', 'placeholder': 'cm'}),
            'max_weight': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.001', 'min': '0.01', 'placeholder': 'kg'}),
            'cost': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0.00', 'placeholder': '$'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

