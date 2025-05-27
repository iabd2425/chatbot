import gradio as gr
import os
import requests

API_URL = "http://localhost:8000"
USE_OPEN_ROUTER = os.getenv("USE_OPEN_ROUTER", "false").lower() == "true"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def chat_with_openrouter(message, history, token):
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
    payload = {
        "model": "mistralai/mixtral-8x7b",
        "messages": [{"role": "user", "content": message}]
    }
    r = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
    if r.status_code == 200:
        reply = r.json()["choices"][0]["message"]["content"]
        history.append((message, reply))
        return history
    else:
        return history + [(message, "Error")]

with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    token_input = gr.Textbox(label="Token")
    send = gr.Button("Send")

    def user_send(message, history, token):
        return chat_with_openrouter(message, history, token)

    send.click(user_send, inputs=[msg, chatbot, token_input], outputs=chatbot)

demo.launch()
