import asyncio
import logging
from typing import AsyncGenerator
import aioboto3
from botocore.config import Config
from core.config import get_settings

logger = logging.getLogger("storage.s3")
settings = get_settings()

session = aioboto3.Session()


def get_boto_config() -> Config:
    return Config(
        s3={"addressing_style": "path"},
        signature_version="s3v4",
        connect_timeout=10,
        read_timeout=60,
        retries={"max_attempts": 3, "mode": "standard"},
        proxies={"http": None, "https": None},
    )


async def get_s3_client() -> AsyncGenerator:
    """FastAPI dependency to yield an async S3 client for MinIO."""
    async with session.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        use_ssl=settings.s3_use_ssl,
        config=get_boto_config(),
    ) as client:
        yield client


async def check_s3_connection() -> bool:
    """Checks connection to MinIO S3 Server."""
    try:
        async with session.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
            use_ssl=settings.s3_use_ssl,
            config=get_boto_config(),
        ) as client:
            response = await asyncio.wait_for(client.list_buckets(), timeout=4.0)
            buckets = [b.get("Name") for b in response.get("Buckets", [])]
            logger.info(f"MinIO S3 connection: OK. Buckets count: {len(buckets)}")
            return True
    except Exception as e:
        logger.warning(f"MinIO S3 connection check failed/timeout ({settings.s3_endpoint}): {str(e)}")
        return False
