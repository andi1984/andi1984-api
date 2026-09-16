from app.core.config import Settings


def test_cors_origins_parsed_from_csv() -> None:
    settings = Settings(cors_origins="https://a.com, https://b.com")
    assert settings.cors_origins == ["https://a.com", "https://b.com"]


def test_defaults() -> None:
    settings = Settings(_env_file=None)
    assert settings.birth_year == 1984
    assert settings.environment == "development"
    assert settings.is_production is False
