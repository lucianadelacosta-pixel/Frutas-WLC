import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

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
        border-radius: 15px;
        padding: 30px;
        max-width: 900px;
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

# Lista inicial basada en tu Excel (se actualiza al subir el archivo en Admin)
if 'productos_wc' not in st.session_state:
    st.session_state.productos_wc = [
        "PAPA", "CEBOLLA", "ANCO", "CABUTIA", "ZANAHORIA", "TOMATE", 
        "HUEVOS", "MANZANA", "BANANA", "CARBON", "ACELGA", "BATATA", "PERA", "NARANJA"
    ]

# --- 3. NAVEGACIÓN ---
st.title("🍎 FRUTAS WC")

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
        st.subheader("Distribución Logística de Frescuras en Córdoba")
        st.markdown("#### **Te lo llevamos a casa**")
        st.write("Calidad seleccionada en frutas, verduras, carbón y más.")

    elif st.session_state.nav == "Crear Pedido":
        st.header("🛒 Armá tu Pedido")
        nombre_c = st.text_input("Nombre / Negocio")
        
        st.write("---")
        col_p, col_c, col_k, col_b = st.columns([3, 1, 1, 1])
        with col_p:
            item_sel = st.selectbox("Seleccioná un producto", st.session_state.productos_wc)
        with col_c:
            cant_sel = st.number_input("Cant (Bultos)", min_value=0, step=1)
        with col_k:
            kg_sel = st.number_input("KG / Unid.", min_value=0.0, step=0.5)
        with col_b:
            st.write(" ")
            if st.button("➕ Añadir"):
                if cant_sel > 0 or kg_sel > 0:
                    st.session_state.lista_temporal.append({"Producto": item_sel, "Cant": cant_sel, "KG_Un": kg_sel})
                else: st.warning("Carga una cantidad.")

        if st.session_state.lista_temporal:
            st.write("### Tu lista actual:")
            st.table(pd.DataFrame(st.session_state.lista_temporal))
            if st.button("🚀 CONFIRMAR PEDIDO FINAL"):
                if nombre_c:
                    st.session_state.pedidos_db.append({
                        "Cliente": nombre_c, 
                        "Fecha": datetime.now().strftime("%d/%m/%Y"), 
                        "Detalle": st.session_state.lista_temporal
                    })
                    st.success("¡Pedido enviado con éxito!")
                    st.session_state.lista_temporal = []
                else: st.error("Falta completar tu nombre.")

# --- 5. CONTENIDO ADMIN (LUCIANA) ---
else:
    if st.session_state.nav == "Precios":
        st.header("⚙️ Actualizar Productos desde Excel")
        st.write("Subí tu archivo para que los clientes vean la lista actualizada.")
        archivo = st.file_uploader("Subir NOTA DE PEDIDO WC (.xlsx)", type=['xlsx'])
        
        if archivo:
            df_excel = pd.read_excel(archivo)
            # Buscamos la columna de descripción
            posibles = ['Descripción', 'DESCRIPCION', 'Detalle', 'DETALLE']
            col_ok = [c for c in df_excel.columns if c in posibles]
            
            if col_ok:
                nuevos = df_excel[col_ok[0]].dropna().unique().tolist()
                st.session_state.productos_wc = sorted(nuevos)
                st.success(f"¡Lista actualizada con {len(nuevos)} productos!")
            else:
                st.error("No encontré la columna 'Descripción' en tu archivo.")

    elif st.session_state.nav == "Resumen":
        st.header("📊 Historial de Pedidos")
        if st.session_state.pedidos_db:
            for p in st.session_state.pedidos_db:
                with st.expander(f"Pedido de {p['Cliente']} - {p['Fecha']}"):
                    st.table(pd.DataFrame(p['Detalle']))
        else:
            st.write("No hay pedidos nuevos.")

# --- 6. ACCESO ADMINISTRACIÓN (AL FINAL) ---
st.write("---")
if st.session_state.rol == "Cliente":
    with st.expander("🔒 Acceso Administración"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("Ingresar Modo Admin"):
            if u == "Luciana" and p == "WC2026":
                st.session_state.rol = "Admin"
                st.session_state.nav = "Resumen"
                st.rerun()
            else:
                st.error("Datos incorrectos")

# WhatsApp
wa_link = "https://wa.me/543516422893?text=Consultas%20FRUTAS%20WC"
st.markdown(f'<a href="{wa_link}" class="wa-float" target="_blank">💬 WhatsApp</a>', unsafe_allow_html=True)
