"""Tests for JWT security module."""

import pytest
from core.security import (
    InvalidTokenError,
    TokenPayload,
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from core.config import Settings


@pytest.fixture
def test_settings():
    return Settings(
        fusionauth_base_url="http://localhost:9011",
        fusionauth_api_key="test",
        jwt_secret_key="test-secret-key-for-testing-32chars!",
        jwt_issuer="test-issuer",
        jwt_audience="test-audience",
        jwt_algorithm="HS256",
        access_token_expire_minutes=15,
        refresh_token_expire_days=7,
        environment="development",
        allowed_origins="http://localhost:3000",
    )


class TestTokenCreation:
    def test_create_access_token(self, test_settings):
        token = create_access_token(
            user_id="user-123",
            application_id="app-456",
            roles=["admin", "user"],
            settings=test_settings,
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self, test_settings):
        token = create_refresh_token(
            user_id="user-123",
            application_id="app-456",
            settings=test_settings,
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_access_token_has_correct_type(self, test_settings):
        token = create_access_token(
            user_id="u1", application_id="a1", settings=test_settings
        )
        payload = decode_token(token, TokenType.ACCESS, settings=test_settings)
        assert payload.type == TokenType.ACCESS

    def test_refresh_token_has_correct_type(self, test_settings):
        token = create_refresh_token(
            user_id="u1", application_id="a1", settings=test_settings
        )
        payload = decode_token(token, TokenType.REFRESH, settings=test_settings)
        assert payload.type == TokenType.REFRESH


class TestTokenDecoding:
    def test_decode_valid_token(self, test_settings):
        token = create_access_token(
            user_id="u1", application_id="a1", roles=["admin"], settings=test_settings
        )
        payload = decode_token(token, TokenType.ACCESS, settings=test_settings)
        assert payload.sub == "u1"
        assert payload.app_id == "a1"
        assert "admin" in payload.roles

    def test_decode_wrong_type_raises(self, test_settings):
        refresh = create_refresh_token(
            user_id="u1", application_id="a1", settings=test_settings
        )
        with pytest.raises(InvalidTokenError):
            decode_token(refresh, TokenType.ACCESS, settings=test_settings)

    def test_decode_tampered_token_raises(self, test_settings):
        token = create_access_token(
            user_id="u1", application_id="a1", settings=test_settings
        )
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(InvalidTokenError):
            decode_token(tampered, TokenType.ACCESS, settings=test_settings)

    def test_decode_wrong_secret_raises(self, test_settings):
        token = create_access_token(
            user_id="u1", application_id="a1", settings=test_settings
        )
        wrong_settings = Settings(
            fusionauth_base_url="http://localhost:9011",
            fusionauth_api_key="test",
            jwt_secret_key="wrong-secret-key-different-32chars!",
            jwt_issuer="test-issuer",
            jwt_audience="test-audience",
            jwt_algorithm="HS256",
            access_token_expire_minutes=15,
            refresh_token_expire_days=7,
            environment="development",
            allowed_origins="http://localhost:3000",
        )
        with pytest.raises(InvalidTokenError):
            decode_token(token, TokenType.ACCESS, settings=wrong_settings)


class TestTokenType:
    def test_access_enum(self):
        assert TokenType.ACCESS == "access"

    def test_refresh_enum(self):
        assert TokenType.REFRESH == "refresh"
