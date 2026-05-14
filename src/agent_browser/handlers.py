from agent_browser.tasks import Handler, TaskOutcome, TaskRequest


def noop(request: TaskRequest) -> TaskOutcome:
    return TaskOutcome(result=f"noop completed: {request.prompt}")


def register_default_handlers(registry: dict[str, Handler]) -> None:
    registry["noop"] = noop
