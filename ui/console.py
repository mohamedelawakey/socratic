import shutil
from rich.console import Console
from rich.theme import Theme

# Modern Dev Theme with sleek accents
custom_theme = Theme({
    "mentor": "bold cyan",
    "mentor.box": "cyan",
    "crash": "bold red",
    "crash.box": "red",
    "code": "bright_white on #1e1e2e",
    "user": "bold yellow",
    "success": "bold green",
    "success.box": "green",
    "subtle": "dim white",
    "badge": "bold black on bright_cyan",
})

# Global rich console instance for socratic (adapts dynamically to window dimensions)
console = Console(
    theme=custom_theme,
    highlight=False,
)
