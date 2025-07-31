import asyncio
from dotenv import load_dotenv
import fitz # PyMuPDF
import json
import os
import uuid

import reflex as rx
# from openai import OpenAI
import openai

class SettingsState(rx.State):
    # The accent color for the app
    color: str = "violet"

    # The font family for the app
    font_family: str = "Poppins"


class ModelSelectionMixin(rx.State, mixin=True):
    llm_engine: str = "google/gemma-3n-e4b-it:free"

    @rx.event
    def change_value(self, llm: str):
        """Change the select value var."""
        self.llm_engine = llm


class UploadState(rx.State):
    """State for uploading one or multiple files, e.g. RAG context."""

    # The documents to list
    rag_document: list[str] = []
    all_uploaded_files: list[str] = []

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handle the upload of file(s).

        Args:
            files: The uploaded files.
        """
        for file in files:
            upload_data = await file.read()
            outfile = rx.get_upload_dir() / file.name

            # Save the file.
            with outfile.open("wb") as file_object:
                file_object.write(upload_data)

            # Update the rag_document var.
            self.rag_document.append(file.name)
        self.all_uploaded_files = [f for f in os.listdir(rx.get_upload_dir())]


    @rx.event
    def cancel_upload(self):
        self.rag_document.clear()
        return rx.cancel_upload("upload1")
    
    @rx.event
    def clear_all_uploaded_files(self):
        for f in os.listdir(rx.get_upload_dir()):
            os.remove(rx.get_upload_dir() / f)
        self.all_uploaded_files = []
        self.rag_document.clear()
        return rx.cancel_upload("upload1")


# Load environment variables
load_dotenv(".env")
# AsyncOpenAI not supported by OpenRouter
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    )


class State(ModelSelectionMixin, rx.State):
    """General App State."""
    # The current question being asked.
    question: str
    # Whether the app is processing a question.
    processing: bool = False
    # Keep track of the chat history as a list of (question, answer, model, nb_input_tokens, nb_output_tokens) tuples.
    chat_history: list[tuple[str, str, str, int, int]] = []
    # Keep history of messages for continuity between follow-up prompts
    messages_history: list[tuple[str, str]] = []
    user_id: str = str(uuid.uuid4())

    query_engine: str
    nb_input_tokens: int
    nb_output_tokens: int
    rag_input: list[dict] = []


    # Extract text from all pages of a PDF and return it in one chunk
    def extract_text_from_pdf(self, pdf_bytes):
        pdf_doc = fitz.open(pdf_bytes)
        text = ""
        for page_num in range(pdf_doc.page_count):
            page = pdf_doc.load_page(page_num)
            text += page.get_text("text")
        
        self.rag_input.append({'pdf_doc': pdf_bytes, 'pdf_text': text})

    def query_pdf(self):#, query: str, model_engine: str):
        for pdf_doc in os.listdir("./uploaded_files"):
            self.extract_text_from_pdf(f"./uploaded_files/{pdf_doc}")


    @rx.event
    async def answer(self, model): #, *args, **kwargs):
        model = self.llm_engine
        # Set the processing state to True.
        self.processing = True
        yield

        # Convert chat history to a list of dictionaries
        chat_history_dicts = []
        messages_history = []
        for chat_history_tuple in self.chat_history:
            chat_history_dicts.append(
                {"role": "user", "content": chat_history_tuple[0]}
            )
            chat_history_dicts.append(
                {"role": "assistant", "content": chat_history_tuple[1]}
            )
            chat_history_dicts.append(
                {"model": chat_history_tuple[2]}
            )
            chat_history_dicts.append(
                {"nb_input_tokens": chat_history_tuple[3]}
            )
            chat_history_dicts.append(
                {"nb_output_tokens": chat_history_tuple[4]}
            )
            # Build up current message on the basis of all previous messages
            messages_history.append(
                {"role": "user", "content": chat_history_tuple[0]}
            )
            messages_history.append(
                {"role": "assistant", "content": chat_history_tuple[1]}
            )

        self.chat_history.append((self.question, "", "", 0, 0))

        # Clear the question input.
        question = self.question
        self.question = ""
        # Yield here to clear the frontend input before continuing.
        yield

        messages_history.append({"role": "assistant", "content": question})

        # Ingest PDF text
        self.query_pdf()


        # Synchronous OpenAI call in an async handler
        def get_openai_response():
            response = client.chat.completions.create(
                model= model,
                messages=[
                {
                    "role": "user",
                    "content": f"{self.rag_input} All preceding content, if any, is PROMPT_CONTEXT. Use PROMPT_CONTEXT to help yourself answer user prompts. {messages_history}.",
                }
            ], 
            # max_tokens=150,
            temperature=0.0,
            top_p=0.1,
            # max_tokens=512,
            stream=False,
            )
            return response #.choices[0].message.content
        
        loop = asyncio.get_event_loop()
        raw_answer = await loop.run_in_executor(None, get_openai_response) # response.choices[0].message.content
        answer = raw_answer.choices[0].message.content
        # Extract other elements from the response
        query_engine = raw_answer.model
        self.query_engine = query_engine
        nb_input_tokens = raw_answer.usage.prompt_tokens
        self.nb_input_tokens = nb_input_tokens
        nb_output_tokens = raw_answer.usage.completion_tokens
        self.nb_output_tokens = nb_output_tokens


        for i in range(len(answer)):
            # Pause to show the streaming effect.
            await asyncio.sleep(0.01)
            # Add one letter at a time to the output.
            self.chat_history[-1] = (
                self.chat_history[-1][0],
                answer[: i + 1],
            )
            yield

        self.chat_history[-1] = (self.chat_history[-1][0], answer, query_engine, nb_input_tokens, nb_output_tokens)
        
        # Add to the answer as the chatbot responds.
        answer = ""
        yield

        # Ensure the final answer is added to chat history
        if answer:
            self.chat_history[-1] = (self.chat_history[-1][0], answer, query_engine, nb_input_tokens, nb_output_tokens)
            yield


        # Set the processing state to False.
        self.processing = False

        
    async def handle_key_down(self, key: str):
        if key == "Enter":
            async for t in self.answer():
                yield t

    @rx.event
    def clear_chat(self):
        # Reset the chat history and processing state
        self.chat_history = []
        self.processing = False
        yield

