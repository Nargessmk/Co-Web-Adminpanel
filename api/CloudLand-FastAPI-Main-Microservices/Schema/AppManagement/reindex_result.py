from pydantic import BaseModel, ConfigDict

from Schema.base import dotnet_pascal


class ReindexResult(BaseModel):
    model_config = ConfigDict(alias_generator=dotnet_pascal, populate_by_name=True)

    is_success: bool = False
    message: str = ""
    processed_count: int = 0
    error_count: int = 0
    details: list[str] | None = None

    @classmethod
    def success(
        cls, processed_count: int, error_count: int, details: list[str] | None = None
    ) -> "ReindexResult":
        return cls(
            is_success=True,
            message="Reindex completed successfully",
            processed_count=processed_count,
            error_count=error_count,
            details=details,
        )

    @classmethod
    def failure(cls, message: str) -> "ReindexResult":
        return cls(is_success=False, message=message)
