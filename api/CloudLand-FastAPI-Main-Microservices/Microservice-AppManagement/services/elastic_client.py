import logging
from typing import Any

from core.config import get_settings

logger = logging.getLogger(__name__)

try:
    from elasticsearch import AsyncElasticsearch
except ImportError:
    AsyncElasticsearch = None

_client: Any = None

INDEX_CONSTANT = "apm-constant"
INDEX_CALENDAR = "calendar-v2"


def get_es_client() -> Any:
    global _client
    if _client is None:
        settings = get_settings()
        if not settings.elasticsearch_url:
            return None
        if AsyncElasticsearch is None:
            return None
        try:
            _client = AsyncElasticsearch(
                settings.elasticsearch_url,
                basic_auth=(settings.elasticsearch_username, settings.elasticsearch_password)
                if settings.elasticsearch_username
                else None,
            )
        except Exception:
            logger.warning("Failed to create Elasticsearch client, disabling ES sync")
            _client = None
    return _client


async def close_es_client() -> None:
    global _client
    if _client is not None:
        try:
            await _client.close()
        except Exception:
            logger.warning("Failed to close Elasticsearch client")
        _client = None


def _dump(dto: Any) -> dict:
    return dto.model_dump(by_alias=True, mode="json")


async def index_document(index: str, doc_id: Any, dto: Any) -> bool:
    client = get_es_client()
    if client is None:
        return False
    try:
        await client.index(index=index, id=str(doc_id), document=_dump(dto))
        return True
    except Exception:
        logger.warning(
            "Elasticsearch index sync failed for %s/%s", index, doc_id, exc_info=True
        )
        return False


async def delete_document(index: str, doc_id: Any) -> None:
    client = get_es_client()
    if client is None:
        return
    try:
        await client.delete(index=index, id=str(doc_id))
    except Exception:
        logger.warning(
            "Elasticsearch delete sync failed for %s/%s", index, doc_id, exc_info=True
        )


async def index_constant(dto: Any) -> None:
    await index_document(INDEX_CONSTANT, dto.id, dto)


async def delete_constant(doc_id: Any) -> None:
    await delete_document(INDEX_CONSTANT, doc_id)


async def index_calendar(dto: Any) -> None:
    await index_document(INDEX_CALENDAR, dto.id, dto)


async def delete_calendar(doc_id: Any) -> None:
    await delete_document(INDEX_CALENDAR, doc_id)


async def bulk_index(index: str, docs: list[tuple[Any, dict]]) -> bool:
    client = get_es_client()
    if client is None:
        return False
    operations: list[dict] = []
    for doc_id, document in docs:
        operations.append({"index": {"_index": index, "_id": str(doc_id)}})
        operations.append(document)
    try:
        response = await client.bulk(operations=operations)
        body = response.body if hasattr(response, "body") else response
        if body.get("errors", False):
            reasons = [
                item.get("error", {}).get("reason", "unknown")
                for item in body.get("items", [])
                if "error" in item.get("index", {})
            ]
            logger.warning(
                "Elasticsearch bulk index returned %d errors for %s (first: %s)",
                len(reasons),
                index,
                reasons[:3],
            )
            return False
        return True
    except Exception:
        logger.warning(
            "Elasticsearch bulk index failed for %s", index, exc_info=True
        )
        return False


async def clear_index(index: str) -> None:
    client = get_es_client()
    if client is None:
        return
    try:
        await client.delete_by_query(
            index=index,
            query={"match_all": {}},
            conflicts="proceed",
        )
    except Exception:
        logger.warning("Elasticsearch delete-by-query failed for %s", index)
