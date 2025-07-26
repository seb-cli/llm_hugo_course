import asyncio
from dotenv import load_dotenv
import fitz # PyMuPDF
import json
import os
import uuid

import httpx
import reflex as rx
from openai import OpenAI, AsyncOpenAI
from types import SimpleNamespace

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
    """Multiple file upload state."""

    # The documents to list
    rag_document: list[str] = []
    all_uploaded_files: list

    @rx.event
    async def handle_upload(
        self, files: list[rx.UploadFile]
    ):
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

    # @rx.event
    def update_uploaded_docs(self):
        self.all_uploaded_files = [f for f in os.listdir(rx.get_upload_dir())]

    @rx.event
    def cancel_upload(self):
        self.rag_document.clear()
        return rx.cancel_upload("upload1")
    
    @rx.event
    def clear_all_uploaded_files(self):
        for f in os.listdir(rx.get_upload_dir()):
            os.remove(f"{os.path.realpath(rx.get_upload_dir())}/{f}")
        return UploadState.cancel_upload



class State(ModelSelectionMixin, rx.State):
    """General App State."""
    rag_input: list[dict] = []
    query_engine: str
    nb_input_tokens: int

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

    # The current question being asked.
    question: str

    # Whether the app is processing a question.
    processing: bool = False

    # Keep track of the chat history as a list of (question, answer) tuples.
    chat_history: list[tuple[str, str]] = []

    user_id: str = str(uuid.uuid4())

    async def answer(self):
        # Set the processing state to True.
        self.processing = True
        yield

        # convert chat history to a list of dictionaries
        chat_history_dicts = []
        for chat_history_tuple in self.chat_history:
            chat_history_dicts.append(
                {"role": "user", "content": chat_history_tuple[0]}
            )
            chat_history_dicts.append(
                {"role": "assistant", "content": chat_history_tuple[1]}
            )

        self.chat_history.append((self.question, ""))

        # Clear the question input.
        question = self.question
        self.question = ""

        # Yield here to clear the frontend input before continuing.
        yield

        # client = httpx.AsyncClient()

        # call the agentic workflow
        # input_payload = {
        #     "chat_history_dicts": chat_history_dicts,
        #     "user_input": question,
        # }
        # input_headers = {
        #     "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
        #     "Content-Type": "application/json",
        # }

        # deployment_name = os.environ.get("DEPLOYMENT_NAME", "MyDeployment")
        # apiserver_url = "https://openrouter.ai/api/v1/chat/completions",
        # response = await client.post(
        #     f"{apiserver_url}",
        #     headers=input_headers,
        #     json={"input": json.dumps(input_payload)},
        #     timeout=60,
        # )
        # answer = response.text


        load_dotenv(".env")
        client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ.get("OPENROUTER_API_KEY"),
            )

        self.query_pdf()

        response = await client.chat.completions.create(
            model= self.llm_engine,
            messages=[
                {
                    "role": "user",
                    "content": f"{self.rag_input}. Consider all preceding content as PROMPT_CONTEXT. On the basis of PROMPT_CONTEXT, {question}",
                }
            ], 
        )

        answer = response.choices[0].message.content
        self.query_engine = response.model
        self.nb_input_tokens = response.usage.prompt_tokens


        for i in range(len(answer)):
            # Pause to show the streaming effect.
            await asyncio.sleep(0.01)
            # Add one letter at a time to the output.
            self.chat_history[-1] = (
                self.chat_history[-1][0],
                answer[: i + 1],
            )
            yield
        

        # Add to the answer as the chatbot responds.
        answer = ""
        yield

        # async for item in json.loads(json.dumps(serial_response), 
        #                              object_hook=lambda item: SimpleNamespace(**item)):
        
        # async for chunk in response:
        #     if not chunk.choices:
        #         continue
        #     delta = chunk.choices[0].delta
        #     if getattr(delta, "content", None) is None:
        #         break
        #     answer += delta.content
        #     self.chat_history[-1] = (self.chat_history[-1][0], answer)
        #     yield delta.content

        async def async_choices(response):
            for choice in response.choices[0]:
                if isinstance(choice, tuple):
                    choice = choice[0]
                if hasattr(choice, "delta"):
                    yield choice


        # async for choice in async_choices(response):
        #     delta = choice.delta
        #     if delta and delta.content:
        #         answer += delta.content
        #         self.chat_history[-1] = (self.chat_history[-1][0], answer)



        async for choice in async_choices(response):
            if hasattr(choice.delta, "content"):
                if choice.delta.content is None:
                    break
                answer += choice.delta.content
                self.chat_history[-1] = (self.chat_history[-1][0], answer)
                yield

        # Ensure the final answer is added to chat history
        if answer:
            self.chat_history[-1] = (self.chat_history[-1][0], answer)
            yield

        # Set the processing state to False.
        self.processing = False

    async def handle_key_down(self, key: str):
        if key == "Enter":
            async for t in self.answer():
                yield t

    def clear_chat(self):
        # Reset the chat history and processing state
        self.chat_history = []
        self.processing = False


