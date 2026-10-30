from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction

from fulfillment.models import Order, OrderItem, Product, ShippingBox, OrderStatus
from fulfillment.services.box_selector import BoxSelectorService
from fulfillment.forms import OrderItemFormSet


def order_list(request):
    """Displays a list of past orders and their recommendation statuses."""
    orders = Order.objects.select_related('recommended_box').prefetch_related('items__product').all()
    return render(request, 'fulfillment/order_list.html', {
        'orders': orders
    })


def order_create(request):
    """
    Creates a new order with selected products and quantities,
    then automatically runs the box selection optimization engine.
    """
    products = Product.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        order = Order()
        formset = OrderItemFormSet(request.POST, instance=order)

        if formset.is_valid():
            # Extract valid rows and combine duplicate product selections if any
            combined_items: dict[int, int] = {}
            for form in formset.cleaned_data:
                if not form or form.get('DELETE'):
                    continue
                product = form.get('product')
                quantity = form.get('quantity')
                if product and quantity:
                    combined_items[product.id] = combined_items.get(product.id, 0) + quantity

            if not combined_items:
                messages.error(request, "Please add at least one product with quantity 1 or more.")
                return render(request, 'fulfillment/order_create.html', {
                    'formset': formset,
                    'products': products
                })

            with transaction.atomic():
                order.save()
                for prod_id, qty in combined_items.items():
                    prod = Product.objects.get(id=prod_id)
                    OrderItem.objects.create(
                        order=order,
                        product=prod,
                        quantity=qty,
                        unit_weight=prod.weight
                    )

                # Run Box Selection Service
                result = BoxSelectorService.recommend_for_order(order)

            if result.is_success:
                messages.success(request, f"Box recommendation generated: {result.box_name}!")
            else:
                messages.warning(request, "Order could not be accommodated in any standard box. See diagnostics below.")

            return redirect('order_recommendation', order_id=order.id)
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        order = Order()
        formset = OrderItemFormSet(instance=order)

    return render(request, 'fulfillment/order_create.html', {
        'formset': formset,
        'products': products
    })


def order_recommendation(request, order_id):
    """Displays the comprehensive packaging recommendation details for an order."""
    order = get_object_or_404(
        Order.objects.select_related('recommended_box').prefetch_related('items__product'),
        id=order_id
    )

    # Re-run simulation to get fine-grained placement coordinates for visualization
    items_input = []
    from fulfillment.services.packing_engine import ItemCuboid
    for item in order.items.all():
        cuboid = ItemCuboid(
            sku=item.product.sku,
            length=item.product.length,
            width=item.product.width,
            height=item.product.height,
            weight=item.unit_weight
        )
        items_input.append((cuboid, item.quantity))

    result = BoxSelectorService.select_box_for_items(items_input)

    return render(request, 'fulfillment/order_recommendation.html', {
        'order': order,
        'result': result
    })


def seed_sample_data(request):
    """Seeds realistic sample products and shipping boxes for demonstration."""
    sample_boxes = [
        {"code": "BOX-S", "name": "Small Parcel Box", "internal_length": Decimal("22.00"), "internal_width": Decimal("16.00"), "internal_height": Decimal("10.00"), "max_weight": Decimal("3.000"), "cost": Decimal("1.25")},
        {"code": "BOX-M", "name": "Medium Shipping Box", "internal_length": Decimal("32.00"), "internal_width": Decimal("24.00"), "internal_height": Decimal("16.00"), "max_weight": Decimal("8.000"), "cost": Decimal("2.20")},
        {"code": "BOX-FLAT", "name": "Flat Mailer Box", "internal_length": Decimal("38.00"), "internal_width": Decimal("28.00"), "internal_height": Decimal("8.00"), "max_weight": Decimal("5.000"), "cost": Decimal("1.80")},
        {"code": "BOX-L", "name": "Large Shipping Box", "internal_length": Decimal("45.00"), "internal_width": Decimal("35.00"), "internal_height": Decimal("25.00"), "max_weight": Decimal("15.000"), "cost": Decimal("3.75")},
        {"code": "BOX-XL", "name": "Heavy Duty Box", "internal_length": Decimal("60.00"), "internal_width": Decimal("45.00"), "internal_height": Decimal("35.00"), "max_weight": Decimal("25.000"), "cost": Decimal("5.50")},
    ]

    sample_products = [
        {"sku": "PROD-BOOK-01", "name": "Hardcover Programming Book", "length": Decimal("24.00"), "width": Decimal("17.00"), "height": Decimal("4.50"), "weight": Decimal("1.100")},
        {"sku": "PROD-MUG-01", "name": "Ceramic Coffee Mug", "length": Decimal("11.00"), "width": Decimal("11.00"), "height": Decimal("11.00"), "weight": Decimal("0.380")},
        {"sku": "PROD-SHOE-01", "name": "Running Shoes (Boxed)", "length": Decimal("32.00"), "width": Decimal("20.00"), "height": Decimal("12.00"), "weight": Decimal("1.250")},
        {"sku": "PROD-LAPTOP-01", "name": "15-inch Laptop", "length": Decimal("36.00"), "width": Decimal("26.00"), "height": Decimal("3.00"), "weight": Decimal("2.200")},
        {"sku": "PROD-ROLLER-01", "name": "Fitness Foam Roller", "length": Decimal("45.00"), "width": Decimal("15.00"), "height": Decimal("15.00"), "weight": Decimal("0.850")},
        {"sku": "PROD-SKI-OVERSIZED", "name": "Cross-Country Skis (Oversized)", "length": Decimal("180.00"), "width": Decimal("15.00"), "height": Decimal("10.00"), "weight": Decimal("3.500")},
    ]

    created_boxes = 0
    for b_data in sample_boxes:
        _, created = ShippingBox.objects.get_or_create(code=b_data["code"], defaults=b_data)
        if created:
            created_boxes += 1

    created_prods = 0
    for p_data in sample_products:
        _, created = Product.objects.get_or_create(sku=p_data["sku"], defaults=p_data)
        if created:
            created_prods += 1

    messages.info(request, f"Sample data loaded: {created_boxes} boxes and {created_prods} products added.")
    return redirect('order_create')

