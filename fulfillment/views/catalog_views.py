from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import ProtectedError
from fulfillment.models import Product, ShippingBox
from fulfillment.forms import ProductForm, ShippingBoxForm


def product_list_create(request):
    """Lists existing products and handles creation of new products."""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.name}' ({product.sku}) added successfully.")
            return redirect('product_list_create')
        else:
            messages.error(request, "Please correct the form errors below.")
    else:
        form = ProductForm()

    products = Product.objects.all().order_by('-created_at')
    return render(request, 'fulfillment/product_list.html', {
        'form': form,
        'products': products
    })


def product_edit(request, pk):
    """Edits an existing product."""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product '{product.name}' updated successfully.")
            return redirect('product_list_create')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProductForm(instance=product)

    return render(request, 'fulfillment/product_edit.html', {
        'form': form,
        'product': product
    })


def product_delete(request, pk):
    """Deletes an existing product or warns if protected by order history."""
    from django.urls import reverse
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        try:
            name = product.name
            product.delete()
            messages.success(request, f"Product '{name}' was deleted.")
        except ProtectedError:
            messages.error(
                request,
                f"Cannot delete '{product.name}' because it is referenced in past orders. "
                "You can uncheck 'Active for shipping' to deactivate it without breaking history."
            )
        return redirect('product_list_create')

    return render(request, 'fulfillment/confirm_delete.html', {
        'item_type': 'Product',
        'item_name': f"{product.name} ({product.sku})",
        'cancel_url': reverse('product_list_create'),
    })


def box_list_create(request):
    """Lists existing shipping boxes and handles creation of new boxes."""
    if request.method == 'POST':
        form = ShippingBoxForm(request.POST)
        if form.is_valid():
            box = form.save()
            messages.success(request, f"Shipping Box '{box.name}' [{box.code}] added successfully.")
            return redirect('box_list_create')
        else:
            messages.error(request, "Please correct the form errors below.")
    else:
        form = ShippingBoxForm()

    boxes = ShippingBox.objects.all().order_by('cost', 'internal_length')
    return render(request, 'fulfillment/box_list.html', {
        'form': form,
        'boxes': boxes
    })


def box_edit(request, pk):
    """Edits an existing shipping box."""
    box = get_object_or_404(ShippingBox, pk=pk)
    if request.method == 'POST':
        form = ShippingBoxForm(request.POST, instance=box)
        if form.is_valid():
            form.save()
            messages.success(request, f"Shipping Box '{box.name}' updated successfully.")
            return redirect('box_list_create')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ShippingBoxForm(instance=box)

    return render(request, 'fulfillment/box_edit.html', {
        'form': form,
        'box': box
    })


def box_delete(request, pk):
    """Deletes an existing shipping box."""
    from django.urls import reverse
    box = get_object_or_404(ShippingBox, pk=pk)
    if request.method == 'POST':
        name = box.name
        code = box.code
        box.delete()
        messages.success(request, f"Shipping Box '{name}' [{code}] was deleted.")
        return redirect('box_list_create')

    return render(request, 'fulfillment/confirm_delete.html', {
        'item_type': 'Shipping Box',
        'item_name': f"{box.name} [{box.code}]",
        'cancel_url': reverse('box_list_create'),
    })
