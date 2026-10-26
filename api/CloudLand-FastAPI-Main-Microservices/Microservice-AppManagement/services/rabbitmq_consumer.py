import asyncio
import json
import logging
from uuid import UUID
from urllib.parse import quote_plus

import aio_pika

from core.config import get_settings
from Models.entity_file_attachment import EntityFileAttachment
from Structure.session import get_db_manager

logger = logging.getLogger("app_management.rabbitmq_consumer")
settings = get_settings()

_consumer_task: asyncio.Task | None = None

EXCHANGE_NAME = "storage.events"
QUEUE_NAME = "app_management.file_attachments"
ROUTING_KEYS = ["file_attachment.upload", "file_attachment.delete"]
RETRY_DELAY_SECONDS = 10
MAX_DELIVERIES = 3


async def process_file_attachment_message(message: aio_pika.abc.AbstractIncomingMessage):
    delivery_count = getattr(message, "delivery_count", 0)

    if delivery_count >= MAX_DELIVERIES:
        logger.warning(
            "Dropping RabbitMQ message after %d deliveries (max=%d) — likely a poison message.",
            delivery_count,
            MAX_DELIVERIES,
        )
        await message.ack()
        return

    try:
        payload = json.loads(message.body.decode())
        event_type = payload.get("event_type") or message.routing_key
        data = payload.get("data") or {}

        logger.info(f"AppManagement received RabbitMQ event '{event_type}': {data}")

        db_mgr = get_db_manager(settings.database_url)

        if event_type == "file_attachment.upload":
            record_id_str = data.get("record_id")
            file_url = data.get("file_url")
            file_ext = data.get("file_extension")
            orig_name = data.get("original_file_name")
            file_size = data.get("file_size_in_bytes", 0)
            user_id_str = data.get("user_id")
            app_id_str = data.get("application_id")
            title = data.get("title")
            desc = data.get("desc")

            rec_id = None
            if record_id_str:
                try:
                    rec_id = UUID(record_id_str)
                except ValueError:
                    logger.warning("Received non-UUID record_id %r — storing NULL", record_id_str)

            user_id = None
            if user_id_str:
                try:
                    user_id = UUID(user_id_str)
                except ValueError:
                    logger.warning("Received non-UUID user_id %r — using system fallback", user_id_str)

            app_id = None
            if app_id_str:
                try:
                    app_id = UUID(app_id_str)
                except ValueError:
                    logger.warning("Received non-UUID app_id %r — storing NULL", app_id_str)

            system_user_uuid = UUID("11111111-1111-1111-1111-111111111111")
            effective_user = user_id or system_user_uuid

            async with db_mgr.get_uow() as uow:
                existing = None
                target_app_id = app_id or rec_id
                from sqlalchemy import select, or_

                if file_url and "user-pic" in file_url:
                    effective_rec_id = rec_id or user_id
                    stmt = select(EntityFileAttachment).where(
                        EntityFileAttachment.record_id == effective_rec_id
                    ).order_by(EntityFileAttachment.create_at.desc())
                    res = await uow.session.execute(stmt)
                    existing = res.scalars().first()

                    if existing:
                        existing.record_id = effective_rec_id
                        existing.application_id = app_id or existing.application_id
                        existing.file_url = file_url
                        existing.file_extension = file_ext
                        existing.original_file_name = orig_name
                        existing.file_size_in_bytes = file_size
                        if title:
                            existing.title = title
                        if desc:
                            existing.desc = desc
                        existing.last_modified_user = effective_user
                        await uow.entity_file_attachments.update(existing)
                        logger.info(f"Successfully updated user-pic EntityFileAttachment {existing.id} for user_id/record_id: {effective_rec_id}")
                    else:
                        attachment = EntityFileAttachment(
                            record_id=effective_rec_id,
                            file_url=file_url,
                            file_extension=file_ext,
                            original_file_name=orig_name,
                            file_size_in_bytes=file_size,
                            title=title or orig_name or "تصویر کاربر",
                            desc=desc or "user-pic",
                            user_created=effective_user,
                            last_modified_user=effective_user,
                            application_id=app_id,
                        )
                        await uow.entity_file_attachments.add(attachment)
                        logger.info(f"Successfully created user-pic EntityFileAttachment in DB for user_id/record_id: {effective_rec_id}")

                elif target_app_id and (rec_id == target_app_id or (file_url and "co-logo" in file_url)):
                    # For co-logo: record_id and application_id are both the application_id
                    logo_app_id = app_id or target_app_id
                    stmt = select(EntityFileAttachment).where(
                        or_(
                            EntityFileAttachment.application_id == logo_app_id,
                            EntityFileAttachment.record_id == logo_app_id,
                        )
                    ).order_by(EntityFileAttachment.create_at.desc())
                    res = await uow.session.execute(stmt)
                    existing = res.scalars().first()

                    if existing:
                        existing.record_id = logo_app_id
                        existing.application_id = logo_app_id
                        existing.file_url = file_url
                        existing.file_extension = file_ext
                        existing.original_file_name = orig_name
                        existing.file_size_in_bytes = file_size
                        if title:
                            existing.title = title
                        if desc:
                            existing.desc = desc
                        existing.last_modified_user = effective_user
                        await uow.entity_file_attachments.update(existing)
                        logger.info(f"Successfully updated co-logo EntityFileAttachment {existing.id} for application_id: {logo_app_id}")
                    else:
                        attachment = EntityFileAttachment(
                            record_id=logo_app_id,
                            file_url=file_url,
                            file_extension=file_ext,
                            original_file_name=orig_name,
                            file_size_in_bytes=file_size,
                            title=title or orig_name or "لوگوی شرکت",
                            desc=desc or "default",
                            user_created=effective_user,
                            last_modified_user=effective_user,
                            application_id=logo_app_id,
                        )
                        await uow.entity_file_attachments.add(attachment)
                        logger.info(f"Successfully created co-logo EntityFileAttachment in DB for application_id: {logo_app_id}")

        elif event_type == "file_attachment.delete":
            file_url = data.get("file_url")
            record_id_str = data.get("record_id")
            async with db_mgr.get_uow() as uow:
                from sqlalchemy import select
                stmt = None
                if file_url:
                    stmt = select(EntityFileAttachment.id).where(EntityFileAttachment.file_url == file_url)
                elif record_id_str:
                    try:
                        rec_uuid = UUID(record_id_str)
                        stmt = select(EntityFileAttachment.id).where(EntityFileAttachment.record_id == rec_uuid)
                    except ValueError:
                        stmt = None

                if stmt is not None:
                    res = await uow.session.execute(stmt)
                    ids = res.scalars().all()
                    for attachment_id in ids:
                        await uow.entity_file_attachments.delete(attachment_id)
                    logger.info(f"Successfully deleted {len(ids)} EntityFileAttachment(s) from DB")

        await message.ack()
    except ValueError as ve:
        logger.error(
            "Permanent error processing RabbitMQ message (delivery_count=%d): %s — dropping message.",
            delivery_count,
            ve,
        )
        await message.ack()
    except Exception as e:
        logger.error(
            f"Error processing file attachment RabbitMQ message (delivery_count={delivery_count}): {e}",
            exc_info=True,
        )
        try:
            await message.nack(requeue=True)
        except Exception as nack_err:
            logger.warning(f"Could not nack message (already acked/nacked?): {nack_err}")


async def _consumer_loop():
    """
    Persistent consumer loop with automatic reconnect on failure.

    Key design decisions:
    - connect_robust() is called WITHOUT reconnect_interval to avoid the
      double-reconnect bug that caused ChannelInvalidStateError.
    - We detect connection closure via close_callbacks + asyncio.Event.
    - On normal closure we reconnect immediately; on error we wait RETRY_DELAY_SECONDS.
    - process_file_attachment_message uses explicit ack/nack (no auto_ack).
    """
    user = quote_plus(settings.rabbitmq_username)
    password = quote_plus(settings.rabbitmq_password)
    url = f"amqp://{user}:{password}@{settings.rabbitmq_host}:5672/"

    while True:
        connection: aio_pika.abc.AbstractRobustConnection | None = None
        reconnect_delay = RETRY_DELAY_SECONDS  # default: delay on error
        try:
            logger.info(
                f"RabbitMQ: connecting to {settings.rabbitmq_host} "
                f"as '{settings.rabbitmq_username}'…"
            )
            # Do NOT pass reconnect_interval — we handle reconnect ourselves.
            connection = await aio_pika.connect_robust(url)

            channel = await connection.channel()
            await channel.set_qos(prefetch_count=10)

            exchange = await channel.declare_exchange(
                EXCHANGE_NAME, aio_pika.ExchangeType.DIRECT, durable=True
            )
            queue = await channel.declare_queue(QUEUE_NAME, durable=True)

            for routing_key in ROUTING_KEYS:
                await queue.bind(exchange, routing_key=routing_key)

            # no_ack=False → we manually ack/nack inside the handler
            await queue.consume(process_file_attachment_message, no_ack=False)
            logger.info(
                f"RabbitMQ Consumer started — listening on '{QUEUE_NAME}' "
                f"queue (exchange: '{EXCHANGE_NAME}')"
            )

            # Block until connection drops or task is cancelled
            closed_event = asyncio.Event()

            def _on_close(sender, exc=None):
                if not closed_event.is_set():
                    closed_event.set()

            connection.close_callbacks.add(_on_close)

            # Guard: connection may already be closed before we register
            if connection.is_closed:
                closed_event.set()

            await closed_event.wait()
            # Connection dropped normally — reconnect quickly
            reconnect_delay = 1
            logger.warning("RabbitMQ connection closed. Will reconnect in %ss…", reconnect_delay)

        except asyncio.CancelledError:
            logger.info("RabbitMQ consumer task cancelled — shutting down.")
            break
        except Exception as e:
            logger.warning(
                f"RabbitMQ Consumer error: {e}. "
                f"Retrying in {RETRY_DELAY_SECONDS} seconds…"
            )
        finally:
            # Always attempt clean close; suppress errors from already-closed connections
            if connection is not None and not connection.is_closed:
                try:
                    await connection.close()
                except Exception:
                    pass

        try:
            await asyncio.sleep(reconnect_delay)
        except asyncio.CancelledError:
            logger.info("RabbitMQ consumer task cancelled during sleep — shutting down.")
            break


def launch_consumer_task():
    global _consumer_task
    _consumer_task = asyncio.create_task(_consumer_loop())


def stop_consumer_task():
    global _consumer_task
    if _consumer_task and not _consumer_task.done():
        _consumer_task.cancel()
        _consumer_task = None
