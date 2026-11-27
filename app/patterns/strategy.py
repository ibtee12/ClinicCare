"""Strategy Pattern for Consultation Billing Discounts.

Implements GoF Behavioral Strategy pattern. Computes eligible discounts
(Senior Citizen, Student, First Visit, Promo Code) and enforces the rule
that only the single highest eligible discount is applied (never stacking).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from app.patterns.singleton import AppConfig


class DiscountStrategy(ABC):
    """Abstract base strategy for discount calculation."""

    @abstractmethod
    def calculate(
        self, base_fee: float, patient_info: Dict[str, Any]
    ) -> float:
        """Calculate discount amount in currency units."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """User-friendly name of the discount."""
        pass


class NoDiscountStrategy(DiscountStrategy):
    """Fallback strategy with zero discount."""

    @property
    def name(self) -> str:
        return "No Discount"

    def calculate(
        self, base_fee: float, patient_info: Dict[str, Any]
    ) -> float:
        return 0.0


class SeniorCitizenDiscountStrategy(DiscountStrategy):
    """Senior citizens aged 60 and above receive a 20% discount."""

    @property
    def name(self) -> str:
        return "Senior Citizen (20%)"

    def calculate(
        self, base_fee: float, patient_info: Dict[str, Any]
    ) -> float:
        if base_fee <= 0:
            return 0.0
        age = patient_info.get("age", 0)
        if age >= 60:
            return round(base_fee * 0.20, 2)
        return 0.0


class StudentDiscountStrategy(DiscountStrategy):
    """Verified students receive a 15% discount."""

    @property
    def name(self) -> str:
        return "Student Discount (15%)"

    def calculate(
        self, base_fee: float, patient_info: Dict[str, Any]
    ) -> float:
        if base_fee <= 0:
            return 0.0
        if patient_info.get("is_student", False):
            return round(base_fee * 0.15, 2)
        return 0.0


class FirstVisitDiscountStrategy(DiscountStrategy):
    """Patients with zero previous visits receive a 10% welcome discount."""

    @property
    def name(self) -> str:
        return "First Visit Discount (10%)"

    def calculate(
        self, base_fee: float, patient_info: Dict[str, Any]
    ) -> float:
        if base_fee <= 0:
            return 0.0
        prior_visits = patient_info.get("prior_visits_count", 0)
        if prior_visits == 0:
            return round(base_fee * 0.10, 2)
        return 0.0


class PromoCodeStrategy(DiscountStrategy):
    """Promo code discount applied from application config."""

    def __init__(self, code: str):
        self.code = (code or "").strip().upper()

    @property
    def name(self) -> str:
        return f"Promo Code ({self.code})"

    def calculate(
        self, base_fee: float, patient_info: Dict[str, Any]
    ) -> float:
        if base_fee <= 0 or not self.code:
            return 0.0
        config = AppConfig()
        rate = config.PROMO_CODES.get(self.code, 0.0)
        return round(base_fee * rate, 2)


class DiscountContext:
    """Context class wrapping strategy execution."""

    def __init__(self, strategy: DiscountStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: DiscountStrategy) -> None:
        self._strategy = strategy

    def execute(self, base_fee: float, patient_info: Dict[str, Any]) -> float:
        return self._strategy.calculate(base_fee, patient_info)


def select_best_discount(
    base_fee: float, patient_info: Dict[str, Any]
) -> Tuple[str, float, float]:
    """Evaluates all candidate strategies and returns best single discount.

    Rule: The highest single discount applies; discounts NEVER stack.

    Returns:
        (strategy_name, discount_amount, final_total)
    """
    if base_fee <= 0:
        return "No Discount", 0.0, 0.0

    candidates = [
        NoDiscountStrategy(),
        SeniorCitizenDiscountStrategy(),
        StudentDiscountStrategy(),
        FirstVisitDiscountStrategy(),
    ]

    promo_code = patient_info.get("promo_code")
    if promo_code:
        candidates.append(PromoCodeStrategy(promo_code))

    best_name = "No Discount"
    max_discount = 0.0

    for strategy in candidates:
        discount = strategy.calculate(base_fee, patient_info)
        if discount > max_discount:
            max_discount = discount
            best_name = strategy.name

    final_total = max(0.0, round(base_fee - max_discount, 2))
    return best_name, max_discount, final_total
