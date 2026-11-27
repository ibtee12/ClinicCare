import pytest
from app.patterns.strategy import (
    NoDiscountStrategy,
    SeniorCitizenDiscountStrategy,
    StudentDiscountStrategy,
    FirstVisitDiscountStrategy,
    PromoCodeStrategy,
    DiscountContext,
    select_best_discount,
)


def test_no_discount():
    strategy = NoDiscountStrategy()
    assert strategy.calculate(1000.0, {}) == 0.0


def test_senior_citizen_discount():
    strategy = SeniorCitizenDiscountStrategy()
    # Age 60 and above gets 20%
    assert strategy.calculate(1000.0, {"age": 65}) == 200.0
    assert strategy.calculate(1000.0, {"age": 60}) == 200.0
    assert strategy.calculate(1000.0, {"age": 59}) == 0.0


def test_student_discount():
    strategy = StudentDiscountStrategy()
    # Student flag gives 15%
    assert strategy.calculate(1000.0, {"is_student": True}) == 150.0
    assert strategy.calculate(1000.0, {"is_student": False}) == 0.0


def test_first_visit_discount():
    strategy = FirstVisitDiscountStrategy()
    # Prior visits == 0 gives 10%
    assert strategy.calculate(1000.0, {"prior_visits_count": 0}) == 100.0
    assert strategy.calculate(1000.0, {"prior_visits_count": 2}) == 0.0


def test_promo_code_discount():
    strategy = PromoCodeStrategy(code="RUET2026")
    assert strategy.calculate(1000.0, {}) == 100.0

    invalid_strategy = PromoCodeStrategy(code="INVALID_CODE")
    assert invalid_strategy.calculate(1000.0, {}) == 0.0


def test_zero_and_negative_base_fee():
    strategy = SeniorCitizenDiscountStrategy()
    assert strategy.calculate(0.0, {"age": 65}) == 0.0
    assert strategy.calculate(-100.0, {"age": 65}) == 0.0


def test_select_best_discount_non_stacking():
    # Patient is Senior (20%), Student (15%), First Visit (10%), with RUET2026 promo (10%)
    # Best discount should be SeniorCitizen (20% = 200.0), NEVER stacking
    patient_info = {
        "age": 65,
        "is_student": True,
        "prior_visits_count": 0,
        "promo_code": "RUET2026",
    }
    best_name, discount_amount, final_total = select_best_discount(
        base_fee=1000.0, patient_info=patient_info
    )
    assert best_name == "Senior Citizen (20%)"
    assert discount_amount == 200.0
    assert final_total == 800.0


def test_discount_context_execution():
    context = DiscountContext(StudentDiscountStrategy())
    amount = context.execute(500.0, {"is_student": True})
    assert amount == 75.0
