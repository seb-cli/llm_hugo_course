import reflex as rx
from llm_frontend.components.hint import hint

badge_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
<rect width="16" height="16" rx="2" fill="#6E56CF"/>
<path d="M10 9V13H12V9H10Z" fill="white"/>
<path d="M4 3V13H6V9H10V7H6V5H10V7H12V3H4Z" fill="white"/>
</svg>
"""


def made_with_reflex() -> rx.Component:
    return rx.link(
        rx.html(badge_svg),
        rx.text(
            "Built with Reflex",
            class_name="font-medium text-sm",
        ),
        href="https://reflex.dev/",
        is_external=True,
        color_scheme="violet",
        class_name="flex flex-row justify-center items-center gap-1.5 opacity-50 hover:opacity-100 w-full transition-opacity",
    )
