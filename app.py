import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN VISUAL (ARIAL + LIMPIEZA) ---
st.set_page_config(page_title="Frutas WLC - Gestión Logística", layout="wide")

st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: "Arial", sans-serif;
    }
    .whatsapp-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #25d366;
        color: white;
        border-radius: 50px;
        padding: 15px 25px;
        font-weight: bold;
        text-decoration: none;
        z-index: 100;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
    }
    /* Estilo para que las tablas se vean más limpias */
    [data-testid="stElementToolbar"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. INICIALIZACIÓN DE DATOS ---
if 'pedidos' not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=[
        "ID", "Cliente", "Producto", "Cantidad", "Unidad", "Fecha_Entrega", "Estado"
    ])

if 'catalogo' not in st.session_state:
    st.session_state.catalogo = pd.DataFrame({
        "Producto": ["Manzana", "Papa", "Especias", "Carbón", "Huevos"],
        "Unidad": ["Kg", "Kg", "100g", "Bolsa 10kg", "Maple x30"],
        "Precio": [1200, 800, 450, 3500, 5200]
    })

# --- 3. MENÚ LATERAL ---
st.sidebar.title("Frutas WLC Admin")
menu = st.sidebar.radio("Navegación", ["Inicio", "Hacer Pedido", "Panel Logístico (Norma)"])

# Carga de Excel para Precios
archivo_precios = st.sidebar.file_uploader("Actualizar Precios", type=['csv', 'xlsx'])
if archivo_precios:
    df_new = pd.read_csv(archivo_precios) if archivo_precios.name.endswith('.csv') else pd.read_excel(archivo_precios)
    st.session_state.catalogo = df_new
    st.sidebar.success("Precios actualizados")

# --- 4. SECCIONES ---

if menu == "Inicio":
    st.title("🍎 Frutas WLC")
    st.subheader("Distribución Logística de Frescura en Córdoba")
    st.image("https://img.freepik.com/foto-gratis/variedad-frutas-verduras-frescas-aisladas-blanco_1232-4545.jpg")
    st.info("🚚 Te lo llevamos a casa. Calidad seleccionada en frutas, verduras, carbón y más.")

elif menu == "Hacer Pedido":
    st.header("Lista de Precios")
    # Mostramos catálogo SIN números a la izquierda
    st.dataframe(st.session_state.catalogo, hide_index=True, use_container_width=True)
    
    with st.form("nuevo_p"):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre del Cliente")
            prod = st.selectbox("Elegí el producto", st.session_state.catalogo["Producto"])
        with c2:
            cant = st.number_input("Cantidad", min_value=1)
            fecha = st.date_input("Fecha de entrega", min_value=datetime.now().date() + timedelta(days=1))
        
        if st.form_submit_button("Confirmar Pedido"):
            nuevo = {"ID": len(st.session_state.pedidos)+1, "Cliente": nombre, "Producto": prod, 
                     "Cantidad": cant, "Unidad": "Sujeto a Catálogo", "Fecha_Entrega": fecha, "Estado": "Pendiente"}
            st.session_state.pedidos = pd.concat([st.session_state.pedidos, pd.DataFrame([nuevo])], ignore_index=True)
            st.success("¡Pedido registrado!")

elif menu == "Panel Logístico (Norma)":
    st.header("📊 Centro de Control Logístico")
    
    # Reporte de Compra
    st.subheader("📋 Lista de compra para el Proveedor")
    f_rep = st.date_input("Ver pedidos para la fecha:")
    df_dia = st.session_state.pedidos[st.session_state.pedidos['Fecha_Entrega'] == f_rep]
    
    if not df_dia.empty:
        rep = df_dia.groupby("Producto")["Cantidad"].sum().reset_index()
        # Mostramos reporte SIN números a la izquierda
        st.dataframe(rep, hide_index=True, use_container_width=True)
        st.download_button("Descargar Reporte CSV", rep.to_csv(index=False), f"compra_{f_rep}.csv")
    else:
        st.write("No hay pedidos para esta fecha.")

    st.divider()
    st.subheader("🔍 Historial de Pedidos")
    # Mostramos historial SIN números a la izquierda
    st.dataframe(st.session_state.pedidos, hide_index=True, use_container_width=True)

# --- 5. BOTÓN WHATSAPP ---
wa_url = "https://wa.me/543516422893?text=Hola%20Frutas%20WLC%20quisiera%20consultar%20por%20un%20pedido"
st.markdown(f'<a href="{wa_url}" class="whatsapp-button" target="_blank">💬 Pedir por WhatsApp</a>', unsafe_allow_html=True)
