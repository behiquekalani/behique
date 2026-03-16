"""Sample skill for Agent Kernel demo."""


def run(text: str = "", **kwargs) -> str:
    """Process text — demo skill that echoes input with transformation."""
    return f"Processed: {text.upper()} (length={len(text)})"
