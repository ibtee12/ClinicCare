from datetime import datetime, timedelta
from app.models.user import User
from app.models.doctor import DoctorProfile
from app.models.appointment import Appointment
from app.models.billing import Invoice, Payment
from app.patterns.adapter import PaymentResult
from app.extensions import db


def create_test_invoice(app):
    with app.app_context():
        doc_u = User(name="Dr. Monir", email="monir@doc.test", role="doctor")
        doc_u.set_password("Pass123!")
        pat_u = User(name="Jamal", email="jamal@pat.test", role="patient")
        pat_u.set_password("Pass123!")
        db.session.add_all([doc_u, pat_u])
        db.session.flush()

        doc_prof = DoctorProfile(user_id=doc_u.id, qualifications="MBBS")
        db.session.add(doc_prof)
        db.session.flush()

        apt = Appointment(
            patient_id=pat_u.id,
            doctor_id=doc_u.id,
            start_datetime=datetime.utcnow() + timedelta(days=2),
            status="PENDING",
        )
        db.session.add(apt)
        db.session.flush()

        inv = Invoice(
            appointment_id=apt.id,
            base_fee=800.0,
            discount_amount=160.0,
            discount_name="Senior Citizen (20%)",
            total=640.0,
            status="UNPAID",
        )
        db.session.add(inv)
        db.session.commit()
        return inv.id, pat_u.id, apt.id


def test_invoice_list_and_detail_view(client, app):
    inv_id, pat_id, apt_id = create_test_invoice(app)

    with client.session_transaction() as sess:
        sess["user_id"] = pat_id
        sess["user_role"] = "patient"
        sess["user_name"] = "Jamal"

    # List view
    res = client.get("/invoices")
    assert res.status_code == 200
    assert b"INV-" in res.data
    assert b"640" in res.data

    # Printable detail view
    res_detail = client.get(f"/invoices/{inv_id}")
    assert res_detail.status_code == 200
    assert b"INVOICE" in res_detail.data
    assert b"Senior Citizen (20%)" in res_detail.data


def test_pay_invoice_card_success(client, app, mocker):
    inv_id, pat_id, apt_id = create_test_invoice(app)

    with client.session_transaction() as sess:
        sess["user_id"] = pat_id
        sess["user_role"] = "patient"
        sess["user_name"] = "Jamal"

    # Use pytest-mock to mock payment gateway adapter
    mock_adapter = mocker.patch(
        "app.routes.billing.get_payment_adapter"
    ).return_value
    mock_adapter.process_payment.return_value = PaymentResult(
        success=True,
        transaction_ref="CARD-TX-MOCK1234",
        message="Approved",
    )

    res = client.post(
        f"/pay/{inv_id}",
        data={
            "method": "card",
            "card_number": "4111222233334444",
            "exp_month": "12",
            "exp_year": "2028",
            "cvv": "123",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"Payment successful" in res.data or b"PAID" in res.data

    with app.app_context():
        inv = db.session.get(Invoice, inv_id)
        assert inv.status == "PAID"
        assert len(inv.payments) == 1
        assert inv.payments[0].transaction_ref == "CARD-TX-MOCK1234"
        apt = db.session.get(Appointment, apt_id)
        assert apt.status == "CONFIRMED"


def test_pay_invoice_wallet_success(client, app, mocker):
    inv_id, pat_id, apt_id = create_test_invoice(app)

    with client.session_transaction() as sess:
        sess["user_id"] = pat_id
        sess["user_role"] = "patient"
        sess["user_name"] = "Jamal"

    mock_adapter = mocker.patch(
        "app.routes.billing.get_payment_adapter"
    ).return_value
    mock_adapter.process_payment.return_value = PaymentResult(
        success=True,
        transaction_ref="BKASH-TX-MOCK5678",
        message="Confirmed",
    )

    res = client.post(
        f"/pay/{inv_id}",
        data={
            "method": "wallet",
            "wallet_number": "01711223344",
            "pin": "12345",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    with app.app_context():
        inv = db.session.get(Invoice, inv_id)
        assert inv.status == "PAID"
        assert inv.payments[0].method == "wallet"


def test_pay_invoice_failure_and_retry(client, app, mocker):
    inv_id, pat_id, apt_id = create_test_invoice(app)

    with client.session_transaction() as sess:
        sess["user_id"] = pat_id
        sess["user_role"] = "patient"
        sess["user_name"] = "Jamal"

    mock_adapter = mocker.patch(
        "app.routes.billing.get_payment_adapter"
    ).return_value
    mock_adapter.process_payment.return_value = PaymentResult(
        success=False,
        transaction_ref="",
        message="Declined: Insufficient funds",
        retryable=True,
    )

    res = client.post(
        f"/pay/{inv_id}",
        data={
            "method": "card",
            "card_number": "4111222233330000",
            "exp_month": "12",
            "exp_year": "2028",
            "cvv": "123",
        },
        follow_redirects=True,
    )
    assert res.status_code == 400
    assert b"Insufficient funds" in res.data
    with app.app_context():
        inv = db.session.get(Invoice, inv_id)
        assert inv.status == "UNPAID"
