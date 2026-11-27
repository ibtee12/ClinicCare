"""Seed script to populate ClinicCare SQLite database with realistic data.

Seed contents:
- 1 Admin: admin@cliniccare.test / Admin123!
- 4 Departments: General Medicine, Cardiology, Pediatrics, Dermatology
- 6 Doctors across departments with weekly availability slots
- 10 Patients (including 1 senior age 65, 1 student)
- 15 Appointments in various statuses (CONFIRMED, COMPLETED, CANCELLED)
- Invoices and Payments for appointments
"""

from datetime import datetime, date, timedelta
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.patient import PatientProfile
from app.models.doctor import Department, DoctorProfile, Availability
from app.models.appointment import Appointment
from app.models.billing import Invoice, Payment
from app.models.notification import Notification


def run_seed():
    """Execute complete database seeding."""
    app = create_app({"SQLALCHEMY_DATABASE_URI": "sqlite:///cliniccare.db"})

    with app.app_context():
        # Clean existing tables
        db.drop_all()
        db.create_all()

        print("Seeding database...")

        # 1. Admin
        admin_user = User(
            name="Clinic Administrator",
            email="admin@cliniccare.test",
            role="admin",
        )
        admin_user.set_password("Admin123!")
        db.session.add(admin_user)

        # 2. Departments
        dept_gm = Department(
            name="General Medicine",
            description="Primary comprehensive adult healthcare.",
        )
        dept_cardio = Department(
            name="Cardiology",
            description="Diagnosis and treatment of heart conditions.",
        )
        dept_pedia = Department(
            name="Pediatrics",
            description="Infant, child and adolescent medical care.",
        )
        dept_derma = Department(
            name="Dermatology",
            description="Skin, nail, hair and cosmetic treatments.",
        )
        db.session.add_all([dept_gm, dept_cardio, dept_pedia, dept_derma])
        db.session.flush()

        # 3. Doctors (6 specialists)
        doctor_data = [
            (
                "Dr. Gregory House",
                "house@cliniccare.test",
                dept_gm.id,
                "MD, DNB (Internal Medicine)",
                600.0,
                "Renowned diagnostician and internal medicine expert.",
            ),
            (
                "Dr. John Watson",
                "watson@cliniccare.test",
                dept_gm.id,
                "MBBS, MRCGP",
                500.0,
                "Experienced physician specializing in preventative care.",
            ),
            (
                "Dr. Cristina Yang",
                "yang@cliniccare.test",
                dept_cardio.id,
                "MD, PhD, FACS (Cardiothoracic)",
                1200.0,
                "Leading cardiothoracic specialist and cardiovascular fellow.",
            ),
            (
                "Dr. Robert Chase",
                "chase@cliniccare.test",
                dept_cardio.id,
                "MBBS, FCPS (Cardiology)",
                850.0,
                "Interventional cardiology and heart failure specialist.",
            ),
            (
                "Dr. Arizona Robbins",
                "robbins@cliniccare.test",
                dept_pedia.id,
                "MD, FAAP (Pediatric Surgery)",
                750.0,
                "Pediatric surgeon dedicated to compassionate childcare.",
            ),
            (
                "Dr. Allison Cameron",
                "cameron@cliniccare.test",
                dept_derma.id,
                "MD, Board Certified Dermatologist",
                700.0,
                "Expert in medical dermatology, allergies and skin health.",
            ),
        ]

        doctors = []
        for name, email, d_id, qual, fee, bio in doctor_data:
            doc_user = User(name=name, email=email, role="doctor")
            doc_user.set_password("Doctor123!")
            db.session.add(doc_user)
            db.session.flush()

            profile = DoctorProfile(
                user_id=doc_user.id,
                department_id=d_id,
                qualifications=qual,
                fee=fee,
                bio=bio,
                is_active=True,
            )
            db.session.add(profile)
            doctors.append(profile)

            # Add availability for weekdays (Monday to Friday, 09:00 - 13:00)
            for w in range(5):
                avail = Availability(
                    doctor_id=doc_user.id,
                    weekday=w,
                    start_time="09:00",
                    end_time="13:00",
                    slot_minutes=30,
                )
                db.session.add(avail)

        db.session.flush()

        # 4. Patients (10 patients, including 1 senior age 65, 1 student)
        patients = []
        patient_info = [
            (
                "Alice Rahman",
                "alice@patient.test",
                65,
                "Female",
                "01711000001",
                "Senior citizen retired educator.",
                False,
            ),
            (
                "Bob Hossain",
                "bob@patient.test",
                21,
                "Male",
                "01811000002",
                "RUET CSE 3rd year undergraduate.",
                True,
            ),
            (
                "Charlie Khan",
                "charlie@patient.test",
                34,
                "Male",
                "01911000003",
                "Occasional asthma and migraines.",
                False,
            ),
            (
                "Diana Ahmed",
                "diana@patient.test",
                29,
                "Female",
                "01722000004",
                "Routine health examinations.",
                False,
            ),
            (
                "Ehsan Chowdhury",
                "ehsan@patient.test",
                42,
                "Male",
                "01833000005",
                "Mild hypertension under management.",
                False,
            ),
            (
                "Farzana Yasmin",
                "farzana@patient.test",
                38,
                "Female",
                "01944000006",
                "Allergies to penicillin.",
                False,
            ),
            (
                "Golam Mostafa",
                "golam@patient.test",
                55,
                "Male",
                "01755000007",
                "Type 2 diabetes under diet control.",
                False,
            ),
            (
                "Hasna Hena",
                "hasna@patient.test",
                24,
                "Female",
                "01866000008",
                "Post-graduate university researcher.",
                True,
            ),
            (
                "Imtiaz Ali",
                "imtiaz@patient.test",
                48,
                "Male",
                "01977000009",
                "Knee arthroscopy history.",
                False,
            ),
            (
                "Jannatul Ferdous",
                "jannat@patient.test",
                31,
                "Female",
                "01788000010",
                "General wellness and fitness consults.",
                False,
            ),
        ]

        for (
            name,
            email,
            age,
            gender,
            phone,
            notes,
            is_student,
        ) in patient_info:
            p_user = User(name=name, email=email, role="patient")
            p_user.set_password("Patient123!")
            db.session.add(p_user)
            db.session.flush()

            p_profile = PatientProfile(
                user_id=p_user.id,
                age=age,
                gender=gender,
                phone=phone,
                address="Dhaka, Bangladesh",
                blood_group="B+",
                medical_history=notes,
                is_student=is_student,
            )
            db.session.add(p_profile)
            patients.append(p_user)

        db.session.flush()

        # 5. Appointments (15 varied appointments, invoices and payments)
        statuses = [
            "CONFIRMED",
            "COMPLETED",
            "CANCELLED",
            "CONFIRMED",
            "COMPLETED",
        ]
        base_date = date.today()

        for i in range(15):
            pt = patients[i % len(patients)]
            doc = doctors[i % len(doctors)]
            status = statuses[i % len(statuses)]
            day_offset = (i - 7)  # Some past, some today/future
            apt_date = base_date + timedelta(days=day_offset)
            apt_dt = datetime.combine(
                apt_date, datetime.strptime("10:00", "%H:%M").time()
            )

            apt = Appointment(
                patient_id=pt.id,
                doctor_id=doc.user_id,
                start_datetime=apt_dt,
                status=status,
                reason="Regular consultation and follow up",
                notes="Prescribed standard vitamins and hydration."
                if status == "COMPLETED"
                else None,
            )
            db.session.add(apt)
            db.session.flush()

            inv_status = (
                "PAID" if status in ["CONFIRMED", "COMPLETED"] else "UNPAID"
            )
            fee = doc.fee
            discount = 0.20 * fee if pt.patient_profile.age >= 60 else 0.0
            total = fee - discount

            inv = Invoice(
                appointment_id=apt.id,
                base_fee=fee,
                discount_amount=discount,
                total=total,
                status=inv_status,
            )
            db.session.add(inv)
            db.session.flush()

            if inv_status == "PAID":
                pmt = Payment(
                    invoice_id=inv.id,
                    method="CARD" if i % 2 == 0 else "BKASH",
                    amount=total,
                    status="SUCCESS",
                    transaction_ref=f"TXN-SEED-{1000 + i}",
                )
                db.session.add(pmt)

            notif = Notification(
                user_id=pt.id,
                channel="in_app",
                message=f"Appointment #{apt.id} is {status.lower()}.",
                is_read=(i % 2 == 0),
            )
            db.session.add(notif)

        db.session.commit()
        print("Database successfully seeded with realistic test fixtures!")


if __name__ == "__main__":
    run_seed()
