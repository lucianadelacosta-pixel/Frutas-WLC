import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN VISUAL (FONDO: fondo.jpg) ---
st.set_page_config(page_title="Frutas WLC", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Ocultar panel lateral y menús innecesarios */
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stHeader"] {background: rgba(0,0,0,0);}
    
    /* Imagen de fondo personalizada */
    .stApp {
        background-image: url("https://raw.githubusercontent.com/tu-usuario/Frutas-WLC/main/fondo.jpg"); 
        background-size: cover;
        background-position: center bottom;
        background-attachment: fixed;
    }
    
    /* Contenedor principal con transparencia para legibilidad */
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.96);
        border-radius: 15px;
        padding: 30px;
        margin-top: 10px;
        max-width: 900px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    }
    
    html, body, [class*="css"] { font-family: "Arial", sans-serif; }
    
    /* Botón WhatsApp Estilizado */
    .wa-float {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #25d366;
        color: white;
        border-radius: 50px;
        padding: 12px 20px;
        display: flex;
        align-items: center;
        gap: 10px;
        text-decoration: none;
        z-index: 100;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INICIALIZACIÓN DE DATOS Y SESIÓN ---
if 'rol' not in st.session_state: st.session_state.rol = "Cliente"
if 'nav' not in st.session_state: st.session_state.nav = "Inicio"
if 'pedidos' not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=["ID", "Cliente", "Producto", "Cantidad", "Fecha_Entrega", "Estado"])
# Catálogo inicial para Frutas WLC
if 'catalogo' not in st.session_state:
    st.session_state.catalogo = pd.DataFrame({
        "Producto": ["Manzana", "Papa", "Especias", "Carbón", "Huevos"],
        "Precio": [1200, 800, 450, 3500, 5200]
    })

# --- 3. TÍTULO Y NAVEGACIÓN DIRECTA (SIN DESPLEGABLES) ---
st.title("🍎 Frutas WLC")
st.write("Distribución logística de frescuras en Córdoba")

# Panel de navegación con botones directos
if st.session_state.rol == "Cliente":
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("🏠 Inicio", use_container_width=True): st.session_state.nav = "Inicio"
    if c2.button("📖 Nosotros", use_container_width=True): st.session_state.nav = "Nosotros"
    if c3.button("🛒 Crear Pedido", use_container_width=True): st.session_state.nav = "Crear Pedido"
    if c4.button("🔎 Mi Pedido", use_container_width=True): st.session_state.nav = "Estado"
else:
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("📊 Resumen", use_container_width=True): st.session_state.nav = "Resumen"
    if c2.button("⚙️ Precios", use_container_width=True): st.session_state.nav = "Precios"
    if c3.button("📦 Proveedores", use_container_width=True): st.session_state.nav = "Proveedores"
    if c4.button("🚪 Salir", use_container_width=True): 
        st.session_state.rol = "Cliente"
        st.rerun()

st.divider()

# --- 4. CONTENIDO DINÁMICO ---
if st.session_state.nav == "Inicio":
    st.markdown("#### **Te lo llevamos a casa**")
    st.write("Calidad seleccionada en frutas, verduras, carbón y más.")

elif st.session_state.nav == "Nosotros":
    st.header("Sobre Nosotros")
    st.write("Soy Luciana y en Frutas WLC nos enfocamos en que recibas lo mejor del campo en tu hogar con eficiencia logística.")

elif st.session_state.nav == "Crear Pedido":
    st.header("Realizá tu Pedido")
    st.dataframe(st.session_state.catalogo, hide_index=True, use_container_width=True)
    with st.form("p_cliente"):
        nombre = st.text_input("Nombre Completo")
        prod = st.selectbox("Producto", st.session_state.catalogo["Producto"])
        cant = st.number_input("Cantidad", min_value=1)
        fecha = st.date_input("Fecha de entrega", min_value=datetime.now().date() + timedelta(days=1))
        if st.form_submit_button("Confirmar Pedido"):
            st.success(f"¡Pedido para {nombre} registrado con éxito!")

# --- 5. ACCESO ADMINISTRATIVO (AL FINAL DE LA PÁGINA) ---
st.write("")
st.write("")
with st.expander("🔒 Acceso Administración"):
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if u == "Luciana" and p == "WLC2026":
            st.session_state.rol = "Admin"
            st.session_state.nav = "Resumen"
            st.rerun()
        else:
            st.error("Datos incorrectos")

# --- 6. BOTÓN WHATSAPP CON LOGO ---
wa_link = "https://wa.me/543516422893?text=Consultas%20Frutas%20WLC"
st.markdown(f'''
    <a href="{wa_link}" class="wa-float" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="20" height="20">
        Consultas a nuestro WhatsApp
    </a>
    ''', unsafe_allow_html=True)
