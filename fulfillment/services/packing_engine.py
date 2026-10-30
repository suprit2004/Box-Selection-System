from dataclasses import dataclass
from decimal import Decimal
import itertools


@dataclass(frozen=True)
class ItemCuboid:
    """Discrete 3D rectangular cuboid representing an individual item to pack."""
    sku: str
    length: Decimal
    width: Decimal
    height: Decimal
    weight: Decimal

    @property
    def volume(self) -> Decimal:
        return self.length * self.width * self.height


@dataclass(frozen=True)
class PlacedCuboid:
    """Represents a cuboid placed at specific 3D coordinates within a box."""
    sku: str
    x: Decimal
    y: Decimal
    z: Decimal
    dx: Decimal
    dy: Decimal
    dz: Decimal

    @property
    def x2(self) -> Decimal:
        return self.x + self.dx

    @property
    def y2(self) -> Decimal:
        return self.y + self.dy

    @property
    def z2(self) -> Decimal:
        return self.z + self.dz


@dataclass(frozen=True)
class BoxSpec:
    """Internal specifications of a shipping box candidate."""
    name: str
    code: str
    length: Decimal
    width: Decimal
    height: Decimal
    max_weight: Decimal
    cost: Decimal

    @property
    def volume(self) -> Decimal:
        return self.length * self.width * self.height


@dataclass
class PackingFitResult:
    """Detailed result of a 3D packing simulation."""
    is_fit: bool
    placed_items: list[PlacedCuboid]
    total_item_volume: Decimal
    box_volume: Decimal
    void_volume: Decimal
    utilization_percentage: Decimal
    unfitted_items: list[ItemCuboid]


class PackingEngine:
    """
    Pure Python 3D geometric bin-packing engine.
    Uses First-Fit Decreasing (FFD) with Extreme Point / Anchor Coordinate tracking
    and 6-axis orthogonal rotation simulation.
    """

    @staticmethod
    def get_rotations(item: ItemCuboid) -> list[tuple[Decimal, Decimal, Decimal]]:
        """Returns all unique 3D orthogonal orientations (dx, dy, dz) for a cuboid."""
        dims = (item.length, item.width, item.height)
        # Unique permutations of (length, width, height)
        return list(set(itertools.permutations(dims)))

    @staticmethod
    def cuboids_overlap(c1: PlacedCuboid, c2: PlacedCuboid) -> bool:
        """
        Determines if two Axis-Aligned Bounding Boxes (AABB) intersect in 3D space.
        Touching adjacent faces are allowed and not considered an overlap.
        """
        overlap_x = max(c1.x, c2.x) < min(c1.x2, c2.x2)
        overlap_y = max(c1.y, c2.y) < min(c1.y2, c2.y2)
        overlap_z = max(c1.z, c2.z) < min(c1.z2, c2.z2)
        return overlap_x and overlap_y and overlap_z

    @classmethod
    def can_pack(cls, box: BoxSpec, items: list[ItemCuboid]) -> PackingFitResult:
        """
        Simulates 3D packing of a list of items into a given box.
        Returns a PackingFitResult indicating whether all items fit cleanly.
        """
        if not items:
            return PackingFitResult(
                is_fit=True,
                placed_items=[],
                total_item_volume=Decimal('0.00'),
                box_volume=box.volume,
                void_volume=box.volume,
                utilization_percentage=Decimal('0.00'),
                unfitted_items=[]
            )

        total_item_volume = sum(i.volume for i in items)
        box_volume = box.volume

        # Immediate volume check: if total item volume exceeds box capacity, cannot fit
        if total_item_volume > box_volume:
            return PackingFitResult(
                is_fit=False,
                placed_items=[],
                total_item_volume=total_item_volume,
                box_volume=box_volume,
                void_volume=box_volume - total_item_volume,
                utilization_percentage=Decimal('0.00'),
                unfitted_items=items
            )

        # Sort items descending by volume (First-Fit Decreasing heuristic)
        sorted_items = sorted(items, key=lambda i: (i.volume, max(i.length, i.width, i.height)), reverse=True)

        placed_items: list[PlacedCuboid] = []
        unfitted_items: list[ItemCuboid] = []
        anchor_points: set[tuple[Decimal, Decimal, Decimal]] = {(Decimal('0.00'), Decimal('0.00'), Decimal('0.00'))}

        for item in sorted_items:
            placed = False

            # Sort candidate anchor points to pack bottom-up (z), back-to-front (y), left-to-right (x)
            sorted_anchors = sorted(anchor_points, key=lambda p: (p[2], p[1], p[0]))

            for px, py, pz in sorted_anchors:
                # Try all 6 unique 3D rotations for this item
                for dx, dy, dz in cls.get_rotations(item):
                    # 1. Boundary check against box internal limits
                    if (px + dx > box.length) or (py + dy > box.width) or (pz + dz > box.height):
                        continue

                    candidate = PlacedCuboid(
                        sku=item.sku,
                        x=px,
                        y=py,
                        z=pz,
                        dx=dx,
                        dy=dy,
                        dz=dz
                    )

                    # 2. Check overlap against all previously placed items
                    has_collision = any(cls.cuboids_overlap(candidate, existing) for existing in placed_items)
                    if has_collision:
                        continue

                    # Placement is valid!
                    placed_items.append(candidate)
                    anchor_points.remove((px, py, pz))

                    # 3. Generate new candidate anchor points created by this cuboid's upper surfaces
                    new_anchors = [
                        (px + dx, py, pz),
                        (px, py + dy, pz),
                        (px, py, pz + dz)
                    ]
                    for nx, ny, nz in new_anchors:
                        if nx < box.length and ny < box.width and nz < box.height:
                            anchor_points.add((nx, ny, nz))

                    placed = True
                    break

                if placed:
                    break

            if not placed:
                unfitted_items.append(item)
                # Fail fast: if any item cannot fit, the box cannot accommodate the order
                return PackingFitResult(
                    is_fit=False,
                    placed_items=placed_items,
                    total_item_volume=total_item_volume,
                    box_volume=box_volume,
                    void_volume=box_volume - total_item_volume,
                    utilization_percentage=Decimal('0.00'),
                    unfitted_items=sorted_items[len(placed_items):]
                )

        void_volume = max(Decimal('0.00'), box_volume - total_item_volume)
        utilization = (total_item_volume / box_volume * Decimal('100.0')).quantize(Decimal('0.01')) if box_volume > 0 else Decimal('0.00')

        return PackingFitResult(
            is_fit=True,
            placed_items=placed_items,
            total_item_volume=total_item_volume,
            box_volume=box_volume,
            void_volume=void_volume,
            utilization_percentage=utilization,
            unfitted_items=[]
        )

