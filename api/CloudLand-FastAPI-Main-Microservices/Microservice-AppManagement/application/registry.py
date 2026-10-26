import importlib
import inspect
import typing
from pathlib import Path
from types import ModuleType

from core.mediator import IRequestHandler, Mediator


def _get_request_type(handler_cls: type) -> type | None:
    for base in getattr(handler_cls, "__orig_bases__", []):
        if getattr(base, "__origin__", None) is IRequestHandler:
            args = typing.get_args(base)
            if args:
                return args[0]
    return None


def _iter_classes(module: ModuleType):
    for _, member in inspect.getmembers(module, inspect.isclass):
        if member.__module__ != module.__name__:
            continue
        if member is IRequestHandler:
            continue
        if issubclass(member, IRequestHandler) and not inspect.isabstract(member):
            yield member


def _discover_handler_modules() -> list[str]:
    """
    Discover all Python modules under application/handlers automatically,
    similar to MediatR's assembly scanning. No manual module list needed.
    """
    handlers_dir = Path(__file__).parent / "handlers"
    if not handlers_dir.exists():
        return []

    package_prefix = f"{__package__}.handlers" if __package__ else "application.handlers"
    modules: list[str] = []

    for py_file in handlers_dir.rglob("*.py"):
        if py_file.name.startswith("_") or py_file.name == "__init__.py":
            continue
        relative = py_file.relative_to(handlers_dir)
        module_path = ".".join(relative.with_suffix("").parts)
        modules.append(f"{package_prefix}.{module_path}")

    return modules


def register_all_handlers(mediator: Mediator) -> None:
    for module_name in _discover_handler_modules():
        module = importlib.import_module(module_name)
        for handler_cls in _iter_classes(module):
            request_type = _get_request_type(handler_cls)
            if request_type is None:
                continue
            if request_type in mediator._request_handlers:
                continue
            mediator.register_request_handler(request_type, handler_cls())
