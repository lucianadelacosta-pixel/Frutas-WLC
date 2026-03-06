import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN VISUAL Y ESTILO ---
st.set_page_config(page_title="FRUTAS WC", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Ocultar barra lateral */
    [data-testid="stSidebar"] {display: none;}
    
    /* Fondo de pantalla con tu imagen fondo.jpg */
    .stApp {
        background-image: url("app/static/fondo.jpg"); 
        background-size: cover;
        background-position: center bottom;
        background-attachment: fixed;
    }
    
    /* Contenedor de contenido con transparencia */
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.96);
        border-radius: 15px;
        padding: 30px;
        max-width: 950px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    }
    
    html, body, [class*="css"] { font-family: "Arial", sans-serif; }
    
    /* Botón flotante de WhatsApp */
    .wa-float {
        position: fixed; bottom: 20px; right: 20px;
        background-color: #25d366; color: white; border-radius: 50px;
        padding: 12px 20px; display: flex; align-items: center; gap: 10px;
        text-decoration: none; z-index: 100; font-weight: bold;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BASE DE DATOS Y ESTADO DE SESIÓN ---
if 'rol' not in st.session_state: st.session_state.rol = "Cliente"
if 'nav' not in st.session_state: st.session_state.nav = "Inicio"
if 'lista_temporal' not in st.session_state: st.session_state.lista_temporal = []
if 'pedidos_db' not in st.session_state: st.session_state.pedidos_db = []

# Lista de productos por defecto (se actualiza al subir el Excel en Admin)
if 'productos_wc' not in st.session_state:
    st.session_state.productos_wc = [
        "Acelga", "Anco", "Banana", "Batata", "Cebolla", "Huevos", 
        "Manzana", "Naranja", "Papa", "Pimiento", "Tomate", "Zanahoria"
    ]

# --- 3. NAVEGACIÓN PRINCIPAL ---
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

# --- 4. SECCIÓN: CREAR PEDIDO ---
if st.session_state.nav == "Crear Pedido" and st.session_state.rol == "Cliente":
    st.header("📝 Nota de Pedido")
    
    # Datos de Identificación
    nombre_c = st.text_input("Nombre del Cliente / Negocio")
    
    # Datos de Logística: Fecha y Rango Horario
    col_f, col_h1, col_h2 = st.columns([2, 1, 1])
    with col_f:
        fecha_e = st.date_input("Fecha de Entrega", min_value=datetime.now().date() + timedelta(days=1))
    with col_h1:
        h_desde = st.time_input("Horario Desde", value=datetime.strptime("08:00", "%H:%M"))
    with col_h2:
        h_hasta = st.time_input("Horario Hasta", value=datetime.strptime("14:00", "%H:%M"))
    
    st.write("---")
    
    # 1. Selector con búsqueda (Autocompletado al escribir)
    st.subheader("Agregar productos de la lista")
    col_p, col_c, col_k, col_b = st.columns([3, 1, 1, 1])
    
    with col_p:
        item_sel = st.selectbox("Escribí para buscar el producto...", st.session_state.productos_wc)
    with col_c:
        cant_sel = st.number_input("Cant. (Bultos)", min_value=0, step=1, key="cant_main")
    with col_k:
        kg_sel = st.number_input("Kg.", min_value=0.0, step=0.5, key="kg_main")
    with col_b:
        st.write(" ")
        if st.button("➕ Agregar"):
            if cant_sel > 0 or kg_sel > 0:
                st.session_state.lista_temporal.append({"Descripción": item_sel, "Cant.": cant_sel, "Kg.": kg_sel})
                st.rerun()

    # 2. Botón para agregar producto que NO está en la lista
    with st.expander("➕ Agregar otro producto que no está en la lista"):
        col_n1, col_n2, col_n3, col_n4 = st.columns([3, 1, 1, 1])
        with col_n1:
            otro_nombre = st.text_input("¿Qué producto buscás?")
        with col_n2:
            otro_cant = st.number_input("Cant.", min_value=0, step=1, key="otro_c")
        with col_n3:
            otro_kg = st.number_input("Kg.", min_value=0.0, step=0.5, key="otro_k")
        with col_n4:
            st.write(" ")
            if st.button("✔ Añadir Especial"):
                if otro_nombre:
                    st.session_state.lista_temporal.append({"Descripción": otro_nombre.upper(), "Cant.": otro_cant, "Kg.": otro_kg})
                    st.rerun()

    # Resumen del pedido
    if st.session_state.lista_temporal:
        st.write("### Tu Pedido Actual:")
        df_temp = pd.DataFrame(st.session_state.lista_temporal)
        st.dataframe(df_temp, hide_index=True, use_container_width=True)
        
        c_borrar, c_enviar = st.columns(2)
        if c_borrar.button("🗑️ Borrar último ítem"):
            st.session_state.lista_temporal.pop()
            st.rerun()
            
        if c_enviar.button("🚀 CONFIRMAR PEDIDO FINAL"):
            if nombre_c:
                resumen_final = {
                    "Cliente": nombre_c, 
                    "Fecha": fecha_e.strftime("%d/%m/%Y"), 
                    "Horario": f"{h_desde.strftime('%H:%M')} a {h_hasta.strftime('%H:%M')}",
                    "Detalle": st.session_state.lista_temporal
                }
                st.session_state.pedidos_db.append(resumen_final)
                st.success(f"¡Pedido de {nombre_c} enviado!")
                st.session_state.lista_temporal = []
            else:
                st.error("Por favor, ingresá tu nombre.")

# --- 5. SECCIONES ADMINISTRATIVAS (LUCIANA) ---
elif st.session_state.nav == "Precios" and st.session_state.rol == "Admin":
    st.header("⚙️ Actualización desde Excel")
    archivo = st.file_uploader("Subí tu archivo de Excel", type=['xlsx'])
    if archivo:
        df_excel = pd.read_excel(archivo, engine='openpyxl')
        if 'Descripción' in df_excel.columns:
            st.session_state.productos_wc = sorted(df_excel['Descripción'].dropna().unique().tolist())
            st.success("¡Lista de productos actualizada!")

elif st.session_state.nav == "Resumen" and st.session_state.rol == "Admin":
    st.header("📊 Pedidos de Clientes")
    for p in st.session_state.pedidos_db:
        with st.expander(f"{p['Cliente']} - Entrega: {p['Fecha']} ({p['Horario']})"):
            st.table(pd.DataFrame(p['Detalle']))

elif st.session_state.nav == "Inicio":
    st.subheader("Distribución Logística de Frescuras en Córdoba")
    st.write("### **Te lo llevamos a casa**")
    st.info("Calidad seleccionada en frutas, verduras, carbón y más.")

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
st.markdown(f'''
    <a href="{wa_link}" class="wa-float" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="20" height="20">
        Consultas a nuestro WhatsApp
    </a>
    ''', unsafe_allow_html=True)
