import streamlit as st
import os
from datetime import datetime
from supabase import create_client, Client
import docx
import html

st.set_page_config(page_title="Generador de Landing Page", layout="wide")
st.title("🌐 Generador de Landing Page Profesional")

# --- Supabase ---
SUPABASE_URL = st.secrets["supabase"]["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["supabase"]["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Login ---
st.sidebar.header("👤 Autenticación de usuario")
email = st.sidebar.text_input("Ingresá tu correo electrónico para usar el asistente")

def obtener_usuario(email):
    if not email:
        return None
    resp = supabase.table("Usuarios").select("*").eq("email", email).execute()
    return resp.data[0] if resp.data else None

# 🟢 Corrección aplicada: validar email antes de llamar a Supabase
if not email:
    st.warning("✉️ Ingresa tu correo en la barra lateral para comenzar.")
    st.stop()

# Ahora sí: primera llamada a Supabase
user = obtener_usuario(email)

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

# --- Sidebar options ---
st.sidebar.header("⚙️ Configuración General")
usar_docx = st.sidebar.checkbox("📄 Cargar datos desde Plantilla.docx (Plantilla.docx en la carpeta)")

# --- Contenedor de datos ---
data_doc = {
    "titulo": "",
    "descripcion": "",
    "empresa": "",
    "url": "",
    "correo": "",
    "hero": "",
    "logo": "",
    "extra": ""
}

# --- Funciones ---
def texto_color(bg_hex):
    bg_hex = bg_hex.lstrip('#')
    r,g,b = int(bg_hex[0:2],16), int(bg_hex[2:4],16), int(bg_hex[4:6],16)
    return "#000" if (0.299*r + 0.587*g + 0.114*b) > 186 else "#fff"

def escape_html(text):
    return html.escape(text or "")

# --- Función para leer configuración y texto adicional del DOCX ---
def read_docx_confiable(path="Plantilla.docx"):
    doc = docx.Document(path)
    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    data = {}

    campos = {
        "Título principal:": "titulo",
        "Descripción principal:": "descripcion",
        "Nombre de la Empresa:": "empresa",
        "URL de la app web:": "url",
        "Correo de contacto:": "correo",
        "Imagen principal (nombre de archivo dentro de /images):": "hero",
        "Logo de la Empresa (nombre de archivo dentro de /images):": "logo"
    }

    for idx, ln in enumerate(lines):
        for k, v in campos.items():
            if k.lower() in ln.lower() and idx+1 < len(lines):
                data[v] = lines[idx+1].strip()

    # Texto adicional
    extra_idx = next((idx for idx, ln in enumerate(lines) if "texto adicional bajo los productos" in ln.lower()), None)
    data["extra"] = "\n".join(lines[extra_idx+1:]).strip() if extra_idx is not None else ""

    # Asegurar campos vacíos
    for key in ["titulo","descripcion","empresa","url","correo","hero","logo","extra"]:
        if key not in data:
            data[key] = ""

    return data

# --- Cargar DOCX ---
if usar_docx:
    if not os.path.exists("Plantilla.docx"):
        st.sidebar.error("No se encontró Plantilla.docx en la carpeta.")
    else:
        try:
            parsed = read_docx_confiable("Plantilla.docx")
            data_doc.update(parsed)
            st.sidebar.success("✅ Plantilla.docx cargada correctamente")
        except Exception as e:
            st.sidebar.error(f"❌ Error leyendo Plantilla.docx: {e}")

# --- Sidebar UI ---
titulo = st.sidebar.text_input("Título principal", data_doc["titulo"] or "")
descripcion = st.sidebar.text_area("Descripción principal", data_doc["descripcion"] or "")
empresa = st.sidebar.text_input("Nombre de la empresa", data_doc["empresa"] or "")
color_fondo = st.sidebar.color_picker("Color de fondo", "#f9f9f9")
url_app_web = st.sidebar.text_input("🌐 URL de tu App Web", data_doc["url"] or "")
correo_destino = st.sidebar.text_input("Correo de contacto HTML (para mailto:)", data_doc["correo"] or "")
color_texto = texto_color(color_fondo)
color_texto_comentarios = st.sidebar.color_picker("Color del texto de los comentarios", "#333333")

# --- Imágenes ---
if not os.path.exists("images"):
    os.mkdir("images")
imagenes = [i for i in os.listdir("images") if i.lower().endswith(("png","jpg","jpeg"))]
if not imagenes:
    st.warning("⚠️ No hay imágenes en 'images'.")
    st.stop()
imagen_hero = st.sidebar.selectbox("🖼️ Imagen principal (hero)", imagenes, index=imagenes.index(data_doc["hero"]) if data_doc.get("hero") in imagenes else 0)
logo_options = ["(Sin logo)"] + imagenes
logo_empresa = st.sidebar.selectbox("🏷️ Logo de la empresa (opcional)", logo_options, index=logo_options.index(data_doc["logo"]) if data_doc.get("logo") in logo_options else 0)

# --- Productos manuales ---
st.header("🛍️ Productos a mostrar")
cantidad = st.number_input("Cantidad de productos a ingresar", min_value=1, max_value=20, value=1, step=1)
productos = []

for i in range(cantidad):
    st.subheader(f"Producto {i+1}")
    nombre = st.text_input(f"Nombre del producto {i+1}", "", key=f"producto_{i}_nombre")
    desc = st.text_area(f"Descripción del producto {i+1}", "", key=f"producto_{i}_desc")
    img_default_index = 0
    img = st.selectbox(f"Imagen del producto {i+1}", imagenes, index=img_default_index, key=f"producto_{i}_img")
    productos.append({"nombre": nombre, "desc": desc, "img": img})

# --- Texto adicional ---
st.header("✏️ Texto adicional")
texto_bajo_productos = st.text_area("Texto adicional debajo de los productos", value=(data_doc.get("extra") or ""))

# --- Comentarios y FAQ ---
comentarios_ejemplo = [
    "Excelente contenido y muy útil para mi PyME.",
    "Los eBooks están muy bien explicados y prácticos.",
    "Recomendado para emprendedores tecnológicos."
]
faqs = [
    {"pregunta":"¿Qué es la Biblioteca Virtual?","respuesta":"Es una colección digital de eBooks de Tecnología."},
    {"pregunta":"¿Cómo accedo?","respuesta":"Desde cualquier dispositivo con Internet."},
    {"pregunta":"¿Se actualiza?","respuesta":"Sí, con nuevos contenidos periódicamente."}
]

# --- HTML final ---
html_productos = "".join([
    '<div class="product-card">'
    + (f'<img src="images/{escape_html(p["img"])}" alt="{escape_html(p["nombre"])}">' if p.get("img") else "")
    + f'<h3>{escape_html(p["nombre"])}</h3>'
    + f'<p>{escape_html(p["desc"]).replace(chr(10), "<br>")}</p>'
    + '</div>'
    for p in productos
])
html_comentarios = "".join([f'<div class="comment">{escape_html(c)}</div>' for c in comentarios_ejemplo])
html_faq = "".join([f'<div class="faq-item"><h4>{escape_html(fq["pregunta"])}</h4><p>{escape_html(fq["respuesta"]).replace(chr(10), "<br>")}</p></div>' for fq in faqs])
extra_html = escape_html(texto_bajo_productos or "").replace("\n","<br>")
html_contacto = f"""
<div class="contact-form">
    <form action="mailto:{correo_destino}" method="post" enctype="text/plain">
        <input type="text" name="Nombre" placeholder="Nombre completo" required>
        <input type="email" name="Correo" placeholder="Correo electrónico" required>
        <textarea name="Mensaje" placeholder="Mensaje" rows="4" required></textarea>
        <input type="submit" value="Enviar">
    </form>
</div>
"""

# --- Botón para visitar app web ---
boton_app_web = f"""
<button onclick="window.open('{url_app_web}','_blank')" style="
    background-color:#0078D4;
    color:white;
    border:none;
    padding:10px 20px;
    border-radius:8px;
    cursor:pointer;
    font-size:16px;
">
    Visitar App Web
</button>
"""

html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape_html(empresa)} - {escape_html(titulo)}</title>
<style>
body {{font-family: 'Segoe UI', Roboto, Arial, sans-serif; background:{color_fondo}; color:{color_texto}; margin:0; padding:0;}}
.header {{display:flex; justify-content:space-between; align-items:center; padding:40px 6%;}}
.hero-img img {{width:100%; max-width:400px; border-radius:12px;}}
.products {{display:flex; flex-wrap:wrap; gap:24px; justify-content:center; padding:40px 6%;}}
.product-card {{width:280px; padding:18px; border-radius:12px; background:{('#fff' if color_texto=='#000' else '#222')}; color:{color_texto};}}
.product-card img {{width:100%; height:160px; object-fit:contain; border-radius:8px;}}
.comments-container, .faq-container {{max-width:800px; margin:0 auto; padding:20px; text-align:center;}}
.comment {{background:#fff; padding:16px; border-radius:10px; margin:12px 0; color:{color_texto_comentarios}; display:inline-block; width:90%;}}
.faq-item h4 {{color:#0078D4;}}
.contact-form {{max-width:520px; margin:24px auto; padding:20px; background:#fff; border-radius:10px;}}
.contact-form input, .contact-form textarea {{width:100%; padding:10px; margin-bottom:12px; border:1px solid #ccc; border-radius:6px;}}
.contact-form input[type=submit] {{background:#0078D4; color:#fff; border:none; padding:10px 14px; border-radius:8px; cursor:pointer;}}
.extra-section {{padding:20px 6%; text-align:center;}}
</style>
</head>
<body>
<header class="header">
  <div>
    {f'<img src="images/{logo_empresa}" alt="Logo" style="width:120px;">' if logo_empresa != "(Sin logo)" else ""}
    <h1>{escape_html(titulo)}</h1>
    <p>{escape_html(descripcion)}</p>
    {boton_app_web}
  </div>
  <div class="hero-img">
    <img src="images/{imagen_hero}" alt="Hero">
  </div>
</header>

<section class="products">{html_productos}</section>
<section class="extra-section">{extra_html or "[Sin texto adicional]"}</section>
<section class="comments-container">{html_comentarios}</section>
<section class="faq-container">{html_faq}</section>
<section>{html_contacto}</section>

<footer style="padding:20px 6%; text-align:center;">
  © {datetime.now().year} {escape_html(empresa)} | Todos los derechos reservados.
</footer>
</body>
</html>
"""

# --- Descargar HTML ---
if st.download_button("⬇️ Descargar HTML", html_template.encode("utf-8"), "landing.html", "text/html"):
    nuevo_total = user["landing"] + 1
    supabase.table("Usuarios").update({"landing": nuevo_total, "ultimo_acceso": datetime.now().isoformat()}).eq("email", email).execute()
    st.success("✅ Landing generada correctamente.")
