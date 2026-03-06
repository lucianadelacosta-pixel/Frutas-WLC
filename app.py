# -*- coding: utf-8 -*-
# FRUTAS WC - App de pedidos con PDF + estados + envío por email
# Autoría: personalizada para Luciana - División Logística
# Requisitos: streamlit, reportlab
# -------------------------------------------------------------
# SMTP: configurar en .streamlit/secrets.toml (ver README arriba)

import streamlit as st
import pandas as pd
import re, uuid, smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta, time
from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm

# =========================
# 0) CONFIG INICIAL & CSS
# =========================
st.set_page_config(page_title="FRUTAS WC", layout="wide", initial_sidebar_state="collapsed")

CUSTOM_CSS = """
<style>
[data-testid="stSidebar"] {display: none;}
.stApp {
    background-size: cover;
    background-position: center bottom;
    background-attachment: fixed;
}
.main .block-container {
    background-color: rgba(255, 255, 255, 0.96);
    border-radius: 15px; padding: 30px; max-width: 980px;
}
.wa-float {
    position: fixed; bottom: 20px; right: 20px;
    background-color: #25d366; color: white; border-radius: 50px;
    padding: 12px 20px; display: flex; align-items: center; gap: 10px;
    text-decoration: none; z-index: 100; font-weight: bold;
}
.stButton>button { border-radius: 8px; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =========================
# 1) STATE & HELPERS
# =========================
def init_state():
    if "nav" not in st.session_state: st.session_state.nav = "Inicio"
    if "rol" not in st.session_state: st.session_state.rol = "Cliente"
    if "lista" not in st.session_state: st.session_state.lista = []
    if "ultimo_pedido" not in st.session_state: st.session_state.ultimo_pedido = None
    if "pedidos" not in st.session_state: st.session_state.pedidos = {}  # id -> pedido

    # Catálogo en el orden de tu plantilla (dos columnas fijas del PDF)
    if "catalogo_left" not in st.session_state:
        st.session_state.catalogo_left = [
            "Acelga","Achicoria","Ajo","Alcaucil","Ananá","Apio","Arándanos","Banana","Batata","Berenjena",
            "Brócoli","Calabacín","Calabaza","Cebolla","Cerezas","Champiñón","Chaucha","Choclo","Ciruela","Coliflor",
            "Durazno","Espárragos","Espinaca","Frutilla","Kiwi","Lechuga","Lechuguin","Limón","Mandarina","Manzana",
            "Manzana (V)","Melón"
        ]
    if "catalogo_right" not in st.session_state:
        st.session_state.catalogo_right = [
            "Naranja","Naranja (O)","Palta","Papa","Papa (Bolsa)","Pepino","Pera","Pimiento","Pomelo","Puerro",
            "Remolacha","Repollo","Rúcula","Sandia","Tomate (Cherry)","Tomate (P)","Tomate (R)","Uva","Verdeo","Zanahoria",
            "Zapallito","Zapallo","Zapallo (N)","Zuchini","Oliva","Miel","Huevos","Carbón","Perejil","Bandejas"
        ]
    if "productos_todos" not in st.session_state:
        st.session_state.productos_todos = st.session_state.catalogo_left + st.session_state.catalogo_right

def normalizar_texto(s: str) -> str:
    return (s or "").strip().upper()

def new_order_id() -> str:
    return uuid.uuid4().hex[:8].upper()

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
def es_email_valido(email: str) -> bool:
    if not email: return False
    return bool(EMAIL_REGEX.match(email.strip()))

def agregar_item(descripcion: str, cant: float, kg: float, tipo: str):
    """Agrega o acumula un item por Descripción+Tipo."""
    if not descripcion: return
    if (cant or 0) <= 0 and (kg or 0.0) <= 0: return

    descripcion = normalizar_texto(descripcion)
    tipo = normalizar_texto(tipo)

    # acumular si ya existe
    for row in st.session_state.lista:
        if row["Descripción"] == descripcion and row["Tipo"] == tipo:
            row["Cant."] = int(row.get("Cant.", 0)) + int(cant or 0)
            row["Kg."] = float(row.get("Kg.", 0.0)) + float(kg or 0.0)
            return

    st.session_state.lista.append({
        "Descripción": descripcion,
        "Cant.": int(cant or 0),
        "Kg.": float(kg or 0.0),
        "Tipo": tipo
    })

def totals(df: pd.DataFrame):
    if df.empty: return 0, 0.0
    return int(df["Cant."].sum()), float(df["Kg."].sum())

def enviar_email_pdf(destinatario: str, asunto: str, cuerpo_txt: str, nombre_pdf: str, pdf_bytes: bytes) -> tuple[bool, str]:
    """
    Envía email con PDF adjunto usando SMTP definido en st.secrets.
    secrets.toml:
      SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM
    """
    try:
        host = st.secrets.get("SMTP_HOST", "")
        port = int(st.secrets.get("SMTP_PORT", 587))
        user = st.secrets.get("SMTP_USER", "")
        password = st.secrets.get("SMTP_PASS", "")
        sender = st.secrets.get("SMTP_FROM", user)

        if not all([host, port, user, password, sender]):
            return False, "SMTP no configurado en st.secrets."

        msg = EmailMessage()
        msg["Subject"] = asunto
        msg["From"] = sender
        msg["To"] = destinatario
        msg.set_content(cuerpo_txt)

        msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename=nombre_pdf)

        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)

        return True, "Email enviado."
    except Exception as e:
        return False, f"Fallo al enviar email: {e}"

# =========================
# 2) PDF NOTA DE PEDIDO (plantilla de Excel)
# =========================
PRODUCTOS_COL_IZQ = [
    "Acelga","Achicoria","Ajo","Alcaucil","Ananá","Apio","Arándanos","Banana","Batata","Berenjena",
    "Brócoli","Calabacín","Calabaza","Cebolla","Cerezas","Champiñón","Chaucha","Choclo","Ciruela","Coliflor",
    "Durazno","Espárragos","Espinaca","Frutilla","Kiwi","Lechuga","Lechuguin","Limón","Mandarina","Manzana",
    "Manzana (V)","Melón"
]
PRODUCTOS_COL_DER = [
    "Naranja","Naranja (O)","Palta","Papa","Papa (Bolsa)","Pepino","Pera","Pimiento","Pomelo","Puerro",
    "Remolacha","Repollo","Rúcula","Sandia","Tomate (Cherry)","Tomate (P)","Tomate (R)","Uva","Verdeo","Zanahoria",
    "Zapallito","Zapallo","Zapallo (N)","Zuchini","Oliva","Miel","Huevos","Carbón","Perejil","Bandejas"
]

def _fmt_num(n, dec=2):
    try:
        v = float(n)
    except Exception:
        return ""
    return f"{v:.{dec}f}"

def generar_pdf_wc(datos_pedido):
    """
    datos_pedido:
      {
        "Cliente": str,
        "Domicilio": str,
        "Fecha": "dd/mm/YYYY",
        "Detalle": [ {"Descripción": str, "Cant.": int|float, "Kg.": float, "Importe": float (opcional)} ]
      }
    """
    buf = BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    margin_x = 15 * mm
    margin_y = 12 * mm

    # Encabezado
    p.setFont("Helvetica-Bold", 16)
    p.drawString(margin_x, h - margin_y - 10, "FRUTAS Y VERDURAS WC")
    p.setFont("Helvetica-Bold", 13)
    p.drawString(margin_x, h - margin_y - 28, "NOTA DE PEDIDO")

    p.setFont("Helvetica", 10)
    p.drawString(margin_x, h - margin_y - 44, "Contacto: 351 6351605")
    p.drawString(margin_x + 150, h - margin_y - 44, "Correo: frutasyverduraswc@gmail.com")

    # Fecha DIA/MES/AÑO
    try:
        dd, mm_, yy = datos_pedido.get("Fecha","").split("/")
