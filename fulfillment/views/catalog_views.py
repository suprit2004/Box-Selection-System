from django.shortcuts import render, redirect
from django.contrib import messages
from fulfillment.models import Product, ShippingBox
from fulfillment.forms import ProductForm, ShippingBoxForm


def product_list_create(request):
    """Lists existing products and handles creation of new products."""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.name}' ({product.sku}) created successfully.")
            return redirect('product_list_create')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProductForm()

    products = Product.objects.all().order_by('-created_at')
    return render(request, 'fulfillment/product_list.html', {
        'form': form,
        'products': products
    })


def box_list_create(request):
    """Lists existing shipping boxes and handles creation of new boxes."""
    if request.method == 'POST':
        form = ShippingBoxForm(request.POST)
        if form.is_valid():
            box = form.save()
            messages.success(request, f"Shipping Box '{box.name}' [{box.code}] created successfully.")
            return redirect('box_list_create')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ShippingBoxForm()

    boxes = ShippingBox.objects.all().order_by('cost', 'internal_length')
    return render(request, 'fulfillment/box_list.html', {
        'form': form,
        'boxes': boxes
    })

