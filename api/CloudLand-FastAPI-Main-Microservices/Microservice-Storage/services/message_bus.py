from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import aio_pika

from urllib.parse import quote_plus

logger = logging.getLogger("storage.message_bus")

_RECONNECT_DELAY_SECONDS = 5


class StorageMessageBus:
    """
    Async RabbitMQ publisher for Microservice-Storage.
    Publishes events to 'storage.events' exchange when files are uploaded/deleted.
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
        self._reconnect_task: asyncio.Task | None = None
        self._shutdown = False

    async def _create_connection(self) -> tuple[
        aio_pika.abc.AbstractRobustConnection | None,
        aio_pika.abc.AbstractChannel | None,
    ]:
        connection = None
        channel = None
        try:
            user = quote_plus(self._username)
            password = quote_plus(self._password)
            url = f"amqp://{user}:{password}@{self._host}:{self._port}{self._vhost}"
            connection = await aio_pika.connect_robust(url)
            channel = await connection.channel()
            logger.info("Storage RabbitMQ connected at %s:%s", self._host, self._port)
            return connection, channel
        except Exception as exc:
            logger.warning("Storage RabbitMQ connection failed: %s", exc)
            if connection is not None and not connection.is_closed:
                try:
                    await connection.close()
                except Exception:
                    pass
            return None, None

    async def connect(self) -> None:
        connection, channel = await self._create_connection()
        self._connection = connection
        self._channel = channel

    async def close(self) -> None:
        self._shutdown = True
        if self._reconnect_task is not None and not self._reconnect_task.done():
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except asyncio.CancelledError:
                pass
            self._reconnect_task = None
        if self._connection and not self._connection.is_closed:
            try:
                await self._connection.close()
            except Exception:
                pass
        self._connection = None
        self._channel = None

    @property
    def is_connected(self) -> bool:
        return self._connection is not None and self._connection.is_closed is False

    async def _reconnect_loop(self) -> None:
        while not self._shutdown:
            if self.is_connected:
                await asyncio.sleep(1)
                continue

            logger.info("Storage RabbitMQ disconnected. Attempting to reconnect...")
            connection, channel = await self._create_connection()
            self._connection = connection
            self._channel = channel
            if self.is_connected:
                logger.info("Storage RabbitMQ reconnected successfully.")
            else:
                logger.warning("Storage RabbitMQ reconnect failed. Retrying in %ss...", _RECONNECT_DELAY_SECONDS)
                await asyncio.sleep(_RECONNECT_DELAY_SECONDS)

    async def start_reconnect_task(self) -> None:
        if self._reconnect_task is None or self._reconnect_task.done():
            self._shutdown = False
            self._reconnect_task = asyncio.create_task(self._reconnect_loop())

    async def publish(
        self,
        exchange_name: str,
        routing_key: str,
        message: dict[str, Any],
    ) -> bool:
        if not self._channel or self._channel.is_closed:
            await self.connect()

        if not self._channel or self._channel.is_closed:
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
                    content_type="application/json",
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=routing_key,
            )
            logger.info("Published Storage event to %s.%s", exchange_name, routing_key)
            return True
        except Exception as exc:
            logger.warning("Failed to publish storage message: %s", exc)
            try:
                if self._channel and not self._channel.is_closed:
                    await self._channel.close()
            except Exception:
                pass
            self._channel = None
            return False

    async def publish_file_uploaded(
        self,
        record_id: str | None,
        file_url: str,
        file_extension: str,
        original_file_name: str,
        file_size_in_bytes: int,
        user_id: str | None = None,
        application_id: str | None = None,
        title: str | None = None,
        desc: str | None = None,
    ) -> bool:
        """Publishes file_attachment.upload event for AppManagement to consume."""
        return await self.publish(
            exchange_name="storage.events",
            routing_key="file_attachment.upload",
            message={
                "event_type": "file_attachment.upload",
                "data": {
                    "record_id": record_id,
                    "file_url": file_url,
                    "file_extension": file_extension,
                    "original_file_name": original_file_name,
                    "file_size_in_bytes": file_size_in_bytes,
                    "user_id": user_id,
                    "application_id": application_id,
                    "title": title,
                    "desc": desc,
                },
            },
        )

    async def publish_file_deleted(self, file_url: str, record_id: str | None = None) -> bool:
        """Publishes file_attachment.delete event for AppManagement to consume."""
        return await self.publish(
            exchange_name="storage.events",
            routing_key="file_attachment.delete",
            message={
                "event_type": "file_attachment.delete",
                "data": {
                    "file_url": file_url,
                    "record_id": record_id,
                },
            },
        )


_message_bus: StorageMessageBus | None = None


def get_storage_message_bus() -> StorageMessageBus:
    global _message_bus
    if _message_bus is None:
        from core.config import get_settings
        settings = get_settings()
        _message_bus = StorageMessageBus(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            username=settings.rabbitmq_username,
            password=settings.rabbitmq_password,
            vhost=settings.rabbitmq_vhost,
        )
    return _message_bus


async def close_storage_message_bus() -> None:
    global _message_bus
    if _message_bus is not None:
        await _message_bus.close()
        _message_bus = None
