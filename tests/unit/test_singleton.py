import threading
from app.patterns.singleton import AppConfig, DatabaseSessionManager


def test_app_config_singleton_identity():
    config1 = AppConfig()
    config2 = AppConfig()
    assert config1 is config2
    assert id(config1) == id(config2)


def test_app_config_attributes():
    config = AppConfig()
    assert hasattr(config, "SECRET_KEY")
    assert hasattr(config, "SQLALCHEMY_DATABASE_URI")
    assert hasattr(config, "CANCELLATION_FULL_REFUND_HOURS")
    assert config.CANCELLATION_FULL_REFUND_HOURS == 24
    assert config.CANCELLATION_MIN_HOURS == 2


def test_singleton_thread_safety():
    instances = []

    def create_instance():
        instances.append(AppConfig())

    threads = [threading.Thread(target=create_instance) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    first = instances[0]
    for inst in instances:
        assert inst is first


def test_database_session_manager_singleton():
    manager1 = DatabaseSessionManager()
    manager2 = DatabaseSessionManager()
    assert manager1 is manager2
    assert hasattr(manager1, "get_session")
