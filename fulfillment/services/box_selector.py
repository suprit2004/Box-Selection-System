from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from django.db import transaction

from fulfillment.models import ShippingBox, Order, OrderStatus
from .packing_engine import PackingEngine, BoxSpec, ItemCuboid, PackingFitResult
from .packing_advisor import PackingAdvisor


@dataclass
class BoxSelectionResult:
    """Standardized output returned by the box selection service."""
    is_success: bool
    status: str
    recommended_box: Optional[ShippingBox]
    box_name: Optional[str]
    box_dimensions: Optional[tuple[Decimal, Decimal, Decimal]]
    total_product_weight: Decimal
    max_weight_capacity: Optional[Decimal]
    box_cost: Optional[Decimal]
    reason: str
    fit_details: Optional[PackingFitResult]


class BoxSelectorService:
    """
    Coordinates input validation, candidate box filtering, cost-optimized ranking,
    and 3D physical feasibility simulation.
    """

    @classmethod
    def to_box_spec(cls, box: ShippingBox) -> BoxSpec:
        """Converts a Django ShippingBox model instance to a lightweight BoxSpec."""
        return BoxSpec(
            name=box.name,
            code=box.code,
            length=box.internal_length,
            width=box.internal_width,
            height=box.internal_height,
            max_weight=box.max_weight,
            cost=box.cost
        )

    @classmethod
    def select_box_for_items(
        cls,
        order_items: list[tuple[ItemCuboid, int]],
        available_boxes: Optional[list[ShippingBox]] = None
    ) -> BoxSelectionResult:
        """
        Pure business logic selection function.
        order_items: list of (ItemCuboid, quantity)
        available_boxes: optional list of ShippingBox instances (queries DB if None)
        """
        # Step 0: Edge case checks
        if not order_items:
            return BoxSelectionResult(
                is_success=False,
                status=OrderStatus.UNPACKABLE,
                recommended_box=None,
                box_name=None,
                box_dimensions=None,
                total_product_weight=Decimal('0.000'),
                max_weight_capacity=None,
                box_cost=None,
                reason="Cannot recommend box: The order contains no items.",
                fit_details=None
            )

        # Validate item properties and flatten quantities
        flattened_items: list[ItemCuboid] = []
        total_weight = Decimal('0.000')
        total_volume = Decimal('0.00')

        for item, qty in order_items:
            if qty < 1:
                return BoxSelectionResult(
                    is_success=False,
                    status=OrderStatus.UNPACKABLE,
                    recommended_box=None,
                    box_name=None,
                    box_dimensions=None,
                    total_product_weight=Decimal('0.000'),
                    max_weight_capacity=None,
                    box_cost=None,
                    reason=f"Invalid item quantity '{qty}' for item '{item.sku}'. Must be at least 1.",
                    fit_details=None
                )
            if item.length <= 0 or item.width <= 0 or item.height <= 0 or item.weight <= 0:
                return BoxSelectionResult(
                    is_success=False,
                    status=OrderStatus.UNPACKABLE,
                    recommended_box=None,
                    box_name=None,
                    box_dimensions=None,
                    total_product_weight=Decimal('0.000'),
                    max_weight_capacity=None,
                    box_cost=None,
                    reason=f"Invalid item dimensions or weight for item '{item.sku}'.",
                    fit_details=None
                )

            for _ in range(qty):
                flattened_items.append(item)
            total_weight += item.weight * qty
            total_volume += item.volume * qty

        # Step 1: Retrieve available active boxes
        if available_boxes is None:
            db_boxes = list(ShippingBox.objects.filter(is_active=True).order_by('cost', 'internal_length'))
        else:
            db_boxes = [b for b in available_boxes if b.is_active]

        box_specs = [cls.to_box_spec(b) for b in db_boxes]

        # Step 2: Stage 1 Fast Filters
        candidate_boxes: list[tuple[ShippingBox, BoxSpec]] = []
        for db_box, spec in zip(db_boxes, box_specs):
            # Weight filter
            if spec.max_weight < total_weight:
                continue
            # Volume filter
            if spec.volume < total_volume:
                continue

            # Dimensional filter for individual items (with rotation)
            box_sorted = sorted([spec.length, spec.width, spec.height])
            item_too_large = False
            for item in flattened_items:
                item_sorted = sorted([item.length, item.width, item.height])
                if item_sorted[0] > box_sorted[0] or item_sorted[1] > box_sorted[1] or item_sorted[2] > box_sorted[2]:
                    item_too_large = True
                    break
            if item_too_large:
                continue

            candidate_boxes.append((db_box, spec))

        # If all boxes were eliminated in Stage 1
        if not candidate_boxes:
            diagnosis = PackingAdvisor.diagnose_failure(flattened_items, box_specs, total_weight)
            return BoxSelectionResult(
                is_success=False,
                status=OrderStatus.UNPACKABLE,
                recommended_box=None,
                box_name=None,
                box_dimensions=None,
                total_product_weight=total_weight,
                max_weight_capacity=None,
                box_cost=None,
                reason=diagnosis,
                fit_details=None
            )

        # Step 3: Sort candidate boxes by Cost ASC, then Internal Volume ASC (Tie-breaker)
        candidate_boxes.sort(key=lambda pair: (pair[1].cost, pair[1].volume))

        # Step 4: Stage 3 Verification via 3D Physical Placement Simulation
        for db_box, spec in candidate_boxes:
            fit_result = PackingEngine.can_pack(spec, flattened_items)
            if fit_result.is_fit:
                reason = PackingAdvisor.generate_success_reason(
                    box=spec,
                    fit_result=fit_result,
                    total_weight=total_weight,
                    candidate_count=len(candidate_boxes)
                )
                return BoxSelectionResult(
                    is_success=True,
                    status=OrderStatus.OPTIMIZED,
                    recommended_box=db_box,
                    box_name=db_box.name,
                    box_dimensions=(spec.length, spec.width, spec.height),
                    total_product_weight=total_weight,
                    max_weight_capacity=spec.max_weight,
                    box_cost=spec.cost,
                    reason=reason,
                    fit_details=fit_result
                )

        # If candidates passed initial filters but failed physical 3D packing
        diagnosis = PackingAdvisor.diagnose_failure(flattened_items, box_specs, total_weight)
        return BoxSelectionResult(
            is_success=False,
            status=OrderStatus.UNPACKABLE,
            recommended_box=None,
            box_name=None,
            box_dimensions=None,
            total_product_weight=total_weight,
            max_weight_capacity=None,
            box_cost=None,
            reason=diagnosis,
            fit_details=None
        )

    @classmethod
    @transaction.atomic
    def recommend_for_order(cls, order: Order) -> BoxSelectionResult:
        """
        Executes box selection for a stored Order model, commits the result to the DB,
        and returns the recommendation result.
        """
        items_query = order.items.select_related('product').all()
        order_items_input: list[tuple[ItemCuboid, int]] = []

        for item in items_query:
            cuboid = ItemCuboid(
                sku=item.product.sku,
                length=item.product.length,
                width=item.product.width,
                height=item.product.height,
                weight=item.unit_weight
            )
            order_items_input.append((cuboid, item.quantity))

        result = cls.select_box_for_items(order_items_input)

        # Persist results back to the Order model
        order.total_weight = result.total_product_weight
        order.total_volume = sum(c.volume * q for c, q in order_items_input) if order_items_input else Decimal('0.00')
        order.recommended_box = result.recommended_box
        order.status = result.status
        order.packing_notes = result.reason
        order.save()

        return result

