from .dashboard_views import dashboard
from .catalog_views import (
    product_list_create,
    product_edit,
    product_delete,
    box_list_create,
    box_edit,
    box_delete,
)
from .order_views import (
    order_list,
    order_create,
    order_recommendation,
    seed_sample_data,
)

__all__ = [
    'dashboard',
    'product_list_create',
    'product_edit',
    'product_delete',
    'box_list_create',
    'box_edit',
    'box_delete',
    'order_list',
    'order_create',
    'order_recommendation',
    'seed_sample_data',
]
