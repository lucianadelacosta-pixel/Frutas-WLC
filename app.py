# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import uuid, smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta, time
from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm

# =========================
# 0) CONFIGURACIÓN Y ESTILO
# =========================
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
    border-radius: 15px; padding: 30px; max-width: 1000px; 
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
}
.wa-float { 
    position: fixed; bottom: 20px; right: 20px; background-color: #25d366; 
    color: white; border-radius: 50px; padding: 12px 20px; 
    display: flex; align-items: center; gap: 10px; text-decoration: none; 
    z-index: 100; font-weight: bold; box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

# =========================
# 1) ESTADO DE SESIÓN
# =========================
if "nav" not in st.session_state: st.session_state.nav = "Inicio"
if "rol" not in st.session_state: st.session_state.rol = "Cliente"
if "lista" not in st.session_state: st.session_state.lista = {} 
if "pedidos" not in st.session_state: st.session_state.pedidos = {}
if "ultimo_pedido" not in st.session_state: st.session_state.ultimo_pedido = None
if "pedido_finalizado" not in st.session_state: st.session_state.pedido_finalizado = False

# Listas basadas exactamente en tu "NOTA DE PEDIDO.csv"
PRODUCTOS_IZQ = [
    "Acelga","Achicoria","Ajo","Alcaucil","Ananá","Apio","Arándanos","Banana","Batata","Berenjena",
    "Brócoli","Calabacín","Calabaza","Cebolla","Cerezas","Champiñón","Chaucha","Choclo","Ciruela","Coliflor",
    "Durazno","Espárragos","Espinaca","Frutilla","Kiwi","Lechuga","Lechuguin","Limón","Mandarina","Manzana",
    "Manzana (V)","Melón"
]
PRODUCTOS_DER = [
    "Naranja","Naranja (O)","Palta","Papa","Papa (Bolsa)","Pepino","Pera","Pimiento","Pomelo","Puerro",
    "Remolacha","Repollo","Rúcula","Sandia","Tomate (Cherry)","Tomate (P)","Tomate (R)","Uva","Verdeo","Zanahoria",
    "Zapallito","Zapallo","Zapallo (N)","Zuchini","Oliva","Miel","Huevos","Carbón","Perejil","Bandejas"
]
TODOS = sorted(PRODUCTOS_IZQ + PRODUCTOS_DER)

# =========================
# 2) FUNCIONES CORE
# =========================
def agregar_item(desc, cant, kg):
    desc = str(desc).strip().upper()
    st.session_state.lista[desc] = {"Cant.": cant, "Kg.": kg}

def generar_pdf_wc(datos):
    buf = BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    mx, my = 10*mm, 10*mm

    # --- ENCABEZADO ---
    p.setFont("Helvetica-Bold", 14)
    p.drawString(mx, h-my-5*mm, "FRUTAS Y VERDURAS WC")
    p.drawRightString(w-mx, h-my-5*mm, "NOTA DE PEDIDO")
    
    p.setFont("Helvetica", 8)
    p.drawString(mx, h-my-10*mm, "Contacto: 351 6351605 | Correo: frutasyverduraswc@gmail.com")
    
    # Fecha separada por campos (Estilo Excel)
    now = datetime.now()
    p.setFont("Helvetica-Bold", 9)
    p.drawString(w-mx-40*mm, h-my-12*mm, f"DIA: {now.day}  MES: {now.month}  AÑO: {now.year}")
    
    # Datos Cliente con recuadro
    p.setLineWidth(0.2)
    p.rect(mx, h-my-32*mm, w-2*mx, 14*mm)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(mx+2*mm, h-my-24*mm, f"CLIENTE: {datos['Cliente']}")
    p.drawString(mx+2*mm, h-my-30*mm, f"DOMICILIO: {datos['Domicilio']}")
    
    # --- TABLA DOBLE COLUMNA ---
    y_start = h-my-42*mm
    col_width = (w - 2*mx) / 2
    
    def dibujar_headers(x, y):
        p.setFillColor(colors.lightgrey)
        p.rect(x, y-4*mm, col_width, 5*mm, fill=1)
        p.setFillColor(colors.black)
        p.setFont("Helvetica-Bold", 8)
        p.drawString(x+2*mm, y-1*mm, "Descripción")
        p.drawString(x+col_width-30*mm, y-1*mm, "Cant.")
        p.drawString(x+col_width-15*mm, y-1*mm, "Kg.")

    dibujar_headers(mx, y_start)
    dibujar_headers(mx + col_width, y_start)
    
    y = y_start - 5*mm
    line_h = 4.3*mm
    pedido = datos['Detalle']

    for i in range(max(len(PRODUCTOS_IZQ), len(PRODUCTOS_DER))):
        p.setFont("Helvetica", 7.5)
        # Columna 1
        if i < len(PRODUCTOS_IZQ):
            item = PRODUCTOS_IZQ[i]
            p.drawString(mx+2*mm, y, item)
            if item.upper() in pedido:
                p.setFont("Helvetica-Bold", 8)
                p.drawString(mx+col_width-28*mm, y, str(pedido[item.upper()]['Cant.']) if pedido[item.upper()]['Cant.']>0 else "")
                p.drawString(mx+col_width-13*mm, y, str(pedido[item.upper()]['Kg.']) if pedido[item.upper()]['Kg.']>0 else "")
                p.setFont("Helvetica", 7.5)
            p.line(mx, y-1*mm, mx+col_width, y-1*mm)

        # Columna 2
        if i < len(PRODUCTOS_DER):
            item = PRODUCTOS_DER[i]
            p.drawString(mx+col_width+2*mm, y, item)
            if item.upper() in pedido:
                p.setFont("Helvetica-Bold", 8)
                p.drawString(mx+2*col_width-28*mm, y, str(pedido[item.upper()]['Cant.']) if pedido[item.upper()]['Cant.']>0 else "")
                p.drawString(mx+2*col_width-13*mm, y, str(pedido[item.upper()]['Kg.']) if pedido[item.upper()]['Kg.']>0 else "")
                p.setFont("Helvetica", 7.5)
            p.line(mx+col_width, y-1*mm, w-mx, y-1*mm)
        y -= line_h

    # Líneas verticales de cierre
    p.line(mx, y_start+1*mm, mx, y+line_h-1*mm)
    p.line(mx+col_width, y_start+1*mm, mx+col_width, y+line_h-1*mm)
    p.line(w-mx, y_start+1*mm, w-mx, y+line_h-1*mm)

    p.showPage()
    p.save()
    buf.seek(0)
    return buf

def enviar_email(dest, asunto, cuerpo, pdf_nombre, pdf_bytes):
    try:
        msg = EmailMessage()
        msg["Subject"] = asunto
        msg["From"] = st.secrets["SMTP_FROM"]
        msg["To"] = dest
        msg.set_content(cuerpo)
        msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename=pdf_nombre)
        with smtplib.SMTP(st.secrets["SMTP_HOST"], st.secrets["SMTP_PORT"], timeout=10) as s:
            s.starttls()
            s.login(st.secrets["SMTP_USER"], st.secrets["SMTP_PASS"])
            s.send_message(msg)
        return True, "Enviado"
    except Exception as e: return False, str(e)

# =========================
# 3) INTERFAZ DE USUARIO
# =========================
st.title("🍎 FRUTAS WC")
c_nav = st.columns(4)
if c_nav[0].button("🏠 Inicio", use_container_width=True): 
    st.session_state.nav = "Inicio"; st.session_state.pedido_finalizado = False
if c_nav[1].button("📖 Nosotros", use_container_width=True): 
    st.session_state.nav = "Nosotros"
if c_nav[2].button("🛒 Crear Pedido", use_container_width=True): 
    st.session_state.nav = "Crear Pedido"; st.session_state.pedido_finalizado = False
if c_nav[3].button("🔎 Mi Pedido", use_container_width=True): 
    st.session_state.nav = "Estado"

st.divider()

if st.session_state.nav == "Crear Pedido":
    if st.session_state.pedido_finalizado:
        st.balloons()
        st.success("## ✅ ¡Pedido Generado con Éxito!")
        p = st.session_state.ultimo_pedido
        st.write(f"ID del pedido: **{p['id']}**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📥 Descargar NOTA DE PEDIDO", data=p['pdf_bytes'], 
                               file_name=f"Pedido_{p['id']}.pdf", mime="application/pdf", use_container_width=True)
        with col2:
            if st.button("🛒 Crear otro pedido", use_container_width=True):
                st.session_state.pedido_finalizado = False; st.rerun()
        
        if st.button("🔎 Ver estado de mis pedidos", use_container_width=True):
            st.session_state.nav = "Estado"; st.session_state.pedido_finalizado = False; st.rerun()

    else:
        st.header("🛒 Armá tu Pedido")
        with st.container():
            c1, c2, c3 = st.columns(3)
            cli = c1.text_input("Nombre / Negocio")
            dom = c2.text_input("Domicilio de Entrega")
            mail = c3.text_input("Email (opcional)")
            
            c_f1, c_f2, c_f3 = st.columns([2,1,1])
            fec = c_f1.date_input("Fecha de entrega", min_value=datetime.now().date() + timedelta(days=1))
            h1 = c_f2.time_input("Desde", value=time(8,0))
            h2 = c_f3.time_input("Hasta", value=time(14,0))

        st.write("---")
        st.subheader("1. Seleccioná del catálogo")
        cp, cc, ck, cb = st.columns([3, 1, 1, 1])
        item_sel = cp.selectbox("Producto", TODOS)
        cant_sel = cc.number_input("Bultos", min_value=0, step=1)
        kg_sel = ck.number_input("Kg.", min_value=0.0, step=0.5)
        if cb.button("➕ Agregar", use_container_width=True):
            if cant_sel > 0 or kg_sel > 0:
                agregar_item(item_sel, cant_sel, kg_sel)
                st.toast(f"Añadido: {item_sel}")

        # Listado visual antes de confirmar
        if st.session_state.lista:
            st.write("### 📋 Resumen actual")
            df = pd.DataFrame.from_dict(st.session_state.lista, orient='index').reset_index()
            df.columns = ["Descripción", "Cant.", "Kg."]
            st.dataframe(df, hide_index=True, use_container_width=True)
            if st.button("🗑️ Vaciar Todo"):
                st.session_state.lista = {}; st.rerun()

        st.write("---")
        with st.expander("➕ ¿No encontrás un producto? Agregalo aquí"):
            ce1, ce2, ce3, ce4 = st.columns([3, 1, 1, 1])
            e_nom = ce1.text_input("Nombre del producto especial")
            e_can = ce2.number_input("Bultos", min_value=0, step=1, key="es_c")
            e_kg = ce3.number_input("Kg.", min_value=0.0, step=0.5, key="es_k")
            if ce4.button("✔ Añadir", use_container_width=True):
                if e_nom: agregar_item(e_nom, e_can, e_kg); st.rerun()

        if st.session_state.lista:
            if st.button("🚀 CONFIRMAR PEDIDO Y GENERAR PDF", use_container_width=True):
                if cli and dom:
                    datos = {
                        "Cliente": cli.upper(), "Domicilio": dom, "Email": mail,
                        "Fecha": fec.strftime("%d/%m/%Y"),
                        "Detalle": dict(st.session_state.lista)
                    }
                    pdf_bytes = generar_pdf_wc(datos).getvalue()
                    oid = uuid.uuid4().hex[:6].upper()
                    pedido = {"id": oid, "resumen": datos, "pdf_bytes": pdf_bytes, "estado": "Nuevo"}
                    st.session_state.pedidos[oid] = pedido
                    st.session_state.ultimo_pedido = pedido
                    st.session_state.pedido_finalizado = True
                    st.session_state.lista = {}
                    st.rerun()
                else: st.error("Completá Nombre y Domicilio.")

elif st.session_state.nav == "Inicio":
    st.subheader("Bienvenida/o a FRUTAS WC")
    st.info("Utilizá el menú superior para armar tu pedido. Recibirás una nota de pedido con el formato oficial.")

elif st.session_state.nav == "Nosotros":
    st.subheader("📖 Sobre Nosotros")
    st.write("Somos proveedores de frutas y verduras frescas con años de experiencia en el mercado.")

elif st.session_state.nav == "Estado":
    st.subheader("🔎 Mis Pedidos")
    if not st.session_state.pedidos: st.warning("No hay pedidos registrados.")
    else:
        for pid, ped in st.session_state.pedidos.items():
            with st.expander(f"Pedido {pid} - {ped['resumen']['Cliente']} ({ped['estado']})"):
                st.write(f"Fecha: {ped['resumen']['Fecha']}")
                st.download_button("📥 Descargar PDF", data=ped['pdf_bytes'], file_name=f"Pedido_{pid}.pdf", key=pid)

# =========================
# 6) ADMIN
# =========================
st.write("---")
if st.session_state.rol == "Cliente":
    with st.expander("🔒 Admin"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if u == st.secrets["ADMIN_USER"] and p == st.secrets["ADMIN_PASS"]:
                st.session_state.rol = "Admin"; st.rerun()
else:
    st.subheader("🛠 Panel de Administración")
    if st.button("Cerrar Sesión Admin"): st.session_state.rol = "Cliente"; st.rerun()
    if not st.session_state.pedidos: st.info("No hay pedidos nuevos.")
    else:
        for pid, ped in st.session_state.pedidos.items():
            with st.expander(f"ORDEN {pid} - {ped['resumen']['Cliente']}"):
                st.write(f"Estado: {ped['estado']}")
                c_a1, c_a2 = st.columns(2)
                if c_a1.button(f"En Distribución {pid}"):
                    ped['estado'] = "En Distribución"
                    if ped['resumen']['Email']:
                        enviar_email(ped['resumen']['Email'], "Pedido en Camino", "Tu pedido WC está en distribución.", f"Pedido_{pid}.pdf", ped['pdf_bytes'])
                    st.rerun()
                if c_a2.button(f"Marcar Entregado {pid}"): ped['estado'] = "Entregado"; st.rerun()

st.markdown(f'<a class="wa-float" href="https://wa.me/543516422893" target="_blank">💬 WhatsApp</a>', unsafe_allow_html=True)
