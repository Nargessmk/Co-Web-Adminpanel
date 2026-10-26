from typing import Any


class AppManagementError(Exception):
    def __init__(self, message: str, status_code: int | None = None, details: Any = None) -> None:
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundError(AppManagementError):
    def __init__(self, message: str = "رکورد مورد نظر یافت نشد", status_code: int = 404, details: Any = None) -> None:
        super().__init__(message, status_code, details)


class ValidationError(AppManagementError):
    def __init__(self, message: str = "اطلاعات ارسالی نامعتبر است", status_code: int = 400, details: Any = None) -> None:
        super().__init__(message, status_code, details)


class DuplicateEntryError(AppManagementError):
    def __init__(self, message: str = "رکورد تکراری است", status_code: int = 409, details: Any = None) -> None:
        super().__init__(message, status_code, details)


class DeleteForbiddenError(AppManagementError):
    def __init__(self, message: str = "حذف این ثابت سیستمی مجاز نمی‌باشد و قفل شده است", status_code: int = 403, details: Any = None) -> None:
        super().__init__(message, status_code, details)


class UpdateForbiddenError(AppManagementError):
    def __init__(self, message: str = "ویرایش این ثابت سیستمی مجاز نمی‌باشد و قفل شده است", status_code: int = 403, details: Any = None) -> None:
        super().__init__(message, status_code, details)