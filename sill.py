# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime
import json
from streamlit_gsheets import GSheetsConnection

# Nombres de las hojas en Google Sheets
SHEET_CLIENTES = "clientes"
SHEET_VEHICULOS = "vehiculos"
SHEET_LLANTAS = "llantas"
SHEET_SERVICIOS = "servicios"
SHEET_USUARIOS = "usuarios"
SHEET_MOVIMIENTOS = "movimientos"
SHEET_ALINEACIONES = "alineaciones"

# Configuración de la página con colores personalizados
st.set_page_config(page_title="Sistema Integrado de Llantas", layout="wide", initial_sidebar_state="expanded")

# CSS personalizado con colores corporativos
st.markdown("""
    <style>
    /* Botones principales */
    .stButton>button {
        background-color: #2A2D62;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #F2B705;
        color: #2A2D62;
        border: none;
    }
    
    /* Tabs - solo texto amarillo, fondo transparente */
    .stTabs [data-baseweb="tab-list"] button {
        background-color: transparent;
        color: #5c5c5c;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: transparent;
        color: #F2B705 !important;
        font-weight: bold;
    }
    
    .stTabs [data-baseweb="tab-list"] button:hover {
        background-color: transparent;
        color: #F2B705;
    }
    
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #F2B705 !important;
    }
    
    /* Radio buttons - FORZAR AMARILLO */
    div[data-baseweb="radio"] > div,
    div[data-baseweb="radio"] > div > div,
    [role="radio"] > div,
    [role="radio"] > div > div {
        border-color: #cccccc !important;
    }
    
    div[data-baseweb="radio"]:hover > div,
    [role="radio"]:hover > div {
        border-color: #F2B705 !important;
    }
    
    div[data-baseweb="radio"] > div > div,
    [role="radio"] > div > div,
    div[aria-checked="true"] > div > div,
    [aria-checked="true"] > div > div {
        background-color: transparent !important;
    }
    
    div[data-baseweb="radio"][aria-checked="true"] > div,
    [role="radio"][aria-checked="true"] > div,
    div[aria-checked="true"] > div {
        border-color: #F2B705 !important;
    }
    
    div[data-baseweb="radio"][aria-checked="true"] > div > div,
    [role="radio"][aria-checked="true"] > div > div,
    div[aria-checked="true"] > div > div {
        background-color: #F2B705 !important;
    }
    
    [class*="st-"][class*="emotion"] [data-baseweb="radio"][aria-checked="true"] > div > div {
        background-color: #F2B705 !important;
    }
    
    [class*="st-"][class*="emotion"] [data-baseweb="radio"][aria-checked="true"] > div {
        border-color: #F2B705 !important;
    }
    
    /* Checkboxes */
    .stCheckbox > label > div[data-testid="stCheckbox"] > div {
        border-color: #cccccc;
    }
    
    .stCheckbox > label > div[data-testid="stCheckbox"]:hover > div {
        border-color: #F2B705;
    }
    
    .stCheckbox > label > div[data-testid="stCheckbox"] > div[data-checked="true"] {
        background-color: #F2B705 !important;
        border-color: #F2B705 !important;
    }
    
    /* Text input focus */
    .stTextInput > div > div > input:focus {
        border-color: #F2B705 !important;
        box-shadow: 0 0 0 1px #F2B705 !important;
    }
    
    /* Number input focus */
    .stNumberInput > div > div > input:focus {
        border-color: #F2B705 !important;
        box-shadow: 0 0 0 1px #F2B705 !important;
    }
    
    /* Date input focus */
    .stDateInput > div > div > input:focus {
        border-color: #F2B705 !important;
        box-shadow: 0 0 0 1px #F2B705 !important;
    }
    
    /* Selectbox focus */
    .stSelectbox > div > div:focus-within {
        border-color: #F2B705 !important;
        box-shadow: 0 0 0 1px #F2B705 !important;
    }
    
    /* Multiselect */
    .stMultiSelect > div > div:focus-within {
        border-color: #F2B705 !important;
        box-shadow: 0 0 0 1px #F2B705 !important;
    }
    
    /* Links */
    a {
        color: #2A2D62 !important;
    }
    
    a:hover {
        color: #F2B705 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ============= CONEXIÓN A GOOGLE SHEETS =============
# URL del spreadsheet
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1H05kURh2Lbo6C1rvOW4RyBNM8fyPFrlHqoT-U0TkCqE"

@st.cache_resource
def get_gsheets_connection():
    """Obtiene la conexión a Google Sheets con Service Account"""
    return st.connection("gsheets", type=GSheetsConnection)

def limpiar_clientes_asignados(valor):
    """Convierte clientes_asignados a string limpio, manejando floats y múltiples NITs"""
    if pd.isna(valor) or valor == '' or valor is None:
        return ''
    # Si es un número (float o int), convertir a int string
    if isinstance(valor, (int, float)):
        return str(int(valor))
    # Si es string, limpiar cada NIT separado por coma
    valor_str = str(valor)
    nits = []
    for nit in valor_str.split(','):
        nit = nit.strip()
        if nit:
            try:
                # Intentar convertir a int para eliminar decimales
                nits.append(str(int(float(nit))))
            except (ValueError, TypeError):
                nits.append(nit)
    return ','.join(nits)

def normalizar_columnas_id(df):
    """Normaliza todas las columnas de ID a tipo string para evitar inconsistencias"""
    columnas_id = ['id_vehiculo', 'id_llanta', 'id_servicio', 'id_movimiento',
                   'id_alineacion', 'id_usuario', 'placa_vehiculo', 'usuario']

    for col in columnas_id:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: str(x).strip() if pd.notna(x) and str(x).strip() != 'nan' else '')

    return df

def generar_id_usuario(nombre, df_usuarios):
    """Genera ID de usuario automático: 3 primeras letras del nombre + consecutivo de 3 dígitos"""
    import unicodedata

    # Limpiar el nombre: quitar acentos y caracteres especiales
    nombre_limpio = unicodedata.normalize('NFD', nombre.upper())
    nombre_limpio = ''.join(c for c in nombre_limpio if unicodedata.category(c) != 'Mn')
    nombre_limpio = ''.join(c for c in nombre_limpio if c.isalpha() or c.isspace())

    # Tomar las primeras 3 letras del primer nombre
    partes = nombre_limpio.split()
    if partes:
        prefijo = partes[0][:3].upper()
    else:
        prefijo = "USR"

    # Asegurar que tenga exactamente 3 caracteres
    prefijo = prefijo.ljust(3, 'X')[:3]

    # Buscar el máximo consecutivo existente para este prefijo
    max_consecutivo = 0
    if not df_usuarios.empty and 'id_usuario' in df_usuarios.columns:
        for id_usr in df_usuarios['id_usuario'].values:
            if pd.notna(id_usr) and str(id_usr).startswith(prefijo):
                try:
                    num = int(str(id_usr)[3:])
                    if num > max_consecutivo:
                        max_consecutivo = num
                except (ValueError, IndexError):
                    pass

    # Generar nuevo ID
    nuevo_consecutivo = max_consecutivo + 1
    nuevo_id = f"{prefijo}{nuevo_consecutivo:03d}"

    return nuevo_id

def leer_hoja(nombre_hoja):
    """Lee una hoja de Google Sheets y retorna un DataFrame"""
    try:
        conn = get_gsheets_connection()
        df = conn.read(
            spreadsheet=SPREADSHEET_URL,
            worksheet=nombre_hoja,
            ttl=300
        )
        if df is None or df.empty:
            return pd.DataFrame()
        # Eliminar filas completamente vacías
        df = df.dropna(how='all')
        # Convertir columnas NIT a string (evitar decimales como 1234567890.0)
        for col in ['nit', 'nit_cliente']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: str(int(x)) if pd.notna(x) and isinstance(x, (int, float)) else str(x) if pd.notna(x) else '')
        # Convertir clientes_asignados a string limpio (manejar floats como 123456789.0)
        if 'clientes_asignados' in df.columns:
            df['clientes_asignados'] = df['clientes_asignados'].apply(limpiar_clientes_asignados)
        # Normalizar todas las columnas ID a string
        df = normalizar_columnas_id(df)
        return df
    except Exception as e:
        st.error(f"Error leyendo {nombre_hoja}: {str(e)}")
        return pd.DataFrame()

def leer_hoja_fresco(nombre_hoja):
    """Lee una hoja de Google Sheets SIN caché - para verificaciones críticas"""
    try:
        conn = get_gsheets_connection()
        df = conn.read(
            spreadsheet=SPREADSHEET_URL,
            worksheet=nombre_hoja,
            ttl=0
        )
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.dropna(how='all')
        # Convertir columnas NIT a string (evitar decimales como 1234567890.0)
        for col in ['nit', 'nit_cliente']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: str(int(x)) if pd.notna(x) and isinstance(x, (int, float)) else str(x) if pd.notna(x) else '')
        # Convertir clientes_asignados a string limpio
        if 'clientes_asignados' in df.columns:
            df['clientes_asignados'] = df['clientes_asignados'].apply(limpiar_clientes_asignados)
        # Normalizar todas las columnas ID a string
        df = normalizar_columnas_id(df)
        return df
    except Exception as e:
        st.error(f"Error leyendo {nombre_hoja}: {str(e)}")
        return pd.DataFrame()

def escribir_hoja(nombre_hoja, df):
    """Escribe un DataFrame a una hoja de Google Sheets y retorna datos frescos"""
    try:
        conn = get_gsheets_connection()
        conn.update(
            spreadsheet=SPREADSHEET_URL,
            worksheet=nombre_hoja,
            data=df
        )
        # Leer datos frescos inmediatamente después de escribir
        df_fresco = conn.read(
            spreadsheet=SPREADSHEET_URL,
            worksheet=nombre_hoja,
            ttl=0
        )
        if df_fresco is not None:
            df_fresco = df_fresco.dropna(how='all')
            # Convertir columnas NIT a string (evitar decimales como 1234567890.0)
            for col in ['nit', 'nit_cliente']:
                if col in df_fresco.columns:
                    df_fresco[col] = df_fresco[col].apply(lambda x: str(int(x)) if pd.notna(x) and isinstance(x, (int, float)) else str(x) if pd.notna(x) else '')
            # Convertir clientes_asignados a string limpio
            if 'clientes_asignados' in df_fresco.columns:
                df_fresco['clientes_asignados'] = df_fresco['clientes_asignados'].apply(limpiar_clientes_asignados)
        return df_fresco if df_fresco is not None else df
    except Exception as e:
        st.error(f"Error escribiendo en {nombre_hoja}: {str(e)}")
        return None

def filtrar_por_clientes(df, columna_nit, clientes_acceso):
    """Filtra un DataFrame por clientes accesibles de forma segura"""
    if df.empty or columna_nit not in df.columns:
        return pd.DataFrame()
    # Convertir ambos a string para comparación consistente
    clientes_acceso_str = [str(c).strip() for c in clientes_acceso]
    return df[df[columna_nit].astype(str).str.strip().isin(clientes_acceso_str)]

def existe_valor(df, columna, valor):
    """Verifica si un valor existe en una columna de forma segura"""
    if df.empty or columna not in df.columns:
        return False
    return str(valor) in df[columna].astype(str).values

def crear_movimiento(id_llanta, tipo, vida, placa_vehiculo='', posicion='', kilometraje=0,
                     nueva_disponibilidad='', marca_reencauche='', ref_reencauche='',
                     precio_reencauche=0, observaciones='', orden_trabajo='', planilla='', operario='',
                     nit_cliente=''):
    """Crea un nuevo registro en la hoja de movimientos"""
    try:
        df_movimientos = leer_hoja(SHEET_MOVIMIENTOS)

        # Obtener nit_cliente de la llanta si no se proporcionó
        if not nit_cliente:
            df_llantas_mov = leer_hoja(SHEET_LLANTAS)
            llanta_match = df_llantas_mov[df_llantas_mov['id_llanta'] == id_llanta]
            nit_cliente = llanta_match['nit_cliente'].values[0] if not llanta_match.empty else ''

        # Generar ID de movimiento con formato id_cliente
        nuevo_id = generar_id_movimiento(nit_cliente) if nit_cliente else 'M001'

        # Obtener usuario actual
        usuario_actual = st.session_state.get('usuario', 'sistema')

        nuevo_movimiento = pd.DataFrame([{
            'id_movimiento': nuevo_id,
            'orden_trabajo': orden_trabajo,
            'planilla': planilla,
            'id_llanta': id_llanta,
            'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'tipo': tipo,
            'vida': vida,
            'placa_vehiculo': placa_vehiculo,
            'posicion': posicion,
            'kilometraje': kilometraje,
            'nueva_disponibilidad': nueva_disponibilidad,
            'marca_reencauche': marca_reencauche,
            'ref_reencauche': ref_reencauche,
            'precio_reencauche': precio_reencauche,
            'observaciones': observaciones,
            'operario': operario,
            'usuario': usuario_actual
        }])

        df_movimientos = pd.concat([df_movimientos, nuevo_movimiento], ignore_index=True)
        escribir_hoja(SHEET_MOVIMIENTOS, df_movimientos)
        return True
    except Exception as e:
        st.error(f"Error creando movimiento: {str(e)}")
        return False

# ============= FUNCIONES DE INICIALIZACIÓN =============
def inicializar_datos():
    """Inicializa los datos en Google Sheets si las hojas están vacías"""
    # Verificar si usuarios está vacío y crear usuarios por defecto
    df_usuarios = leer_hoja(SHEET_USUARIOS)
    if df_usuarios.empty:
        usuarios_default = pd.DataFrame([
            {'id_usuario': 'ADM001', 'usuario': 'admin', 'password': 'admin123', 'nivel': 1, 'nombre': 'Administrador', 'clientes_asignados': ''},
            {'id_usuario': 'SUP001', 'usuario': 'supervisor', 'password': 'super123', 'nivel': 2, 'nombre': 'Supervisor', 'clientes_asignados': ''},
            {'id_usuario': 'ADM002', 'usuario': 'admin_cliente', 'password': 'cliente123', 'nivel': 4, 'nombre': 'Admin Cliente', 'clientes_asignados': ''},
            {'id_usuario': 'OPE001', 'usuario': 'operario', 'password': 'oper123', 'nivel': 3, 'nombre': 'Operario', 'clientes_asignados': ''}
        ])
        escribir_hoja(SHEET_USUARIOS, usuarios_default)

# ============= FUNCIONES AUXILIARES =============
def calcular_costo_km_vida(id_llanta, vida, guardar=False):
    """
    Calcula el costo/km de una llanta en una vida específica
    Formula: precio_vida / km_recorridos_en_vida
    Si guardar=True, actualiza el CSV con el valor calculado
    Retorna None si no hay suficientes datos
    """
    try:
        df_llantas = leer_hoja(SHEET_LLANTAS)
        df_servicios = leer_hoja(SHEET_SERVICIOS)
        
        llanta = df_llantas[df_llantas['id_llanta'] == id_llanta]
        if llanta.empty:
            return None
        
        # Obtener el precio de la vida correspondiente
        precio_col = f'precio_vida{vida}'
        if precio_col not in llanta.columns or pd.isna(llanta.iloc[0][precio_col]):
            return None
        
        precio = float(llanta.iloc[0][precio_col])
        
        # Obtener servicios de esa vida específica
        servicios_vida = df_servicios[
            (df_servicios['id_llanta'] == id_llanta) & 
            (df_servicios['vida'] == vida)
        ]
        
        if servicios_vida.empty or len(servicios_vida) < 2:
            return None
        
        # Calcular kilómetros recorridos en esa vida
        km_inicial = servicios_vida['kilometraje'].min()
        km_final = servicios_vida['kilometraje'].max()
        km_recorridos = km_final - km_inicial
        
        if km_recorridos <= 0:
            return None
        
        # Calcular costo/km
        costo_km = precio / km_recorridos
        costo_km_redondeado = round(costo_km, 2)
        
        # Guardar en CSV si se solicita
        if guardar:
            costo_col = f'costo_km_vida{vida}'
            df_llantas.loc[df_llantas['id_llanta'] == id_llanta, costo_col] = costo_km_redondeado
            escribir_hoja(SHEET_LLANTAS, df_llantas)
        
        return costo_km_redondeado
    
    except Exception as e:
        return None

def calcular_costo_km_acumulado(id_llanta):
    """
    Calcula el costo/km acumulado de todas las vidas de una llanta
    Formula: suma(precios_vidas) / km_totales
    """
    try:
        df_llantas = leer_hoja(SHEET_LLANTAS)
        df_servicios = leer_hoja(SHEET_SERVICIOS)
        
        llanta = df_llantas[df_llantas['id_llanta'] == id_llanta]
        if llanta.empty:
            return None
        
        # Sumar todos los precios de vidas que se han usado
        vida_val = llanta.iloc[0].get('vida_actual', llanta.iloc[0].get('vida', 1))
        vida_actual = int(vida_val) if pd.notna(vida_val) else 1
        precio_total = 0
        
        for v in range(1, vida_actual + 2):  # +2 porque vida 0 = nueva (vida1)
            precio_col = f'precio_vida{v}'
            if precio_col in llanta.columns and pd.notna(llanta.iloc[0][precio_col]):
                precio_total += float(llanta.iloc[0][precio_col])
        
        # Obtener todos los servicios de la llanta
        servicios_llanta = df_servicios[df_servicios['id_llanta'] == id_llanta]
        
        if servicios_llanta.empty or len(servicios_llanta) < 2:
            return None
        
        # Calcular kilómetros totales recorridos
        km_inicial = servicios_llanta['kilometraje'].min()
        km_final = servicios_llanta['kilometraje'].max()
        km_totales = km_final - km_inicial
        
        if km_totales <= 0 or precio_total <= 0:
            return None
        
        # Calcular costo/km acumulado
        costo_km_acumulado = precio_total / km_totales
        return round(costo_km_acumulado, 2)
    
    except Exception as e:
        return None

def actualizar_costos_km_llanta(id_llanta):
    """
    Actualiza todos los costos/km de una llanta después de registrar un servicio
    Recalcula costo_km_vida1, costo_km_vida2, costo_km_vida3, costo_km_vida4
    """
    try:
        df_llantas = leer_hoja(SHEET_LLANTAS)
        
        llanta = df_llantas[df_llantas['id_llanta'] == id_llanta]
        if llanta.empty:
            return False
        
        vida_val = llanta.iloc[0].get('vida_actual', llanta.iloc[0].get('vida', 1))
        vida_actual = int(vida_val) if pd.notna(vida_val) else 1

        # Recalcular costos para cada vida que se ha usado
        for v in range(1, 5):  # Vidas 1, 2, 3, 4
            if v <= vida_actual + 1:  # +1 porque vida 0 = nueva (vida1)
                costo_km = calcular_costo_km_vida(id_llanta, v, guardar=False)
                costo_col = f'costo_km_vida{v}'
                
                if costo_km is not None:
                    df_llantas.loc[df_llantas['id_llanta'] == id_llanta, costo_col] = costo_km
                else:
                    # Si no hay suficientes datos, dejar en 0 o None
                    if costo_col in df_llantas.columns:
                        df_llantas.loc[df_llantas['id_llanta'] == id_llanta, costo_col] = None
        
        escribir_hoja(SHEET_LLANTAS, df_llantas)
        return True
    
    except Exception as e:
        return False

def tiene_acceso_cliente(nit_cliente):
    """Verifica si el usuario tiene acceso al cliente especificado"""
    nivel = st.session_state.get('nivel', 999)

    # Solo nivel 1 (Admin) tiene acceso a todos los clientes
    if nivel == 1:
        return True

    # Niveles 2, 3 y 4 solo acceden a clientes asignados
    if nivel in [2, 3, 4]:
        clientes_asignados = st.session_state.get('clientes_asignados', '')
        if clientes_asignados:
            lista_clientes = [c.strip() for c in clientes_asignados.split(',')]
            return str(nit_cliente) in lista_clientes
        return False

    return False

def obtener_clientes_accesibles():
    """Retorna lista de NITs de clientes a los que el usuario tiene acceso"""
    nivel = st.session_state.get('nivel', 999)

    # Solo nivel 1 (Admin) ve todos los clientes
    if nivel == 1:
        df_clientes = leer_hoja(SHEET_CLIENTES)
        return df_clientes['nit'].tolist() if not df_clientes.empty else []

    # Niveles 2, 3 y 4 solo ven clientes asignados
    if nivel in [2, 3, 4]:
        clientes_asignados = st.session_state.get('clientes_asignados', '')
        # Asegurar que sea string válido (puede ser NaN, None, float)
        if clientes_asignados and pd.notna(clientes_asignados) and isinstance(clientes_asignados, str):
            return [c.strip() for c in clientes_asignados.split(',') if c.strip()]
        return []

    return []

def obtener_operarios_cliente(nit_cliente):
    """Retorna lista de operarios (usuarios nivel 3) asignados a un cliente específico"""
    df_usuarios = leer_hoja(SHEET_USUARIOS)

    if df_usuarios.empty:
        return []

    operarios = []
    for idx, row in df_usuarios.iterrows():
        nivel = row.get('nivel', 0)
        # Solo operarios (nivel 3)
        if int(nivel) == 3:
            clientes_asignados = row.get('clientes_asignados', '')
            if clientes_asignados and pd.notna(clientes_asignados):
                lista_clientes = [c.strip() for c in str(clientes_asignados).split(',') if c.strip()]
                if str(nit_cliente) in lista_clientes:
                    nombre = row.get('nombre', row.get('usuario', 'Sin nombre'))
                    operarios.append(nombre)

    return operarios

def obtener_id_cliente(nit_cliente):
    """Obtiene el id_cliente a partir del NIT. Retorna el id_cliente o 'XX00' si no existe."""
    df_clientes = leer_hoja(SHEET_CLIENTES)
    if df_clientes.empty or 'id_cliente' not in df_clientes.columns:
        return 'XX00'
    cliente_data = df_clientes[df_clientes['nit'] == nit_cliente]
    if cliente_data.empty:
        return 'XX00'
    id_cliente = str(cliente_data['id_cliente'].values[0]).strip()
    return id_cliente if id_cliente and id_cliente != 'nan' else 'XX00'

def generar_id_cliente(nombre_cliente, df_clientes):
    """
    Genera ID de cliente: 2 primeras letras del nombre + consecutivo 2 dígitos.
    Ejemplo: TR01, TR02, ME01
    """
    import unicodedata

    nombre_limpio = unicodedata.normalize('NFD', nombre_cliente.upper())
    nombre_limpio = ''.join(c for c in nombre_limpio if unicodedata.category(c) != 'Mn')
    nombre_limpio = ''.join(c for c in nombre_limpio if c.isalpha())

    prefijo = nombre_limpio[:2] if len(nombre_limpio) >= 2 else nombre_limpio.ljust(2, 'X')

    # Buscar máximo consecutivo GLOBAL entre todos los clientes
    max_consecutivo = 0
    if not df_clientes.empty and 'id_cliente' in df_clientes.columns:
        for id_val in df_clientes['id_cliente'].values:
            if pd.notna(id_val):
                id_str = str(id_val).strip()
                # Extraer el número final (últimos dígitos) de cualquier id_cliente
                num_str = ''
                for c in reversed(id_str):
                    if c.isdigit():
                        num_str = c + num_str
                    else:
                        break
                if num_str:
                    try:
                        num = int(num_str)
                        if num > max_consecutivo:
                            max_consecutivo = num
                    except ValueError:
                        pass

    nuevo_id = f"{prefijo}{max_consecutivo + 1:02d}"
    return nuevo_id

def _max_consecutivo_por_prefijo(df, col_id, prefijo_completo):
    """Busca el máximo consecutivo en una columna para un prefijo dado (ej: TR01_V)."""
    max_num = 0
    if not df.empty and col_id in df.columns:
        for id_val in df[col_id].values:
            if pd.notna(id_val):
                id_str = str(id_val).strip()
                if id_str.startswith(prefijo_completo):
                    resto = id_str[len(prefijo_completo):]
                    # Extraer solo los dígitos iniciales (antes de _ o texto opcional)
                    num_str = ''
                    for c in resto:
                        if c.isdigit():
                            num_str += c
                        else:
                            break
                    if num_str:
                        try:
                            num = int(num_str)
                            if num > max_num:
                                max_num = num
                        except ValueError:
                            pass
    return max_num

def generar_id_unico(nit_cliente, frente=None, id_usuario=None, tipo='vehiculo'):
    """
    Genera ID único para vehículos y llantas basado en id_cliente.
    Formato vehículo: {id_cliente}_V{2 dígitos}           → TR01_V01
    Formato llanta:   {id_cliente}_{frente}_LL{2 dígitos}  → TR01_BO_LL01
    """
    import unicodedata
    id_cliente = obtener_id_cliente(nit_cliente)

    if tipo == 'vehiculo':
        prefijo_completo = id_cliente + '_V'
        df_datos = leer_hoja(SHEET_VEHICULOS)
        col_id = 'id_vehiculo'
    else:
        if frente:
            f_limpio = unicodedata.normalize('NFD', str(frente).upper())
            f_limpio = ''.join(c for c in f_limpio if unicodedata.category(c) != 'Mn')
            f_limpio = ''.join(c for c in f_limpio if c.isalpha())
            frente_abbrev = f_limpio[:2] if len(f_limpio) >= 2 else f_limpio.ljust(2, 'X')
        else:
            frente_abbrev = 'GE'
        prefijo_completo = f"{id_cliente}_{frente_abbrev}_LL"
        df_datos = leer_hoja(SHEET_LLANTAS)
        col_id = 'id_llanta'

    max_num = _max_consecutivo_por_prefijo(df_datos, col_id, prefijo_completo)
    return f"{prefijo_completo}{max_num + 1:02d}"

def generar_id_servicio(nit_cliente, frente=None):
    """
    Genera ID de servicio basado en id_cliente.
    Formato: {id_cliente}_S{4 dígitos}  → TR01_S0001
    """
    id_cliente = obtener_id_cliente(nit_cliente)
    df_servicios = leer_hoja(SHEET_SERVICIOS)

    prefijo_completo = id_cliente + '_S'
    max_num = _max_consecutivo_por_prefijo(df_servicios, 'id_servicio', prefijo_completo)

    return f"{prefijo_completo}{max_num + 1:04d}"

def generar_id_alineacion(nit_cliente):
    """
    Genera ID de alineación basado en id_cliente.
    Formato: {id_cliente}_A{3 dígitos}  → TR01_A001
    """
    id_cliente = obtener_id_cliente(nit_cliente)
    df_alineaciones = leer_hoja(SHEET_ALINEACIONES)

    prefijo_completo = id_cliente + '_A'
    max_num = _max_consecutivo_por_prefijo(df_alineaciones, 'id_alineacion', prefijo_completo)

    return f"{prefijo_completo}{max_num + 1:03d}"

def generar_id_movimiento(nit_cliente):
    """
    Genera ID de movimiento basado en id_cliente.
    Formato: {id_cliente}_M{3 dígitos}  → TR01_M001
    """
    id_cliente = obtener_id_cliente(nit_cliente)
    df_movimientos = leer_hoja(SHEET_MOVIMIENTOS)

    prefijo_completo = id_cliente + '_M'
    max_num = _max_consecutivo_por_prefijo(df_movimientos, 'id_movimiento', prefijo_completo)

    return f"{prefijo_completo}{max_num + 1:03d}"

# ============= SISTEMA DE AUTENTICACIÓN =============
def login():
    """Sistema de login con niveles de usuario"""
    st.title("🔐 Sistema Integrado de Llantas")
    st.subheader("Inicio de Sesión")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        
        if st.button("Iniciar Sesión", use_container_width=True):
            df_usuarios = leer_hoja(SHEET_USUARIOS)
            user_data = df_usuarios[(df_usuarios['usuario'] == usuario) & (df_usuarios['password'] == password)]
            
            if not user_data.empty:
                st.session_state['logged_in'] = True
                st.session_state['usuario'] = usuario
                st.session_state['nivel'] = int(user_data.iloc[0]['nivel'])
                st.session_state['nombre'] = user_data.iloc[0]['nombre']

                # Guardar clientes_asignados (ya viene limpio desde leer_hoja)
                if 'clientes_asignados' in user_data.columns:
                    clientes_valor = user_data.iloc[0]['clientes_asignados']
                    # Usar limpiar_clientes_asignados por seguridad
                    st.session_state['clientes_asignados'] = limpiar_clientes_asignados(clientes_valor)
                else:
                    st.session_state['clientes_asignados'] = ''

                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

def verificar_permiso(nivel_requerido):
    """Verifica si el usuario tiene el nivel necesario"""
    if st.session_state.get('nivel', 999) > nivel_requerido:
        st.error(f"⛔ No tienes permisos suficientes. Se requiere nivel {nivel_requerido} o superior.")
        return False
    return True

# ============= FUNCIÓN: SUBIR DATOS CSV =============
def subir_datos_csv():
    """Función para cargar datos desde archivos CSV usando append"""

    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("📤 Subir Datos desde CSV")

    if not verificar_permiso(1):  # Solo Administrador puede subir CSV
        return
    
    st.subheader("Selecciona qué datos deseas cargar")
    
    tipo_dato = st.selectbox(
        "Tipo de Datos",
        options=["Clientes", "Vehículos", "Llantas", "Servicios", "Movimientos"]
    )
    
    archivo = st.file_uploader(f"Subir archivo CSV de {tipo_dato}", type=['csv'])
    
    if archivo is not None:
        try:
            df_nuevo = pd.read_csv(archivo, encoding='utf-8')
            
            st.write("**Vista previa de los datos:**")
            st.dataframe(df_nuevo.head(), use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Confirmar y Agregar Datos", type="primary"):
                    if tipo_dato == "Clientes":
                        df_existente = leer_hoja(SHEET_CLIENTES)
                        df_combinado = pd.concat([df_existente, df_nuevo], ignore_index=True)
                        escribir_hoja(SHEET_CLIENTES, df_combinado)
                    elif tipo_dato == "Vehículos":
                        df_existente = leer_hoja(SHEET_VEHICULOS)
                        df_combinado = pd.concat([df_existente, df_nuevo], ignore_index=True)
                        escribir_hoja(SHEET_VEHICULOS, df_combinado)
                    elif tipo_dato == "Llantas":
                        df_existente = leer_hoja(SHEET_LLANTAS)
                        df_combinado = pd.concat([df_existente, df_nuevo], ignore_index=True)
                        escribir_hoja(SHEET_LLANTAS, df_combinado)
                    elif tipo_dato == "Servicios":
                        df_existente = leer_hoja(SHEET_SERVICIOS)
                        df_combinado = pd.concat([df_existente, df_nuevo], ignore_index=True)
                        escribir_hoja(SHEET_SERVICIOS, df_combinado)
                    elif tipo_dato == "Movimientos":
                        df_existente = leer_hoja(SHEET_MOVIMIENTOS)
                        df_combinado = pd.concat([df_existente, df_nuevo], ignore_index=True)
                        escribir_hoja(SHEET_MOVIMIENTOS, df_combinado)

                    st.success(f"✅ Datos de {tipo_dato} agregados exitosamente")
                    st.rerun()
            
            with col2:
                if st.button("❌ Cancelar"):
                    st.rerun()
                    
        except Exception as e:
            st.error(f"Error al leer el archivo: {str(e)}")
            st.info("Asegúrate de que el CSV tenga las columnas correctas y esté codificado en UTF-8")

# ============= FUNCIÓN: ELIMINAR Y CORREGIR DATOS =============
def eliminar_corregir_datos():
    """Función para eliminar o corregir datos"""
    
    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("✏️ Eliminar o Corregir Datos")
    
    if not verificar_permiso(2):
        return
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚛 Vehículos", "⚙️ Llantas", "🛠️ Servicios", "👤 Clientes", "📦 Movimientos"])
    
    with tab1:
        st.subheader("Gestión de Vehículos")
        df_vehiculos = leer_hoja(SHEET_VEHICULOS)
        
        if not df_vehiculos.empty:
            clientes_acceso = obtener_clientes_accesibles()
            df_vehiculos = filtrar_por_clientes(df_vehiculos, 'nit_cliente', clientes_acceso)
            
            if not df_vehiculos.empty:
                id_editar = st.selectbox("Seleccionar Vehículo",
                    df_vehiculos['id_vehiculo'].values,
                    format_func=lambda x: f"ID {x} - {df_vehiculos[df_vehiculos['id_vehiculo']==x]['placa_vehiculo'].values[0]}",
                    key="select_vehiculo_editar")
                
                vehiculo = df_vehiculos[df_vehiculos['id_vehiculo'] == id_editar].iloc[0]

                st.info(f"**Vehículo seleccionado:** {id_editar} | Placa: {vehiculo.get('placa_vehiculo', 'N/A')} | Marca: {vehiculo.get('marca', 'N/A')} | Línea: {vehiculo.get('linea', 'N/A')} | Estado: {vehiculo.get('estado', 'N/A')}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    nueva_marca = st.text_input("Marca", value=vehiculo.get('marca', ''), key=f"edit_marca_vehiculo_{id_editar}")
                    nuevo_estado = st.selectbox("Estado",
                        options=['no_asignado', 'activo', 'fuera_de_servicio'],
                        index=['no_asignado', 'activo', 'fuera_de_servicio'].index(vehiculo.get('estado', 'no_asignado')),
                        key=f"edit_estado_vehiculo_{id_editar}")

                with col2:
                    nueva_linea = st.text_input("Línea", value=vehiculo.get('linea', ''), key=f"edit_linea_vehiculo_{id_editar}")
                    nuevo_km_inicial = st.number_input("Kilometraje Inicial", value=float(vehiculo.get('kilometraje_inicial', 0)), key=f"edit_km_vehiculo_{id_editar}")

                with col3:
                    nueva_tipologia = st.text_input("Tipología", value=vehiculo.get('tipologia', ''), key=f"edit_tipologia_vehiculo_{id_editar}")
                    nuevo_calculo = st.selectbox("Cálculo KMs",
                        options=['odometro', 'promedio', 'tabla'],
                        index=['odometro', 'promedio', 'tabla'].index(vehiculo.get('calculo_kms', 'odometro')),
                        key=f"edit_calculo_vehiculo_{id_editar}")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("💾 Guardar Cambios", key="guardar_vehiculo"):
                        df_todos = leer_hoja(SHEET_VEHICULOS)
                        df_todos.loc[df_todos['id_vehiculo'] == id_editar, 'marca'] = nueva_marca
                        df_todos.loc[df_todos['id_vehiculo'] == id_editar, 'linea'] = nueva_linea
                        df_todos.loc[df_todos['id_vehiculo'] == id_editar, 'tipologia'] = nueva_tipologia
                        df_todos.loc[df_todos['id_vehiculo'] == id_editar, 'estado'] = nuevo_estado
                        df_todos.loc[df_todos['id_vehiculo'] == id_editar, 'kilometraje_inicial'] = nuevo_km_inicial
                        df_todos.loc[df_todos['id_vehiculo'] == id_editar, 'calculo_kms'] = nuevo_calculo
                        escribir_hoja(SHEET_VEHICULOS, df_todos)
                        st.success("✅ Vehículo actualizado con éxito")
                        st.rerun()
                
                with col_btn2:
                    if st.button("🗑️ Eliminar Vehículo", key="eliminar_vehiculo"):
                        df_todos = leer_hoja(SHEET_VEHICULOS)
                        df_todos = df_todos[df_todos['id_vehiculo'] != id_editar]
                        escribir_hoja(SHEET_VEHICULOS, df_todos)
                        st.success("✅ Vehículo eliminado con éxito")
                        st.rerun()
            else:
                st.info("No tienes vehículos accesibles")
        else:
            st.info("No hay vehículos registrados")
    
    with tab2:
        st.subheader("Gestión de Llantas")
        df_llantas = leer_hoja(SHEET_LLANTAS)
        
        if not df_llantas.empty:
            clientes_acceso = obtener_clientes_accesibles()
            df_llantas = filtrar_por_clientes(df_llantas, 'nit_cliente', clientes_acceso)
            
            if not df_llantas.empty:
                id_editar = st.selectbox("Seleccionar Llanta", df_llantas['id_llanta'].values, key="select_llanta_editar")
                
                llanta = df_llantas[df_llantas['id_llanta'] == id_editar].iloc[0]

                st.info(f"**Llanta seleccionada:** {id_editar} | Marca: {llanta.get('marca_llanta', 'N/A')} | Ref: {llanta.get('referencia', 'N/A')} | Dimensión: {llanta.get('dimension', 'N/A')} | Disponibilidad: {llanta.get('disponibilidad', 'N/A')}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    nueva_marca = st.text_input("Marca", value=llanta.get('marca_llanta', ''), key=f"edit_marca_llanta_{id_editar}")
                    nueva_referencia = st.text_input("Referencia", value=llanta.get('referencia', ''), key=f"edit_referencia_llanta_{id_editar}")

                with col2:
                    nueva_dimension = st.text_input("Dimensión", value=llanta.get('dimension', ''), key=f"edit_dimension_llanta_{id_editar}")
                    precio_v1 = st.number_input("Precio Vida 1", value=float(llanta.get('precio_vida1', 0)), key=f"edit_precio_v1_llanta_{id_editar}")

                with col3:
                    precio_v2 = st.number_input("Precio Vida 2", value=float(llanta.get('precio_vida2', 0)), key=f"edit_precio_v2_llanta_{id_editar}")
                    precio_v3 = st.number_input("Precio Vida 3", value=float(llanta.get('precio_vida3', 0)), key=f"edit_precio_v3_llanta_{id_editar}")

                precio_v4 = st.number_input("Precio Vida 4", value=float(llanta.get('precio_vida4', 0)), key=f"edit_precio_v4_llanta_{id_editar}")
                
                st.info("💡 Los costos/km se recalculan automáticamente al guardar cambios")
                
                if st.button("💾 Guardar Cambios", key="guardar_llanta"):
                    df_todos = leer_hoja(SHEET_LLANTAS)
                    df_todos.loc[df_todos['id_llanta'] == id_editar, 'marca_llanta'] = nueva_marca
                    df_todos.loc[df_todos['id_llanta'] == id_editar, 'referencia'] = nueva_referencia
                    df_todos.loc[df_todos['id_llanta'] == id_editar, 'dimension'] = nueva_dimension
                    df_todos.loc[df_todos['id_llanta'] == id_editar, 'precio_vida1'] = precio_v1
                    df_todos.loc[df_todos['id_llanta'] == id_editar, 'precio_vida2'] = precio_v2
                    df_todos.loc[df_todos['id_llanta'] == id_editar, 'precio_vida3'] = precio_v3
                    df_todos.loc[df_todos['id_llanta'] == id_editar, 'precio_vida4'] = precio_v4
                    escribir_hoja(SHEET_LLANTAS, df_todos)
                    
                    # Recalcular costos/km después de guardar
                    actualizar_costos_km_llanta(id_editar)
                    
                    st.success("✅ Llanta actualizada con éxito")
                    st.rerun()
                
                if st.button("🗑️ Eliminar Llanta", key="eliminar_llanta"):
                    df_todos = leer_hoja(SHEET_LLANTAS)
                    df_todos = df_todos[df_todos['id_llanta'] != id_editar]
                    escribir_hoja(SHEET_LLANTAS, df_todos)
                    st.success("✅ Llanta eliminada con éxito")
                    st.rerun()
            else:
                st.info("No tienes llantas accesibles")
        else:
            st.info("No hay llantas registradas")
    
    with tab3:
        st.subheader("Gestión de Servicios")
        df_servicios = leer_hoja(SHEET_SERVICIOS)

        if not df_servicios.empty:
            id_servicio_editar = st.selectbox("Seleccionar Servicio", df_servicios['id_servicio'].values, key="select_servicio_editar")

            servicio = df_servicios[df_servicios['id_servicio'] == id_servicio_editar].iloc[0]

            st.info(f"**Servicio seleccionado:** {id_servicio_editar} | Llanta: {servicio.get('id_llanta', 'N/A')} | Placa: {servicio.get('placa_vehiculo', 'N/A')} | Fecha: {servicio.get('fecha', 'N/A')} | Tipo: {servicio.get('tipo_servicio', 'N/A')}")

            col1, col2, col3 = st.columns(3)

            with col1:
                # Fecha del servicio
                fecha_actual = servicio.get('fecha', '')
                try:
                    fecha_parsed = datetime.strptime(str(fecha_actual), "%d/%m/%Y").date() if fecha_actual else datetime.now().date()
                except:
                    fecha_parsed = datetime.now().date()
                nueva_fecha = st.date_input("Fecha", value=fecha_parsed, key=f"edit_fecha_servicio_{id_servicio_editar}")

                # Kilometraje
                km_actual = int(servicio.get('kilometraje', 0)) if pd.notna(servicio.get('kilometraje')) else 0
                nuevo_km = st.number_input("Kilometraje", min_value=0, value=km_actual, key=f"edit_km_servicio_{id_servicio_editar}")

            with col2:
                st.write("**Profundidades (mm)**")
                prof1_actual = float(servicio.get('profundidad_1', 10.0)) if pd.notna(servicio.get('profundidad_1')) else 10.0
                prof2_actual = float(servicio.get('profundidad_2', 10.0)) if pd.notna(servicio.get('profundidad_2')) else 10.0
                prof3_actual = float(servicio.get('profundidad_3', 10.0)) if pd.notna(servicio.get('profundidad_3')) else 10.0

                nueva_prof1 = st.number_input("Profundidad 1", min_value=0.0, max_value=30.0, value=prof1_actual, step=0.5, key=f"edit_prof1_{id_servicio_editar}")
                nueva_prof2 = st.number_input("Profundidad 2", min_value=0.0, max_value=30.0, value=prof2_actual, step=0.5, key=f"edit_prof2_{id_servicio_editar}")
                nueva_prof3 = st.number_input("Profundidad 3", min_value=0.0, max_value=30.0, value=prof3_actual, step=0.5, key=f"edit_prof3_{id_servicio_editar}")

            with col3:
                st.write("**Servicios Realizados**")
                edit_rotacion = st.checkbox("Rotación", value=(servicio.get('rotacion', 'No') == 'Sí'), key=f"edit_rotacion_{id_servicio_editar}")
                if edit_rotacion:
                    edit_pos_nueva = st.text_input("Nueva Posición", value=servicio.get('posicion_nueva', ''), key=f"edit_pos_nueva_{id_servicio_editar}")
                else:
                    edit_pos_nueva = ""
                edit_balanceo = st.checkbox("Balanceo", value=(servicio.get('balanceo', 'No') == 'Sí'), key=f"edit_balanceo_{id_servicio_editar}")
                edit_reparacion = st.checkbox("Reparación", value=(servicio.get('reparacion', 'No') == 'Sí'), key=f"edit_reparacion_{id_servicio_editar}")
                edit_despinche = st.checkbox("Despinche", value=(servicio.get('despinche', 'No') == 'Sí'), key=f"edit_despinche_{id_servicio_editar}")
                edit_regrabacion = st.checkbox("Regrabación", value=(servicio.get('regrabacion', 'No') == 'Sí'), key=f"edit_regrabacion_{id_servicio_editar}")
                edit_torqueo = st.checkbox("Torqueo", value=(servicio.get('torqueo', 'No') == 'Sí'), key=f"edit_torqueo_{id_servicio_editar}")

            # Comentario FVU (campo adicional)
            comentario_actual = servicio.get('comentario_fvu', '') if pd.notna(servicio.get('comentario_fvu')) else ''
            nuevo_comentario = st.text_area("Comentario FVU", value=comentario_actual, key=f"edit_comentario_fvu_{id_servicio_editar}")

            col_btn1, col_btn2 = st.columns(2)

            with col_btn1:
                if st.button("💾 Guardar Cambios", key="guardar_servicio", type="primary"):
                    if edit_rotacion and not edit_pos_nueva:
                        st.error("Si hay rotación, debes especificar la nueva posición")
                    else:
                        # Actualizar los campos editables
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'fecha'] = nueva_fecha.strftime("%d/%m/%Y")
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'kilometraje'] = nuevo_km
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'profundidad_1'] = nueva_prof1
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'profundidad_2'] = nueva_prof2
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'profundidad_3'] = nueva_prof3
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'rotacion'] = 'Sí' if edit_rotacion else 'No'
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'posicion_nueva'] = edit_pos_nueva if edit_rotacion else ''
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'balanceo'] = 'Sí' if edit_balanceo else 'No'
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'reparacion'] = 'Sí' if edit_reparacion else 'No'
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'despinche'] = 'Sí' if edit_despinche else 'No'
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'regrabacion'] = 'Sí' if edit_regrabacion else 'No'
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'torqueo'] = 'Sí' if edit_torqueo else 'No'
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'comentario_fvu'] = nuevo_comentario

                        escribir_hoja(SHEET_SERVICIOS, df_servicios)

                        # Recalcular costos si cambió el kilometraje
                        id_llanta_servicio = servicio.get('id_llanta')
                        if id_llanta_servicio:
                            actualizar_costos_km_llanta(id_llanta_servicio)

                        st.success("✅ Servicio actualizado con éxito")
                        st.rerun()

            with col_btn2:
                if st.button("🗑️ Eliminar Servicio", key="eliminar_servicio"):
                    df_servicios = df_servicios[df_servicios['id_servicio'] != id_servicio_editar]
                    escribir_hoja(SHEET_SERVICIOS, df_servicios)
                    st.success("✅ Servicio eliminado con éxito")
                    st.rerun()

            # Mostrar información de referencia
            st.divider()
            st.caption(f"ID Llanta: {servicio.get('id_llanta', 'N/A')} | Placa: {servicio.get('placa_vehiculo', 'N/A')} | Posición original: {servicio.get('posicion', 'N/A')} | Vida: {servicio.get('vida', 'N/A')}")
        else:
            st.info("No hay servicios registrados")
    
    with tab4:
        st.subheader("Gestión de Clientes")
        
        if st.session_state.get('nivel') != 1:
            st.warning("⚠️ Solo el Administrador puede editar clientes")
            return
        
        df_clientes = leer_hoja(SHEET_CLIENTES)
        
        if not df_clientes.empty:
            nit_editar = st.selectbox("Seleccionar Cliente", df_clientes['nit'].values, key="select_cliente_editar")
            
            cliente = df_clientes[df_clientes['nit'] == nit_editar].iloc[0]

            st.info(f"**Cliente seleccionado:** NIT: {nit_editar} | Nombre: {cliente.get('nombre_cliente', 'N/A')}")

            nuevo_nombre = st.text_input("Nombre Cliente", value=cliente['nombre_cliente'], key=f"edit_nombre_cliente_{nit_editar}")
            
            if st.button("💾 Guardar Cambios", key="guardar_cliente"):
                df_clientes.loc[df_clientes['nit'] == nit_editar, 'nombre_cliente'] = nuevo_nombre
                escribir_hoja(SHEET_CLIENTES, df_clientes)
                st.success("✅ Cliente actualizado con éxito")
                st.rerun()
            
            if st.button("🗑️ Eliminar Cliente", key="eliminar_cliente"):
                df_clientes = df_clientes[df_clientes['nit'] != nit_editar]
                escribir_hoja(SHEET_CLIENTES, df_clientes)
                st.success("✅ Cliente eliminado con éxito")
                st.rerun()
        else:
            st.info("No hay clientes registrados")

    with tab5:
        st.subheader("Gestión de Movimientos")

        df_movimientos = leer_hoja(SHEET_MOVIMIENTOS)

        if not df_movimientos.empty:
            # Filtrar por clientes accesibles
            clientes_acceso = obtener_clientes_accesibles()
            if st.session_state.get('nivel') != 1:
                df_llantas_temp = leer_hoja(SHEET_LLANTAS)
                llantas_cliente = df_llantas_temp[df_llantas_temp['nit_cliente'].isin(clientes_acceso)]['id_llanta'].tolist()
                df_movimientos = df_movimientos[df_movimientos['id_llanta'].isin(llantas_cliente)]

            if not df_movimientos.empty:
                id_mov_editar = st.selectbox(
                    "Seleccionar Movimiento",
                    options=df_movimientos['id_movimiento'].values,
                    format_func=lambda x: f"ID {x} - Llanta {df_movimientos[df_movimientos['id_movimiento']==x]['id_llanta'].values[0]} - {df_movimientos[df_movimientos['id_movimiento']==x]['tipo'].values[0]} ({df_movimientos[df_movimientos['id_movimiento']==x]['fecha'].values[0]})",
                    key="select_movimiento_editar"
                )

                movimiento = df_movimientos[df_movimientos['id_movimiento'] == id_mov_editar].iloc[0]

                st.info(f"**Movimiento seleccionado:** {id_mov_editar} | Llanta: {movimiento.get('id_llanta', 'N/A')} | Tipo: {movimiento.get('tipo', 'N/A')} | Placa: {movimiento.get('placa_vehiculo', 'N/A')} | Fecha: {movimiento.get('fecha', 'N/A')}")

                col1, col2, col3 = st.columns(3)

                with col1:
                    # Tipo de movimiento
                    tipos_mov = ['montaje', 'desmontaje', 'aprobacion_reencauche', 'rotacion', 'otro']
                    tipo_actual = movimiento.get('tipo', 'otro')
                    tipo_idx = tipos_mov.index(tipo_actual) if tipo_actual in tipos_mov else 4
                    nuevo_tipo = st.selectbox("Tipo", options=tipos_mov, index=tipo_idx, key=f"edit_tipo_mov_{id_mov_editar}")

                    # Vida
                    vida_mov = int(movimiento.get('vida', 1)) if pd.notna(movimiento.get('vida')) else 1
                    vida_mov = max(1, vida_mov)  # Asegurar que sea al menos 1
                    # Limpiar session_state si tiene valor inválido
                    vida_key = f"edit_vida_mov_{id_mov_editar}"
                    if vida_key in st.session_state and st.session_state[vida_key] < 1:
                        del st.session_state[vida_key]
                    nueva_vida = st.number_input("Vida", min_value=1, max_value=4, value=vida_mov, key=vida_key)

                with col2:
                    # Placa vehículo
                    placa_mov = movimiento.get('placa_vehiculo', '') if pd.notna(movimiento.get('placa_vehiculo')) else ''
                    nueva_placa = st.text_input("Placa Vehículo", value=placa_mov, key=f"edit_placa_mov_{id_mov_editar}")

                    # Posición
                    pos_mov = movimiento.get('posicion', '') if pd.notna(movimiento.get('posicion')) else ''
                    nueva_posicion = st.text_input("Posición", value=pos_mov, key=f"edit_pos_mov_{id_mov_editar}")

                with col3:
                    # Kilometraje
                    km_mov = int(movimiento.get('kilometraje', 0)) if pd.notna(movimiento.get('kilometraje')) else 0
                    nuevo_km = st.number_input("Kilometraje", min_value=0, value=km_mov, key=f"edit_km_mov_{id_mov_editar}")

                    # Nueva disponibilidad
                    disp_mov = movimiento.get('nueva_disponibilidad', '') if pd.notna(movimiento.get('nueva_disponibilidad')) else ''
                    nueva_disp = st.text_input("Nueva Disponibilidad", value=disp_mov, key=f"edit_disp_mov_{id_mov_editar}")

                # Datos de reencauche (si aplica)
                st.write("**Datos de Reencauche (si aplica):**")
                col4, col5, col6 = st.columns(3)

                with col4:
                    marca_reenc = movimiento.get('marca_reencauche', '') if pd.notna(movimiento.get('marca_reencauche')) else ''
                    nueva_marca_reenc = st.text_input("Marca Reencauche", value=marca_reenc, key=f"edit_marca_reenc_{id_mov_editar}")

                with col5:
                    ref_reenc = movimiento.get('ref_reencauche', '') if pd.notna(movimiento.get('ref_reencauche')) else ''
                    nueva_ref_reenc = st.text_input("Ref. Reencauche", value=ref_reenc, key=f"edit_ref_reenc_{id_mov_editar}")

                with col6:
                    precio_reenc = float(movimiento.get('precio_reencauche', 0)) if pd.notna(movimiento.get('precio_reencauche')) else 0
                    nuevo_precio_reenc = st.number_input("Precio Reencauche", min_value=0.0, value=precio_reenc, key=f"edit_precio_reenc_{id_mov_editar}")

                # Observaciones
                obs_mov = movimiento.get('observaciones', '') if pd.notna(movimiento.get('observaciones')) else ''
                nuevas_obs = st.text_area("Observaciones", value=obs_mov, key=f"edit_obs_mov_{id_mov_editar}")

                col_btn1, col_btn2 = st.columns(2)

                with col_btn1:
                    if st.button("💾 Guardar Cambios", key="guardar_movimiento", type="primary"):
                        df_mov_todos = leer_hoja(SHEET_MOVIMIENTOS)
                        df_mov_todos.loc[df_mov_todos['id_movimiento'] == id_mov_editar, 'tipo'] = nuevo_tipo
                        df_mov_todos.loc[df_mov_todos['id_movimiento'] == id_mov_editar, 'vida'] = nueva_vida
                        df_mov_todos.loc[df_mov_todos['id_movimiento'] == id_mov_editar, 'placa_vehiculo'] = nueva_placa
                        df_mov_todos.loc[df_mov_todos['id_movimiento'] == id_mov_editar, 'posicion'] = nueva_posicion
                        df_mov_todos.loc[df_mov_todos['id_movimiento'] == id_mov_editar, 'kilometraje'] = nuevo_km
                        df_mov_todos.loc[df_mov_todos['id_movimiento'] == id_mov_editar, 'nueva_disponibilidad'] = nueva_disp
                        df_mov_todos.loc[df_mov_todos['id_movimiento'] == id_mov_editar, 'marca_reencauche'] = nueva_marca_reenc
                        df_mov_todos.loc[df_mov_todos['id_movimiento'] == id_mov_editar, 'ref_reencauche'] = nueva_ref_reenc
                        df_mov_todos.loc[df_mov_todos['id_movimiento'] == id_mov_editar, 'precio_reencauche'] = nuevo_precio_reenc
                        df_mov_todos.loc[df_mov_todos['id_movimiento'] == id_mov_editar, 'observaciones'] = nuevas_obs
                        escribir_hoja(SHEET_MOVIMIENTOS, df_mov_todos)
                        st.success("✅ Movimiento actualizado con éxito")
                        st.rerun()

                with col_btn2:
                    if st.button("🗑️ Eliminar Movimiento", key="eliminar_movimiento"):
                        df_mov_todos = leer_hoja(SHEET_MOVIMIENTOS)
                        df_mov_todos = df_mov_todos[df_mov_todos['id_movimiento'] != id_mov_editar]
                        escribir_hoja(SHEET_MOVIMIENTOS, df_mov_todos)
                        st.success("✅ Movimiento eliminado con éxito")
                        st.rerun()

                # Mostrar información de referencia
                st.divider()
                st.caption(f"ID Llanta: {movimiento.get('id_llanta', 'N/A')} | Fecha: {movimiento.get('fecha', 'N/A')} | Usuario: {movimiento.get('usuario', 'N/A')}")
            else:
                st.info("No tienes movimientos accesibles")
        else:
            st.info("No hay movimientos registrados")

# ============= FUNCIÓN: LLANTAS DISPONIBLES =============
def ver_llantas_disponibles():
    """Función para ver todas las llantas y su disponibilidad"""
    
    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("🔍 Estado de Llantas")
    
    df_llantas = leer_hoja(SHEET_LLANTAS)
    
    if df_llantas.empty:
        st.info("No hay llantas registradas")
        return
    
    clientes_acceso = obtener_clientes_accesibles()
    df_llantas = filtrar_por_clientes(df_llantas, 'nit_cliente', clientes_acceso)
    
    if df_llantas.empty or 'disponibilidad' not in df_llantas.columns:
        st.info("No tienes llantas accesibles")
        return

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Ver Todas", "✅ Aprobar Reencauches", "💰 Análisis de Costos", "💲 Asignación de Precios"])

    with tab1:
        st.subheader("Inventario Completo de Llantas")

        # --- FILTROS ---
        df_clientes_f = leer_hoja(SHEET_CLIENTES)
        df_clientes_f = filtrar_por_clientes(df_clientes_f, 'nit', clientes_acceso)
        df_vehiculos_f = leer_hoja(SHEET_VEHICULOS)
        df_vehiculos_f = filtrar_por_clientes(df_vehiculos_f, 'nit_cliente', clientes_acceso)

        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            opciones_clientes = ['Todos'] + list(df_clientes_f['nombre_cliente'].values) if not df_clientes_f.empty else ['Todos']
            filtro_cliente = st.selectbox("Cliente", options=opciones_clientes, key="estado_filtro_cliente")

        with col_f2:
            if filtro_cliente != 'Todos' and not df_clientes_f.empty:
                nit_filtro = df_clientes_f[df_clientes_f['nombre_cliente'] == filtro_cliente]['nit'].values[0]
                vehiculos_cliente = df_vehiculos_f[df_vehiculos_f['nit_cliente'] == nit_filtro]
                frentes_disponibles = ['Todos'] + list(vehiculos_cliente['frente'].unique()) if not vehiculos_cliente.empty and 'frente' in vehiculos_cliente.columns else ['Todos']
            else:
                frentes_disponibles = ['Todos']
            filtro_frente = st.selectbox("Frente", options=frentes_disponibles, key="estado_filtro_frente")

        with col_f3:
            opciones_disp = ['Todas'] + list(df_llantas['disponibilidad'].unique())
            filtro_disp = st.selectbox("Disponibilidad", options=opciones_disp, key="estado_filtro_disp")

        # --- APLICAR FILTROS ---
        df_filtrado = df_llantas.copy()

        if filtro_cliente != 'Todos' and not df_clientes_f.empty:
            nit_filtro = df_clientes_f[df_clientes_f['nombre_cliente'] == filtro_cliente]['nit'].values[0]
            df_filtrado = df_filtrado[df_filtrado['nit_cliente'] == nit_filtro]

            if filtro_frente != 'Todos':
                placas_frente = df_vehiculos_f[
                    (df_vehiculos_f['nit_cliente'] == nit_filtro) &
                    (df_vehiculos_f['frente'] == filtro_frente)
                ]['placa_vehiculo'].values
                col_placa = 'placa_actual' if 'placa_actual' in df_filtrado.columns else 'placa_vehiculo'
                df_filtrado = df_filtrado[df_filtrado[col_placa].isin(placas_frente)]

        if filtro_disp != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['disponibilidad'] == filtro_disp]

        # --- ENRIQUECER CON DATOS DE ÚLTIMO SERVICIO ---
        df_servicios_est = leer_hoja(SHEET_SERVICIOS)
        if not df_servicios_est.empty and 'id_llanta' in df_servicios_est.columns:
            col_orden = 'timestamp' if 'timestamp' in df_servicios_est.columns else 'fecha'
            ultimo_srv = df_servicios_est.sort_values(col_orden).groupby('id_llanta').last().reset_index()
            cols_srv = ['id_llanta']
            if 'kilometraje' in ultimo_srv.columns:
                ultimo_srv = ultimo_srv.rename(columns={'kilometraje': 'ultimo_km'})
                cols_srv.append('ultimo_km')
            if 'fecha' in ultimo_srv.columns:
                ultimo_srv = ultimo_srv.rename(columns={'fecha': 'fecha_ultimo_servicio'})
                cols_srv.append('fecha_ultimo_servicio')
            if len(cols_srv) > 1:
                df_filtrado = df_filtrado.merge(ultimo_srv[cols_srv], on='id_llanta', how='left')

        # --- COLUMNAS A MOSTRAR ---
        columnas_mostrar = ['id_llanta', 'marca_llanta', 'referencia', 'dimension', 'disponibilidad',
                           'placa_actual', 'posicion_actual', 'vida_actual',
                           'ultimo_km', 'fecha_ultimo_servicio',
                           'precio_vida1', 'precio_vida2', 'precio_vida3', 'precio_vida4',
                           'costo_km_vida1', 'costo_km_vida2', 'costo_km_vida3', 'costo_km_vida4']

        columnas_disponibles = [col for col in columnas_mostrar if col in df_filtrado.columns]
        st.dataframe(df_filtrado[columnas_disponibles], use_container_width=True, hide_index=True)
        st.caption(f"Total llantas: {len(df_filtrado)}")
    
    with tab2:
        st.subheader("✅ Aprobar Reencauches")

        if st.session_state.get('nivel', 99) != 1:
            st.warning("⚠️ Solo el administrador puede aprobar reencauches")
        else:
            llantas_reencauche = df_llantas[
                (df_llantas['disponibilidad'] == 'reencauche') &
                (df_llantas['estado_reencauche'] == 'condicionada_planta')
            ]

            if not llantas_reencauche.empty:
                st.info(f"📋 **{len(llantas_reencauche)} llantas** pendientes de aprobación de planta de reencauche")

                # Formulario de datos del reencauche
                st.write("### Datos del Reencauche")
                col_form1, col_form2, col_form3 = st.columns(3)

                with col_form1:
                    marca_reencauche = st.text_input("🏭 Marca Reencauche", placeholder="Ej: Vipal, Bandag")
                with col_form2:
                    referencia_reencauche = st.text_input("📋 Referencia", placeholder="Ej: VT120, BDR-AS")
                with col_form3:
                    precio_reencauche = st.number_input("💰 Precio Reencauche", min_value=0.0, value=0.0, step=10000.0)

                st.divider()
                st.write("### Seleccionar Llantas a Aprobar")
                st.caption("Marca las llantas que deseas aprobar con los datos ingresados arriba")

                # Inicializar estado de selección si no existe
                if 'llantas_seleccionadas' not in st.session_state:
                    st.session_state.llantas_seleccionadas = []

                # Mostrar tabla con checkboxes
                llantas_seleccionadas = []
                for idx, row in llantas_reencauche.iterrows():
                    id_llanta = row['id_llanta']
                    marca_original = row.get('marca_llanta', 'N/A')
                    referencia_original = row.get('referencia', 'N/A')
                    dimension = row.get('dimension', 'N/A')
                    vida_val = row.get('vida_actual', row.get('vida', 1))
                    vida_actual = int(vida_val) if pd.notna(vida_val) else 1
                    vida_nueva = vida_actual + 1

                    col_check, col_info, col_vida = st.columns([0.5, 3, 1])

                    with col_check:
                        seleccionada = st.checkbox("", key=f"sel_{id_llanta}", label_visibility="collapsed")
                        if seleccionada:
                            llantas_seleccionadas.append(id_llanta)

                    with col_info:
                        st.write(f"**ID {id_llanta}** - {marca_original} {referencia_original} ({dimension})")

                    with col_vida:
                        st.write(f"Vida {vida_actual} → **{vida_nueva}**")

                st.divider()

                # Botón de aprobación múltiple
                col_btn1, col_btn2 = st.columns([1, 3])
                with col_btn1:
                    aprobar_btn = st.button("✅ Aprobar Seleccionadas", type="primary", disabled=len(llantas_seleccionadas) == 0)

                with col_btn2:
                    if len(llantas_seleccionadas) > 0:
                        st.write(f"Se aprobarán **{len(llantas_seleccionadas)}** llantas")

                if aprobar_btn:
                    if not marca_reencauche:
                        st.error("⚠️ Debes ingresar la marca del reencauche")
                    elif not referencia_reencauche:
                        st.error("⚠️ Debes ingresar la referencia del reencauche")
                    elif precio_reencauche <= 0:
                        st.error("⚠️ Debes ingresar el precio del reencauche")
                    elif len(llantas_seleccionadas) == 0:
                        st.error("⚠️ Debes seleccionar al menos una llanta")
                    else:
                        df_todos = leer_hoja(SHEET_LLANTAS)
                        aprobadas = 0

                        for id_llanta in llantas_seleccionadas:
                            llanta_row = llantas_reencauche[llantas_reencauche['id_llanta'] == id_llanta].iloc[0]
                            # Usar vida_actual o vida según la columna disponible
                            vida_col = 'vida_actual' if 'vida_actual' in llanta_row.index else 'vida'
                            vida_actual = int(llanta_row[vida_col]) if pd.notna(llanta_row.get(vida_col)) else 1
                            vida_nueva = vida_actual + 1

                            # Guardar marca y referencia del reencauche
                            marca_ref_reencauche = f"{marca_reencauche} - {referencia_reencauche}"
                            if vida_nueva == 2:
                                df_todos.loc[df_todos['id_llanta'] == id_llanta, 'reencauche1'] = marca_ref_reencauche
                                df_todos.loc[df_todos['id_llanta'] == id_llanta, 'precio_vida2'] = precio_reencauche
                            elif vida_nueva == 3:
                                df_todos.loc[df_todos['id_llanta'] == id_llanta, 'reencauche2'] = marca_ref_reencauche
                                df_todos.loc[df_todos['id_llanta'] == id_llanta, 'precio_vida3'] = precio_reencauche
                            elif vida_nueva == 4:
                                df_todos.loc[df_todos['id_llanta'] == id_llanta, 'reencauche3'] = marca_ref_reencauche
                                df_todos.loc[df_todos['id_llanta'] == id_llanta, 'precio_vida4'] = precio_reencauche

                            df_todos.loc[df_todos['id_llanta'] == id_llanta, 'vida_actual'] = vida_nueva
                            df_todos.loc[df_todos['id_llanta'] == id_llanta, 'estado_reencauche'] = 'aprobado'
                            df_todos.loc[df_todos['id_llanta'] == id_llanta, 'disponibilidad'] = 'recambio'
                            df_todos.loc[df_todos['id_llanta'] == id_llanta, 'fecha_modificacion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                            # Crear movimiento de aprobación de reencauche
                            crear_movimiento(
                                id_llanta=id_llanta,
                                tipo='aprobacion_reencauche',
                                vida=vida_nueva,
                                marca_reencauche=marca_reencauche,
                                ref_reencauche=referencia_reencauche,
                                precio_reencauche=precio_reencauche
                            )
                            aprobadas += 1

                        escribir_hoja(SHEET_LLANTAS, df_todos)
                        st.success(f"✅ {aprobadas} llantas aprobadas - Marca: {marca_reencauche}, Ref: {referencia_reencauche}, Precio: ${precio_reencauche:,.0f}")
                        st.rerun()
            else:
                st.info("✨ No hay llantas pendientes de aprobación de reencauche")
    
    with tab3:
        st.subheader("💰 Análisis de Costos por Kilómetro")
        
        # Seleccionar llanta para análisis
        id_llanta_analisis = st.selectbox(
            "Seleccionar Llanta",
            options=df_llantas['id_llanta'].values,
            format_func=lambda x: f"ID {x} - {df_llantas[df_llantas['id_llanta']==x]['marca_llanta'].values[0]}"
        )
        
        llanta_sel = df_llantas[df_llantas['id_llanta'] == id_llanta_analisis].iloc[0]
        vida_val = llanta_sel.get('vida_actual', llanta_sel.get('vida', 1))
        vida_actual = int(vida_val) if pd.notna(vida_val) else 1

        st.write(f"**Llanta ID {id_llanta_analisis}** - Vida Actual: {vida_actual}")
        
        # Botón para recalcular costos
        if st.button("🔄 Recalcular Costos/km", type="secondary"):
            if actualizar_costos_km_llanta(id_llanta_analisis):
                st.success("✅ Costos recalculados exitosamente")
                st.rerun()
            else:
                st.error("❌ Error al recalcular costos")
        
        st.divider()
        
        # Mostrar costos por vida (valores guardados en CSV)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Precio Vida 1", f"${llanta_sel.get('precio_vida1', 0):,.0f}")
            costo_v1 = llanta_sel.get('costo_km_vida1', None)
            if costo_v1 and not pd.isna(costo_v1):
                st.metric("Costo/km Vida 1", f"${float(costo_v1):,.2f}")
            else:
                st.info("Sin datos suficientes")
        
        with col2:
            st.metric("Precio Vida 2", f"${llanta_sel.get('precio_vida2', 0):,.0f}")
            costo_v2 = llanta_sel.get('costo_km_vida2', None)
            if costo_v2 and not pd.isna(costo_v2):
                st.metric("Costo/km Vida 2", f"${float(costo_v2):,.2f}")
            else:
                st.info("Sin datos suficientes")
        
        with col3:
            st.metric("Precio Vida 3", f"${llanta_sel.get('precio_vida3', 0):,.0f}")
            costo_v3 = llanta_sel.get('costo_km_vida3', None)
            if costo_v3 and not pd.isna(costo_v3):
                st.metric("Costo/km Vida 3", f"${float(costo_v3):,.2f}")
            else:
                st.info("Sin datos suficientes")
        
        with col4:
            st.metric("Precio Vida 4", f"${llanta_sel.get('precio_vida4', 0):,.0f}")
            costo_v4 = llanta_sel.get('costo_km_vida4', None)
            if costo_v4 and not pd.isna(costo_v4):
                st.metric("Costo/km Vida 4", f"${float(costo_v4):,.2f}")
            else:
                st.info("Sin datos suficientes")
        
        st.divider()

        # Costo acumulado
        costo_acumulado = calcular_costo_km_acumulado(id_llanta_analisis)
        if costo_acumulado:
            st.success(f"**Costo/km Acumulado Total:** ${costo_acumulado:,.2f}")
        else:
            st.info("No hay suficientes datos de servicios para calcular el costo/km acumulado")

    with tab4:
        st.subheader("💲 Asignación de Precios")

        if st.session_state.get('nivel', 99) != 1:
            st.warning("⚠️ Solo el administrador puede asignar precios")
        else:
            st.info("Edita los precios directamente en la tabla y presiona **Guardar Cambios**.")

            cols_precio = ['id_llanta', 'nit_cliente', 'marca_llanta', 'referencia', 'dimension',
                           'precio_vida1', 'precio_vida2', 'precio_vida3', 'precio_vida4']
            cols_disponibles = [c for c in cols_precio if c in df_llantas.columns]
            df_precios = df_llantas[cols_disponibles].copy()

            for col in ['precio_vida1', 'precio_vida2', 'precio_vida3', 'precio_vida4']:
                if col in df_precios.columns:
                    df_precios[col] = pd.to_numeric(df_precios[col], errors='coerce').fillna(0)

            column_config = {
                'id_llanta':    st.column_config.TextColumn("ID Llanta",   disabled=True),
                'nit_cliente':  st.column_config.TextColumn("NIT Cliente", disabled=True),
                'marca_llanta': st.column_config.TextColumn("Marca",       disabled=True),
                'referencia':   st.column_config.TextColumn("Referencia",  disabled=True),
                'dimension':    st.column_config.TextColumn("Dimensión",   disabled=True),
                'precio_vida1': st.column_config.NumberColumn("Precio Vida 1", min_value=0, format="$ %d"),
                'precio_vida2': st.column_config.NumberColumn("Precio Vida 2", min_value=0, format="$ %d"),
                'precio_vida3': st.column_config.NumberColumn("Precio Vida 3", min_value=0, format="$ %d"),
                'precio_vida4': st.column_config.NumberColumn("Precio Vida 4", min_value=0, format="$ %d"),
            }

            edited_df = st.data_editor(
                df_precios,
                column_config=column_config,
                hide_index=True,
                use_container_width=True,
                key="editor_precios"
            )

            if st.button("💾 Guardar Cambios de Precios", type="primary"):
                df_todos = leer_hoja_fresco(SHEET_LLANTAS)
                for _, row in edited_df.iterrows():
                    id_llanta = row['id_llanta']
                    for col in ['precio_vida1', 'precio_vida2', 'precio_vida3', 'precio_vida4']:
                        if col in edited_df.columns:
                            df_todos.loc[df_todos['id_llanta'] == id_llanta, col] = row[col]
                df_todos['fecha_modificacion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                escribir_hoja(SHEET_LLANTAS, df_todos)
                st.success("✅ Precios actualizados exitosamente")
                st.rerun()

# Continuará en la siguiente parte debido a límite de caracteres...

# ============= FUNCIÓN 1: GESTIÓN DE CLIENTES =============
def crear_cliente():
    """Función para crear clientes con frentes"""
    
    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("👤 Gestión de Clientes")

    if not verificar_permiso(1):  # Solo Administrador puede crear clientes
        return
    
    tab1, tab2 = st.tabs(["➕ Crear Cliente", "📋 Ver Clientes"])
    
    with tab1:
        st.subheader("Crear Nuevo Cliente")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nit = st.text_input("NIT (10 dígitos)", max_chars=10)
            nombre_cliente = st.text_input("Nombre del Cliente")
        
        with col2:
            num_frentes = st.number_input("Número de Frentes", min_value=0, max_value=20, value=1)
        
        frentes = []
        if num_frentes > 0:
            st.write("**Nombres de los Frentes:**")
            cols = st.columns(3)
            for i in range(num_frentes):
                with cols[i % 3]:
                    frente = st.text_input(f"Frente {i+1}", key=f"frente_{i}")
                    if frente:
                        frentes.append(frente)
        
        # Mostrar mensaje de éxito si viene de crear cliente
        if st.session_state.get('cliente_creado'):
            st.success("✅ ¡Cliente creado con éxito!")
            st.session_state['cliente_creado'] = False

        # Evitar doble click
        guardando = st.session_state.get('guardando_cliente', False)

        if st.button("💾 Guardar Cliente", type="primary", disabled=guardando):
            if len(nit) != 10 or not nit.isdigit():
                st.error("El NIT debe tener exactamente 10 dígitos numéricos")
            elif not nombre_cliente:
                st.error("Debes ingresar el nombre del cliente")
            elif num_frentes > 0 and len(frentes) != num_frentes:
                st.error("Debes ingresar todos los nombres de frentes")
            else:
                st.session_state['guardando_cliente'] = True
                # Leer datos frescos SIN caché para verificar duplicados
                df_clientes = leer_hoja_fresco(SHEET_CLIENTES)

                # Verificar si el NIT ya existe
                if existe_valor(df_clientes, 'nit', nit):
                    st.error("Este NIT ya está registrado")
                    st.session_state['guardando_cliente'] = False
                else:
                    # Generar id_cliente automático
                    id_cliente = generar_id_cliente(nombre_cliente, df_clientes)

                    nuevo_cliente = pd.DataFrame([{
                        'id_cliente': id_cliente,
                        'nit': nit,
                        'nombre_cliente': nombre_cliente,
                        'frentes': json.dumps(frentes) if frentes else json.dumps([]),
                        'fecha_creacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }])

                    df_clientes = pd.concat([df_clientes, nuevo_cliente], ignore_index=True)
                    escribir_hoja(SHEET_CLIENTES, df_clientes)
                    st.session_state['cliente_creado'] = True
                    st.session_state['guardando_cliente'] = False
                    st.rerun()
    
    with tab2:
        df_clientes = leer_hoja(SHEET_CLIENTES)
        
        if st.session_state.get('nivel') == 4:
            clientes_acceso = obtener_clientes_accesibles()
            df_clientes = filtrar_por_clientes(df_clientes, 'nit', clientes_acceso)
        
        if not df_clientes.empty:
            for idx, row in df_clientes.iterrows():
                with st.expander(f"🏢 {row.get('nombre_cliente', 'N/A')} - NIT: {row.get('nit', 'N/A')}"):
                    frentes = json.loads(row.get('frentes', '[]')) if row.get('frentes') else []
                    if frentes:
                        st.write(f"**Frentes:** {', '.join(frentes)}")
                    else:
                        st.write("**Sin frentes**")
                    st.write(f"**Fecha de Creación:** {row.get('fecha_creacion', 'N/A')}")
        else:
            st.info("No hay clientes registrados o no tienes acceso")

# ============= FUNCIÓN 2: GESTIÓN DE VEHÍCULOS =============
def crear_vehiculos():
    """Función para crear vehículos asociados a cliente y frente"""
    
    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("🚛 Gestión de Vehículos")
    
    if not verificar_permiso(2):
        return
    
    df_clientes = leer_hoja(SHEET_CLIENTES)
    
    clientes_acceso = obtener_clientes_accesibles()
    df_clientes = filtrar_por_clientes(df_clientes, 'nit', clientes_acceso)
    
    if df_clientes.empty:
        st.warning("⚠️ Primero debes crear un cliente o no tienes acceso")
        return
    
    tab1, tab2 = st.tabs(["➕ Registrar Vehículo", "📋 Ver Vehículos"])
    
    with tab1:
        st.subheader("Registrar Nuevo Vehículo")
        
        col1, col2, col3 = st.columns(3)

        with col1:
            cliente_seleccionado = st.selectbox(
                "Cliente",
                options=df_clientes['nit'].values if not df_clientes.empty and 'nit' in df_clientes.columns else [],
                format_func=lambda x: f"{df_clientes[df_clientes['nit']==x]['nombre_cliente'].values[0]} - {x}" if not df_clientes.empty else str(x)
            )

            # ID del usuario (opcional) - el sistema generará un ID único
            id_vehiculo_usuario = st.text_input("ID Vehículo (opcional)", placeholder="Ej: V01, 123, etc.")
            st.caption("💡 El sistema generará un ID único: [Cliente][Frente][Consecutivo]_[Tu ID]")

            marca = st.text_input("Marca (ej: Freightliner)")
        
        with col2:
            linea = st.text_input("Línea (ej: Cascadia)")
            tipologia = st.selectbox("Tipología", ["Camión", "Tractomula", "Volqueta", "Turbo", "Sencillo", "Otro"])
            placa_vehiculo = st.text_input("Placa del Vehículo").upper()
        
        with col3:
            frentes_cliente = json.loads(df_clientes[df_clientes['nit']==cliente_seleccionado]['frentes'].values[0])
            if frentes_cliente:
                frente = st.selectbox("Frente", options=frentes_cliente)
            else:
                frente = st.text_input("Frente (sin frentes definidos)", value="General")
            
            estado = st.selectbox("Estado", ["no_asignado", "activo", "fuera_de_servicio"])
            kilometraje_inicial = st.number_input("Kilometraje Inicial", min_value=0, value=0)
        
        calculo_kms = st.selectbox("Cálculo de Kilómetros", ["odometro", "promedio", "tabla"])
        
        if st.button("💾 Registrar Vehículo", type="primary"):
            if not placa_vehiculo or not marca or not linea:
                st.error("Debes completar todos los campos obligatorios")
            else:
                # Leer datos frescos SIN caché para verificar duplicados
                df_vehiculos = leer_hoja_fresco(SHEET_VEHICULOS)

                if existe_valor(df_vehiculos, 'placa_vehiculo', placa_vehiculo):
                    st.error("Esta placa ya está registrada")
                else:
                    # Generar ID único para el vehículo
                    id_vehiculo = generar_id_unico(cliente_seleccionado, tipo='vehiculo')

                    nuevo_vehiculo = pd.DataFrame([{
                        'id_vehiculo': id_vehiculo,
                        'nit_cliente': cliente_seleccionado,
                        'marca': marca,
                        'linea': linea,
                        'tipologia': tipologia,
                        'placa_vehiculo': placa_vehiculo,
                        'frente': frente,
                        'estado': estado,
                        'kilometraje_inicial': kilometraje_inicial,
                        'calculo_kms': calculo_kms,
                        'fecha_creacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }])
                    
                    df_vehiculos = pd.concat([df_vehiculos, nuevo_vehiculo], ignore_index=True)
                    escribir_hoja(SHEET_VEHICULOS, df_vehiculos)
                    st.success(f"✅ Vehículo creado con éxito - ID: **{id_vehiculo}**")
                    st.balloons()
                    st.rerun()                
      
    with tab2:
        df_vehiculos = leer_hoja(SHEET_VEHICULOS)
        
        df_vehiculos = filtrar_por_clientes(df_vehiculos, 'nit_cliente', clientes_acceso)
        
        if not df_vehiculos.empty:
            df_display = df_vehiculos.merge(df_clientes[['nit', 'nombre_cliente']], left_on='nit_cliente', right_on='nit')
            columnas_mostrar = ['id_vehiculo', 'nombre_cliente', 'marca', 'linea', 'placa_vehiculo', 
                               'tipologia', 'frente', 'estado', 'kilometraje_inicial', 'calculo_kms']
            st.dataframe(df_display[[col for col in columnas_mostrar if col in df_display.columns]], use_container_width=True, hide_index=True)
        else:
            st.info("No hay vehículos registrados o no tienes acceso")

# ============= FUNCIÓN 3: GESTIÓN DE LLANTAS =============
def crear_llantas():
    """Función para crear llantas y asociarlas a clientes"""
    
    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("⚙️ Gestión de Llantas")
    
    if not verificar_permiso(3):
        return
    
    df_clientes = leer_hoja(SHEET_CLIENTES)
    df_llantas = leer_hoja(SHEET_LLANTAS)
    
    clientes_acceso = obtener_clientes_accesibles()
    df_clientes = filtrar_por_clientes(df_clientes, 'nit', clientes_acceso)
    
    if df_clientes.empty:
        st.warning("⚠️ Primero debes crear un cliente o no tienes acceso")
        return
    
    tab1, tab2 = st.tabs(["➕ Registrar Llanta", "📋 Ver Llantas"])
    
    with tab1:
        st.subheader("Registrar Nueva Llanta")
        
        col1, col2 = st.columns(2)

        with col1:
            def format_cliente(x):
                try:
                    nombre = df_clientes[df_clientes['nit']==x]['nombre_cliente'].values
                    return nombre[0] if len(nombre) > 0 else f"NIT: {x}"
                except:
                    return f"NIT: {x}"

            cliente_seleccionado = st.selectbox(
                "Cliente",
                options=df_clientes['nit'].values,
                format_func=format_cliente,
                key="llanta_cliente"
            )

            # Obtener frentes del cliente seleccionado
            frentes_cliente_data = df_clientes[df_clientes['nit']==cliente_seleccionado]['frentes'].values
            if len(frentes_cliente_data) > 0 and pd.notna(frentes_cliente_data[0]):
                try:
                    frentes_cliente = json.loads(frentes_cliente_data[0])
                except:
                    frentes_cliente = []
            else:
                frentes_cliente = []

            if frentes_cliente:
                frente_llanta = st.selectbox("Frente", options=frentes_cliente, key="llanta_frente")
            else:
                frente_llanta = st.text_input("Frente (sin frentes definidos)", value="General", key="llanta_frente_txt")

            marca_llanta = st.text_input("Marca de Llanta")
            referencia = st.text_input("Diseño (ej: XZA2)")

        with col2:
            dimension = st.text_input("Dimensión (ej: 295/80R22.5)")

            # ID del usuario (opcional) - el sistema generará un ID único
            id_llanta_usuario = st.text_input("ID Llanta (opcional)", placeholder="Ej: L01, 123, etc.")
            st.caption("💡 El sistema generará un ID único: [Cliente][Frente][Consecutivo]_[Tu ID]")

        if st.button("💾 Registrar Llanta", type="primary"):
            if not dimension or not referencia or not marca_llanta:
                st.error("Debes completar todos los campos")
            else:
                # Leer datos frescos SIN caché para verificar duplicados
                df_llantas = leer_hoja_fresco(SHEET_LLANTAS)

                # Generar ID único para la llanta incluyendo el frente
                id_llanta = generar_id_unico(cliente_seleccionado, frente=frente_llanta, tipo='llanta')
                # Anexar ID opcional del usuario si fue proporcionado
                if id_llanta_usuario and id_llanta_usuario.strip():
                    id_llanta = f"{id_llanta}_{id_llanta_usuario.strip()}"

                nueva_llanta = pd.DataFrame([{
                    'id_llanta': id_llanta,
                    'nit_cliente': str(cliente_seleccionado),
                    'marca_llanta': marca_llanta,
                    'referencia': referencia,
                    'dimension': dimension,
                    'vida_actual': 1,
                    'disponibilidad': 'llanta_nueva',
                    'kilometros_totales': 0,
                    'km_ultimo_montaje': 0,
                    'total_regrabaciones': 0,
                    'placa_actual': '',
                    'posicion_actual': '',
                    'estado_reencauche': '',
                    'precio_vida1': 0,
                    'reencauche1': '',
                    'precio_vida2': 0,
                    'reencauche2': '',
                    'precio_vida3': 0,
                    'reencauche3': '',
                    'precio_vida4': 0,
                    'costo_km_vida1': 0,
                    'costo_km_vida2': 0,
                    'costo_km_vida3': 0,
                    'costo_km_vida4': 0,
                    'fecha_creacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'fecha_modificacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])

                df_llantas = pd.concat([df_llantas, nueva_llanta], ignore_index=True)
                escribir_hoja(SHEET_LLANTAS, df_llantas)
                st.success(f"✅ Llanta creada con éxito - ID: **{id_llanta}**")
                st.balloons()
                st.rerun()
    
    with tab2:
        df_llantas = leer_hoja(SHEET_LLANTAS)
        
        df_llantas = filtrar_por_clientes(df_llantas, 'nit_cliente', clientes_acceso)
        
        if not df_llantas.empty:
            df_display = df_llantas.merge(df_clientes[['nit', 'nombre_cliente']], left_on='nit_cliente', right_on='nit', how='left')
            df_display['nombre_cliente'].fillna('Cliente Inválido', inplace=True)
            columnas_mostrar = ['id_llanta', 'nombre_cliente', 'marca_llanta', 'referencia', 'dimension', 
                               'disponibilidad', 'placa_vehiculo', 'vida', 'precio_vida1', 'precio_vida2', 
                               'precio_vida3', 'precio_vida4', 'costo_km_vida1', 'costo_km_vida2',
                               'costo_km_vida3', 'costo_km_vida4']
            st.dataframe(df_display[[col for col in columnas_mostrar if col in df_display.columns]], use_container_width=True, hide_index=True)
        else:
            st.info("No hay llantas registradas o no tienes acceso")

# Debido al límite de caracteres, las funciones restantes (montaje, servicios, desmontaje, reportes, gestión de usuarios y main) 
# permanecen igual que en el código original con ajustes menores para compatibilidad.
# Se incluyen las firmas principales:

def montaje_llantas(embedded=False):
    """Función para montar llantas en vehículos"""

    if not embedded:
        st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
        st.header("🔧 Montaje de Llantas")

        if not verificar_permiso(3):
            return

    df_llantas = leer_hoja_fresco(SHEET_LLANTAS)
    df_vehiculos = leer_hoja(SHEET_VEHICULOS)

    clientes_acceso = obtener_clientes_accesibles()
    df_llantas = filtrar_por_clientes(df_llantas, 'nit_cliente', clientes_acceso)
    df_vehiculos = filtrar_por_clientes(df_vehiculos, 'nit_cliente', clientes_acceso)

    if df_vehiculos.empty:
        st.warning("⚠️ No hay vehículos registrados para tus clientes")
        return

    # Verificar que el DataFrame tiene las columnas necesarias
    if df_llantas.empty or 'disponibilidad' not in df_llantas.columns or 'estado_reencauche' not in df_llantas.columns:
        st.warning("⚠️ No hay llantas registradas o no se pueden cargar los datos")
        return

    # Campos de orden de trabajo y planilla (primeras columnas)
    col_ot1, col_ot2 = st.columns(2)
    with col_ot1:
        orden_trabajo = st.text_input("📋 Orden de Trabajo", placeholder="Ej: OT-2024-001", key="montaje_ot")
    with col_ot2:
        planilla = st.text_input("📄 Planilla", placeholder="Número de planilla", key="montaje_planilla")

    st.divider()

    col1, col2 = st.columns(2)

    # PRIMERO: Seleccionar vehículo
    with col1:
        placa_vehiculo = st.selectbox(
            "1️⃣ Seleccionar Vehículo",
            options=df_vehiculos['placa_vehiculo'].values,
            format_func=lambda x: f"{x} - {df_vehiculos[df_vehiculos['placa_vehiculo']==x]['marca'].values[0] if 'marca' in df_vehiculos.columns else ''}"
        )

    # Obtener el nit_cliente y kilometraje del vehículo seleccionado
    vehiculo_seleccionado = df_vehiculos[df_vehiculos['placa_vehiculo'] == placa_vehiculo]
    nit_cliente_vehiculo = vehiculo_seleccionado['nit_cliente'].values[0] if not vehiculo_seleccionado.empty else None

    # Filtrar llantas disponibles SOLO del mismo cliente que el vehículo
    llantas_cliente = df_llantas[df_llantas['nit_cliente'] == nit_cliente_vehiculo]
    llantas_disponibles = llantas_cliente[
        (llantas_cliente['disponibilidad'].isin(['llanta_nueva', 'recambio'])) |
        ((llantas_cliente['disponibilidad'] == 'reencauche') & (llantas_cliente['estado_reencauche'] == 'aprobado'))
    ]

    # SEGUNDO: Seleccionar llanta (filtrada por cliente del vehículo)
    with col2:
        if llantas_disponibles.empty:
            st.warning(f"⚠️ No hay llantas disponibles para este cliente")
            id_llanta = None
        else:
            id_llanta = st.selectbox(
                "2️⃣ Seleccionar Llanta",
                options=llantas_disponibles['id_llanta'].values,
                format_func=lambda x: f"ID {x} - {llantas_disponibles[llantas_disponibles['id_llanta']==x]['marca_llanta'].values[0]} {llantas_disponibles[llantas_disponibles['id_llanta']==x]['dimension'].values[0]} (Vida {int(llantas_disponibles[llantas_disponibles['id_llanta']==x]['vida_actual'].values[0]) if 'vida_actual' in llantas_disponibles.columns and pd.notna(llantas_disponibles[llantas_disponibles['id_llanta']==x]['vida_actual'].values[0]) else 1})"
            )

    # Verificar posiciones ocupadas en el vehículo seleccionado
    col_placa = 'placa_actual' if 'placa_actual' in df_llantas.columns else 'placa_vehiculo'
    llantas_montadas_vehiculo = df_llantas[
        (df_llantas['disponibilidad'] == 'al_piso') &
        (df_llantas[col_placa].astype(str) == str(placa_vehiculo))
    ]
    posiciones_ocupadas = {}
    if not llantas_montadas_vehiculo.empty:
        col_pos = 'posicion_actual' if 'posicion_actual' in llantas_montadas_vehiculo.columns else 'pos_final'
        if col_pos in llantas_montadas_vehiculo.columns:
            for _, row in llantas_montadas_vehiculo.iterrows():
                pos_raw = row.get(col_pos, '')
                # Normalizar: si es numérico (1.0, 2.0), convertir a entero string ("1", "2")
                try:
                    pos = str(int(float(pos_raw)))
                except (ValueError, TypeError):
                    pos = str(pos_raw).strip().upper()
                if pos and pos != 'nan' and pos != '':
                    posiciones_ocupadas[pos] = str(row['id_llanta'])

    # Información del vehículo seleccionado (recuadro azul)
    km_vehiculo = vehiculo_seleccionado.iloc[0].get('kilometraje_inicial', 0) if not vehiculo_seleccionado.empty else 0
    km_vehiculo = float(km_vehiculo) if pd.notna(km_vehiculo) else 0
    marca_veh = vehiculo_seleccionado.iloc[0].get('marca', '') if not vehiculo_seleccionado.empty else ''
    if posiciones_ocupadas:
        ocupadas_texto = " | ".join([f"**{pos}**: {id_ll}" for pos, id_ll in sorted(posiciones_ocupadas.items())])
        st.info(f"🚛 Vehículo: **{placa_vehiculo}** ({marca_veh}) | 📏 Km inicial: **{km_vehiculo:,.0f}** | 📍 Posiciones ocupadas: {ocupadas_texto}")
    else:
        st.info(f"🚛 Vehículo: **{placa_vehiculo}** ({marca_veh}) | 📏 Km inicial: **{km_vehiculo:,.0f}** | 📍 Sin llantas montadas")

    col3, col4 = st.columns(2)
    with col3:
        posicion = st.text_input("3️⃣ Posición (ej: DI, DD, TI1)")
    with col4:
        kilometraje = st.number_input("4️⃣ Kilometraje del Vehículo", min_value=0, value=0)

    # Validar si la posición ingresada ya está ocupada
    # Normalizar igual que las posiciones almacenadas
    posicion_stripped = posicion.strip() if posicion else ''
    try:
        posicion_normalizada = str(int(float(posicion_stripped)))
    except (ValueError, TypeError):
        posicion_normalizada = posicion_stripped.upper()
    posicion_ocupada = posicion_normalizada in posiciones_ocupadas if posicion_normalizada else False
    if posicion_ocupada:
        st.error(f"⚠️ La posición **{posicion_normalizada}** ya está ocupada por la llanta **{posiciones_ocupadas[posicion_normalizada]}**. Desmonta esa llanta primero o elige otra posición.")

    # Obtener operarios del cliente
    operarios_disponibles = obtener_operarios_cliente(nit_cliente_vehiculo)

    if operarios_disponibles:
        operario = st.selectbox("👷 Operario", options=operarios_disponibles, key="montaje_operario")
    else:
        operario = st.text_input("👷 Operario", placeholder="No hay operarios asignados a este cliente", key="montaje_operario_txt")

    if st.button("🔧 Montar Llanta", type="primary"):
        if id_llanta is None:
            st.error("No hay llantas disponibles para montar")
        elif not posicion:
            st.error("Debes especificar la posición")
        elif posicion_ocupada:
            st.error(f"No se puede montar: la posición **{posicion_normalizada}** ya está ocupada por la llanta **{posiciones_ocupadas[posicion_normalizada]}**")
        elif kilometraje <= 0:
            st.error("Debes ingresar el kilometraje actual del vehículo")
        else:
            df_llantas = leer_hoja_fresco(SHEET_LLANTAS)

            # Re-verificar ocupación con datos frescos antes de montar
            col_placa_fresh = 'placa_actual' if 'placa_actual' in df_llantas.columns else 'placa_vehiculo'
            col_pos_fresh = 'posicion_actual' if 'posicion_actual' in df_llantas.columns else 'pos_final'
            llantas_fresh = df_llantas[
                (df_llantas['disponibilidad'] == 'al_piso') &
                (df_llantas[col_placa_fresh].astype(str) == str(placa_vehiculo))
            ]
            for _, row_f in llantas_fresh.iterrows():
                pos_raw_f = row_f.get(col_pos_fresh, '')
                try:
                    p_f = str(int(float(pos_raw_f)))
                except (ValueError, TypeError):
                    p_f = str(pos_raw_f).strip().upper() if not pd.isna(pos_raw_f) else ''
                if p_f and p_f not in ('nan', '') and p_f == posicion_normalizada:
                    st.error(f"⚠️ La posición **{posicion_normalizada}** fue ocupada recientemente por la llanta **{row_f['id_llanta']}**. No se puede montar.")
                    st.stop()

            # Obtener vida actual de la llanta
            vida_actual = df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'vida_actual'].values[0] if 'vida_actual' in df_llantas.columns else 1
            vida_actual = int(vida_actual) if pd.notna(vida_actual) else 1

            # Actualizar datos en hoja llantas (nuevos nombres de columnas)
            df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'disponibilidad'] = 'al_piso'
            df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'placa_actual'] = placa_vehiculo
            df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'posicion_actual'] = posicion
            df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'estado_reencauche'] = ''
            df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'km_ultimo_montaje'] = kilometraje
            df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'fecha_modificacion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            escribir_hoja(SHEET_LLANTAS, df_llantas)

            # Crear movimiento de montaje
            crear_movimiento(
                id_llanta=id_llanta,
                tipo='montaje',
                vida=vida_actual,
                placa_vehiculo=placa_vehiculo,
                posicion=posicion,
                kilometraje=kilometraje,
                orden_trabajo=orden_trabajo,
                planilla=planilla,
                operario=operario
            )

            # Crear registro en servicios para el montaje
            df_servicios = leer_hoja(SHEET_SERVICIOS)
            df_vehiculos_srv = leer_hoja(SHEET_VEHICULOS)

            # Obtener datos del vehículo
            vehiculo_data = df_vehiculos_srv[df_vehiculos_srv['placa_vehiculo'] == placa_vehiculo].iloc[0]
            frente = vehiculo_data.get('frente', 'General')
            tipologia = vehiculo_data.get('tipologia', '')

            # Obtener datos de la llanta
            llanta_data = df_llantas[df_llantas['id_llanta'] == id_llanta].iloc[0]
            disponibilidad_anterior = llanta_data.get('disponibilidad', 'llanta_nueva')

            # Generar ID de servicio
            id_servicio = generar_id_servicio(nit_cliente_vehiculo)

            nuevo_servicio = pd.DataFrame([{
                'id_servicio': id_servicio,
                'orden_trabajo': orden_trabajo,
                'planilla': planilla,
                'fecha': datetime.now().strftime("%d/%m/%Y"),
                'id_llanta': id_llanta,
                'placa_vehiculo': placa_vehiculo,
                'posicion': posicion,
                'vida': vida_actual,
                'tipologia': tipologia,
                'tipo_servicio': 'montaje',
                'disponibilidad': 'al_piso',
                'kilometraje': kilometraje,
                'rotacion': 'No',
                'posicion_nueva': '',
                'profundidad_1': 0,
                'profundidad_2': 0,
                'profundidad_3': 0,
                'balanceo': 'No',
                'reparacion': 'No',
                'despinche': 'No',
                'regrabacion': 'No',
                'torqueo': 'No',
                'inspeccion': 'No',
                'insumos': '',
                'comentario_fvu': '',
                'operario': operario,
                'usuario_registro': st.session_state['usuario'],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])

            df_servicios = pd.concat([df_servicios, nuevo_servicio], ignore_index=True)
            escribir_hoja(SHEET_SERVICIOS, df_servicios)

            st.success(f"✅ Llanta ID {id_llanta} montada en vehículo {placa_vehiculo} - Posición: {posicion} - Km: {kilometraje:,}")
            st.info(f"📋 Servicio de montaje registrado: {id_servicio}")
            st.rerun()

def registrar_servicios(embedded=False):
    """Función para registrar servicios de mantenimiento"""

    if not embedded:
        st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
        st.header("🛠️ Registro de Servicios")

        if not verificar_permiso(3):
            return

    df_llantas = leer_hoja(SHEET_LLANTAS)
    df_vehiculos = leer_hoja(SHEET_VEHICULOS)

    clientes_acceso = obtener_clientes_accesibles()
    df_llantas = filtrar_por_clientes(df_llantas, 'nit_cliente', clientes_acceso)

    # Verificar que el DataFrame tiene la columna necesaria
    if df_llantas.empty or 'disponibilidad' not in df_llantas.columns:
        st.warning("⚠️ No hay llantas registradas o no se pueden cargar los datos")
        return

    llantas_en_piso = df_llantas[df_llantas['disponibilidad'] == 'al_piso']

    if llantas_en_piso.empty:
        st.warning("⚠️ No hay llantas montadas para registrar servicios")
        return

    st.subheader("Formulario de Servicio")

    # Determinar nombre de columna de placa (compatibilidad)
    placa_col = 'placa_actual' if 'placa_actual' in llantas_en_piso.columns else 'placa_vehiculo'
    pos_col = 'posicion_actual' if 'posicion_actual' in llantas_en_piso.columns else 'pos_final'

    # Campos de orden de trabajo y planilla (primeras columnas)
    col_ot1, col_ot2 = st.columns(2)
    with col_ot1:
        orden_trabajo = st.text_input("📋 Orden de Trabajo", placeholder="Ej: OT-2024-001", key="srv_ot")
    with col_ot2:
        planilla = st.text_input("📄 Planilla", placeholder="Número de planilla", key="srv_planilla")

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        # 5.1 - Mostrar profundidad y km sobre la casilla de selección
        df_servicios_hist = leer_hoja(SHEET_SERVICIOS)
        llanta_opciones = llantas_en_piso['id_llanta'].values

        id_llanta = st.selectbox(
            "ID Llanta",
            options=llanta_opciones,
            format_func=lambda x: f"ID {x} - Placa: {llantas_en_piso[llantas_en_piso['id_llanta']==x][placa_col].values[0] if placa_col in llantas_en_piso.columns else 'N/A'}",
            key="srv_id_llanta"
        )

        fecha_servicio = st.date_input("Fecha del Servicio", datetime.now(), key="srv_fecha")
        kilometraje = st.number_input("Kilometraje", min_value=0, value=0, key="srv_km")

    # Mostrar info completa de la llanta seleccionada en recuadro azul
    llanta_sel = llantas_en_piso[llantas_en_piso['id_llanta'] == id_llanta].iloc[0]
    posicion_actual = llanta_sel.get('posicion_actual', llanta_sel.get('pos_final', ''))
    vida_actual = int(llanta_sel.get('vida_actual', llanta_sel.get('vida', 1))) if pd.notna(llanta_sel.get('vida_actual', llanta_sel.get('vida', 1))) else 1
    marca_ll = llanta_sel.get('marca_llanta', 'N/A')
    ref_ll = llanta_sel.get('referencia', 'N/A')
    dim_ll = llanta_sel.get('dimension', 'N/A')
    disp_ll = llanta_sel.get('disponibilidad', 'N/A')

    # Buscar último servicio para profundidades y km
    info_ultimo = ""
    if not df_servicios_hist.empty and 'id_llanta' in df_servicios_hist.columns:
        servicios_llanta = df_servicios_hist[df_servicios_hist['id_llanta'] == id_llanta]
        if not servicios_llanta.empty:
            ultimo_servicio = servicios_llanta.iloc[-1]
            ult_km = ultimo_servicio.get('kilometraje', 'N/A')
            ult_p1 = ultimo_servicio.get('profundidad_1', 'N/A')
            ult_p2 = ultimo_servicio.get('profundidad_2', 'N/A')
            ult_p3 = ultimo_servicio.get('profundidad_3', 'N/A')
            info_ultimo = f"  \nÚltimo servicio → Km: **{ult_km}** | Prof: Int:**{ult_p1}**mm · Cen:**{ult_p2}**mm · Ext:**{ult_p3}**mm"
        else:
            info_ultimo = "  \nSin servicios previos registrados"
    else:
        info_ultimo = "  \nSin servicios previos registrados"

    pos_prefill = str(posicion_actual).strip() if pd.notna(posicion_actual) and str(posicion_actual).strip().lower() != 'nan' else ''
    st.info(
        f"**Llanta:** {id_llanta} | **Marca:** {marca_ll} | **Ref:** {ref_ll} | **Dimensión:** {dim_ll}  \n"
        f"**Posición actual:** {pos_prefill or 'Sin asignar'} | **Vida:** {vida_actual} | **Disponibilidad:** {disp_ll}"
        f"{info_ultimo}"
    )

    posicion_input = st.text_input(
        "📍 Posición de la llanta (obligatorio)",
        value=pos_prefill,
        key="srv_posicion",
        placeholder="Ej: DI, DD, TI1",
        help="Confirma o corrige la posición actual. Se actualizará en la ficha de la llanta."
    )

    with col2:
        st.write("**Profundidades (mm)**")
        profundidad_1 = st.number_input("Profundidad 1 (interna)", min_value=0.0, max_value=30.0, value=0.0, step=0.5, key="srv_prof1")
        profundidad_2 = st.number_input("Profundidad 2 (centro)", min_value=0.0, max_value=30.0, value=0.0, step=0.5, key="srv_prof2")
        profundidad_3 = st.number_input("Profundidad 3 (externa)", min_value=0.0, max_value=30.0, value=0.0, step=0.5, key="srv_prof3")

    with col3:
        st.write("**Servicios Realizados**")
        balanceo = st.checkbox("Balanceo", key="srv_balanceo")
        reparacion = st.checkbox("Reparación", key="srv_reparacion")
        despinche = st.checkbox("Despinche", key="srv_despinche")
        regrabacion = st.checkbox("Regrabación", key="srv_regrabacion")
        torqueo = st.checkbox("Torqueo", key="srv_torqueo")
        inspeccion = st.checkbox("Inspección", key="srv_inspeccion")

        # 5.2 - Casilla insumos cuando se marque balanceo o reparación
        insumos = ""
        if balanceo or reparacion:
            insumos = st.text_input("📦 Insumos utilizados", placeholder="Ej: Parche, pegamento, plomos", key="srv_insumos")

    # Obtener NIT del cliente de la llanta seleccionada para filtrar operarios
    llanta_sel_temp = llantas_en_piso[llantas_en_piso['id_llanta'] == id_llanta].iloc[0]
    nit_cliente_temp = llanta_sel_temp['nit_cliente']
    operarios_disponibles = obtener_operarios_cliente(nit_cliente_temp)

    # Selector de operario
    st.divider()
    if operarios_disponibles:
        operario = st.selectbox("👷 Operario", options=operarios_disponibles, key="srv_operario")
    else:
        operario = st.text_input("👷 Operario", placeholder="No hay operarios asignados a este cliente", key="srv_operario_txt")

    if st.button("💾 Registrar Servicio", type="primary", key="srv_btn_registrar"):
        if not posicion_input or not posicion_input.strip():
            st.error("⚠️ Debes ingresar la posición de la llanta para registrar el servicio")
            st.stop()

        df_servicios = leer_hoja(SHEET_SERVICIOS)
        df_llantas = leer_hoja_fresco(SHEET_LLANTAS)
        df_vehiculos = leer_hoja(SHEET_VEHICULOS)

        llanta_data = df_llantas[df_llantas['id_llanta'] == id_llanta]
        if llanta_data.empty:
            st.error("No se encontró la llanta seleccionada")
            st.stop()

        llanta_data = llanta_data.iloc[0]
        placa = llanta_data.get('placa_actual', llanta_data.get('placa_vehiculo', ''))
        nit_cliente = llanta_data['nit_cliente']
        posicion = posicion_input.strip()
        vida = llanta_data.get('vida_actual', llanta_data.get('vida', 1))
        disponibilidad = llanta_data.get('disponibilidad', '')

        vehiculo_match = df_vehiculos[df_vehiculos['placa_vehiculo'] == placa]
        if vehiculo_match.empty:
            frente = 'General'
            tipologia = ''
        else:
            vehiculo_data = vehiculo_match.iloc[0]
            frente = vehiculo_data.get('frente', 'General')
            tipologia = vehiculo_data.get('tipologia', '')

        id_servicio = generar_id_servicio(nit_cliente)

        # Determinar tipo de servicio principal
        tipos_servicio = []
        if balanceo: tipos_servicio.append('Balanceo')
        if reparacion: tipos_servicio.append('Reparación')
        if despinche: tipos_servicio.append('Despinche')
        if regrabacion: tipos_servicio.append('Regrabación')
        if torqueo: tipos_servicio.append('Torqueo')
        if inspeccion: tipos_servicio.append('Inspección')
        tipo_servicio = ', '.join(tipos_servicio) if tipos_servicio else 'Inspección'

        nuevo_servicio = pd.DataFrame([{
            'id_servicio': id_servicio,
            'orden_trabajo': orden_trabajo,
            'planilla': planilla,
            'fecha': fecha_servicio.strftime("%d/%m/%Y"),
            'id_llanta': id_llanta,
            'placa_vehiculo': placa,
            'posicion': posicion,
            'vida': vida,
            'tipologia': tipologia,
            'tipo_servicio': tipo_servicio,
            'disponibilidad': disponibilidad,
            'kilometraje': kilometraje,
            'rotacion': 'No',
            'posicion_nueva': '',
            'profundidad_1': profundidad_1,
            'profundidad_2': profundidad_2,
            'profundidad_3': profundidad_3,
            'balanceo': 'Sí' if balanceo else 'No',
            'reparacion': 'Sí' if reparacion else 'No',
            'despinche': 'Sí' if despinche else 'No',
            'regrabacion': 'Sí' if regrabacion else 'No',
            'torqueo': 'Sí' if torqueo else 'No',
            'inspeccion': 'Sí' if inspeccion else 'No',
            'insumos': insumos,
            'comentario_fvu': '',
            'operario': operario,
            'usuario_registro': st.session_state['usuario'],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])

        df_servicios = pd.concat([df_servicios, nuevo_servicio], ignore_index=True)
        escribir_hoja(SHEET_SERVICIOS, df_servicios)

        # Actualizar posición en llantas (siempre) y regrabaciones si aplica
        df_llantas_update = leer_hoja_fresco(SHEET_LLANTAS)
        df_llantas_update.loc[df_llantas_update['id_llanta'] == id_llanta, 'posicion_actual'] = posicion
        df_llantas_update.loc[df_llantas_update['id_llanta'] == id_llanta, 'fecha_modificacion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        regrabaciones_nuevo = None
        if regrabacion:
            regrabaciones_actual = df_llantas_update.loc[df_llantas_update['id_llanta'] == id_llanta, 'total_regrabaciones'].values
            regrabaciones_actual = int(regrabaciones_actual[0]) if len(regrabaciones_actual) > 0 and pd.notna(regrabaciones_actual[0]) else 0
            regrabaciones_nuevo = regrabaciones_actual + 1
            df_llantas_update.loc[df_llantas_update['id_llanta'] == id_llanta, 'total_regrabaciones'] = regrabaciones_nuevo
        escribir_hoja(SHEET_LLANTAS, df_llantas_update)

        # ACTUALIZAR COSTOS/KM AUTOMÁTICAMENTE
        actualizar_costos_km_llanta(id_llanta)

        st.success(f"✅ Servicio {id_servicio} registrado exitosamente para llanta ID {id_llanta}")
        if regrabacion:
            st.info(f"🔧 Regrabación registrada. Total regrabaciones: {regrabaciones_nuevo}")
        st.info("💡 Los costos/km se han actualizado automáticamente")

        st.session_state['servicio_completado'] = True
        st.session_state['id_llanta_servicio'] = id_llanta
        st.rerun()

    if st.session_state.get('servicio_completado', False):
        st.divider()
        st.subheader("¿Qué deseas hacer ahora?")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("➕ Registrar Otro Servicio", use_container_width=True, key="srv_btn_otro"):
                st.session_state['servicio_completado'] = False
                st.rerun()

        with col2:
            if embedded:
                st.info("💡 Para desmontar, ve al tab **Desmontaje** arriba.")
            else:
                if st.button("🔽 Realizar Desmontaje", use_container_width=True, type="primary", key="srv_btn_desmontaje"):
                    st.session_state['servicio_completado'] = False
                    st.session_state['ir_a_desmontaje'] = True
                    st.rerun()

    # ============= 5.4 y 5.5: HISTORIAL DE SERVICIOS CON FILTROS =============
    st.divider()
    st.subheader("📋 Historial de Servicios")
    df_servicios = leer_hoja(SHEET_SERVICIOS)
    df_llantas_hist = leer_hoja(SHEET_LLANTAS)

    if not df_servicios.empty:
        # Filtrar por clientes accesibles
        df_vehiculos_hist = leer_hoja(SHEET_VEHICULOS)
        df_vehiculos_hist = filtrar_por_clientes(df_vehiculos_hist, 'nit_cliente', clientes_acceso)
        placas_accesibles = df_vehiculos_hist['placa_vehiculo'].unique() if not df_vehiculos_hist.empty else []

        if 'placa_vehiculo' in df_servicios.columns:
            df_servicios_filtrado = df_servicios[df_servicios['placa_vehiculo'].isin(placas_accesibles)]
        else:
            df_servicios_filtrado = df_servicios

        if not df_servicios_filtrado.empty:
            # 5.5 - FILTROS
            st.write("**Filtros:**")
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)

            with col_f1:
                # Filtro Cliente
                df_clientes_f = leer_hoja(SHEET_CLIENTES)
                df_clientes_f = filtrar_por_clientes(df_clientes_f, 'nit', clientes_acceso)
                opciones_clientes = ['Todos'] + list(df_clientes_f['nombre_cliente'].values) if not df_clientes_f.empty else ['Todos']
                filtro_cliente = st.selectbox("Cliente", options=opciones_clientes, key="hist_filtro_cliente")

                # Filtro Frente
                if filtro_cliente != 'Todos' and not df_clientes_f.empty:
                    nit_filtro = df_clientes_f[df_clientes_f['nombre_cliente'] == filtro_cliente]['nit'].values[0]
                    vehiculos_cliente = df_vehiculos_hist[df_vehiculos_hist['nit_cliente'] == nit_filtro]
                    frentes_disponibles = ['Todos'] + list(vehiculos_cliente['frente'].unique()) if not vehiculos_cliente.empty else ['Todos']
                else:
                    frentes_disponibles = ['Todos']
                filtro_frente = st.selectbox("Frente", options=frentes_disponibles, key="hist_filtro_frente")

            with col_f2:
                # Filtro Fecha Inicial y Final
                filtro_fecha_ini = st.date_input("Fecha Inicial", value=None, key="hist_fecha_ini")
                filtro_fecha_fin = st.date_input("Fecha Final", value=None, key="hist_fecha_fin")

            with col_f3:
                # Filtro Placa
                placas_opciones = ['Todas'] + list(df_servicios_filtrado['placa_vehiculo'].unique())
                filtro_placa = st.selectbox("Placa Vehículo", options=placas_opciones, key="hist_filtro_placa")

                # Filtro ID Llanta
                llantas_opciones_filtro = ['Todas'] + list(df_servicios_filtrado['id_llanta'].unique())
                filtro_id_llanta = st.selectbox("ID Llanta", options=llantas_opciones_filtro, key="hist_filtro_llanta")

            with col_f4:
                # Filtro Tipo de Servicio
                tipos_opciones = ['Todos']
                if 'tipo_servicio' in df_servicios_filtrado.columns:
                    tipos_opciones += list(df_servicios_filtrado['tipo_servicio'].dropna().unique())
                filtro_tipo = st.selectbox("Tipo de Servicio", options=tipos_opciones, key="hist_filtro_tipo")

                # Filtro Operario
                operarios_opciones = ['Todos']
                if 'operario' in df_servicios_filtrado.columns:
                    operarios_opciones += list(df_servicios_filtrado['operario'].dropna().unique())
                filtro_operario = st.selectbox("Operario", options=operarios_opciones, key="hist_filtro_operario")

            # Aplicar filtros
            df_resultado = df_servicios_filtrado.copy()

            if filtro_cliente != 'Todos' and not df_clientes_f.empty:
                nit_filtro = df_clientes_f[df_clientes_f['nombre_cliente'] == filtro_cliente]['nit'].values[0]
                placas_cliente = df_vehiculos_hist[df_vehiculos_hist['nit_cliente'] == nit_filtro]['placa_vehiculo'].values
                df_resultado = df_resultado[df_resultado['placa_vehiculo'].isin(placas_cliente)]

                if filtro_frente != 'Todos':
                    placas_frente = df_vehiculos_hist[(df_vehiculos_hist['nit_cliente'] == nit_filtro) & (df_vehiculos_hist['frente'] == filtro_frente)]['placa_vehiculo'].values
                    df_resultado = df_resultado[df_resultado['placa_vehiculo'].isin(placas_frente)]

            if filtro_fecha_ini and 'fecha' in df_resultado.columns:
                df_resultado['fecha_dt'] = pd.to_datetime(df_resultado['fecha'], format='%d/%m/%Y', errors='coerce')
                df_resultado = df_resultado[df_resultado['fecha_dt'] >= pd.Timestamp(filtro_fecha_ini)]

            if filtro_fecha_fin and 'fecha' in df_resultado.columns:
                if 'fecha_dt' not in df_resultado.columns:
                    df_resultado['fecha_dt'] = pd.to_datetime(df_resultado['fecha'], format='%d/%m/%Y', errors='coerce')
                df_resultado = df_resultado[df_resultado['fecha_dt'] <= pd.Timestamp(filtro_fecha_fin)]

            if filtro_placa != 'Todas':
                df_resultado = df_resultado[df_resultado['placa_vehiculo'] == filtro_placa]

            if filtro_id_llanta != 'Todas':
                df_resultado = df_resultado[df_resultado['id_llanta'] == filtro_id_llanta]

            if filtro_tipo != 'Todos' and 'tipo_servicio' in df_resultado.columns:
                df_resultado = df_resultado[df_resultado['tipo_servicio'] == filtro_tipo]

            if filtro_operario != 'Todos' and 'operario' in df_resultado.columns:
                df_resultado = df_resultado[df_resultado['operario'] == filtro_operario]

            # Eliminar columna temporal
            if 'fecha_dt' in df_resultado.columns:
                df_resultado = df_resultado.drop(columns=['fecha_dt'])

            # 5.4 - Enriquecer con datos de llantas (marca, referencia, dimensión)
            if not df_llantas_hist.empty:
                cols_llanta = ['id_llanta']
                for c in ['marca_llanta', 'referencia', 'dimension']:
                    if c in df_llantas_hist.columns:
                        cols_llanta.append(c)
                df_resultado = df_resultado.merge(df_llantas_hist[cols_llanta], on='id_llanta', how='left', suffixes=('', '_llanta'))

            # 5.4 - Columnas a mostrar
            columnas_mostrar = ['planilla', 'placa_vehiculo', 'kilometraje', 'marca_llanta', 'referencia',
                               'dimension', 'id_servicio', 'fecha', 'id_llanta', 'tipo_servicio', 'operario',
                               'profundidad_1', 'profundidad_2', 'profundidad_3']
            columnas_disponibles = [col for col in columnas_mostrar if col in df_resultado.columns]

            st.dataframe(df_resultado[columnas_disponibles].sort_values('id_servicio', ascending=False) if 'id_servicio' in df_resultado.columns else df_resultado[columnas_disponibles], use_container_width=True, hide_index=True)
            st.caption(f"Total registros: {len(df_resultado)}")
        else:
            st.info("No hay servicios registrados para tus clientes")
    else:
        st.info("No hay servicios registrados")

def desmontaje_llantas(embedded=False):
    """Función para desmontar llantas y cambiar disponibilidad"""

    if not embedded:
        st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
        st.header("🔽 Desmontaje de Llantas")

        if not verificar_permiso(2):
            return

    df_llantas = leer_hoja(SHEET_LLANTAS)

    clientes_acceso = obtener_clientes_accesibles()
    df_llantas = filtrar_por_clientes(df_llantas, 'nit_cliente', clientes_acceso)

    # Verificar que el DataFrame tiene la columna necesaria
    if df_llantas.empty or 'disponibilidad' not in df_llantas.columns:
        st.warning("⚠️ No hay llantas registradas o no se pueden cargar los datos")
        return

    llantas_montadas = df_llantas[df_llantas['disponibilidad'] == 'al_piso']

    if llantas_montadas.empty:
        st.warning("⚠️ No hay llantas montadas para desmontar")
        return

    # Campos de orden de trabajo y planilla (primeras columnas)
    col_ot1, col_ot2 = st.columns(2)
    with col_ot1:
        orden_trabajo = st.text_input("📋 Orden de Trabajo", placeholder="Ej: OT-2024-001", key="desmontaje_ot")
    with col_ot2:
        planilla = st.text_input("📄 Planilla", placeholder="Número de planilla", key="desmontaje_planilla")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        # Usar placa_actual en lugar de placa_vehiculo
        placa_col = 'placa_actual' if 'placa_actual' in llantas_montadas.columns else 'placa_vehiculo'
        id_llanta = st.selectbox(
            "Seleccionar Llanta a Desmontar",
            options=llantas_montadas['id_llanta'].values,
            format_func=lambda x: f"ID {x} - Placa: {llantas_montadas[llantas_montadas['id_llanta']==x][placa_col].values[0] if placa_col in llantas_montadas.columns else 'N/A'}",
            key="desm_id_llanta"
        )

    with col2:
        nueva_disponibilidad = st.selectbox(
            "Nueva Disponibilidad",
            options=['recambio', 'reencauche', 'FVU'],
            key="desm_nueva_disp"
        )

    # Obtener datos de la llanta seleccionada
    llanta_sel = llantas_montadas[llantas_montadas['id_llanta'] == id_llanta].iloc[0]
    posicion_actual = llanta_sel.get('posicion_actual', llanta_sel.get('pos_final', ''))
    placa_actual = llanta_sel.get('placa_actual', llanta_sel.get('placa_vehiculo', ''))
    vida_actual = int(llanta_sel.get('vida_actual', llanta_sel.get('vida', 1))) if pd.notna(llanta_sel.get('vida_actual', llanta_sel.get('vida', 1))) else 1

    st.info(f"📍 Posición actual: **{posicion_actual}** | 🚛 Placa: **{placa_actual}** | 🔄 Vida: **{vida_actual}**")

    col3, col4 = st.columns(2)
    with col3:
        kilometraje = st.number_input("Kilometraje actual del vehículo", min_value=0, value=0, key="desm_km")

    razon_fvu = None
    if nueva_disponibilidad == 'FVU':
        with col4:
            razon_fvu = st.text_input("Razón de FVU (Fuera de Uso)", key="desm_razon_fvu")

    # Obtener operarios del cliente
    nit_cliente_llanta = llanta_sel['nit_cliente']
    operarios_disponibles = obtener_operarios_cliente(nit_cliente_llanta)

    if operarios_disponibles:
        operario = st.selectbox("👷 Operario", options=operarios_disponibles, key="desmontaje_operario")
    else:
        operario = st.text_input("👷 Operario", placeholder="No hay operarios asignados a este cliente", key="desmontaje_operario_txt")

    if st.button("🔽 Desmontar Llanta", type="primary", key="desm_btn_desmontar"):
        if kilometraje <= 0:
            st.error("Debes ingresar el kilometraje actual del vehículo")
        elif nueva_disponibilidad == 'FVU' and not razon_fvu:
            st.error("Debes especificar la razón del desecho")
        else:
            df_llantas = leer_hoja(SHEET_LLANTAS)

            # Calcular kilómetros recorridos y sumar a kilometros_totales
            llanta_data = df_llantas[df_llantas['id_llanta'] == id_llanta].iloc[0]
            km_ultimo_montaje = float(llanta_data.get('km_ultimo_montaje', 0)) if pd.notna(llanta_data.get('km_ultimo_montaje', 0)) else 0
            kilometros_totales_actual = float(llanta_data.get('kilometros_totales', 0)) if pd.notna(llanta_data.get('kilometros_totales', 0)) else 0

            # Calcular km recorridos en este período
            km_recorridos = max(0, kilometraje - km_ultimo_montaje)
            nuevo_total_km = kilometros_totales_actual + km_recorridos

            # Limpiar placa y posición actuales
            df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'placa_actual'] = ''
            df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'posicion_actual'] = ''
            df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'kilometros_totales'] = nuevo_total_km
            df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'fecha_modificacion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            observaciones = ''
            if nueva_disponibilidad == 'reencauche':
                df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'disponibilidad'] = 'reencauche'
                df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'estado_reencauche'] = 'condicionada_planta'
                mensaje = f"✅ Llanta ID {id_llanta} desmontada. Estado: REENCAUCHE - Condicionada en planta"
            elif nueva_disponibilidad == 'FVU':
                df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'disponibilidad'] = 'FVU'
                df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'estado_reencauche'] = ''
                observaciones = f"FVU: {razon_fvu}"
                mensaje = f"✅ Llanta ID {id_llanta} desmontada. Estado: FVU (Fuera de Uso)"
            else:
                df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'disponibilidad'] = 'recambio'
                df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'estado_reencauche'] = ''
                mensaje = f"✅ Llanta ID {id_llanta} desmontada. Estado: RECAMBIO (Disponible)"

            escribir_hoja(SHEET_LLANTAS, df_llantas)

            # Crear movimiento de desmontaje
            crear_movimiento(
                id_llanta=id_llanta,
                tipo='desmontaje',
                vida=vida_actual,
                placa_vehiculo=placa_actual,
                posicion=posicion_actual,
                kilometraje=kilometraje,
                nueva_disponibilidad=nueva_disponibilidad,
                observaciones=observaciones,
                orden_trabajo=orden_trabajo,
                planilla=planilla,
                operario=operario
            )

            # Crear registro en servicios para el desmontaje
            df_servicios = leer_hoja(SHEET_SERVICIOS)
            df_vehiculos_srv = leer_hoja(SHEET_VEHICULOS)

            # Obtener datos del vehículo
            vehiculo_srv = df_vehiculos_srv[df_vehiculos_srv['placa_vehiculo'] == placa_actual]
            frente = vehiculo_srv.iloc[0].get('frente', 'General') if not vehiculo_srv.empty else 'General'
            tipologia = vehiculo_srv.iloc[0].get('tipologia', '') if not vehiculo_srv.empty else ''

            # Generar ID de servicio
            id_servicio = generar_id_servicio(nit_cliente_llanta)

            nuevo_servicio = pd.DataFrame([{
                'id_servicio': id_servicio,
                'orden_trabajo': orden_trabajo,
                'planilla': planilla,
                'fecha': datetime.now().strftime("%d/%m/%Y"),
                'id_llanta': id_llanta,
                'placa_vehiculo': placa_actual,
                'posicion': posicion_actual,
                'vida': vida_actual,
                'tipologia': tipologia,
                'tipo_servicio': 'desmontaje',
                'disponibilidad': nueva_disponibilidad,
                'kilometraje': kilometraje,
                'rotacion': 'No',
                'posicion_nueva': '',
                'profundidad_1': 0,
                'profundidad_2': 0,
                'profundidad_3': 0,
                'balanceo': 'No',
                'reparacion': 'No',
                'despinche': 'No',
                'regrabacion': 'No',
                'torqueo': 'No',
                'inspeccion': 'No',
                'insumos': '',
                'comentario_fvu': observaciones,
                'operario': operario,
                'usuario_registro': st.session_state['usuario'],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])

            df_servicios = pd.concat([df_servicios, nuevo_servicio], ignore_index=True)
            escribir_hoja(SHEET_SERVICIOS, df_servicios)

            st.success(mensaje)
            st.info(f"📊 Km recorridos este período: **{km_recorridos:,.0f}** | Total acumulado: **{nuevo_total_km:,.0f}** km")
            st.info(f"📋 Servicio de desmontaje registrado: {id_servicio}")
            st.rerun()

# ============= FUNCIÓN: REGISTRAR ALINEACIÓN =============
def registrar_alineacion(embedded=False):
    """Función para registrar alineaciones de vehículos"""

    if not embedded:
        st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
        st.header("🔧 Registro de Alineación")

        if not verificar_permiso(3):
            return

    clientes_acceso = obtener_clientes_accesibles()

    if not clientes_acceso:
        st.warning("No tienes clientes asignados")
        return

    df_vehiculos = leer_hoja(SHEET_VEHICULOS)
    df_vehiculos = filtrar_por_clientes(df_vehiculos, 'nit_cliente', clientes_acceso)

    # Solo vehículos activos
    if 'estado' in df_vehiculos.columns:
        df_vehiculos = df_vehiculos[df_vehiculos['estado'] == 'activo']

    if df_vehiculos.empty:
        st.warning("No hay vehículos activos disponibles")
        return

    tab1, tab2 = st.tabs(["➕ Nueva Alineación", "📋 Historial de Alineaciones"])

    with tab1:
        st.subheader("Registrar Nueva Alineación")

        # Campos de orden de trabajo y planilla (primeras columnas)
        col_ot1, col_ot2 = st.columns(2)
        with col_ot1:
            orden_trabajo = st.text_input("📋 Orden de Trabajo", placeholder="Ej: OT-2024-001", key="alineacion_ot")
        with col_ot2:
            planilla = st.text_input("📄 Planilla", placeholder="Número de planilla", key="alineacion_planilla")

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            placa_vehiculo = st.selectbox(
                "Seleccionar Vehículo",
                options=df_vehiculos['placa_vehiculo'].values,
                format_func=lambda x: f"{x} - {df_vehiculos[df_vehiculos['placa_vehiculo']==x]['marca'].values[0]} {df_vehiculos[df_vehiculos['placa_vehiculo']==x]['linea'].values[0]}",
                key="alineacion_placa"
            )

            fecha_alineacion = st.date_input("Fecha del Servicio", value=datetime.now(), key="alineacion_fecha")

        # Información del vehículo seleccionado (recuadro azul)
        vehiculo_info = df_vehiculos[df_vehiculos['placa_vehiculo'] == placa_vehiculo].iloc[0]
        marca_alin = vehiculo_info.get('marca', '')
        linea_alin = vehiculo_info.get('linea', '')
        km_ini_alin = float(vehiculo_info.get('kilometraje_inicial', 0)) if pd.notna(vehiculo_info.get('kilometraje_inicial', 0)) else 0
        tipologia_alin = vehiculo_info.get('tipologia', '')
        st.info(f"🚛 Vehículo: **{placa_vehiculo}** | {marca_alin} {linea_alin} | Tipología: **{tipologia_alin}** | 📏 Km inicial: **{km_ini_alin:,.0f}**")

        with col2:
            vehiculo_data = df_vehiculos[df_vehiculos['placa_vehiculo'] == placa_vehiculo].iloc[0]
            km_inicial = float(vehiculo_data.get('kilometraje_inicial', 0)) if pd.notna(vehiculo_data.get('kilometraje_inicial', 0)) else 0

            kilometraje = st.number_input(
                "Kilometraje del Vehículo",
                min_value=0,
                value=0,
                step=1,
                key="alineacion_km"
            )

            observaciones = st.text_area("Observaciones", key="alineacion_obs")

        # Obtener operarios del cliente
        nit_cliente_vehiculo = vehiculo_data['nit_cliente']
        operarios_disponibles = obtener_operarios_cliente(nit_cliente_vehiculo)

        if operarios_disponibles:
            operario = st.selectbox("👷 Operario", options=operarios_disponibles, key="alineacion_operario")
        else:
            operario = st.text_input("👷 Operario", placeholder="No hay operarios asignados a este cliente", key="alineacion_operario_txt")

        if st.button("💾 Registrar Alineación", type="primary", key="btn_registrar_alineacion"):
            df_alineaciones = leer_hoja(SHEET_ALINEACIONES)

            nit_cliente = vehiculo_data['nit_cliente']

            # Generar ID de alineación con formato id_cliente
            nuevo_id = generar_id_alineacion(nit_cliente)

            nueva_alineacion = pd.DataFrame([{
                'id_alineacion': nuevo_id,
                'orden_trabajo': orden_trabajo,
                'planilla': planilla,
                'fecha': fecha_alineacion.strftime("%d/%m/%Y"),
                'placa_vehiculo': placa_vehiculo,
                'nit_cliente': nit_cliente,
                'kilometraje': kilometraje,
                'observaciones': observaciones,
                'operario': operario,
                'usuario_registro': st.session_state['usuario'],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])

            df_alineaciones = pd.concat([df_alineaciones, nueva_alineacion], ignore_index=True)
            escribir_hoja(SHEET_ALINEACIONES, df_alineaciones)

            st.success(f"✅ Alineación #{nuevo_id} registrada exitosamente para vehículo {placa_vehiculo}")
            st.balloons()

    with tab2:
        st.subheader("Historial de Alineaciones")

        df_alineaciones = leer_hoja(SHEET_ALINEACIONES)

        if not df_alineaciones.empty:
            # Filtrar por clientes accesibles
            df_alineaciones = filtrar_por_clientes(df_alineaciones, 'nit_cliente', clientes_acceso)

            if not df_alineaciones.empty:
                # Filtro por placa
                placas_disponibles = ['Todas'] + list(df_alineaciones['placa_vehiculo'].unique())
                filtro_placa = st.selectbox("Filtrar por Vehículo", options=placas_disponibles, key="filtro_alineacion_placa")

                if filtro_placa != 'Todas':
                    df_alineaciones = df_alineaciones[df_alineaciones['placa_vehiculo'] == filtro_placa]

                columnas_mostrar = ['id_alineacion', 'fecha', 'placa_vehiculo', 'kilometraje', 'observaciones', 'usuario_registro']
                columnas_disponibles = [col for col in columnas_mostrar if col in df_alineaciones.columns]

                st.dataframe(df_alineaciones[columnas_disponibles].sort_values('id_alineacion', ascending=False), use_container_width=True, hide_index=True)
            else:
                st.info("No hay alineaciones registradas para tus clientes")
        else:
            st.info("No hay alineaciones registradas")

def rotacion_completa():
    """Función para realizar rotación completa de llantas en un vehículo"""

    df_llantas = leer_hoja_fresco(SHEET_LLANTAS)
    df_vehiculos = leer_hoja(SHEET_VEHICULOS)

    clientes_acceso = obtener_clientes_accesibles()
    df_vehiculos = filtrar_por_clientes(df_vehiculos, 'nit_cliente', clientes_acceso)
    df_llantas = filtrar_por_clientes(df_llantas, 'nit_cliente', clientes_acceso)

    if df_vehiculos.empty:
        st.warning("⚠️ No hay vehículos registrados para tus clientes")
        return

    # Solo vehículos activos
    if 'estado' in df_vehiculos.columns:
        df_vehiculos_activos = df_vehiculos[df_vehiculos['estado'] == 'activo']
    else:
        df_vehiculos_activos = df_vehiculos

    if df_vehiculos_activos.empty:
        st.warning("⚠️ No hay vehículos activos disponibles")
        return

    # Campos de orden de trabajo y planilla
    col_ot1, col_ot2 = st.columns(2)
    with col_ot1:
        orden_trabajo = st.text_input("📋 Orden de Trabajo", placeholder="Ej: OT-2024-001", key="rot_ot")
    with col_ot2:
        planilla = st.text_input("📄 Planilla", placeholder="Número de planilla", key="rot_planilla")

    st.divider()

    # Seleccionar vehículo
    placa_vehiculo = st.selectbox(
        "🚛 Seleccionar Vehículo",
        options=df_vehiculos_activos['placa_vehiculo'].values,
        format_func=lambda x: f"{x} - {df_vehiculos_activos[df_vehiculos_activos['placa_vehiculo']==x]['marca'].values[0] if 'marca' in df_vehiculos_activos.columns else ''}",
        key="rot_placa"
    )

    # Obtener datos del vehículo
    vehiculo_data = df_vehiculos_activos[df_vehiculos_activos['placa_vehiculo'] == placa_vehiculo].iloc[0]
    nit_cliente = vehiculo_data['nit_cliente']
    marca_rot = vehiculo_data.get('marca', '')
    linea_rot = vehiculo_data.get('linea', '')
    tipologia_rot = vehiculo_data.get('tipologia', '')
    km_ini_rot = float(vehiculo_data.get('kilometraje_inicial', 0)) if pd.notna(vehiculo_data.get('kilometraje_inicial', 0)) else 0

    st.info(f"🚛 Vehículo: **{placa_vehiculo}** | {marca_rot} {linea_rot} | Tipología: **{tipologia_rot}** | 📏 Km inicial: **{km_ini_rot:,.0f}**")

    # Filtrar llantas montadas en este vehículo
    col_placa = 'placa_actual' if 'placa_actual' in df_llantas.columns else 'placa_vehiculo'
    col_pos = 'posicion_actual' if 'posicion_actual' in df_llantas.columns else 'pos_final'

    llantas_vehiculo = df_llantas[
        (df_llantas['disponibilidad'] == 'al_piso') &
        (df_llantas[col_placa].astype(str) == str(placa_vehiculo))
    ].copy()

    if llantas_vehiculo.empty:
        st.warning(f"⚠️ No hay llantas montadas en el vehículo {placa_vehiculo}")
        return

    if len(llantas_vehiculo) < 2:
        st.warning("⚠️ Se necesitan al menos 2 llantas montadas para realizar una rotación")
        return

    # Kilometraje
    kilometraje = st.number_input("📏 Kilometraje actual del vehículo", min_value=0, value=0, key="rot_km")

    st.divider()
    st.subheader("📍 Asignar nuevas posiciones")
    st.caption("Ingresa la nueva posición para cada llanta. Deja igual si no se mueve.")

    # Normalizar posiciones actuales (evita "nan" cuando no hay posición guardada)
    nuevas_posiciones = {}
    posiciones_actuales = {}
    for _, row in llantas_vehiculo.iterrows():
        id_ll = str(row['id_llanta'])
        pos_raw = row.get(col_pos, '')
        if pd.isna(pos_raw) or str(pos_raw).strip().lower() in ('nan', ''):
            pos_actual = ''
        else:
            try:
                pos_actual = str(int(float(pos_raw)))
            except (ValueError, TypeError):
                pos_actual = str(pos_raw).strip()
        posiciones_actuales[id_ll] = pos_actual

    # Crear inputs para cada llanta
    cols_header = st.columns([2, 2, 1, 2, 2])
    cols_header[0].write("**ID Llanta**")
    cols_header[1].write("**Marca / Dim.**")
    cols_header[2].write("**Km montaje**")
    cols_header[3].write("**Pos. Actual**")
    cols_header[4].write("**Nueva Posición**")

    for _, row in llantas_vehiculo.iterrows():
        id_ll = str(row['id_llanta'])
        pos_actual = posiciones_actuales[id_ll]
        marca = row.get('marca_llanta', '')
        dimension = row.get('dimension', '')
        km_raw = row.get('km_ultimo_montaje', None)
        try:
            km_txt = f"{int(float(km_raw)):,}" if pd.notna(km_raw) and str(km_raw).strip().lower() != 'nan' else 'N/A'
        except (ValueError, TypeError):
            km_txt = 'N/A'

        cols = st.columns([2, 2, 1, 2, 2])
        cols[0].write(f"`{id_ll}`")
        cols[1].write(f"{marca} {dimension}")
        cols[2].write(km_txt)
        cols[3].write(f"**{pos_actual}**" if pos_actual else "⚠️ *sin pos.*")
        nueva_pos = cols[4].text_input(
            "Nueva pos.", value=pos_actual, key=f"rot_pos_{id_ll}",
            label_visibility="collapsed"
        )
        nuevas_posiciones[id_ll] = nueva_pos.strip()

    # Operario
    operarios_disponibles = obtener_operarios_cliente(nit_cliente)
    st.divider()
    if operarios_disponibles:
        operario = st.selectbox("👷 Operario", options=operarios_disponibles, key="rot_operario")
    else:
        operario = st.text_input("👷 Operario", placeholder="No hay operarios asignados", key="rot_operario_txt")

    # Validar que haya al menos un cambio
    hay_cambio = any(
        nuevas_posiciones[id_ll] != posiciones_actuales[id_ll]
        for id_ll in posiciones_actuales
    )

    # Validar duplicados en nuevas posiciones
    pos_nuevas_list = [v for v in nuevas_posiciones.values() if v]
    hay_duplicados = len(pos_nuevas_list) != len(set(pos_nuevas_list))

    if hay_duplicados:
        st.error("⚠️ Hay posiciones duplicadas en la asignación. Cada llanta debe tener una posición única.")

    if not hay_cambio:
        st.warning("⚠️ No hay cambios de posición. Modifica al menos una posición para registrar la rotación.")

    if st.button("🔄 Ejecutar Rotación", type="primary", key="rot_btn_ejecutar", disabled=(not hay_cambio or hay_duplicados)):
        if kilometraje <= 0:
            st.error("Debes ingresar el kilometraje actual del vehículo")
        else:
            df_llantas_update = leer_hoja(SHEET_LLANTAS)
            df_servicios = leer_hoja(SHEET_SERVICIOS)

            frente = vehiculo_data.get('frente', 'General')
            tipologia = vehiculo_data.get('tipologia', '')

            llantas_rotadas = []
            for id_ll, nueva_pos in nuevas_posiciones.items():
                pos_anterior = posiciones_actuales[id_ll]
                if nueva_pos != pos_anterior:
                    # Actualizar posición en tabla de llantas
                    df_llantas_update.loc[df_llantas_update['id_llanta'].astype(str) == id_ll, 'posicion_actual'] = nueva_pos
                    df_llantas_update.loc[df_llantas_update['id_llanta'].astype(str) == id_ll, 'fecha_modificacion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    llantas_rotadas.append({
                        'id_llanta': id_ll,
                        'pos_anterior': pos_anterior,
                        'pos_nueva': nueva_pos
                    })

            escribir_hoja(SHEET_LLANTAS, df_llantas_update)

            # Crear un registro de servicio por cada llanta rotada
            for ll_rot in llantas_rotadas:
                id_servicio = generar_id_servicio(nit_cliente)

                # Obtener vida actual
                llanta_row = df_llantas_update[df_llantas_update['id_llanta'].astype(str) == ll_rot['id_llanta']]
                vida = int(llanta_row['vida_actual'].values[0]) if not llanta_row.empty and 'vida_actual' in llanta_row.columns and pd.notna(llanta_row['vida_actual'].values[0]) else 1

                nuevo_servicio = pd.DataFrame([{
                    'id_servicio': id_servicio,
                    'orden_trabajo': orden_trabajo,
                    'planilla': planilla,
                    'fecha': datetime.now().strftime("%d/%m/%Y"),
                    'id_llanta': ll_rot['id_llanta'],
                    'placa_vehiculo': placa_vehiculo,
                    'posicion': ll_rot['pos_anterior'],
                    'vida': vida,
                    'tipologia': tipologia,
                    'tipo_servicio': 'rotacion',
                    'disponibilidad': 'al_piso',
                    'kilometraje': kilometraje,
                    'rotacion': 'Sí',
                    'posicion_nueva': ll_rot['pos_nueva'],
                    'profundidad_1': 0,
                    'profundidad_2': 0,
                    'profundidad_3': 0,
                    'balanceo': 'No',
                    'reparacion': 'No',
                    'despinche': 'No',
                    'regrabacion': 'No',
                    'torqueo': 'No',
                    'inspeccion': 'No',
                    'insumos': '',
                    'comentario_fvu': '',
                    'operario': operario,
                    'usuario_registro': st.session_state['usuario'],
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])

                df_servicios = pd.concat([df_servicios, nuevo_servicio], ignore_index=True)

            escribir_hoja(SHEET_SERVICIOS, df_servicios)

            # Crear movimientos de rotación
            for ll_rot in llantas_rotadas:
                crear_movimiento(
                    id_llanta=ll_rot['id_llanta'],
                    tipo='rotacion',
                    vida=1,
                    placa_vehiculo=placa_vehiculo,
                    posicion=ll_rot['pos_nueva'],
                    kilometraje=kilometraje,
                    observaciones=f"Rotación: {ll_rot['pos_anterior']} → {ll_rot['pos_nueva']}",
                    orden_trabajo=orden_trabajo,
                    planilla=planilla,
                    operario=operario
                )

            resumen = " | ".join([f"{ll['id_llanta']}: {ll['pos_anterior']}→{ll['pos_nueva']}" for ll in llantas_rotadas])
            st.success(f"✅ Rotación completada: {len(llantas_rotadas)} llanta(s) rotadas")
            st.info(f"📋 {resumen}")
            st.balloons()
            st.rerun()


# ============= FUNCIÓN: SERVICIOS INTEGRADOS (WRAPPER CON TABS) =============
def servicios_integrados():
    """Función principal que centraliza todos los servicios en tabs"""

    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("🛠️ Servicios")

    if not verificar_permiso(3):
        return

    tab_srv, tab_montaje, tab_desmontaje, tab_alineacion, tab_rotacion = st.tabs([
        "🛠️ Registro de Servicio",
        "🔧 Montaje",
        "🔽 Desmontaje",
        "📐 Alineación",
        "🔄 Rotación Completa"
    ])

    with tab_srv:
        registrar_servicios(embedded=True)

    with tab_montaje:
        montaje_llantas(embedded=True)

    with tab_desmontaje:
        desmontaje_llantas(embedded=True)

    with tab_alineacion:
        registrar_alineacion(embedded=True)

    with tab_rotacion:
        rotacion_completa()


def reportes():
    """Función para generar reportes y análisis"""
    
    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("📊 Reportes y Análisis")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Desgaste de Llantas", "🛠️ Servicios por Llanta", "🚛 Servicios por Vehículo", "📊 Estado de Flota", "📥 Exportar Datos"])
    
    with tab1:
        st.subheader("Análisis de Desgaste")
        
        df_servicios = leer_hoja(SHEET_SERVICIOS)
        
        if df_servicios.empty:
            st.info("No hay datos de servicios para analizar")
        else:
            col1, col2 = st.columns(2)
            with col1:
                filtro_llantas = st.multiselect(
                    "Filtrar Llantas",
                    options=['Todas'] + list(df_servicios['id_llanta'].unique()),
                    default=['Todas']
                )
            
            if 'Todas' in filtro_llantas:
                id_llanta_filtro = st.selectbox(
                    "Seleccionar Llanta para Análisis",
                    options=df_servicios['id_llanta'].unique()
                )
            else:
                id_llanta_filtro = st.selectbox(
                    "Seleccionar Llanta para Análisis",
                    options=filtro_llantas
                )
            
            servicios_llanta = df_servicios[df_servicios['id_llanta'] == id_llanta_filtro].sort_values('timestamp')
            
            if not servicios_llanta.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Total de Servicios", len(servicios_llanta))
                    st.metric("Profundidad Promedio Actual", 
                             f"{servicios_llanta.iloc[-1][['profundidad_1', 'profundidad_2', 'profundidad_3']].mean():.2f} mm")
                
                with col2:
                    if len(servicios_llanta) > 1:
                        primera_prof = servicios_llanta.iloc[0][['profundidad_1', 'profundidad_2', 'profundidad_3']].mean()
                        ultima_prof = servicios_llanta.iloc[-1][['profundidad_1', 'profundidad_2', 'profundidad_3']].mean()
                        desgaste = primera_prof - ultima_prof
                        st.metric("Desgaste Total", f"{desgaste:.2f} mm")
                        
                        fecha_inicio = pd.to_datetime(servicios_llanta.iloc[0]['timestamp'])
                        fecha_fin = pd.to_datetime(servicios_llanta.iloc[-1]['timestamp'])
                        dias_uso = (fecha_fin - fecha_inicio).days
                        
                        if dias_uso > 0:
                            st.metric("Desgaste Promedio Diario", f"{desgaste/dias_uso:.3f} mm/día")
                
                st.divider()
                st.write("**Historial de Profundidades**")
                columnas_reporte = [col for col in ['id_servicio', 'fecha', 'kilometraje', 'profundidad_1', 'profundidad_2', 'profundidad_3', 'pos_final', 'comentario_fvu'] if col in servicios_llanta.columns]
                st.dataframe(servicios_llanta[columnas_reporte], use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("Servicios por Llanta")
        
        df_servicios = leer_hoja(SHEET_SERVICIOS)
        
        if not df_servicios.empty:
            resumen = df_servicios.groupby('id_llanta').agg({
                'id_servicio': 'count',
                'rotacion': lambda x: (x == 'Sí').sum(),
                'balanceo': lambda x: (x == 'Sí').sum(),
                'reparacion': lambda x: (x == 'Sí').sum() if 'reparacion' in df_servicios.columns else 0,
                'despinche': lambda x: (x == 'Sí').sum() if 'despinche' in df_servicios.columns else 0,
                'regrabacion': lambda x: (x == 'Sí').sum(),
                'torqueo': lambda x: (x == 'Sí').sum()
            }).reset_index()

            resumen.columns = ['ID Llanta', 'Total Servicios', 'Rotaciones', 'Balanceos', 'Reparaciones', 'Despinches', 'Regrabaciones', 'Torqueos']
            
            st.dataframe(resumen, use_container_width=True, hide_index=True)
            
            st.divider()
            id_llanta_detalle = st.selectbox(
                "Ver Detalle de Llanta",
                options=df_servicios['id_llanta'].unique(),
                key="detalle_servicios"
            )
            
            servicios_detalle = df_servicios[df_servicios['id_llanta'] == id_llanta_detalle].sort_values('timestamp', ascending=False)
            st.dataframe(servicios_detalle, use_container_width=True, hide_index=True)
        else:
            st.info("No hay servicios registrados")
    
    with tab3:
        st.subheader("Servicios por Vehículo")
        
        df_servicios = leer_hoja(SHEET_SERVICIOS)
        
        if not df_servicios.empty:
            col1, col2 = st.columns(2)
            with col1:
                filtro_vehiculos = st.multiselect(
                    "Filtrar Vehículos",
                    options=['Todos'] + list(df_servicios['placa_vehiculo'].unique()),
                    default=['Todos']
                )
            
            if 'Todos' in filtro_vehiculos:
                vehiculo_filtro = st.selectbox(
                    "Seleccionar Vehículo",
                    options=df_servicios['placa_vehiculo'].unique()
                )
            else:
                vehiculo_filtro = st.selectbox(
                    "Seleccionar Vehículo",
                    options=filtro_vehiculos
                )
            
            servicios_vehiculo = df_servicios[df_servicios['placa_vehiculo'] == vehiculo_filtro].sort_values('timestamp', ascending=False)
            
            if not servicios_vehiculo.empty:
                st.metric("Total de Servicios en este Vehículo", len(servicios_vehiculo))
                
                st.divider()
                st.write("**Historial de Servicios**")
                columnas_vehiculo = [col for col in ['id_servicio', 'fecha', 'id_llanta', 'pos_inicial', 'vida', 'tipologia', 'kilometraje', 'profundidad_1', 'profundidad_2', 'profundidad_3'] if col in servicios_vehiculo.columns]
                st.dataframe(servicios_vehiculo[columnas_vehiculo], use_container_width=True, hide_index=True)
        else:
            st.info("No hay servicios registrados")
    
    with tab4:
        st.subheader("Estado General de la Flota")
        
        df_llantas = leer_hoja(SHEET_LLANTAS)
        df_vehiculos = leer_hoja(SHEET_VEHICULOS)
        
        clientes_acceso = obtener_clientes_accesibles()
        df_llantas = filtrar_por_clientes(df_llantas, 'nit_cliente', clientes_acceso)
        df_vehiculos = filtrar_por_clientes(df_vehiculos, 'nit_cliente', clientes_acceso)
        
        if not df_llantas.empty and 'disponibilidad' in df_llantas.columns:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Llantas", len(df_llantas))

            with col2:
                en_uso = len(df_llantas[df_llantas['disponibilidad'] == 'al_piso'])
                st.metric("Llantas en Uso", en_uso)
            
            with col3:
                disponibles = len(df_llantas[df_llantas['disponibilidad'].isin(['llanta_nueva', 'recambio'])])
                st.metric("Llantas Disponibles", disponibles)
            
            with col4:
                fvu = len(df_llantas[df_llantas['disponibilidad'] == 'FVU'])
                st.metric("Llantas FVU", fvu)
            
            st.divider()
            
            st.write("**Distribución por Estado**")
            estado_counts = df_llantas['disponibilidad'].value_counts()
            st.bar_chart(estado_counts)
            
            st.divider()
            
            st.write("**Llantas por Vehículo**")
            if not df_vehiculos.empty:
                vehiculos_con_llantas = df_llantas[df_llantas['placa_vehiculo'] != ''].groupby('placa_vehiculo').size().reset_index(name='cantidad_llantas')
                vehiculos_info = df_vehiculos.merge(vehiculos_con_llantas, on='placa_vehiculo', how='left')
                vehiculos_info['cantidad_llantas'].fillna(0, inplace=True)
                st.dataframe(vehiculos_info[['placa_vehiculo', 'marca', 'linea', 'tipologia', 'frente', 'estado', 'cantidad_llantas']], use_container_width=True, hide_index=True)
        else:
            st.info("No hay llantas registradas o no tienes acceso")
    
    with tab5:
        st.subheader("Exportar Datos")

        st.write("Descarga los datos en formato CSV para análisis externo")

        # Obtener clientes accesibles para filtrar exportaciones
        clientes_acceso_export = obtener_clientes_accesibles()

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📥 Descargar Servicios", use_container_width=True):
                df_servicios = leer_hoja(SHEET_SERVICIOS)
                # Filtrar por cliente si no es admin
                if st.session_state.get('nivel') != 1:
                    df_llantas_temp = leer_hoja(SHEET_LLANTAS)
                    llantas_cliente = df_llantas_temp[df_llantas_temp['nit_cliente'].isin(clientes_acceso_export)]['id_llanta'].tolist()
                    df_servicios = df_servicios[df_servicios['id_llanta'].isin(llantas_cliente)]
                csv = df_servicios.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="💾 Servicios.csv",
                    data=csv,
                    file_name=f"servicios_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime='text/csv'
                )

            if st.button("📥 Descargar Llantas", use_container_width=True):
                df_llantas = leer_hoja(SHEET_LLANTAS)
                df_llantas = filtrar_por_clientes(df_llantas, 'nit_cliente', clientes_acceso_export)
                csv = df_llantas.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="💾 Llantas.csv",
                    data=csv,
                    file_name=f"llantas_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime='text/csv'
                )

        with col2:
            if st.button("📥 Descargar Vehículos", use_container_width=True):
                df_vehiculos = leer_hoja(SHEET_VEHICULOS)
                df_vehiculos = filtrar_por_clientes(df_vehiculos, 'nit_cliente', clientes_acceso_export)
                csv = df_vehiculos.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="💾 Vehiculos.csv",
                    data=csv,
                    file_name=f"vehiculos_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime='text/csv'
                )

            if st.button("📥 Descargar Clientes", use_container_width=True):
                df_clientes = leer_hoja(SHEET_CLIENTES)
                df_clientes = filtrar_por_clientes(df_clientes, 'nit', clientes_acceso_export)
                csv = df_clientes.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="💾 Clientes.csv",
                    data=csv,
                    file_name=f"clientes_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime='text/csv'
                )

        with col3:
            if st.button("📥 Descargar Movimientos", use_container_width=True):
                df_movimientos = leer_hoja(SHEET_MOVIMIENTOS)
                # Filtrar por cliente si no es admin
                if st.session_state.get('nivel') != 1:
                    df_llantas_temp = leer_hoja(SHEET_LLANTAS)
                    llantas_cliente = df_llantas_temp[df_llantas_temp['nit_cliente'].isin(clientes_acceso_export)]['id_llanta'].tolist()
                    df_movimientos = df_movimientos[df_movimientos['id_llanta'].isin(llantas_cliente)]
                csv = df_movimientos.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="💾 Movimientos.csv",
                    data=csv,
                    file_name=f"movimientos_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime='text/csv'
                )

# ============= FUNCIÓN: MI PERFIL =============
def mi_perfil():
    """Permite a cualquier usuario editar su propio perfil"""

    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("👤 Mi Perfil")

    usuario_actual = st.session_state.get('usuario', '')

    # Leer datos del usuario actual
    df_usuarios = leer_hoja(SHEET_USUARIOS)
    usuario_data = df_usuarios[df_usuarios['usuario'] == usuario_actual]

    if usuario_data.empty:
        st.error("Error al cargar datos del usuario")
        return

    usuario_data = usuario_data.iloc[0]

    st.subheader("Editar mis datos")

    col1, col2 = st.columns(2)

    with col1:
        nuevo_usuario = st.text_input("Nombre de Usuario", value=usuario_data.get('usuario', ''), key="mi_perfil_usuario")
        nuevo_nombre = st.text_input("Nombre Completo", value=usuario_data.get('nombre', ''), key="mi_perfil_nombre")

    with col2:
        nueva_password = st.text_input("Nueva Contraseña (dejar vacío para mantener)", type="password", key="mi_perfil_password")
        confirmar_password = st.text_input("Confirmar Contraseña", type="password", key="mi_perfil_confirmar")

    st.info(f"**Nivel de acceso:** {usuario_data.get('nivel', '')} - No modificable")

    if st.button("💾 Guardar Cambios", key="guardar_mi_perfil", type="primary"):
        if not nuevo_usuario:
            st.error("El nombre de usuario no puede estar vacío")
        elif not nuevo_nombre:
            st.error("El nombre completo no puede estar vacío")
        elif nueva_password and nueva_password != confirmar_password:
            st.error("Las contraseñas no coinciden")
        else:
            df_todos = leer_hoja(SHEET_USUARIOS)

            # Verificar que el nuevo nombre de usuario no exista (si cambió)
            if nuevo_usuario != usuario_actual:
                if existe_valor(df_todos, 'usuario', nuevo_usuario):
                    st.error("Este nombre de usuario ya existe")
                    st.stop()

            # Actualizar datos
            df_todos.loc[df_todos['usuario'] == usuario_actual, 'usuario'] = nuevo_usuario
            df_todos.loc[df_todos['usuario'] == nuevo_usuario, 'nombre'] = nuevo_nombre

            # Solo actualizar contraseña si se proporcionó una nueva
            if nueva_password:
                df_todos.loc[df_todos['usuario'] == nuevo_usuario, 'password'] = nueva_password

            escribir_hoja(SHEET_USUARIOS, df_todos)

            # Actualizar session_state con los nuevos datos
            st.session_state['usuario'] = nuevo_usuario
            st.session_state['nombre'] = nuevo_nombre

            st.success("✅ Perfil actualizado con éxito")
            st.rerun()

def gestion_usuarios():
    """Función para gestionar usuarios (solo nivel 1)"""
    
    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("👥 Gestión de Usuarios")
    
    if not verificar_permiso(1):
        return
    
    tab1, tab2, tab3 = st.tabs(["➕ Crear Usuario", "📋 Ver Usuarios", "✏️ Editar/Eliminar"])

    with tab1:
        st.subheader("Crear Nuevo Usuario")

        col1, col2 = st.columns(2)

        with col1:
            nuevo_usuario = st.text_input("Nombre de Usuario", key="crear_nuevo_usuario")
            nuevo_nombre = st.text_input("Nombre Completo", key="crear_nombre_completo")

        with col2:
            nueva_password = st.text_input("Contraseña", type="password", key="crear_password")
            nuevo_nivel = st.selectbox("Nivel de Acceso",
                                      options=[1, 2, 3, 4],
                                      format_func=lambda x: f"Nivel {x} - {'Administrador' if x==1 else 'Supervisor' if x==2 else 'Operario' if x==3 else 'Admin Cliente'}",
                                      key="crear_nivel_acceso")

        clientes_seleccionados = ""
        if nuevo_nivel in [2, 3, 4]:
            nivel_nombre = 'Supervisor' if nuevo_nivel == 2 else 'Operario' if nuevo_nivel == 3 else 'Admin Cliente'
            st.write(f"**Asignar Clientes para {nivel_nombre}**")
            df_clientes = leer_hoja(SHEET_CLIENTES)
            if not df_clientes.empty:
                clientes_opciones = st.multiselect(
                    "Seleccionar Clientes",
                    options=df_clientes['nit'].values,
                    format_func=lambda x: f"{df_clientes[df_clientes['nit']==x]['nombre_cliente'].values[0]} - {x}",
                    key="crear_clientes_asignados"
                )
                clientes_seleccionados = ','.join([str(c) for c in clientes_opciones])

        if st.button("💾 Crear Usuario", type="primary"):
            if not nuevo_usuario or not nueva_password or not nuevo_nombre:
                st.error("Debes completar todos los campos")
            elif nuevo_nivel in [2, 3, 4] and not clientes_seleccionados:
                st.error(f"Debes asignar al menos un cliente para este nivel de usuario")
            else:
                # Leer datos frescos SIN caché para verificar duplicados
                df_usuarios = leer_hoja_fresco(SHEET_USUARIOS)

                if existe_valor(df_usuarios, 'usuario', nuevo_usuario):
                    st.error("Este nombre de usuario ya existe")
                else:
                    # Generar ID de usuario automático
                    id_usuario = generar_id_usuario(nuevo_nombre, df_usuarios)

                    nuevo_user = pd.DataFrame([{
                        'id_usuario': id_usuario,
                        'usuario': nuevo_usuario,
                        'password': nueva_password,
                        'nivel': nuevo_nivel,
                        'nombre': nuevo_nombre,
                        'clientes_asignados': clientes_seleccionados
                    }])

                    df_usuarios = pd.concat([df_usuarios, nuevo_user], ignore_index=True)
                    escribir_hoja(SHEET_USUARIOS, df_usuarios)
                    st.success(f"✅ Usuario creado con éxito - ID: {id_usuario}")
                    st.balloons()
                    st.rerun()
    
    with tab2:
        df_usuarios = leer_hoja(SHEET_USUARIOS)
        df_clientes = leer_hoja(SHEET_CLIENTES)
        
        for idx, row in df_usuarios.iterrows():
            with st.expander(f"👤 {row.get('nombre', 'N/A')} - Nivel {row.get('nivel', 'N/A')}"):
                st.write(f"**ID Usuario:** {row.get('id_usuario', 'N/A')}")
                st.write(f"**Usuario:** {row.get('usuario', 'N/A')}")
                nivel = row.get('nivel', 0)
                st.write(f"**Nivel:** {nivel} - {'Administrador' if nivel==1 else 'Supervisor' if nivel==2 else 'Operario' if nivel==3 else 'Admin Cliente'}")
                
                clientes_asignados = row.get('clientes_asignados', '')
                if nivel in [2, 3, 4] and clientes_asignados and pd.notna(clientes_asignados):
                    clientes_nits = str(clientes_asignados).split(',')
                    nombres_clientes = []
                    for nit in clientes_nits:
                        if nit and existe_valor(df_clientes, 'nit', nit):
                            cliente_row = df_clientes[df_clientes['nit'].astype(str) == str(nit)]
                            if not cliente_row.empty:
                                nombre = cliente_row['nombre_cliente'].values[0]
                                nombres_clientes.append(f"{nombre} ({nit})")
                    if nombres_clientes:
                        st.write(f"**Clientes Asignados:** {', '.join(nombres_clientes)}")
        
        st.info("""
        **Niveles de Usuario:**
        - **Nivel 1 (Administrador)**: Acceso total al sistema
        - **Nivel 2 (Supervisor)**: Vehículos, Llantas, Montaje, Servicios, Desmontaje, Reportes, Editar datos (solo clientes asignados)
        - **Nivel 3 (Operario)**: Llantas, Montaje, Servicios, Desmontaje, Reportes - Solo registrar, NO editar (solo clientes asignados)
        - **Nivel 4 (Admin Cliente)**: Vehículos, Llantas, Estado, Montaje, Servicios, Desmontaje, Reportes, Editar (solo clientes asignados, NO gestión de clientes)
        """)

    with tab3:
        st.subheader("Editar o Eliminar Usuario")

        df_usuarios = leer_hoja(SHEET_USUARIOS)
        df_clientes = leer_hoja(SHEET_CLIENTES)

        if not df_usuarios.empty:
            usuario_editar = st.selectbox(
                "Seleccionar Usuario",
                options=df_usuarios['usuario'].values,
                format_func=lambda x: f"[{df_usuarios[df_usuarios['usuario']==x]['id_usuario'].values[0] if 'id_usuario' in df_usuarios.columns and pd.notna(df_usuarios[df_usuarios['usuario']==x]['id_usuario'].values[0]) else 'Sin ID'}] {df_usuarios[df_usuarios['usuario']==x]['nombre'].values[0]} ({x}) - Nivel {df_usuarios[df_usuarios['usuario']==x]['nivel'].values[0]}",
                key="select_usuario_editar"
            )

            usuario_data = df_usuarios[df_usuarios['usuario'] == usuario_editar].iloc[0]

            # No permitir editar el propio usuario admin que está logueado
            if usuario_editar == st.session_state.get('usuario'):
                st.warning("⚠️ No puedes editar tu propio usuario mientras estás conectado")
            else:
                st.write("**Datos del Usuario:**")

                # Mostrar ID de usuario (no editable)
                id_usuario_actual = usuario_data.get('id_usuario', 'Sin ID')
                st.info(f"🆔 **ID Usuario:** {id_usuario_actual} (no editable)")

                col1, col2 = st.columns(2)

                with col1:
                    edit_usuario = st.text_input("Nombre de Usuario", value=usuario_data.get('usuario', ''), key="edit_usuario_nombre")
                    edit_nombre = st.text_input("Nombre Completo", value=usuario_data.get('nombre', ''), key="edit_nombre_usuario")

                with col2:
                    edit_password = st.text_input("Nueva Contraseña (dejar vacío para mantener)", type="password", key="edit_password_usuario")
                    niveles = [1, 2, 3, 4]
                    nivel_actual = int(usuario_data.get('nivel', 3)) if pd.notna(usuario_data.get('nivel')) else 3
                    nivel_idx = niveles.index(nivel_actual) if nivel_actual in niveles else 2
                    edit_nivel = st.selectbox(
                        "Nivel de Acceso",
                        options=niveles,
                        index=nivel_idx,
                        format_func=lambda x: f"Nivel {x} - {'Administrador' if x==1 else 'Supervisor' if x==2 else 'Operario' if x==3 else 'Admin Cliente'}",
                        key="edit_nivel_usuario"
                    )

                # Asignar clientes si el nivel lo requiere
                edit_clientes = ""
                if edit_nivel in [2, 3, 4]:
                    nivel_nombre = 'Supervisor' if edit_nivel == 2 else 'Operario' if edit_nivel == 3 else 'Admin Cliente'
                    st.write(f"**Asignar Clientes para {nivel_nombre}**")
                    if not df_clientes.empty:
                        # Obtener clientes actuales asignados
                        clientes_actuales = []
                        clientes_asignados_str = usuario_data.get('clientes_asignados', '')
                        if clientes_asignados_str and pd.notna(clientes_asignados_str) and isinstance(clientes_asignados_str, str):
                            clientes_actuales = [c.strip() for c in clientes_asignados_str.split(',') if c.strip()]

                        clientes_opciones_edit = st.multiselect(
                            "Seleccionar Clientes",
                            options=df_clientes['nit'].values,
                            default=[c for c in clientes_actuales if c in df_clientes['nit'].values],
                            format_func=lambda x: f"{df_clientes[df_clientes['nit']==x]['nombre_cliente'].values[0]} - {x}",
                            key="edit_clientes_usuario"
                        )
                        edit_clientes = ','.join([str(c) for c in clientes_opciones_edit])

                col_btn1, col_btn2 = st.columns(2)

                with col_btn1:
                    if st.button("💾 Guardar Cambios", key="guardar_usuario", type="primary"):
                        if not edit_usuario:
                            st.error("El nombre de usuario no puede estar vacío")
                        elif not edit_nombre:
                            st.error("El nombre completo no puede estar vacío")
                        elif edit_nivel in [2, 3, 4] and not edit_clientes:
                            st.error("Debes asignar al menos un cliente para este nivel")
                        else:
                            df_todos = leer_hoja(SHEET_USUARIOS)

                            # Verificar que el nuevo nombre de usuario no exista (si cambió)
                            if edit_usuario != usuario_editar:
                                if existe_valor(df_todos, 'usuario', edit_usuario):
                                    st.error("Este nombre de usuario ya existe")
                                    st.stop()

                            # Actualizar todos los campos incluyendo el nombre de usuario
                            df_todos.loc[df_todos['usuario'] == usuario_editar, 'usuario'] = edit_usuario
                            df_todos.loc[df_todos['usuario'] == edit_usuario, 'nombre'] = edit_nombre
                            df_todos.loc[df_todos['usuario'] == edit_usuario, 'nivel'] = edit_nivel
                            df_todos.loc[df_todos['usuario'] == edit_usuario, 'clientes_asignados'] = edit_clientes

                            # Solo actualizar contraseña si se proporcionó una nueva
                            if edit_password:
                                df_todos.loc[df_todos['usuario'] == edit_usuario, 'password'] = edit_password

                            escribir_hoja(SHEET_USUARIOS, df_todos)
                            st.success("✅ Usuario actualizado con éxito")
                            st.rerun()

                with col_btn2:
                    if st.button("🗑️ Eliminar Usuario", key="eliminar_usuario"):
                        df_todos = leer_hoja(SHEET_USUARIOS)
                        df_todos = df_todos[df_todos['usuario'] != usuario_editar]
                        escribir_hoja(SHEET_USUARIOS, df_todos)
                        st.success("✅ Usuario eliminado con éxito")
                        st.rerun()
        else:
            st.info("No hay usuarios registrados")

def main():
    """Función principal del sistema"""
    
    inicializar_datos()
    
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if not st.session_state['logged_in']:
        login()
        return
    
    with st.sidebar:
        st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/logo-sill.jpg", use_container_width=True)
        
        st.markdown("""
            <div style="background-color: #272F59; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                <h2 style="color: white; text-align: center; margin: 0;">Sistema Integrado de Llantas</h2>
            </div>
        """, unsafe_allow_html=True)
        
        st.write(f"**Usuario:** {st.session_state['nombre']}")
        st.write(f"**Nivel:** {st.session_state['nivel']}")
        
        st.divider()
        
        st.subheader("¿Qué quieres hacer hoy?")

        nivel_usuario = st.session_state['nivel']

        # Menú base para todos los usuarios
        opciones_menu = {}

        # Nivel 1 (Admin): Acceso total
        if nivel_usuario == 1:
            opciones_menu = {
                "👤 Gestión de Clientes": "clientes",
                "🚛 Gestión de Vehículos": "vehiculos",
                "⚙️ Gestión de Llantas": "llantas",
                "🔍 Estado de Llantas": "estado_llantas",
                "🛠️ Servicios": "servicios_integrados",
                "📊 Reportes y Análisis": "reportes",
                "📤 Subir Datos CSV": "subir_csv",
                "✏️ Editar/Eliminar Datos": "editar_datos",
                "👥 Gestión de Usuarios": "usuarios",
                "🔑 Mi Perfil": "mi_perfil"
            }
        # Nivel 2 (Supervisor): Vehículos, Llantas, Servicios, Reportes, Editar
        elif nivel_usuario == 2:
            opciones_menu = {
                "🚛 Gestión de Vehículos": "vehiculos",
                "⚙️ Gestión de Llantas": "llantas",
                "🔍 Estado de Llantas": "estado_llantas",
                "🛠️ Servicios": "servicios_integrados",
                "📊 Reportes y Análisis": "reportes",
                "✏️ Editar/Eliminar Datos": "editar_datos",
                "🔑 Mi Perfil": "mi_perfil"
            }
        # Nivel 3 (Operario): Llantas, Servicios, Reportes (solo ver, no editar)
        elif nivel_usuario == 3:
            opciones_menu = {
                "⚙️ Gestión de Llantas": "llantas",
                "🔍 Estado de Llantas": "estado_llantas",
                "🛠️ Servicios": "servicios_integrados",
                "📊 Reportes y Análisis": "reportes",
                "🔑 Mi Perfil": "mi_perfil"
            }
        # Nivel 4 (Admin Cliente): Vehículos, Llantas, Estado, Servicios, Reportes, Editar (NO clientes)
        elif nivel_usuario == 4:
            opciones_menu = {
                "🚛 Gestión de Vehículos": "vehiculos",
                "⚙️ Gestión de Llantas": "llantas",
                "🔍 Estado de Llantas": "estado_llantas",
                "🛠️ Servicios": "servicios_integrados",
                "📊 Reportes y Análisis": "reportes",
                "✏️ Editar/Eliminar Datos": "editar_datos",
                "🔑 Mi Perfil": "mi_perfil"
            }

        opcion = st.radio("Menú Principal", list(opciones_menu.keys()), label_visibility="collapsed")
        
        st.divider()
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        
        st.divider()
        
        with st.expander("ℹ️ Información de Permisos"):
            if st.session_state['nivel'] == 1:
                st.success("✅ Acceso Total al Sistema")
            elif st.session_state['nivel'] == 2:
                st.info("✅ Vehículos, Llantas, Servicios (Montaje, Desmontaje, Alineación, Rotación), Reportes, Editar datos, Mi Perfil\n❌ Clientes, Subir CSV, Usuarios")
            elif st.session_state['nivel'] == 3:
                st.warning("✅ Llantas, Servicios (Montaje, Desmontaje, Alineación, Rotación), Reportes, Mi Perfil (solo registrar)\n❌ Vehículos, Clientes, Editar datos")
            elif st.session_state['nivel'] == 4:
                st.info("✅ Vehículos, Llantas, Estado, Servicios (Montaje, Desmontaje, Alineación, Rotación), Reportes, Editar, Mi Perfil (solo clientes asignados)\n❌ Gestión de Clientes, Subir CSV, Usuarios")
        
        st.divider()
        
        logo_url = "https://elchorro.com.co/wp-content/uploads/2025/04/ch-plano.png?w=106&h=106"
        col_logo, col_texto = st.columns([1, 3], vertical_alignment="center")
        with col_logo:
            st.image(logo_url, width=60)
        with col_texto:
            st.markdown("""
                <div style="font-size:10px; line-height:1.1;">
                    <span style="font-style:italic;">Este programa fue desarrollado por:</span><br>
                    <span style="font-weight:bold;">Daniel Cortázar Triana</span><br>
                    <span style="font-weight:bold;">El Chorro Producciones SAS</span>
                </div>
            """, unsafe_allow_html=True)
    
    opcion_seleccionada = opciones_menu[opcion]

    if opcion_seleccionada == "clientes":
        crear_cliente()
    elif opcion_seleccionada == "vehiculos":
        crear_vehiculos()
    elif opcion_seleccionada == "llantas":
        crear_llantas()
    elif opcion_seleccionada == "estado_llantas":
        ver_llantas_disponibles()
    elif opcion_seleccionada == "servicios_integrados":
        servicios_integrados()
    elif opcion_seleccionada == "reportes":
        reportes()
    elif opcion_seleccionada == "subir_csv":
        subir_datos_csv()
    elif opcion_seleccionada == "editar_datos":
        eliminar_corregir_datos()
    elif opcion_seleccionada == "usuarios":
        gestion_usuarios()
    elif opcion_seleccionada == "mi_perfil":
        mi_perfil()

if __name__ == "__main__":
    main()
