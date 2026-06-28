from ai_hiring_intelligence.core.config import Settings


def test_settings_defaults() -> None:
    settings = Settings()

    assert settings.app_name == "AI Hiring Intelligence"
    assert settings.app_env == "local"
    assert settings.log_level == "INFO"

