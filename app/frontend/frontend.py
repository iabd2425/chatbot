import re
import gradio as gr
import requests
from jose import jwt 
import os
from dotenv import load_dotenv
from styles import CSS
from config import SECRET_KEY
from api import login_user, get_users, create_user, update_user, delete_user, chat_with_bot

chat_history = [
]

# ---------------- BACKEND FUNCIONES ----------------
def login_and_fetch_users(username, password):
    try:
        response = login_user(username, password)
        if response is not None:                
            token = response["access_token"]
            decoded = jwt.decode(token, key={SECRET_KEY}, options={"verify_signature": False})
            is_admin = decoded.get("is_admin", False)
            users_table_data = get_users(token)
            formatted_table = [[u["id"], u["username"], "Admin" if u["is_admin"] else "Usuario", "✏️", "🗑️"] for u in users_table_data]
            return "", gr.update(visible=False), gr.update(visible=is_admin), gr.update(visible=not is_admin), token, formatted_table, users_table_data, "", ""
        else:
            return "❌ Login inválido", gr.update(), gr.update(), gr.update(), "", [], []
    except Exception as e:
        return f"⚠️ Error conectando al servidor: {e}", gr.update(), gr.update(), gr.update(), "", [], []

def user_query(message, chat_history):
    if not message or not message.strip():
        return "", chat_history
    else:
        chat_history.append({"role": "user", "content": message})
        return message, chat_history


def reemplazar_nombres_por_urls(mensaje: str, dataset_hoteles: list) -> str:
    for hotel in dataset_hoteles:
        nombre = re.escape(hotel["nombre"])
        url = hotel.get("url", "")
        if url:
            # Reemplaza el nombre por un enlace Markdown
            mensaje = re.sub(rf'\b{nombre}\b', f"[{hotel['nombre']}]({url})", mensaje, count=1)
        location = hotel.get("coordenadas", {})
        if location and len(dataset_hoteles) == 1:
            iframe = generar_iframe_mapa(location)
            mensaje += iframe 
    return mensaje

def generar_iframe_mapa(location: dict) -> str:
    try:
        lat = float(location["lat"])
        lon = float(location["lon"])
        bbox = f"{lon-0.01:.6f}%2C{lat-0.01:.6f}%2C{lon+0.01:.6f}%2C{lat+0.01:.6f}"
        marker = f"{lat}%2C{lon}"
        src = f"https://www.openstreetmap.org/export/embed.html?bbox={bbox}&layer=mapnik&marker={marker}"
        return (
            f'<iframe width="100%" height="200" frameborder="1" scrolling="no" '
            f'marginheight="0" marginwidth="0" src="{src}"></iframe>'
        )
    except (KeyError, TypeError, ValueError):
        return ""
    
def chat_response(message, chat_history, token):    
    if "hotel" in message.lower() or "alojamiento" in message.lower() or "reserva" in message.lower():
        respuesta = chat_with_bot(message, token)
        reply = respuesta["respuesta"]
        ds = respuesta["resultados"]
        reply = reemplazar_nombres_por_urls(reply, ds)        
        chat_history.append({"role": "assistant", "content": reply})
    else:
        chat_history.append({"role": "assistant", "content": "Lo siento, no puedo ayudarte con eso."})
        html = "<div class='chat-container'>"
        for turn in chat_history:
            role_class = "user-msg" if turn["role"] == "user" else "bot-msg"
            html += f"<div class='chat-msg {role_class}'><span style='color:black; font-weight:bold;'>{turn['content']}</span></div>"
            html += "</div>"
    return chat_history, ""    
        #return f"<div class='chat-msg user-msg'><span style='color:black; font-weight:bold;'>❌ Error: {response.status_code} - {response.text}</span></div>", ""


# ---------------- INTERFAZ GRADIO ----------------
with gr.Blocks(css=CSS) as chatbot:
    
    with gr.Row(elem_id="header-row", equal_height=True):
        with gr.Column(scale=0, min_width=80, elem_id="logo-col"):
            gr.Image(value="app/frontend/assets/logo.png", show_label=False, show_download_button=False, show_fullscreen_button=False, elem_id="logo-image")
        with gr.Column(scale=1, elem_id="text-col"):
            gr.Markdown("<h3 style='color:#1d71b8;'>Chatbot sobre hoteles andaluces de Booking.com</h3>", elem_id="title-text")

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
        with gr.Row():
            gr.Markdown("### 💬 Chatbot", elem_id="chat-title")
            logout_btn2 = gr.Button("Cerrar sesión")
        chat_html_box = gr.Chatbot(elem_id="chat-box",type="messages", sanitize_html=False, height="70vh", show_label=False)
        #chat_html_box = gr.HTML(elem_id="chat-box")
        msg_input = gr.Textbox(label="Tu pregunta")
        send_btn = gr.Button("Enviar")       
        
    
    msg_input.submit(fn=user_query, 
                     inputs=[msg_input, chat_html_box], 
                     outputs=[msg_input, chat_html_box],queue=False).then(fn=chat_response, 
                                                              inputs=[msg_input, chat_html_box, token_state], 
                                                              outputs=[chat_html_box, msg_input])

    send_btn.click(fn=user_query, 
                     inputs=[msg_input, chat_html_box], 
                     outputs=[msg_input, chat_html_box],queue=False).then(fn=chat_response, 
                                                              inputs=[msg_input, chat_html_box, token_state], 
                                                              outputs=[chat_html_box, msg_input])

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
        outputs=[login_status, login_section, admin_section, user_section, token_state, users_table, current_user_list, user_input, pass_input])

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
    logout_btn2.click(fn=lambda: (chat_history.clear(),
                                 "Sesión cerrada",
                                 gr.update(visible=True),
                                 gr.update(visible=False),
                                 gr.update(visible=False),
                                 "",  
                                 gr.update(value=[])
                                )[1:],  # ignoramos el resultado de chat_history.clear()
                                outputs=[login_status, login_section, admin_section, user_section,token_state, chat_html_box]
                     )



chatbot.launch(share=True, server_port=8080)