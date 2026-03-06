import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm

# =========================
# 1) CONFIG INICIAL & CSS
# =========================
st.set_page_config(page_title="FRUTAS WC", layout="wide", initial_sidebar_state="collapsed")

CUSTOM_CSS = """
<style>
[data-testid="stSidebar"] {display: none;}
.stApp {
    background-image: url("app/static/fondo.jpg");
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
# 2) STATE & HELPERS
# =========================
def init_state():
    if "nav" not in st.session_state: st.session_state.nav = "Inicio"
    if "rol" not in st.session_state: st.session_state.rol = "Cliente"
    if "lista" not in st.session_state: st.session_state.lista = []
    if "productos" not in st.session_state:
        st.session_state.productos = [
            "Acelga", "Anco", "Banana", "Cebolla", "Huevos", "Papa", "Tomate"
        ]
    if "ultimo_pedido" not in st.session_state: st.session_state.ultimo_pedido = None

def normalizar_texto(s: str) -> str:
    return (s or "").strip().upper()

def agregar_item(descripcion: str, cant: int, kg: float, tipo: str):
    """Agrega o acumula un item (si misma desc y tipo)."""
    if not descripcion:
        return
    if cant <= 0 and kg <= 0:
        return
    descripcion = normalizar_texto(descripcion)
    tipo = normalizar_texto(tipo)

    # Buscar si ya existe mismo item/tipo y acumular
    for row in st.session_state.lista:
        if row["Descripción"] == descripcion and row["Tipo"] == tipo:
            row["Cant."] = int(row.get("Cant.", 0)) + int(cant)
            row["Kg."] = float(row.get("Kg.", 0.0)) + float(kg)
            break
    else:
        st.session_state.lista.append({
            "Descripción": descripcion,
            "Cant.": int(cant),
            "Kg.": float(kg),
            "Tipo": tipo
        })

def totals(df: pd.DataFrame):
    if df.empty:
        return 0, 0.0
    return int(df["Cant."].sum()), float(df["Kg."].sum())

def format_phone_message(cliente: str, fecha: str, horario: str, df: pd.DataFrame) -> str:
    """Construye texto para WhatsApp."""
    lines = [
        f"Hola! Soy {cliente}. Quiero confirmar mi pedido:",
        f"Entrega: {fecha} ({horario})",
        "",
        "Detalle:"
    ]
    for _, r in df.iterrows():
        lines.append(f"- {r['Descripción']} | Bultos: {int(r['Cant.'])} | Kg: {r['Kg.']:.2f} | {r['Tipo']}")
    c_tot, k_tot = totals(df)
    lines += ["", f"Totales → Bultos: {c_tot}  |  Kg: {k_tot:.2f}"]
    return "\n".join(lines)

# =========================
# 3) PDF MEJORADO
# =========================
def generar_pdf(datos_pedido):
    """
    datos_pedido:
      {
        "Cliente": str,
        "Fecha": "dd/mm/YYYY",
        "Horario": "HH:MM a HH:MM",
        "Detalle": [ {Descripción, Cant., Kg., Tipo}, ... ]
      }
    """
    buf = BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    margin_x = 20 * mm
    margin_y = 15 * mm
    cursor_y = h - margin_y

    def header_footer(page_num):
