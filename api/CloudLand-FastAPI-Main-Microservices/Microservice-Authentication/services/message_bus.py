"""
RabbitMQ message bus using aio-pika.

Mirrors C# MassTransit + RabbitMQ usage pattern:
- Connects on startup, publishes events for auth operations
- Endpoint name formatter: kebab-case with 'notification.service' prefix
- Graceful degradation: if RabbitMQ is unavailable, logs warning and continues
"""

from __future__ import annotations

import json
import logging
from typing import Any
from urllib.parse import quote_plus

import aio_pika

logger = logging.getLogger(__name__)


class MessageBus:
    """
    Async RabbitMQ connection wrapper for publishing messages.
    Mirrors MassTransit's UsingRabbitMq pattern from C# Program.cs.
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        vhost: str,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._vhost = vhost
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None

    async def connect(self) -> None:
        """Establish RabbitMQ connection."""
        try:
            user = quote_plus(self._username)
            password = quote_plus(self._password)
            url = f"amqp://{user}:{password}@{self._host}:{self._port}{self._vhost}"
            self._connection = await aio_pika.connect_robust(url)
            self._channel = await self._connection.channel()
            logger.info("RabbitMQ connected at %s:%s", self._host, self._port)
        except Exception as exc:
            logger.warning("RabbitMQ connection failed: %s — message bus disabled", exc)
            self._connection = None
            self._channel = None

    async def close(self) -> None:
        """Close RabbitMQ connection."""
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
        self._connection = None
        self._channel = None

    @property
    def is_connected(self) -> bool:
        return self._connection is not None and self._connection.is_closed is False

    async def publish(
        self,
        exchange_name: str,
        routing_key: str,
        message: dict[str, Any],
        content_type: str = "application/json",
    ) -> bool:
        """
        Publish a message to an exchange.

        Mirrors MassTransit publish pattern:
        - exchange_name maps to MassTransit's endpoint name formatter
        - routing_key is the kebab-case message type
        """
        if not self._channel:
            logger.warning("RabbitMQ not connected — message dropped: %s.%s", exchange_name, routing_key)
            return False

        try:
            exchange = await self._channel.declare_exchange(
                exchange_name,
                aio_pika.ExchangeType.DIRECT,
                durable=True,
            )
            body = json.dumps(message, default=str).encode()
            await exchange.publish(
                aio_pika.Message(
                    body=body,
                    content_type=content_type,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=routing_key,
            )
            logger.debug("Published to %s.%s", exchange_name, routing_key)
            return True
        except Exception as exc:
            logger.warning("Failed to publish message: %s", exc)
            return False

    async def publish_notification(self, event_type: str, data: dict[str, Any]) -> bool:
        """
        Convenience method for publishing auth-related notifications.
        Uses 'notification.service' exchange — matches C# MassTransit
        KebabCaseEndpointNameFormatter("notification.service", false).
        """
        return await self.publish(
            exchange_name="notification.service",
            routing_key=event_type,
            message={"event_type": event_type, "data": data},
        )


# ---------------------------------------------------------------------------
# Singleton management
# ---------------------------------------------------------------------------

_message_bus: MessageBus | None = None


def get_message_bus() -> MessageBus:
    """Return the shared MessageBus instance (created lazily)."""
    global _message_bus
    if _message_bus is None:
        from core.config import get_settings
        settings = get_settings()
        _message_bus = MessageBus(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            username=settings.rabbitmq_username,
            password=settings.rabbitmq_password,
            vhost=settings.rabbitmq_vhost,
        )
    return _message_bus


async def close_message_bus() -> None:
    """Close the shared RabbitMQ connection."""
    global _message_bus
    if _message_bus is not None:
        await _message_bus.close()
        _message_bus = None
