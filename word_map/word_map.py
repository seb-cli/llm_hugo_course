import reflex as rx

from word_map import style
from word_map.state import SettingsState, UploadState
from word_map.components.settings import settings_icon
from word_map.components.reset import reset
from word_map.views.templates import templates
from word_map.views.chat import chat, action_bar, rag_input


@rx.page(
    title="Word Map",
    description="A chatbot powered by Reflex!",
    on_load=UploadState.clear_all_uploaded_files)
def index() -> rx.Component:
    return rx.theme(
        rx.el.style(
            f""":w
            :root {{
                --font-family: "{SettingsState.font_family}", sans-serif;
            }}
        """
        ),
        # Top bar with the reset and settings buttons
        rx.box(
            reset(),
            settings_icon(),
            class_name="top-4 right-4 absolute flex flex-row items-center gap-3.5",
        ),
        # Main content
        rx.box(
            # Prompt examples
            templates(),
            # Chat history
            chat(),
            # Action bar
            action_bar(),
            class_name="relative flex flex-col justify-between gap-20 mx-auto px-6 pt-16 lg:pt-6 pb-6 max-w-4xl h-screen",
        ),
        accent_color=SettingsState.color,
    )


app = rx.App(stylesheets=style.STYLESHEETS, style={"font_family": "var(--font-family)"})
# app.add_page(
#     index, title="Chatbot", description="A chatbot powered by Reflex!"
# )
