import streamlit as st
import os
import csv
from datetime import datetime
from supabase import create_client, Client

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

# Si el usuario no existe, lo crea automáticamente
if not user:
    supabase.table("Usuarios").insert({
        "email": email,
        "landing": 0,
        "ultimo_acceso": datetime.now().isoformat()
    }).execute()
    user = obtener_usuario(email)

# Si ya tiene 5 landings, bloqueo
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
    st.link_button("Ver App Web", url_app_web)
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
                st.image(os.path.join("images", p["img"]), width=160)
                st.caption(p["nombre"])
                st.write(p["desc"])
else:
    st.info("Agrega productos en la sección superior para verlos aquí.")

st.divider()
st.subheader("Información adicional")
for line in texto_bajo_productos.splitlines():
    if line.strip():
        st.write(line)
st.divider()

st.subheader("💬 Comentarios de usuarios")
for c in comentarios_ejemplo:
    st.info(c)

# -------------------
# CSS DE TARJETAS Y HERO
# -------------------
if plantilla == "Clásica":
    css_cards = """
    .card {background:#fff; border-radius:12px; box-shadow:0 4px 8px rgba(0,0,0,0.1); width:180px; padding:15px; text-align:center;}
    .card img {width:100%; height:auto;}
    .card h3, .card p {color: #111;}
    """
elif plantilla == "Moderna":
    css_cards = """
    .card {background:#fff; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.15); width:180px; padding:15px; text-align:center; transition: transform 0.3s, box-shadow 0.3s;}
    .card img {width:100%; height:auto;}
    .card h3, .card p {color: #111;}
    .card:hover {transform: translateY(-5px); box-shadow:0 8px 20px rgba(0,0,0,0.2);}
    """
else:
    css_cards = """
    .card {background:#fff; border-radius:8px; width:180px; padding:10px; text-align:center; border:1px solid #ddd;}
    .card img {width:100%; height:auto;}
    .card h3, .card p {color: #111;}
    """

# -------------------
# HTML FINAL
# -------------------
html_productos = "".join([f"<div class='card'><img src='images/{p['img']}'><h3>{p['nombre']}</h3><p>{p['desc']}</p></div>" for p in productos])
html_comentarios = "".join([f"<div class='comentario' style='color:{color_texto_comentarios}; background-color:#f9f9f9; padding:12px; border-radius:10px; margin:5px 0;'>{c}</div>" for c in comentarios_ejemplo])
logo_html = f'<img src="images/{logo_empresa}" width="100">' if logo_empresa != "(Sin logo)" else ""

html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{empresa} - {titulo}</title>
<style>
body {{font-family: Arial, sans-serif; background: {color_fondo}; color: {color_texto}; margin:0; padding:0;}}
h1,h2,h3 {{color:{color_texto};}}
p {{color:{color_texto}; font-size:16px;}}
img {{border-radius:10px;}}

.header {{
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 20px 40px;
  gap: 40px;
}}
.header .left {{flex: 1; text-align: left; padding-right: 20px;}}
.header .right {{flex: 0 0 480px; text-align: right;}}
.header .right img {{
  width: 100%;
  max-width: 500px;
  height: auto;
  object-fit: contain;
  display: block;
  border-radius: 12px;
  margin-top: 40px;
}}

.productos {{display:flex; flex-wrap:wrap; justify-content:center; gap:20px; margin:20px 0;}}
{css_cards}
.comentarios {{display:flex; flex-direction:column; align-items:center; gap:15px; margin:20px 0;}}
.btn {{display:inline-block; padding:12px 25px; margin-top:15px; background-color:#ff6600; color:#fff; border-radius:6px; text-decoration:none; font-weight:bold;}}
form {{display:flex; flex-direction:column; align-items:center; gap:10px; margin:20px 0;}}
form input, form textarea {{width:300px; padding:8px; border-radius:5px; border:1px solid #ccc;}}
form input[type="submit"] {{width:150px; background-color:#ff6600; color:#fff; border:none; cursor:pointer; font-weight:bold;}}
</style>
</head>
<body>
<div class="header">
  <div class="left">
    {logo_html}
    <h1>{titulo}</h1>
    <p>{descripcion}</p>
    <a href="{url_app_web}" target="_blank" class="btn">Ver App Web</a>
  </div>
  <div class="right">
    <img src="images/{imagen_hero}" alt="Hero">
  </div>
</div>

<h2 style="text-align:center;">Nuestros Productos</h2>
<div class="productos">{html_productos}</div>

<h3 style="text-align:center;">Información adicional</h3>
<p style="text-align:center;">{texto_bajo_productos.replace(chr(10), '<br>')}</p>

<h3 style="text-align:center;">Comentarios de usuarios</h3>
<div class="comentarios">{html_comentarios}</div>

<h3 style="text-align:center;">Formulario de contacto</h3>
<form action="mailto:{correo_destino}" method="post" enctype="text/plain">
<input type="text" name="Nombre" placeholder="Nombre completo" required>
<input type="email" name="Correo" placeholder="Correo electrónico" required>
<textarea name="Mensaje" placeholder="Mensaje" rows="4" required></textarea>
<input type="submit" value="Enviar">
</form>

<p style="text-align:center;"><a href="{url_app_web}" target="_blank" class="btn">Ver App Web</a></p>
<footer style="text-align:center; padding:20px; margin-top:40px; background-color:#f1f1f1; color:#555; font-size:14px;">
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
