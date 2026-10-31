from decimal import Decimal
from typing import Optional
from .packing_engine import BoxSpec, ItemCuboid, PackingFitResult


class PackingAdvisor:
    """
    Provides warehouse-ready packaging insights, explanations, and diagnostics.
    """

    @staticmethod
    def generate_success_reason(
        box: BoxSpec,
        fit_result: PackingFitResult,
        total_weight: Decimal,
        candidate_count: int
    ) -> str:
        """
        Generates a transparent, professional explanation for why this box was selected.
        """
        weight_margin = box.max_weight - total_weight
        return (
            f"Selected {box.name} ({box.code}) at ₹{box.cost:.2f} as the lowest-cost option among "
            f"{candidate_count} evaluated boxes. Accommodates all items with {fit_result.utilization_percentage:.1f}% "
            f"space utilization, leaving {fit_result.void_volume:,.1f} cm³ for protective dunnage. "
            f"Weight buffer remaining: {weight_margin:.3f} kg."
        )

    @staticmethod
    def diagnose_failure(
        items: list[ItemCuboid],
        available_boxes: list[BoxSpec],
        total_weight: Decimal
    ) -> str:
        """
        Produces actionable diagnostic explanations when no available box can fit an order.
        """
        if not available_boxes:
            return "No active shipping boxes are currently available in the warehouse inventory."

        max_inventory_weight = max(b.max_weight for b in available_boxes)
        if total_weight > max_inventory_weight:
            overage = total_weight - max_inventory_weight
            return (
                f"Weight Capacity Exceeded: The total order weight is {total_weight:.3f} kg, which exceeds "
                f"the highest rated box in stock ({max_inventory_weight:.3f} kg) by {overage:.3f} kg. "
                f"Recommendation: Split the order into multiple shipments or route to freight freight/crate handling."
            )

        # Check if an individual item is physically larger than every box
        for item in items:
            item_sorted = sorted([item.length, item.width, item.height])
            can_fit_in_any = False
            for b in available_boxes:
                b_sorted = sorted([b.length, b.width, b.height])
                if item_sorted[0] <= b_sorted[0] and item_sorted[1] <= b_sorted[1] and item_sorted[2] <= b_sorted[2]:
                    can_fit_in_any = True
                    break

            if not can_fit_in_any:
                return (
                    f"Oversized Item: Product '{item.sku}' with dimensions "
                    f"{item.length} x {item.width} x {item.height} cm exceeds the physical boundaries "
                    f"of all available shipping boxes. Recommendation: Special oversized packaging required."
                )

        # If items individually fit and weight is within limits, items together exceeded multi-item packing
        total_volume = sum(i.volume for i in items)
        max_box_volume = max(b.volume for b in available_boxes)
        if total_volume > max_box_volume:
            return (
                f"Cumulative Volume Exceeded: Total item volume ({total_volume:,.1f} cm³) exceeds "
                f"the largest single box ({max_box_volume:,.1f} cm³). "
                f"Recommendation: Split the order across multiple boxes."
            )

        return (
            "Packing Geometry Conflict: Items individually fit in stock boxes and total weight is within limits, "
            "but their combined 3D shapes cannot be physically packed into any single box without overlapping. "
            "Recommendation: Split into two separate boxes."
        )

