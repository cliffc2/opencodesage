"""
Lite plug-in registry for OpenCode/OpenSage notes integration.
Provides a lightweight mechanism to react to note writes without changing core APIs.
"""

from typing import Callable, List

_registered_hooks: List[Callable[[str, dict], None]] = []


def register_note_hook(func: Callable[[str, dict], None]) -> None:
    """Register a hook to be called on note events."""
    _registered_hooks.append(func)


def notify(event: str, payload: dict) -> None:
    """Notify all registered hooks about an event."""
    for hook in list(_registered_hooks):
        try:
            hook(event, payload)
        except Exception:
            pass


def load_plugins(directory: str = "./plugs") -> None:
    """Dynamically load all plugin modules in the given directory.
    Each plugin should expose a register_hooks(register) function and call register with
    a function to register hooks (e.g., register_note_hook).
    """
    import importlib.util
    from pathlib import Path

    base = Path(directory)
    if not base.exists() or not base.is_dir():
        return

    for py in base.glob("*.py"):
        name = py.name
        if name.startswith("_") or name in ("registry.py", "__init__.py"):
            continue
        spec = importlib.util.spec_from_file_location(name[:-3], str(py))
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)  # type: ignore
        except Exception:
            continue
        if hasattr(module, "register_hooks"):  # type: ignore
            try:
                module.register_hooks(register_note_hook)  # type: ignore
            except Exception:
                pass


def register_note_hook(func: Callable[[str, dict], None]) -> None:
    _registered_hooks.append(func)
