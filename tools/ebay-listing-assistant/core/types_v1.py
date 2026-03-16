"""
V1-specific input types — extends core types with seller cost data.
Keeps types.py clean for the shared pipeline contract.
"""

from dataclasses import dataclass, field
from core.types import ProductInput


@dataclass
class V1ProductInput:
    """Extended input for V1 — wraps ProductInput with seller cost data."""
    product: ProductInput
    weight_oz: float = 0.0
    quantity: int = 1
    item_cost: float = 0.0         # What Kalani paid for it
    desired_margin: float = 0.20    # 20% default profit margin
    fragile: bool = False
    hashtags: list[str] = field(default_factory=list)

    @classmethod
    def from_quick_input(
        cls,
        name: str,
        condition: str = "Used",
        weight_oz: float = 12.0,
        item_cost: float = 0.0,
        quantity: int = 1,
        fragile: bool = False,
        hashtags: list[str] = None,
        image_paths: list[str] = None,
        notes: str = None,
    ) -> "V1ProductInput":
        """
        Quick constructor for common use case.

        Example:
            V1ProductInput.from_quick_input(
                "Hello Kitty Strawberry Coffee Mug",
                condition="New",
                weight_oz=16,
                item_cost=5.00,
                quantity=3,
                fragile=True,
                hashtags=["hellokitty", "coffeemug", "kawaii"],
            )
        """
        product = ProductInput(
            name=name,
            image_path=image_paths[0] if image_paths else None,
            condition=condition,
            notes=notes,
        )
        return cls(
            product=product,
            weight_oz=weight_oz,
            quantity=quantity,
            item_cost=item_cost,
            desired_margin=0.20,
            fragile=fragile,
            hashtags=hashtags or [],
        )
