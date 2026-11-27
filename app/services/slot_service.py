"""Slot generation and availability scheduling service."""

from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any
from app.models.doctor import Availability
from app.models.appointment import Appointment


def parse_time_str(t_str: str) -> time:
    """Parse 'HH:MM' string into datetime.time object."""
    parts = [int(p) for p in t_str.strip().split(":")]
    return time(hour=parts[0], minute=parts[1])


def get_available_slots(
    doctor_id: int, target_date: date
) -> List[Dict[str, Any]]:
    """Generate discrete time slots for a doctor on a specific date.

    Identifies booked vs free slots by checking non-cancelled appointments.
    """
    weekday = target_date.weekday()  # 0=Monday, 6=Sunday
    availabilities = Availability.query.filter_by(
        doctor_id=doctor_id, weekday=weekday
    ).all()

    # Query active appointments for this doctor on target_date
    start_of_day = datetime.combine(target_date, time.min)
    end_of_day = datetime.combine(target_date, time.max)

    booked_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.start_datetime >= start_of_day,
        Appointment.start_datetime <= end_of_day,
        Appointment.status.notin_(["CANCELLED"]),
    ).all()

    booked_times = {
        apt.start_datetime.strftime("%H:%M"): apt
        for apt in booked_appointments
    }

    slots = []
    for avail in availabilities:
        start_t = parse_time_str(avail.start_time)
        end_t = parse_time_str(avail.end_time)
        delta = timedelta(minutes=avail.slot_minutes)

        current_dt = datetime.combine(target_date, start_t)
        end_dt = datetime.combine(target_date, end_t)

        while current_dt + delta <= end_dt:
            t_str = current_dt.strftime("%H:%M")
            display_str = current_dt.strftime("%I:%M %p")
            is_booked = t_str in booked_times
            apt_obj = booked_times.get(t_str)

            slots.append(
                {
                    "time_str": t_str,
                    "display_time": display_str,
                    "datetime": current_dt,
                    "is_booked": is_booked,
                    "appointment_id": apt_obj.id if apt_obj else None,
                }
            )
            current_dt += delta

    # Sort slots chronologically
    slots.sort(key=lambda s: s["datetime"])
    return slots
