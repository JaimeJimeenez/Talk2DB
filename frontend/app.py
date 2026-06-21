import os

import gradio as gr

from api.api import completion

APP_TITLE = os.getenv("APP_TITLE", "Talk2DB")

if __name__ == "__main__":
    gr.ChatInterface(
        fn=completion,
        title=APP_TITLE,
    ).launch(
        server_name=os.getenv("GRADIO_SERVER_NAME", "0.0.0.0"),
        server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860")),
    )
