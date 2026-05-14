"""Local-first browser automation runtime."""

__version__ = "0.1.0"

from agent_browser import handlers, tasks

handlers.register_default_handlers(tasks.HANDLERS)
