import gradio as gr
import requests
import jwt
import os
from dotenv import load_dotenv
from chatbot_elastic import query_elasticsearch_raw
from gpt_razona_sobre import gpt_razona_sobre
load_dotenv()

BACKEND_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
USE_OPEN_ROUTER = os.getenv("USE_OPEN_ROUTER", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")

chat_history = [
    {
        "role": "system",
        "content": "Eres un asistente inteligente capaz de responder preguntas de forma precisa sobre hoteles, útil y amigable. Puedes interpretar preguntas en lenguaje natural y ofrecer respuestas basadas en información proporcionada por el sistema o general."
    }
]

# ---------------- BACKEND FUNCIONES ----------------
def login_and_fetch_users(username, password):
    try:
        response = requests.post(f"{BACKEND_URL}/login", data={"username": username, "password": password})
        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            decoded = jwt.decode(token, options={"verify_signature": False})
            is_admin = decoded.get("is_admin", False)
            users_table_data = get_users(token)
            formatted_table = [[u["id"], u["username"], "Admin" if u["is_admin"] else "Usuario", "✏️", "🗑️"] for u in users_table_data]
            return "", gr.update(visible=False), gr.update(visible=is_admin), gr.update(visible=not is_admin), token, formatted_table, users_table_data
        else:
            return "❌ Login inválido", gr.update(), gr.update(), gr.update(), "", [], []
    except Exception as e:
        return f"⚠️ Error conectando al servidor: {e}", gr.update(), gr.update(), gr.update(), "", [], []

def get_users(token):
    try:
        response = requests.get(f"{BACKEND_URL}/users", headers={"Authorization": f"Bearer {token}"})
        return response.json() if response.status_code == 200 else []
    except:
        return []

def create_user(username, password, is_admin, token):
    try:
        response = requests.post(f"{BACKEND_URL}/register", json={
            "username": username,
            "password": password,
            "is_admin": is_admin
        }, headers={"Authorization": f"Bearer {token}"})
        return "✅ Usuario creado" if response.status_code == 200 else "❌ Error creando"
    except Exception as e:
        return f"⚠️ Error: {e}"
    
    

def update_user(user_id, username, password, is_admin, token):
    payload = {"username": username, "is_admin": is_admin}
    if password:
        payload["password"] = password
    try:
        r = requests.put(f"{BACKEND_URL}/users/{user_id}", json=payload, headers={"Authorization": f"Bearer {token}"})
        return "✅ Usuario actualizado" if r.status_code == 200 else "❌ Error"
    except Exception as e:
        return f"⚠️ Error: {e}"

def delete_user(user_id, token):
    try:
        r = requests.delete(f"{BACKEND_URL}/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
        return "✅ Usuario eliminado" if r.status_code == 200 else "❌ No se pudo eliminar"
    except:
        return "⚠️ Error al eliminar"
def chat_response(message):
    if "hotel" in message.lower() or "alojamiento" in message.lower() or "reserva" in message.lower():
        docs = query_elasticsearch_raw(message, size=8)
        if not docs:
            return "<div class='chat-msg bot-msg'><span style='color:black; font-weight:bold;'>❌ No se encontraron hoteles relevantes.</span></div>", ""

        razonamiento = gpt_razona_sobre(docs, message)
        razonamiento_html = razonamiento.replace('\n', '<br>')

        # Buscar el hotel mencionado en la respuesta
        hotel_elegido = None
        for h in docs:
            if h.get("nombre", "").lower() in razonamiento.lower():
                hotel_elegido = h
                break

        coords_html = ""
        if hotel_elegido and hotel_elegido.get("coordenadas"):
            coords = hotel_elegido["coordenadas"]
            lat, lon = coords.get("lat"), coords.get("lon")
            if lat and lon:
                coords_html = f"""
                    <div style='margin-top:20px'>
                        <iframe
                            width="100%"
                            height="300"
                            frameborder="0"
                            scrolling="no"
                            marginheight="0"
                            marginwidth="0"
                            src="https://www.openstreetmap.org/export/embed.html?bbox={lon-0.01}%2C{lat-0.01}%2C{lon+0.01}%2C{lat+0.01}&layer=mapnik&marker={lat}%2C{lon}">
                        </iframe>
                        <small>
                            <a href="https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=15/{lat}/{lon}" target="_blank">Ver mapa más grande</a>
                        </small>
                    </div>
                """

        html = f"""
        <div class='chat-container'>
            <div class='chat-msg bot-msg'>
                <span style='color:black; font-weight:bold;'>{razonamiento_html}</span>
                {coords_html}
            </div>
        </div>
        """
        return html, ""

    # Fallback
    if not USE_OPEN_ROUTER or not OPENAI_API_KEY:
        return "<div class='chat-msg user-msg'><span style='color:black; font-weight:bold;'>⚠️ Configuración inválida. Revisa .env</span></div>", ""

    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "openai/gpt-3.5-turbo", "messages": chat_history + [{"role": "user", "content": message}]}

    try:
        response = requests.post(f"{OPENAI_BASE_URL}/chat/completions", json=payload, headers=headers)
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            chat_history.append({"role": "user", "content": message})
            chat_history.append({"role": "assistant", "content": reply})

            html = "<div class='chat-container'>"
            for turn in chat_history:
                role_class = "user-msg" if turn["role"] == "user" else "bot-msg"
                html += f"<div class='chat-msg {role_class}'><span style='color:black; font-weight:bold;'>{turn['content']}</span></div>"
            html += "</div>"
            return html, ""
        return f"<div class='chat-msg user-msg'><span style='color:black; font-weight:bold;'>❌ Error: {response.status_code} - {response.text}</span></div>", ""
    except Exception as e:
        return f"<div class='chat-msg user-msg'><span style='color:black; font-weight:bold;'>🚨 Error al conectar: {e}</span></div>", ""

# ---------------- INTERFAZ GRADIO ----------------
with gr.Blocks(css="""
               

.gradio-container {
    height: 100vh;
    background-color: #0e0e11; /* Muy importante para quitar el blanco lateral */
    display: flex;
    justify-content: center;
    align-items: center;
}

.login-box {
    background: #ffffff;
    width: 100%;
    max-width: 480px;
    padding: 3rem 2.5rem;
    border-radius: 20px;
    box-shadow: 0 15px 45px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease-in-out;
    animation: fadeIn 0.8s ease-in-out;
               
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.login-box:hover {
    transform: translateY(-4px);
}

.login-box h2 {
    font-size: 2rem;
    margin-bottom: 2rem;
    text-align: center;
    color: #1e3a8a;
    font-weight: 700;
}

.login-box .gr-textbox {
    width: 100%;
    padding: 1rem;
    border-radius: 12px;
    border: 1px solid #cbd5e1;
    font-size: 1rem;
    background: #f8fafc;
    margin-bottom: 1.5rem;
    transition: box-shadow 0.3s ease;
}

.login-box .gr-textbox:focus-within {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.login-box .gr-button {
    width: 100%;
    padding: 1rem;
    background: linear-gradient(to right, #3b82f6, #1d4ed8);
    color: white;
    font-size: 1rem;
    font-weight: 600;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    transition: background 0.3s ease, transform 0.2s ease;
}

.login-box .gr-button:hover {
    background: linear-gradient(to right, #2563eb, #1e40af);
    transform: scale(1.02);
}

.login-box .gr-button:active {
    transform: scale(0.98);
}

    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        background: #f5f5f5;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-family: sans-serif;
    }
    .chat-msg {
        margin: 0.5rem 0;
        padding: 0.7rem 1rem;
        border-radius: 12px;
        max-width: 80%;
        word-wrap: break-word;
        display: inline-block;
    }
    .user-msg {
        background: #dcf8c6;
        float: right;
        clear: both;
    }
    .bot-msg {
        background: #ffffff;
        border: 1px solid #ccc;
        float: left;
        clear: both;
    }
    .modal {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: #222;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 0 20px rgba(255, 0, 0, 0.5);
        max-width: 500px;
        margin: auto;
        z-index: 1000;
    }
""") as demo:
    gr.Markdown("# 🧠 Login y Panel de Administración / Chatbot")

    token_state = gr.State("")
    current_user_list = gr.State([])

    with gr.Group(visible=True, elem_classes=["login-box"]) as login_section:
        user_input = gr.Textbox(label="Usuario")
        pass_input = gr.Textbox(label="Contraseña", type="password")
        login_btn = gr.Button("Iniciar sesión")
        login_status = gr.Textbox(label="Estado", interactive=False)

    with gr.Group(visible=False) as admin_section:
        gr.Markdown("### 👑 Panel de Administración")
        users_table = gr.Dataframe(headers=["ID", "Usuario", "Rol", "✏️ EDITAR", "🗑️ BORRAR"], interactive=False, row_count=0)
        with gr.Row():
            new_user_btn = gr.Button("CREAR NUEVO USUARIO")
            logout_btn1 = gr.Button("CERRAR SESION")

    with gr.Group(visible=False, elem_classes=["modal"]) as edit_modal:
        gr.Markdown("### ✏️ Editar usuario")
        edit_id = gr.Textbox(label="ID", interactive=False)
        edit_username = gr.Textbox(label="Nombre")
        edit_password = gr.Textbox(label="Nueva contraseña", type="password")
        edit_admin = gr.Checkbox(label="¿Es admin?")
        edit_btn = gr.Button("Guardar cambios")
        cancel_edit = gr.Button("❌ Cancelar")
        edit_status = gr.Textbox(label="Resultado", interactive=False)

    with gr.Group(visible=False, elem_classes=["modal"]) as create_modal:
        gr.Markdown("### ➕ Crear nuevo usuario")
        create_username = gr.Textbox(label="Nombre")
        create_password = gr.Textbox(label="Contraseña", type="password")
        create_admin = gr.Checkbox(label="¿Es admin?")
        create_btn = gr.Button("Crear")
        cancel_create = gr.Button("❌ Cancelar")
        create_status = gr.Textbox(label="Resultado", interactive=False)

    with gr.Group(visible=False, elem_classes=["modal"]) as delete_modal:
        gr.Markdown("### ⚠️ Confirmar eliminación")
        confirm_text = gr.Textbox(interactive=False)
        confirm_user_id = gr.Textbox(visible=False)
        delete_accept = gr.Button("✅ Sí, eliminar")
        delete_cancel = gr.Button("❌ Cancelar")
        delete_status = gr.Textbox(label="Resultado", interactive=False)

    with gr.Group(visible=False) as user_section:
        gr.Markdown("### 💬 Chatbot")
        chat_html_box = gr.HTML(elem_id="chat-box")
        msg_input = gr.Textbox(label="Tu mensaje")
        send_btn = gr.Button("Enviar")
        logout_btn2 = gr.Button("Cerrar sesión")
    send_btn.click(fn=chat_response, inputs=[msg_input], outputs=[chat_html_box, msg_input])

    def handle_table_click(evt: gr.SelectData, token, current_users):
        if not current_users or not isinstance(current_users, list):
            return gr.update(visible=False), "", "", False, "", gr.update(visible=False), "", ""
        row, col = evt.index
        if row >= len(current_users):
            return gr.update(visible=False), "", "", False, "", gr.update(visible=False), "", ""
        selected = current_users[row]
        if col == 3:
            return gr.update(visible=True), selected["id"], selected["username"], "", selected["is_admin"], gr.update(visible=False), "", ""
        elif col == 4:
            return gr.update(visible=False), "", "", False, "", gr.update(visible=True), f"¿Eliminar a '{selected['username']}'?", selected["id"]
        return gr.update(visible=False), "", "", False, "", gr.update(visible=False), "", ""

    def handle_create(username, password, is_admin, token):
        msg = create_user(username, password, is_admin, token)
        return msg, gr.update(visible=False), [[u["id"], u["username"], "Admin" if u["is_admin"] else "Usuario", "✏️", "🗑️"] for u in get_users(token)]

    def handle_edit(uid, username, password, is_admin, token):
        msg = update_user(uid, username, password, is_admin, token)
        return msg, gr.update(visible=False), [[u["id"], u["username"], "Admin" if u["is_admin"] else "Usuario", "✏️", "🗑️"] for u in get_users(token)]

    def handle_delete(uid, token):
        msg = delete_user(uid, token)
        return msg, gr.update(visible=False), [[u["id"], u["username"], "Admin" if u["is_admin"] else "Usuario", "✏️", "🗑️"] for u in get_users(token)]

    login_btn.click(fn=login_and_fetch_users, inputs=[user_input, pass_input],
        outputs=[login_status, login_section, admin_section, user_section, token_state, users_table, current_user_list])

    users_table.select(fn=handle_table_click, inputs=[token_state, current_user_list],
        outputs=[edit_modal, edit_id, edit_username, edit_password, edit_admin, delete_modal, confirm_text, confirm_user_id])

    create_btn.click(fn=handle_create,
        inputs=[create_username, create_password, create_admin, token_state],
        outputs=[create_status, create_modal, users_table])

    edit_btn.click(fn=handle_edit,
        inputs=[edit_id, edit_username, edit_password, edit_admin, token_state],
        outputs=[edit_status, edit_modal, users_table])

    delete_accept.click(fn=handle_delete,
        inputs=[confirm_user_id, token_state],
        outputs=[delete_status, delete_modal, users_table])

    delete_cancel.click(fn=lambda: gr.update(visible=False), outputs=[delete_modal])

    new_user_btn.click(fn=lambda: gr.update(visible=True), outputs=[create_modal])
    cancel_create.click(fn=lambda: gr.update(visible=False), outputs=[create_modal])
    cancel_edit.click(fn=lambda: gr.update(visible=False), outputs=[edit_modal])

    logout_btn1.click(fn=lambda: ("Sesión cerrada", gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), ""),
        outputs=[login_status, login_section, admin_section, user_section, token_state])
    logout_btn2.click(fn=lambda: ("Sesión cerrada", gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), ""),
        outputs=[login_status, login_section, admin_section, user_section, token_state])



demo.launch()