import logging


def on_note_write(event: str, payload: dict) -> None:
    if event == "notes_write":
        logger = logging.getLogger("notes_plug")
        logger.info("Notes plug: wrote key=%s", payload.get("key"))


def register_hooks(register):
    # Register the hook function with the registry
    register(on_note_write)
