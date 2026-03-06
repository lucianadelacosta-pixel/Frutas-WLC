import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="FRUTAS WC", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
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
        border-radius: 15px; padding: 30px; max-width: 950px;
    }
    .wa-float {
        position: fixed; bottom: 20px; right: 20px;
        background-color: #25d366; color: white; border-radius: 50px;
        padding: 12px 20px; display: flex; align-items: center; gap: 10px;
        text-decoration: none; z-index: 100; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNCIÓN PARA GENERAR EL PDF ---
def generar_pdf(datos_pedido):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, h - 50, "FRUTAS WC - NOTA DE PEDIDO")
    p.setFont("Helvetica", 10)
    p.drawString(50, h - 65, "Contacto: 351 6351605 | Correo: frutasyverduraswc@gmail.com")
    p.line(50, h - 70, 550, h - 70)

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, h - 100, f"Cliente: {datos_pedido['Cliente']}")
    p.setFont("Helvetica", 11)
    p.drawString(50, h - 115, f"Fecha de Entrega: {datos_pedido['Fecha']}")
    p.drawString(50, h - 130, f"Rango Horario: {datos_pedido['Horario']}")

    y = h - 170
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y, "Descripción")
    p.drawString(250, y, "Cant.")
    p.drawString(320, y, "Kg.")
    p.drawString(400, y, "Tipo")
    p.line(50, y - 5, 550, y - 5)
    
    y -= 20
    p.setFont("Helvetica", 10)
    for item in datos_pedido['Detalle']:
        p.drawString(50, y, str(item['Descripción']))
        p.drawString(250, y, str(item['Cant.']))
        p.drawString(320, y, str(item['Kg.']))
        p.drawString(400, y, str(item['Tipo']))
        y -= 15
        if y < 50:
            p.showPage()
            y = h - 50

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# --- 3. ESTADO DE SESIÓN ---
if 'nav' not in st.session_state: st.session_state.nav = "Inicio"
if 'rol' not in st.session_state: st.session_state.rol = "Cliente"
if 'lista_temporal' not in st.session_state: st.session_state.lista_temporal = []
if 'productos_wc' not in st.session_state:
    st.session_state.productos_wc = ["Acelga", "Anco", "Banana", "Cebolla", "Huevos", "Papa", "Tomate"]

# --- 4. NAVEGACIÓN ---
st.title("🍎 FRUTAS WC
