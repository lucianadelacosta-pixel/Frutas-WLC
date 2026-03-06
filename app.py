# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import uuid
from datetime import datetime, timedelta, time
from io import BytesIO

# Librerías para el PDF (Asegúrate de tener reportlab en requirements.txt)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

# --- 1. CONFIGURACIÓN Y ESTILO ---
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
    border-radius: 15px; padding: 30px; max-width: 980px; 
}
/* Estilo para el fondo verde de éxito */
.success-banner {
    padding: 25px;
    background-color: #28a745;
    color: white;
    border-radius: 12px;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 25px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
}
.wa-float { 
    position: fixed; bottom: 20px; right: 20px; background-color: #25d366; 
    color: white; border-radius: 50px; padding: 12px 20px; 
    display: flex; align-items: center; gap: 10px; text-decoration: none; 
    z-index: 100; font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# --- 2. ESTADO DE SESIÓN ---
if "nav" not in st.session_state: st.session_state.nav = "Inicio"
if "lista" not in st.session_state: st.session_state.lista = []
if "pedido_finalizado" not in st.session_state: st.session_state.pedido_finalizado = False
if "nro_actual" not in st.session_state: st.session_state.nro_actual = ""

PRODUCTOS = sorted(["Acelga","Achicoria","Ajo","Ananá","Apio","Banana","Batata","Berenjena","Cebolla","Choclo","Naranja","Palta","Papa","Pimiento","Tomate (R)","Huevos","Carbón"])

# --- 3. FUNCIONES ---
def agregar_item(desc, cant, kg, tipo):
    desc = str(desc).strip().upper()
    for row in st.session_state.lista:
        if row["Descripción"] == desc:
            row["Cant."] += cant
            row["Kg."] += kg
            return
    st.session_state.lista.append({"Descripción": desc, "Cant.": cant, "Kg.": kg, "Tipo": tipo})

def generar_pdf_wc(datos, nro):
    buf = BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    mx, my = 15*mm, 15*mm

    p.setFont("Helvetica-Bold", 16)
    p.drawString(mx, h-my, f"FRUTAS Y VERDURAS WC - NOTA #{nro}")
    p.setFont("Helvetica", 10)
    p.drawString(mx, h-my-15, "Contacto: 351 6351605 | Correo: frutasyverduraswc@gmail.com")
    p.line(mx, h-my-20, w-mx, h-my-20)

    p.setFont("Helvetica-Bold", 12)
    p.drawString(mx, h-my-45, f"Cliente: {datos['Cliente']}")
    p.setFont("Helvetica", 10)
    p.drawString(mx, h-my-60, f"Fecha de Entrega: {datos['Fecha']}")
    
    y = h-my-90
    p.setFont("Helvetica-Bold", 10)
    p.drawString(mx, y, "Descripción")
    p.drawString(mx+250, y, "Bultos")
    p.drawString(mx+320, y, "Kg.")
    p.line(mx, y-5, w-mx, y-5)
    
    y -= 20
    p.setFont("Helvetica", 10)
    for it in datos['Detalle']:
        p.drawString(mx, y, it['Descripción'])
        p.drawString(mx+250, y, str(it['Cant.']))
        p.drawString(mx+320, y, str(it['Kg.']))
        y -= 15
    
    p.showPage()
    p.save()
    buf.seek(0)
    return buf

# --- 4. INTERFAZ ---
st.title("🍎 FRUTAS WC")
c_nav = st.columns(4)
if c_nav[0].button("🏠 Inicio", use_container_width=True): st.session_state.nav = "Inicio"
if c_nav[2].button("🛒 Crear Pedido", use_container_width=True): 
    st.session_state.nav = "Crear Pedido"
    st.session_state.pedido_finalizado = False # Resetear al volver a entrar

st.divider()

if st.session_state.nav == "Crear Pedido":
    # MOSTRAR MENSAJE DE ÉXITO SI CORRESPONDE
    if st.session_state.pedido_finalizado:
        st.markdown(f'''
            <div class="success-banner">
                ✅ PEDIDO SOLICITADO CON ÉXITO<br>
                <span style="font-size: 18px;">Número de Pedido: {st.session_state.nro_actual}</span>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.button("Hacer un nuevo pedido"):
            st.session_state.pedido_finalizado = False
            st.session_state.lista = []
            st.rerun()
    
    else:
        st.header("📝 Armá tu Pedido")
        cli = st.text_input("Nombre del Cliente / Negocio")
        fec = st.date_input("Fecha de entrega", min_value=datetime.now().date() + timedelta(days=1))

        st.write("---")
        st.subheader("1. Seleccioná del catálogo")
        cp, cc, ck, cb = st.columns([3, 1, 1, 1])
        item = cp.selectbox("Producto", PRODUCTOS)
        cant = cc.number_input("Bultos", min_value=0, step=1, key="c_cat")
        kg = ck.number_input("Kg.", min_value=0.0, step=0.5, key="k_cat")
        if cb.button("➕ Agregar"):
            if cant > 0 or kg > 0:
                agregar_item(item, cant, kg, "CATÁLOGO")
                st.rerun()

        # PEDIDO ACTUAL JUSTO DEBAJO
        if st.session_state.lista:
            st.write("### 📋 Tu Pedido Actual")
            st.dataframe(pd.DataFrame(st.session_state.lista), hide_index=True, use_container_width=True)
            if st.button("🗑️ Borrar último ítem"):
                st.session_state.lista.pop()
                st.rerun()
            st.write("---")

        # PRODUCTO ESPECIAL AL FINAL
        with st.expander("➕ Agregar producto que NO está en la lista"):
            ce1, ce2, ce3, ce4 = st.columns([3, 1, 1, 1])
            e_nom = ce1.text_input("Nombre producto especial")
            e_can = ce2.number_input("Bultos", min_value=0, step=1, key="c_esp")
            e_kg = ce3.number_input("Kg.", min_value=0.0, step=0.5, key="k_esp")
            if ce4.button("✔ Añadir"):
                if e_nom:
                    agregar_item(e_nom, e_can, e_kg, "ESPECIAL")
                    st.rerun()

        # BOTÓN FINAL DE CONFIRMACIÓN
        if st.session_state.lista:
            st.write(" ")
            if st.button("🚀 FINALIZAR Y GENERAR PDF", use_container_width=True):
                if cli:
                    nro = uuid.uuid4().hex[:6].upper()
                    datos = {
                        "Cliente": cli.upper(),
                        "Fecha": fec.strftime("%d/%m/%Y"),
                        "Detalle": st.session_state.lista
                    }
                    # Generar PDF para descarga inmediata
                    pdf_io = generar_pdf_wc(datos, nro)
                    
                    # Guardar estado para mostrar el banner verde
                    st.session_state.nro_actual = nro
                    st.session_state.pedido_finalizado = True
                    
                    # El botón de descarga debe aparecer para que se lleven el comprobante
                    st.download_button("📥 Descargar Comprobante PDF", data=pdf_io, file_name=f"Pedido_{nro}.pdf", mime="application/pdf")
                    st.rerun()
                else:
                    st.error("Por favor, ingresá el nombre del cliente.")

elif st.session_state.nav == "Inicio":
    st.subheader("Distribución Logística de Frescuras en Córdoba")
    st.info("Utilizá el menú de arriba para comenzar tu pedido.")

# WhatsApp Flotante
st.markdown(f'<a class="wa-float" href="https://wa.me/543516422893" target="_blank">💬 WhatsApp</a>', unsafe_allow_html=True)
