import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN VISUAL (FONDO Y ESTILO) ---
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
        border-radius: 15px;
        padding: 30px;
        max-width: 950px;
    }
    html, body, [class*="css"] { font-family: "Arial", sans-serif; }
    .wa-float {
        position: fixed; bottom: 20px; right: 20px;
        background-color: #25d366; color: white; border-radius: 50px;
        padding: 12px 20px; display: flex; align-items: center; gap: 10px;
        text-decoration: none; z-index: 100; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BASE DE DATOS Y ESTADO ---
if 'rol' not in st.session_state: st.session_state.rol = "Cliente"
if 'nav' not in st.session_state: st.session_state.nav = "Inicio"
if 'lista_temporal' not in st.session_state: st.session_state.lista_temporal = []
if 'pedidos_db' not in st.session_state: st.session_state.pedidos_db = []

# Productos iniciales extraídos de tus columnas
if 'productos_wc' not in st.session_state:
    st.session_state.productos_wc = [
        "Acelga", "Ajo", "Anco", "Banana", "Batata", "Cebolla", 
        "Huevos", "Manzana", "Naranja", "Papa", "Tomate", "Zanahoria"
    ]

# --- 3. NAVEGACIÓN ---
st.title("🍎 FRUTAS WC")
st.write("Distribución logística de frescuras en Córdoba")

if st.session_state.rol == "Cliente":
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("🏠 Inicio", use_container_width=True): st.session_state.nav = "Inicio"
    if c2.button("📖 Nosotros", use_container_width=True): st.session_state.nav = "Nosotros"
    if c3.button("🛒 Crear Pedido", use_container_width=True): st.session_state.nav = "Crear Pedido"
    if c4.button("🔎 Mi Pedido", use_container_width=True): st.session_state.nav = "Estado"
else:
    c1, c2, c3 = st.columns(3)
    if c1.button("📊 Resumen Pedidos", use_container_width=True): st.session_state.nav = "Resumen"
    if c2.button("⚙️ Actualizar Excel", use_container_width=True): st.session_state.nav = "Precios"
    if c3.button("🚪 Salir Modo Admin", use_container_width=True): 
        st.session_state.rol = "Cliente"
        st.session_state.nav = "Inicio"
        st.rerun()

st.divider()

# --- 4. CONTENIDO CLIENTE ---
if st.session_state.rol == "Cliente":
    if st.session_state.nav == "Inicio":
        st.subheader("¡Bienvenida a nuestra tienda online!")
        st.write("Seleccionamos lo mejor del mercado para llevarlo directamente a tu domicilio.")

    elif st.session_state.nav == "Crear Pedido":
        st.header("📝 Armá tu Pedido")
        nombre_c = st.text_input("Nombre del Cliente / Negocio")
        
        st.write("---")
        st.subheader("Agregar productos a la lista")
        col_p, col_c, col_k, col_b = st.columns([3, 1, 1, 1])
        
        with col_p:
            item_sel = st.selectbox("Seleccioná un producto", st.session_state.productos_wc)
        with col_c:
            cant_sel = st.number_input("Cant. (Bultos)", min_value=0, step=1)
        with col_k:
            kg_sel = st.number_input("Kg.", min_value=0.0, step=0.5)
        with col_b:
            st.write(" ")
            if st.button("➕ Agregar"):
                if cant_sel > 0 or kg_sel > 0:
                    st.session_state.lista_temporal.append({
                        "Descripción": item_sel, 
                        "Cant.": cant_sel, 
                        "Kg.": kg_sel
                    })
                else: st.warning("Ingresá una cantidad o Kg.")

        if st.session_state.lista_temporal:
            st.write("### Tu Pedido Actual:")
            st.dataframe(pd.DataFrame(st.session_state.lista_temporal), hide_index=True, use_container_width=True)
            
            c_del, c_env = st.columns(2)
            if c_del.button("🗑️ Borrar último ítem"):
                st.session_state.lista_temporal.pop()
                st.rerun()
            
            if c_env.button("🚀 CONFIRMAR PEDIDO FINAL"):
                if nombre_c:
                    st.session_state.pedidos_db.append({
                        "Cliente": nombre_c, 
                        "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"), 
                        "Detalle": st.session_state.lista_temporal
                    })
                    st.success(f"¡Pedido de {nombre_c} enviado!")
                    st.session_state.lista_temporal = []
                else: st.error("Falta el nombre del cliente.")

# --- 5. CONTENIDO ADMIN (LUCIANA) ---
else:
    if st.session_state.nav == "Precios":
        st.header("⚙️ Actualización desde Excel")
        st.write("Subí tu archivo 'LISTA DE PRECIOS WC.xlsx' para actualizar los productos.")
        archivo = st.file_uploader("Seleccionar archivo", type=['xlsx'])
        
        if archivo:
            df_excel = pd.read_excel(archivo)
            if 'Descripción' in df_excel.columns:
                nuevos = df_excel['Descripción'].dropna().unique().tolist()
                st.session_state.productos_wc = sorted(nuevos)
                st.success(f"Se actualizaron {len(nuevos)} productos.")
            else:
                st.error("No se encontró la columna 'Descripción'.")

    elif st.session_state.nav == "Resumen":
        st.header("📊 Pedidos de Clientes")
        if st.session_state.pedidos_db:
            for p in st.session_state.pedidos_db:
                with st.expander(f"Pedido: {p['Cliente']} - {p['Fecha']}"):
                    st.table(pd.DataFrame(p['Detalle']))
        else:
            st.write("No hay pedidos registrados.")

# --- 6. ACCESO ADMINISTRACIÓN AL FINAL ---
st.write("---")
if st.session_state.rol == "Cliente":
    with st.expander("🔒 Acceso Administración"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("Entrar Modo Admin"):
            if u == "Luciana" and p == "WC2026":
                st.session_state.rol = "Admin"
                st.session_state.nav = "Resumen"
                st.rerun()

# WhatsApp
wa_url = "https://wa.me/543516422893?text=Hola%20Luciana%2C%20tengo%20una%20consulta%20en%20FRUTAS%20WC"
st.markdown(f'<a href="{wa_url}" class="wa-float" target="_blank">💬 WhatsApp</a>', unsafe_allow_html=True)
