import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN VISUAL Y FONDO VIBRANTE ---
st.set_page_config(page_title="Frutas WLC", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-image: url("https://img.freepik.com/foto-gratis/fondo-frutas-verduras-frescas-tonos-verdes-naranjas_1232-4545.jpg");
        background-size: cover;
        background-attachment: fixed;
    }
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.92);
        border-radius: 15px;
        padding: 30px;
        margin-top: 20px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    }
    /* Estilo para los botones de navegación inferior */
    .nav-button {
        display: inline-block;
        padding: 10px 20px;
        margin: 5px;
        border-radius: 10px;
        background-color: #ffffff;
        border: 1px solid #ddd;
        text-decoration: none;
        color: #333;
        font-weight: bold;
    }
    .wa-float {
        position: fixed;
        bottom: 80px; /* Subido para no tapar la navegación */
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
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SISTEMA DE SESIÓN Y LOGIN ---
if 'rol' not in st.session_state:
    st.session_state.rol = "Cliente"
if 'pedidos' not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=["ID", "Cliente", "Producto", "Cantidad", "Fecha_Entrega", "Estado"])
if 'catalogo' not in st.session_state:
    st.session_state.catalogo = pd.DataFrame({
        "Producto": ["Manzana", "Papa", "Especias", "Carbón", "Huevos"],
        "Precio": [1200, 800, 450, 3500, 5200]
    })

# --- 3. ÁREA DE LOGIN DISCRETA (Barra lateral) ---
with st.sidebar:
    st.write("---")
    if st.session_state.rol == "Cliente":
        if st.checkbox("Acceso Administración"):
            user = st.text_input("Usuario")
            pw = st.text_input("Contraseña", type="password")
            if st.button("Ingresar"):
                if user == "Luciana" and pw == "WLC2026":
                    st.session_state.rol = "Admin"
                    st.rerun()
                else:
                    st.error("Datos incorrectos")
    else:
        st.write(f"Conectada como: **Luciana**")
        if st.button("Cerrar Sesión"):
            st.session_state.rol = "Cliente"
            st.rerun()

# --- 4. PANEL DE NAVEGACIÓN (BOTONES DIRECTOS) ---
st.write("---")
if st.session_state.rol == "Cliente":
    c1, c2, c3, c4 = st.columns(4)
    with c1: btn_inicio = st.button("🏠 Inicio")
    with c2: btn_nosotros = st.button("📖 Nosotros")
    with c3: btn_pedido = st.button("🛒 Crear Pedido")
    with c4: btn_estado = st.button("🔎 Estado")
    
    # Lógica de navegación cliente
    if 'nav' not in st.session_state: st.session_state.nav = "Inicio"
    if btn_inicio: st.session_state.nav = "Inicio"
    if btn_nosotros: st.session_state.nav = "Nosotros"
    if btn_pedido: st.session_state.nav = "Crear Pedido"
    if btn_estado: st.session_state.nav = "Estado"

else: # NAVEGACIÓN ADMIN
    c1, c2, c3 = st.columns(3)
    with c1: btn_resumen = st.button("📊 Resumen Pedidos")
    with c2: btn_precios = st.button("⚙️ Precios")
    with c3: btn_prov = st.button("📦 Proveedores")
    
    if 'nav_admin' not in st.session_state: st.session_state.nav_admin = "Resumen"
    if btn_resumen: st.session_state.nav_admin = "Resumen"
    if btn_precios: st.session_state.nav_admin = "Precios"
    if btn_prov: st.session_state.nav_admin = "Proveedores"

st.write("---")

# --- 5. CONTENIDO SEGÚN SELECCIÓN ---
if st.session_state.rol == "Cliente":
    if st.session_state.nav == "Inicio":
        st.title("🍎 Frutas WLC")
        st.subheader("Distribución Logística de Frescuras en Córdoba")
        st.write("### **Te lo llevamos a casa**")
        st.info("Calidad seleccionada en frutas, verduras, carbón y más.")

    elif st.session_state.nav == "Nosotros":
        st.header("Sobre Nosotros")
        st.write("Somos Luciana y el equipo de Frutas WLC. Llevamos frescura a tu hogar con eficiencia logística.")

    elif st.session_state.nav == "Crear Pedido":
        st.header("Realizá tu Pedido")
        st.dataframe(st.session_state.catalogo, hide_index=True, use_container_width=True)
        with st.form("p_cliente"):
            nombre = st.text_input("Tu Nombre")
            prod = st.selectbox("Producto", st.session_state.catalogo["Producto"])
            cant = st.number_input("Cantidad", min_value=1)
            fecha = st.date_input("Fecha de entrega", min_value=datetime.now().date() + timedelta(days=1))
            if st.form_submit_button("Confirmar"):
                nuevo = {"ID": len(st.session_state.pedidos)+1, "Cliente": nombre, "Producto": prod, 
                         "Cantidad": cant, "Fecha_Entrega": fecha, "Estado": "Pendiente"}
                st.session_state.pedidos = pd.concat([st.session_state.pedidos, pd.DataFrame([nuevo])], ignore_index=True)
                st.success("¡Pedido creado!")

    elif st.session_state.nav == "Estado":
        st.header("Seguimiento")
        st.write("Buscá tu pedido por número.")

else: # CONTENIDO ADMIN
    if st.session_state.nav_admin == "Resumen":
        st.header("Resumen General de Pedidos")
        st.dataframe(st.session_state.pedidos, hide_index=True, use_container_width=True)
    elif st.session_state.nav_admin == "Precios":
        st.header("Actualizar Catálogo")
        f = st.file_uploader("Subir Excel", type=['xlsx'])
    elif st.session_state.nav_admin == "Proveedores":
        st.header("Reporte de Compras")

# --- 6. WHATSAPP FLOTANTE ---
wa_link = "https://wa.me/543516422893?text=Consultas%20Frutas%20WLC"
st.markdown(f"""
    <a href="{wa_link}" class="wa-float" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="20" height="20">
        Consultas a nuestro WhatsApp
    </a>
    """, unsafe_allow_html=True)
