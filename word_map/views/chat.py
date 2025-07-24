import os
import reflex as rx
from word_map.components.badge import made_with_reflex
from word_map.state import State, UploadState, ModelSelectionMixin #, ManualRAGState


def qa(question: str, answer: str) -> rx.Component:
    return rx.box(
        # Question
        rx.box(
            rx.markdown(
                question,
                class_name="[&>p]:!my-2.5",
            ),
            class_name="relative bg-slate-3 px-5 rounded-3xl max-w-[70%] text-slate-12 self-end",
        ),
        # Answer
        rx.box(
            rx.vstack(
                rx.badge(f"{State.query_engine}"),
                rx.box(
                    rx.image(
                        src="word_map.png",
                        class_name="h-6" + rx.cond(State.processing, " animate-pulse", ""),
                    ),
                ),
            ),
            rx.box(
                rx.markdown(
                    answer,
                    class_name="[&>p]:!my-2.5",
                ),
                rx.box(
                    rx.hstack(
                        rx.badge(f"Nb tokens in first prompt = {State.nb_input_tokens} "),
                        rx.el.button(
                            rx.icon(tag="copy", size=18),
                            class_name="p-1 text-slate-10 hover:text-slate-11 transform transition-colors cursor-pointer",
                            on_click=[rx.set_clipboard(answer), rx.toast("Copied!")],
                            title="Copy",
                        ),
                        class_name="-bottom-9 left-5 absolute opacity-0 group-hover:opacity-100 transition-opacity",
                    ),
                ),
                class_name="relative bg-accent-4 px-5 rounded-3xl max-w-[70%] text-slate-12 self-start",
            ),
            class_name="flex flex-row gap-6",
        ),
        class_name="flex flex-col gap-8 pb-10 group",
    )


def chat() -> rx.Component:
    """A chat in the style of text messages."""
    return rx.scroll_area(
        rx.foreach(
            State.chat_history,
            lambda messages: qa(messages[0], messages[1]),
        ),
        scrollbars="vertical",
        class_name="w-full",
    )

def select_llm_engine():
    return rx.center(
        rx.select(
            ["google/gemma-3n-e4b-it:free", "openai/gpt-3.5-turbo", "deepseek/deepseek-r1-0528:free"],
            value=State.llm_engine,
            on_change=State.change_value,
        ),
        rx.badge(State.llm_engine),
    )


def rag_input():
    """The main view."""
    return rx.vstack(
        rx.hstack(
            rx.foreach(
                rx.selected_files("upload1"), 
                rx.badge
            ),
            padding="1em",
        ),
        rx.hstack(
            rx.upload.root(
                rx.button(
                    "Select File(s) for Context (RAG)",
                ),
                multiple=True,
                id="upload1",
                class_name="left-2 relative bg-accent-9 hover:bg-accent-10 disabled:hover:bg-accent-9 opacity-85 disabled:opacity-50 p-1.5 rounded-full transition-colors -translate-y-1/2 cursor-pointer disabled:cursor-default",
            ),
            rx.button(
                "Upload",
                on_click=UploadState.handle_upload(
                    rx.upload_files(upload_id="upload1")
                ),
                class_name="left-1 relative bg-accent-9 hover:bg-accent-10 disabled:hover:bg-accent-9 opacity-65 disabled:opacity-50 p-1.5 rounded-full transition-colors -translate-y-1/2 cursor-pointer disabled:cursor-default",
            ),
            rx.button(
                "Clear",
                on_click=rx.clear_selected_files("upload1"),
                class_name="left-0 relative bg-accent-9 hover:bg-accent-10 disabled:hover:bg-accent-9 opacity-65 disabled:opacity-50 p-1.5 rounded-full transition-colors -translate-y-1/2 cursor-pointer disabled:cursor-default",
            ),
        ),
        rx.hstack(
            rx.foreach(
                UploadState.rag_document,
                lambda rag_document: rx.badge(rag_document, direction="row"),
            ),
            padding="1em",
        ),
        rx.button(
            "Cancel Upload",
            on_click=UploadState.cancel_upload(),
            class_name="left-3 relative bg-accent-9 hover:bg-accent-10 disabled:hover:bg-accent-9 opacity-65 disabled:opacity-50 p-1.5 rounded-full transition-colors -translate-y-1/2 cursor-pointer disabled:cursor-default",
        ),
        # rx.hstack(
        #     rx.button(
        #         "Ingest context (RAG)",
        #         on_click=UploadState.update_uploaded_docs(),
        #         # on_click=State.query_pdf(),
        #         class_name="left-3 relative bg-accent-9 hover:bg-accent-10 disabled:hover:bg-accent-9 opacity-65 disabled:opacity-50 p-1.5 rounded-full transition-colors -translate-y-1/2 cursor-pointer disabled:cursor-default",
        #     ),
        #     # rx.foreach(
        #     #     os.listdir("./uploaded_files"),
        #     #     lambda f: rx.badge(f),
        #     # )
        # ),
        display=rx.cond(State.chat_history, "none", "flex"),
        # padding="5em",
    )


def action_bar() -> rx.Component:
    return rx.box(
        rag_input(),
        rx.box(
            rx.el.input(
                placeholder="Ask anything",
                on_blur=State.set_question,
                id="input1",
                class_name="box-border bg-slate-3 px-4 py-2 pr-14 rounded-full w-full outline-none focus:outline-accent-10 h-[48px] text-slate-12 placeholder:text-slate-9",
            ),
            rx.el.button(
                rx.cond(
                    State.processing,
                    rx.icon(
                        tag="loader-circle",
                        size=19,
                        color="white",
                        class_name="animate-spin",
                    ),
                    rx.icon(tag="arrow-up", size=19, color="white"),
                ),
                on_click=[State.answer, rx.set_value("input1", "")],
                class_name="top-1/2 right-4 absolute bg-accent-9 hover:bg-accent-10 disabled:hover:bg-accent-9 opacity-65 disabled:opacity-50 p-1.5 rounded-full transition-colors -translate-y-1/2 cursor-pointer disabled:cursor-default",
                disabled=rx.cond(
                    State.processing | (State.question == ""), True, False
                ),
            ),
            class_name="relative w-full",
        ),
        # Select the LLM engine
        select_llm_engine(),
        # Made with Reflex link
        made_with_reflex(),
        class_name="flex flex-col justify-center items-center gap-6 w-full",
    )


color = "rgb(107,99,246)"


