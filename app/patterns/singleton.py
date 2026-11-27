"""Singleton Pattern Implementation for ClinicCare.

Provides thread-safe Singleton metaclass, centralized AppConfig,
and DatabaseSessionManager for consistent shared state.
"""

import os
import threading


class SingletonMeta(type):
    """Thread-safe Singleton metaclass implementing GoF Creational pattern."""

    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        # Double-checked locking optimization
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]

    @classmethod
    def reset_instances(cls):
        """Helper for testing to reset singletons if needed."""
        with cls._lock:
            cls._instances.clear()


class AppConfig(metaclass=SingletonMeta):
    """Centralized application configuration singleton."""

    def __init__(self):
        self.SECRET_KEY = os.environ.get(
            "SECRET_KEY", "cliniccare-dev-secret-ruet-2026"
        )
        self.SQLALCHEMY_DATABASE_URI = os.environ.get(
            "DATABASE_URL", "sqlite:///cliniccare.db"
        )
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.CANCELLATION_FULL_REFUND_HOURS = int(
            os.environ.get("CANCELLATION_FULL_REFUND_HOURS", 24)
        )
        self.CANCELLATION_MIN_HOURS = int(
            os.environ.get("CANCELLATION_MIN_HOURS", 2)
        )
        self.MAX_BOOKING_DAYS_AHEAD = int(
            os.environ.get("MAX_BOOKING_DAYS_AHEAD", 60)
        )
        self.PROMO_CODES = {
            "RUET2026": 0.10,
            "HEALTHCARE15": 0.15,
            "WELCOME5": 0.05,
        }


class DatabaseSessionManager(metaclass=SingletonMeta):
    """Singleton session coordinator managing database connections."""

    def __init__(self, db=None):
        self._db = db
        self._active_sessions = set()

    def set_db(self, db):
        self._db = db

    def get_session(self):
        if self._db is not None:
            return self._db.session
        return None
