"""Tests for Sentry integration."""

import logging
from unittest.mock import MagicMock, patch

import pytest
import sentry_sdk

from core.config import Settings
from core.logging import SentryHandler, setup_logging
from core.sentry import init_sentry


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
        sentry_dsn="https://test-key@o123456.ingest.sentry.io/1234567",
        sentry_traces_sample_rate=1.0,
    )


@pytest.fixture
def settings_without_sentry():
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
        sentry_dsn="",
    )


class TestSentryInitialization:
    def test_init_sentry_with_dsn(self, test_settings):
        with patch("core.sentry.sentry_sdk.init") as mock_init:
            init_sentry(test_settings)
            mock_init.assert_called_once()
            call_kwargs = mock_init.call_args[1]
            assert call_kwargs["dsn"] == test_settings.sentry_dsn
            assert call_kwargs["environment"] == test_settings.environment

    def test_init_sentry_without_dsn(self, settings_without_sentry):
        with patch("core.sentry.sentry_sdk.init") as mock_init:
            init_sentry(settings_without_sentry)
            mock_init.assert_not_called()

    def test_sentry_logging_integration_configured(self, test_settings):
        with patch("core.sentry.sentry_sdk.init") as mock_init:
            init_sentry(test_settings)
            call_kwargs = mock_init.call_args[1]
            integrations = call_kwargs["integrations"]
            assert any(
                isinstance(i, sentry_sdk.integrations.logging.LoggingIntegration)
                for i in integrations
            )

    def test_sentry_fastapi_integration_configured(self, test_settings):
        with patch("core.sentry.sentry_sdk.init") as mock_init:
            init_sentry(test_settings)
            call_kwargs = mock_init.call_args[1]
            integrations = call_kwargs["integrations"]
            assert any(
                isinstance(i, sentry_sdk.integrations.fastapi.FastApiIntegration)
                for i in integrations
            )


class TestSentryHandler:
    def test_sentry_handler_capture_exception(self):
        handler = SentryHandler(level=logging.WARNING)
        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="test.py",
            lineno=1,
            msg="Test error",
            args=(),
            exc_info=(ValueError, ValueError("test error"), None),
        )

        with patch("core.logging.sentry_sdk.capture_exception") as mock_capture:
            handler.emit(record)
            mock_capture.assert_called_once()

    def test_sentry_handler_capture_message(self):
        handler = SentryHandler(level=logging.WARNING)
        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="test.py",
            lineno=1,
            msg="Test warning message",
            args=(),
            exc_info=None,
        )

        with patch("core.logging.capture_message") as mock_capture:
            handler.emit(record)
            mock_capture.assert_called_once_with(
                "Test warning message",
                level="warning",
            )

    def test_sentry_handler_sets_tags(self):
        handler = SentryHandler(level=logging.WARNING)
        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        with patch("core.logging.set_tag") as mock_set_tag:
            handler.emit(record)
            mock_set_tag.assert_any_call("logger", "test")


class TestLoggingSetup:
    def test_sentry_handler_added_when_dsn_present(self, test_settings):
        setup_logging(test_settings)
        root_logger = logging.getLogger()
        sentry_handlers = [
            h for h in root_logger.handlers if isinstance(h, SentryHandler)
        ]
        assert len(sentry_handlers) == 1

    def test_sentry_handler_not_added_when_dsn_absent(self, settings_without_sentry):
        setup_logging(settings_without_sentry)
        root_logger = logging.getLogger()
        sentry_handlers = [
            h for h in root_logger.handlers if isinstance(h, SentryHandler)
        ]
        assert len(sentry_handlers) == 0


class TestExceptionHandlerIntegration:
    def test_exception_handler_captures_to_sentry(self):
        from middleware.exception_handler import global_exception_handler
        from fastapi import Request
        from starlette.testclient import TestClient

        mock_request = MagicMock(spec=Request)
        mock_request.method = "GET"
        mock_request.url.path = "/test"

        exc = ValueError("Test exception")

        with patch("middleware.exception_handler.sentry_sdk.capture_exception") as mock_capture:
            import asyncio

            async def run():
                return await global_exception_handler(mock_request, exc)

            response = asyncio.run(run())
            assert response.status_code == 500
            mock_capture.assert_called_once_with(exc)
