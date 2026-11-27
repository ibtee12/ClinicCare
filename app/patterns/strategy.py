"""Initial Draft: Discount Strategy pattern (Deliberately incomplete for review cycle)."""

from abc import ABC, abstractmethod


class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, base_fee: float, patient_info: dict) -> float:
        pass


class NoDiscountStrategy(DiscountStrategy):
    def calculate(self, base_fee: float, patient_info: dict) -> float:
        return 0.0


class SeniorCitizenDiscountStrategy(DiscountStrategy):
    def calculate(self, base_fee: float, patient_info: dict) -> float:
        if patient_info.get("age", 0) >= 60:
            return base_fee * 0.20
        return 0.0
