import gradio as gr
from api import login_user, get_users
from auth import save_token, get_token, clear_token

def handle_login(username, password):
    token = login_user(username, password)
    if token:
        save_token(token)
        return gr.update(visible=False), gr.update(visible=True), ""
    return gr.update(), gr.update(), "❌ Login fallido"

def handle_logout():
    clear_token()
    return gr.update(visible=True), gr.update(visible=False)

def render_admin_panel():
    token = get_token()
    users = get_users(token)
    if users:
        return "\n".join([f"{u['id']} - {u['username']} - admin: {u['is_admin']}" for u in users])
    return "❌ Error obteniendo usuarios"

with gr.Blocks() as demo:
    with gr.Group(visible=True) as login_section:
        gr.Markdown("# Login")
        user = gr.Textbox(label="Usuario")
        passwd = gr.Textbox(label="Contraseña", type="password")
        login_btn = gr.Button("Iniciar sesión")
        login_output = gr.Textbox(label="Estado", interactive=False)

    with gr.Group(visible=False) as panel_section:
        gr.Markdown("## Panel de Administración")
        users_box = gr.Textbox(lines=10, interactive=False)
        refresh_btn = gr.Button("Refrescar usuarios")
        logout_btn = gr.Button("Cerrar sesión")

    login_btn.click(handle_login, inputs=[user, passwd], outputs=[login_section, panel_section, login_output])
    refresh_btn.click(lambda: render_admin_panel(), outputs=users_box)
    logout_btn.click(handle_logout, outputs=[login_section, panel_section])

demo.launch()
