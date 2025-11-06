import streamlit as st
import os
from datetime import datetime
from supabase import create_client, Client
from openai import OpenAI
import json

# -------------------
# CONFIGURACIÓN
# -------------------
st.set_page_config(page_title="Generador de Landing Page", layout="wide")
st.title("🌐 Generador de Landing Page Profesional")

# -------------------
# CONEXIÓN A SUPABASE
# -------------------
SUPABASE_URL = st.secrets["supabase"]["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["supabase"]["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------
# LOGIN SIMPLE POR EMAIL
# -------------------
st.sidebar.header("👤 Autenticación de usuario")
email = st.sidebar.text_input("Ingresá tu correo electrónico para usar el asistente")

def obtener_usuario(email):
    if not email:
        return None
    user_resp = supabase.table("Usuarios").select("*").eq("email", email).execute()
    return user_resp.data[0] if user_resp.data else None

user = obtener_usuario(email)

if not email:
    st.warning("✉️ Ingresa tu correo en la barra lateral para comenzar.")
    st.stop()

if not user:
    supabase.table("Usuarios").insert({
        "email": email,
        "landing": 0,
        "ultimo_acceso": datetime.now().isoformat()
    }).execute()
    user = obtener_usuario(email)

if user["landing"] >= 5:
    st.error("🚫 Has alcanzado el límite máximo de 5 landings.")
    st.stop()

# -------------------
# CONFIGURACIÓN GENERAL
# -------------------
st.sidebar.header("⚙️ Configuración General")

titulo = st.sidebar.text_input("Título principal", "Academia Gestión - eBooks de Tecnología")
descripcion = st.sidebar.text_area("Descripción principal", "Desarrollamos herramientas digitales para potenciar tu negocio y conectar con tus clientes.")
empresa = st.sidebar.text_input("Nombre de la empresa", "Academia Gestión")
color_fondo = st.sidebar.color_picker("Color de fondo", "#f9f9f9")
url_app_web = st.sidebar.text_input("🌐 URL de tu App Web", "https://miappweb.com")
correo_destino = st.sidebar.text_input("Correo de contacto HTML (para mailto:)", "tuemail@dominio.com")

plantilla = st.sidebar.selectbox(
    "Elige una plantilla de landing",
    ["Clásica", "Moderna", "Minimalista"]
)

# -------------------
# FUNCIONES DE COLOR
# -------------------
def texto_color(bg_hex):
    bg_hex = bg_hex.lstrip('#')
    r, g, b = int(bg_hex[0:2], 16), int(bg_hex[2:4], 16), int(bg_hex[4:6], 16)
    luminosidad = 0.299*r + 0.587*g + 0.114*b
    return "#000" if luminosidad > 186 else "#fff"

color_texto = texto_color(color_fondo)
color_texto_comentarios = st.sidebar.color_picker("Color del texto de los comentarios", "#333333")

# -------------------
# IMÁGENES
# -------------------
if not os.path.exists("images"):
    os.mkdir("images")
    st.warning("Se creó la carpeta 'images'. Agrega imágenes y recarga la app.")

imagenes = [img for img in os.listdir("images") if img.lower().endswith((".png", ".jpg", ".jpeg"))]
if not imagenes:
    st.warning("⚠️ No hay imágenes en la carpeta 'images'. Agrega al menos una .jpg o .png.")
    st.stop()

imagen_hero = st.sidebar.selectbox("🖼️ Imagen principal (hero)", imagenes, index=0)
logo_empresa = st.sidebar.selectbox("🏷️ Logo de la empresa (opcional)", ["(Sin logo)"] + imagenes, index=1 if len(imagenes) > 1 else 0)

# -------------------
# PRODUCTOS
# -------------------
st.header("🛍️ Productos a mostrar")
cantidad_productos = st.number_input("Cantidad de productos", 1, 10, 2)
productos = []
for i in range(int(cantidad_productos)):
    st.subheader(f"Producto {i+1}")
    nombre = st.text_input(f"Nombre del producto {i+1}", key=f"nombre_{i}")
    desc = st.text_area(f"Descripción del producto {i+1}", key=f"desc_{i}")
    img = st.selectbox(f"Imagen del producto {i+1}", imagenes, key=f"img_{i}")
    if nombre.strip() and desc.strip():
        productos.append({"nombre": nombre, "desc": desc, "img": img})

# -------------------
# TEXTO ADICIONAL
# -------------------
st.header("✏️ Texto adicional")
texto_bajo_productos = st.text_area(
    "Texto adicional debajo de los productos",
    "Instalá la web app de manera GRATUITA (no necesitás Google Play ni App Store), en tres simples pasos:\n\n"
    "1️⃣ Abri la app con Google Chrome.\n"
    "2️⃣ Tocá los tres puntitos arriba a la derecha.\n"
    "3️⃣ Seleccioná 'Añadir a la pantalla de inicio' ¡y listo!\n\n"
    "Contáctanos hoy mismo para conocer más."
)

# -------------------
# FAQ GENERADAS POR IA
# -------------------
st.header("🤖 Preguntas Frecuentes generadas por IA")
try:
    client = OpenAI(api_key=st.secrets["openai"]["api_key"])
    prompt = f"""
    Genera tres preguntas y respuestas breves tipo FAQ en español sobre el siguiente tema:
    Título: {titulo}
    Descripción: {descripcion}
    Devuelve una lista JSON con 'pregunta' y 'respuesta'.
    """
    faq_response = client.responses.create(model="gpt-4.1-mini", input=prompt)
    faq_text = faq_response.output[0].content[0].text
    faqs = json.loads(faq_text)
except Exception:
    faqs = [
        {"pregunta": "¿Qué es la Biblioteca Virtual?", "respuesta": "Es una colección digital de recursos y herramientas creadas por inteligencia artificial."},
        {"pregunta": "¿Cómo accedo a los contenidos?", "respuesta": "Podés ingresar desde cualquier dispositivo, sin necesidad de instalar nada."},
        {"pregunta": "¿El contenido se actualiza automáticamente?", "respuesta": "Sí, la IA añade nuevos recursos y guías en función de las tendencias del mercado."}
    ]

# -------------------
# COMENTARIOS
# -------------------
comentarios_ejemplo = [
    "Excelente contenido y muy útil para mi PyME.",
    "Los eBooks están muy bien explicados y prácticos.",
    "Recomendado para emprendedores tecnológicos."
]

# -------------------
# PREVISUALIZACIÓN
# -------------------
st.header("🔎 Vista previa directa")

col1, col2 = st.columns([2, 1])
with col1:
    if logo_empresa != "(Sin logo)":
        st.image(os.path.join("images", logo_empresa), width=100)
    st.subheader(titulo)
    st.write(descripcion)
    st.markdown(
        f'<a href="{url_app_web}" target="_blank">'
        f'<button style="background-color:#0078D4;color:white;border:none;'
        f'padding:10px 18px;border-radius:6px;cursor:pointer;">Visitar App Web</button></a>',
        unsafe_allow_html=True
    )
with col2:
    st.image(os.path.join("images", imagen_hero), use_container_width=True)

st.divider()
st.subheader("Nuestros Productos")
if productos:
    filas = [productos[i:i+3] for i in range(0, len(productos), 3)]
    for fila in filas:
        cols = st.columns(len(fila))
        for i, p in enumerate(fila):
            with cols[i]:
                st.image(os.path.join("images", p["img"]), width=220)
                st.caption(p["nombre"])
                st.write(p["desc"])
else:
    st.info("Agrega productos en la sección superior para verlos aquí.")

st.divider()
st.subheader("💬 Comentarios de usuarios")
for c in comentarios_ejemplo:
    st.info(c)

st.divider()
st.subheader("📚 Preguntas Frecuentes – Biblioteca Virtual")
for f in faqs:
    st.markdown(f"**{f['pregunta']}**\n\n{f['respuesta']}")

# -------------------
# HTML FINAL (TARJETAS ALINEADAS Y AJUSTADAS)
# -------------------
html_productos = "".join([
    f"<div class='product-card'><img src='images/{p['img']}' alt='{p['nombre']}'><h3>{p['nombre']}</h3><p>{p['desc']}</p></div>"
    for p in productos
])
html_comentarios = "".join([f"<div class='comment'><p>“{c}”</p></div>" for c in comentarios_ejemplo])
html_faq = "".join([f"<div class='faq-item'><h4>{f['pregunta']}</h4><p>{f['respuesta']}</p></div>" for f in faqs])

html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{empresa} - {titulo}</title>
<style>
body {{
  font-family: 'Segoe UI', Roboto, Arial, sans-serif;
  background: {color_fondo};
  color: {color_texto};
  margin: 0;
  padding: 0;
  line-height: 1.6;
}}

header {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  padding: 60px 8%;
}}

header .text-content {{
  flex: 1;
  min-width: 280px;
}}

header h1 {{
  font-size: 2.4rem;
  margin-bottom: 10px;
}}

header p {{
  font-size: 1.1rem;
  max-width: 500px;
  margin-bottom: 20px;
}}

.hero-img {{
  flex: 1;
  text-align: center;
}}

.hero-img img {{
  width: 100%;
  max-width: 400px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}}

.btn-primary {{
  background-color: #0078D4;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  display: inline-block;
  transition: all 0.2s ease;
}}

.btn-primary:hover {{
  background-color: #005fa3;
}}

.section {{
  padding: 60px 8%;
  text-align: center;
}}

.products {{
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 30px;
  margin-top: 40px;
}}

.product-card {{
  background: {("#fff" if color_texto == "#000" else "#222")};
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 14px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  width: 280px;
  min-height: 380px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 20px;
  text-align: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}}

.product-card:hover {{
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.15);
}}

.product-card img {{
  width: 100%;
  max-width: 260px;
  max-height: 200px;
  height: auto;
  object-fit: contain;
  border-radius: 10px;
  margin-bottom: 12px;
  display: block;
  margin-left: auto;
  margin-right: auto;
}}

.product-card h3 {{
  color: {color_texto};
  margin: 10px 0 6px 0;
}}

.product-card p {{
  color: {color_texto};
  font-size: 15px;
  line-height: 1.5;
}}

.comments {{
  max-width: 800px;
  margin: 0 auto;
}}

.comment {{
  background: #ffffffd9;
  border-radius: 12px;
  box-shadow: 0 3px 8px rgba(0,0,0,0.1);
  margin: 15px 0;
  padding: 20px;
  font-style: italic;
  color: {color_texto_comentarios};
}}

form {{
  max-width: 420px;
  margin: 40px auto;
  background: #fff;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}}

form input, form textarea {{
  width: 100%;
  margin-bottom: 10px;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ccc;
}}

form input[type="submit"] {{
  background-color: #0078D4;
  color: #fff;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
}}

form input[type="submit"]:hover {{
  background-color: #005fa3;
}}

.faq {{
  max-width: 800px;
  margin: 40px auto;
  background: {("#fff" if color_texto == "#000" else "#222")};
  padding: 30px;
  border-radius: 14px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.08);
  text-align: left;
}}

.faq-item h4 {{
  color: #0078D4;
  margin-bottom: 5px;
  font-weight: 600;
}}

.faq-item p {{
  color: {color_texto};
  margin: 0 0 15px 0;
  line-height: 1.6;
}}

footer {{
  background: #f1f1f1;
  padding: 20px;
  text-align: center;
  color: #555;
  font-size: 0.9rem;
  margin-top: 60px;
}}
</style>
</head>
<body>

<header>
  <div class="text-content">
    {f'<img src="images/{logo_empresa}" alt="Logo" style="width:120px;margin-bottom:20px;">' if logo_empresa != "(Sin logo)" else ""}
    <h1>{titulo}</h1>
    <p>{descripcion}</p>
    <a href="{url_app_web}" target="_blank" class="btn-primary">Visitar App Web</a>
  </div>
  <div class="hero-img">
    <img src="images/{imagen_hero}" alt="Hero">
  </div>
</header>

<section class="section">
  <h2>Nuestros Productos</h2>
  <div class="products">{html_productos}</div>
</section>

<section class="section">
  <h3>💬 Comentarios de usuarios</h3>
  <div class="comments">{html_comentarios}</div>
</section>

<section class="section">
  <h3>Formulario de contacto</h3>
  <form action="mailto:{correo_destino}" method="post" enctype="text/plain">
    <input type="text" name="Nombre" placeholder="Nombre completo" required>
    <input type="email" name="Correo" placeholder="Correo electrónico" required>
    <textarea name="Mensaje" placeholder="Mensaje" rows="4" required></textarea>
    <input type="submit" value="Enviar">
  </form>
</section>

<section class="section">
  <h3>📚 Preguntas Frecuentes – Biblioteca Virtual</h3>
  <div class="faq">{html_faq}</div>
</section>

<footer>
  © {datetime.now().year} {empresa} | Todos los derechos reservados.
</footer>

</body>
</html>
"""

# -------------------
# DESCARGAR Y ACTUALIZAR SUPABASE
# -------------------
if st.download_button("⬇️ Descargar HTML", html_template.encode("utf-8"), "landing.html", "text/html"):
    nuevo_total = user["landing"] + 1
    supabase.table("Usuarios").update({
        "landing": nuevo_total,
        "ultimo_acceso": datetime.now().isoformat()
    }).eq("email", email).execute()
    st.success(f"✅ Landing generada correctamente. Ahora tienes {nuevo_total} landing(s) creadas.")
