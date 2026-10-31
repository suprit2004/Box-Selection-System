from decimal import Decimal
from django.shortcuts import render
from fulfillment.models import Product, ShippingBox, Order, OrderStatus


def dashboard(request):
    """
    Main warehouse management dashboard displaying key operational KPIs,
    box availability, and recent packaging recommendations.
    """
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    
    total_boxes = ShippingBox.objects.count()
    active_boxes = ShippingBox.objects.filter(is_active=True).count()
    
    total_orders = Order.objects.count()
    optimized_orders = Order.objects.filter(status=OrderStatus.OPTIMIZED).count()
    unpackable_orders = Order.objects.filter(status=OrderStatus.UNPACKABLE).count()
    
    success_rate = (
        round((optimized_orders / total_orders) * 100, 1)
        if total_orders > 0 else 0.0
    )

    recent_orders = (
        Order.objects.select_related('recommended_box')
        .prefetch_related('items__product')
        .order_by('-created_at')[:6]
    )

    stock_boxes = ShippingBox.objects.filter(is_active=True).order_by('cost')[:5]

    return render(request, 'fulfillment/dashboard.html', {
        'total_products': total_products,
        'active_products': active_products,
        'total_boxes': total_boxes,
        'active_boxes': active_boxes,
        'total_orders': total_orders,
        'optimized_orders': optimized_orders,
        'unpackable_orders': unpackable_orders,
        'success_rate': success_rate,
        'recent_orders': recent_orders,
        'stock_boxes': stock_boxes,
    })

