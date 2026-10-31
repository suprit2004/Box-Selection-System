from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from fulfillment.models import Order, OrderItem, Product


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select product-select'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control quantity-input',
                'min': '1',
                'value': '1',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True).order_by('name')
        self.fields['product'].empty_label = "-- Select Product --"
        # quantity is not required at the form level; the view enforces at least
        # one valid product+quantity pair across the whole formset.
        self.fields['quantity'].required = False

    def validate_unique(self):
    
        pass


class OrderItemBaseFormSet(BaseInlineFormSet):

    def validate_unique(self):
        # Intentionally suppressed — see docstring above.
        pass


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    formset=OrderItemBaseFormSet,  # Use custom base to suppress cross-row uniqueness check
    extra=0,           # Zero server-side blank rows; JS adds rows via empty_form
    can_delete=True,   # Renders DELETE checkbox for rows bound to existing DB records
    min_num=1,         # At least one form must be submitted
    validate_min=True, # Enforce min_num during full_clean()
)
