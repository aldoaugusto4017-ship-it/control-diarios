import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página web
st.set_page_config(page_title="Control Diario de Lecturas con Historial", layout="wide")

st.title("📊 Control Diario de Lecturas (Histórico y Automático)")
st.write("El sistema registra automáticamente la fecha actual, la hora de carga y guarda el historial para consultas pasadas.")

# Lista completa de portales con los diarios principales al inicio (antes de COH)
portales_completos = [ "EDM",
    "EDITORIAL MUNDO",
    "EDITORIAL NACIONAL",
"LN", "P12", "CR-CL", "TIEMPO ARG", "EL VIGIA", "DIARIO OCTUBRE",
    "COH", "CD-LJ-ET", "TS-PRL", 
    "XH-EPL-HTV", "DW-AM", "RT-SPK", 
    "ANSA-REUTER"]
    # EQUIPOS POLITICOS
    "Partidos políticos",
    "Sindicatos",
    "Eclesiástico",
    "Coyuntura económica",
    "Fuerzas de seguridad",
    "Simbólico",
    "Poder judicial",
    
    # Informes por regiones
    "EEUU",
    "Europa",
    "Rusia",
    "Asia occidental",
    "Asia pacifico",
    "África",
    "Latinoamérica"
]]
# Nombre del archivo donde se guardará el historial en tu compu
ARCHIVO_HISTORIAL = "historial_lecturas.csv"

# Pestañas para cada día
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
tabs = st.tabs(dias)

# Función para manejar cada solapa
def gestionar_dia(nombre_dia):
    st.subheader(f"Planilla del día: {nombre_dia}")
    
    # Fecha de hoy automática
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    st.info(f"📅 Fecha actual del sistema: {fecha_hoy}")
    
    # Tabla base con la cantidad exacta de portales (24 filas)
    df_base = pd.DataFrame({
        "Portal": portales_completos,
        "C1: GER": [False] * len(portales_completos),
        "C1: FLOR": [False] * len(portales_completos),
        "C2: JR": [False] * len(portales_completos),
        "C2: AG": [False] * len(portales_completos),
    })
    
    # Editor interactivo
    df_editado = st.data_editor(
        df_base, 
        use_container_width=True, 
        hide_index=True,
        key=f"editor_{nombre_dia}"
    )
    
    # Botón para guardar con fecha y hora exacta
    if st.button(f"💾 Guardar y Registrar {nombre_dia}", key=f"btn_{nombre_dia}"):
        hora_actual = datetime.now().strftime("%H:%M:%S")
        
        # Transformamos la tabla para guardarla fila por fila con su marca de tiempo
        registros_nuevos = []
        for index, row in df_editado.iterrows():
            for persona in ["C1: GER", "C1: FLOR", "C2: JR", "C2: AG"]:
                if row[persona]: # Si está marcado como leído
                    registros_nuevos.append({
                        "Fecha": fecha_hoy,
                        "Dia_Semana": nombre_dia,
                        "Hora": hora_actual,
                        "Portal": row["Portal"],
                        "Persona": persona
                    })
        
        df_nuevo = pd.DataFrame(registros_nuevos)
        
        # Si ya existía un historial previo, lo combinamos
        try:
            df_existente = pd.read_csv(ARCHIVO_HISTORIAL)
            df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
        except FileNotFoundError:
            df_final = df_nuevo
        
        # Guardamos en el archivo CSV local
        df_final.to_csv(ARCHIVO_HISTORIAL, index=False)
        st.success(f"¡Registros de {nombre_dia} guardados exitosamente a las {hora_actual}!")

# Asignamos la lógica a cada solapa
for i, tab in enumerate(tabs):
    with tab:
        gestionar_dia(dias[i])

st.divider()

# Sección de Consulta Histórica (Para ver lecturas pasadas)
st.header("📂 Consultar Historial de Lecturas Pasadas")
if st.button("🔄 Cargar / Actualizar Historial"):
    try:
        df_historial = pd.read_csv(ARCHIVO_HISTORIAL)
        st.dataframe(df_historial, use_container_width=True)
        
        # Opción para descargar el historial completo
        csv_data = df_historial.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar todo el historial en archivo",
            data=csv_data,
            file_name="historial_completo_lecturas.csv",
            mime="text/csv",
        )
    except FileNotFoundError:
        st.warning("Aún no hay registros guardados en el historial. ¡Realiza tu primera carga arriba!")
        import streamlit as st
import pandas as pd
import os

# Nombre del archivo de registros
ARCHIVO_HISTORIAL = "historial_lecturas.csv"

st.header("📊 Consulta e Historial de Lecturas")

if os.path.exists(ARCHIVO_HISTORIAL):
    df = pd.read_csv(ARCHIVO_HISTORIAL)
    
    # Asegurar formato correcto de fechas
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    
    # ---------------------------------------------------------
    # 1. BÚSQUEDA POR FECHA Y NOMBRE (CANTIDAD DE DIARIOS)
    # ---------------------------------------------------------
    st.subheader("🔍 Buscador de diarios leídos por fecha y persona")
    
    col1, col2 = st.columns(2)
    with col1:
        fecha_busqueda = st.date_input("Seleccionar fecha:")
    with col2:
        nombres_disponibles = ["Todos"] + list(df['Persona'].dropna().unique())
        nombre_busqueda = st.selectbox("Seleccionar persona:", nombres_disponibles)
        
    # Filtrado dinámico
    df_filtrado = df[df['Fecha'].dt.date == fecha_busqueda]
    if nombre_busqueda != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Persona'] == nombre_busqueda]
        
    cantidad_leida = len(df_filtrado)
    
    st.info(f"📌 **Total de diarios leídos:** {cantidad_leida}")
    if not df_filtrado.empty:
        st.dataframe(df_filtrado)
    else:
        st.warning("No hay registros para la fecha y persona seleccionadas.")

    st.markdown("---")

    # ---------------------------------------------------------
    # 2. TOTALIDAD DE DIARIOS LEÍDOS POR SEMANA (POR NOMBRE)
    # ---------------------------------------------------------
    st.subheader("📅 Total semanal por persona")
    
    # Se extrae el año y el número de semana
    df['Semana'] = df['Fecha'].dt.isocalendar().week
    df['Año'] = df['Fecha'].dt.year
    
    # Agrupación por año, semana y persona
    resumen_semanal = df.groupby(['Año', 'Semana', 'Persona']).size().reset_index(name='Diarios Leídos')
    
    st.dataframe(resumen_semanal)

    st.markdown("---")

    # ---------------------------------------------------------
    # 3. TOTALIDAD DE DIARIOS LEÍDOS POR MES (POR NOMBRE)
    # ---------------------------------------------------------
    st.subheader("📆 Total mensual por persona")
    
    # Se extrae el año y el mes
    df['Mes'] = df['Fecha'].dt.strftime('%Y-%m (%B)')
    
    # Agrupación por mes y persona
    resumen_mensual = df.groupby(['Mes', 'Persona']).size().reset_index(name='Diarios Leídos')
    
    st.dataframe(resumen_mensual)

else:
    st.info("Aún no hay registros cargados en el historial.")
    
