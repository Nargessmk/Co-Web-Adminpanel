import logging
from typing import Any, List, Optional, Tuple
from elasticsearch import AsyncElasticsearch
from core.config import get_settings

logger = logging.getLogger("background_task.elastic")
settings = get_settings()

_es_client: Optional[AsyncElasticsearch] = None


def get_es_client() -> Optional[AsyncElasticsearch]:
    global _es_client
    if _es_client is None:
        if not settings.elasticsearch_url:
            logger.warning("Elasticsearch URL not configured.")
            return None

        kwargs: dict = {"hosts": [settings.elasticsearch_url], "verify_certs": False}
        if settings.elasticsearch_username and settings.elasticsearch_password:
            kwargs["basic_auth"] = (
                settings.elasticsearch_username,
                settings.elasticsearch_password,
            )

        try:
            _es_client = AsyncElasticsearch(**kwargs)
            logger.info("Initialized AsyncElasticsearch client.")
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch client: {e}")
            return None

    return _es_client


async def close_es_client():
    global _es_client
    if _es_client is not None:
        await _es_client.close()
        _es_client = None
        logger.info("Closed AsyncElasticsearch client.")


async def clear_index(index_name: str) -> bool:
    client = get_es_client()
    if client is None:
        return False
    try:
        exists = await client.indices.exists(index=index_name)
        if exists:
            await client.delete_by_query(
                index=index_name,
                body={"query": {"match_all": {}}},
                conflicts="proceed",
            )
            logger.info(f"Cleared existing documents from index: {index_name}")
        return True
    except Exception as e:
        logger.error(f"Error clearing index {index_name}: {e}")
        return False


async def bulk_index(index_name: str, docs: List[Tuple[str, dict]]) -> bool:
    client = get_es_client()
    if client is None:
        return False
    if not docs:
        return True

    operations = []
    for doc_id, body in docs:
        operations.append({"index": {"_index": index_name, "_id": doc_id}})
        operations.append(body)

    try:
        response = await client.bulk(operations=operations)
        if response.get("errors"):
            logger.error(f"Bulk indexing into {index_name} had errors: {response}")
            return False
        return True
    except Exception as e:
        logger.error(f"Failed bulk index for {index_name}: {e}")
        return False
