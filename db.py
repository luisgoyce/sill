"""
db.py — Capa de acceso a datos para SILL usando Supabase (REST API).
Reemplaza la conexión a Google Sheets manteniendo la misma interfaz:
  leer_hoja(nombre) → pd.DataFrame
  escribir_hoja(nombre, df) → pd.DataFrame | None
"""
import os
import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ─────────────────────────────────────────────────────────────
# Conexión a Supabase
# ─────────────────────────────────────────────────────────────

def _get_supabase_url() -> str:
    return os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL", "")

def _get_supabase_key() -> str:
    return os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY", "")

@st.cache_resource
def get_supabase_client() -> Client:
    """Singleton del cliente Supabase."""
    url = _get_supabase_url()
    key = _get_supabase_key()
    if not url or not key:
        st.error("⚠️ Faltan las variables SUPABASE_URL y/o SUPABASE_KEY. "
                 "Configúralas en .streamlit/secrets.toml o como variables de entorno.")
        st.stop()
    return create_client(url, key)

# ─────────────────────────────────────────────────────────────
# Mapeo de nombres de hoja → tabla/vista
# ─────────────────────────────────────────────────────────────

TABLE_MAP = {
    "clientes": "clientes",
    "vehiculos": "vehiculos",
    "llantas": "llantas",
    "servicios": "servicios",
    "usuarios": "usuarios",
    "movimientos": "vw_movimientos",   # Vista (lectura) — escritura va a servicios
    "alineaciones": "alineaciones",
}

PRIMARY_KEYS = {
    "clientes": "id_cliente",
    "vehiculos": "id_vehiculo",
    "llantas": "id_llanta",
    "servicios": "id_servicio",
    "usuarios": "id_usuario",
    "alineaciones": "id_alineacion",
}

# Columnas de movimientos → servicios (para escritura)
MOV_TO_SERV_COLUMNS = {
    "id_movimiento": "id_servicio",
    "tipo": "tipo_servicio",
    "usuario": "usuario_registro",
}

# ─────────────────────────────────────────────────────────────
# Lectura
# ─────────────────────────────────────────────────────────────

def leer_hoja(nombre_hoja: str) -> pd.DataFrame:
    """Lee una tabla/vista de Supabase y retorna un DataFrame."""
    try:
        sb = get_supabase_client()
        table_name = TABLE_MAP.get(nombre_hoja, nombre_hoja)
        response = sb.table(table_name).select("*").execute()
        data = response.data
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df = _postprocess(df, nombre_hoja)
        return df
    except Exception as e:
        st.error(f"Error leyendo {nombre_hoja}: {str(e)}")
        return pd.DataFrame()


def leer_hoja_fresco(nombre_hoja: str) -> pd.DataFrame:
    """Lee sin caché (en Supabase siempre es fresco)."""
    return leer_hoja(nombre_hoja)


# ─────────────────────────────────────────────────────────────
# Escritura
# ─────────────────────────────────────────────────────────────

def escribir_hoja(nombre_hoja: str, df: pd.DataFrame) -> pd.DataFrame | None:
    """
    Escribe un DataFrame completo a Supabase (simula el overwrite de Google Sheets).
    Estrategia: UPSERT todas las filas + DELETE las que ya no están.
    Retorna el DataFrame actualizado desde la BD.
    """
    try:
        if df is None or df.empty:
            print(f"[DB] escribir_hoja({nombre_hoja}): DataFrame vacío o None, retornando.")
            return df

        sb = get_supabase_client()

        # Caso especial: escribir en "movimientos" → insertar en servicios
        if nombre_hoja == "movimientos":
            return _escribir_movimientos(sb, df)

        table_name = TABLE_MAP.get(nombre_hoja, nombre_hoja)
        pk = PRIMARY_KEYS.get(nombre_hoja)

        if not pk:
            st.error(f"No se encontró primary key para {nombre_hoja}")
            return None

        # Limpiar DataFrame para serialización
        df_clean = _prepare_for_write(df, nombre_hoja)
        print(f"[DB] escribir_hoja({nombre_hoja}): {len(df_clean)} filas, columnas: {list(df_clean.columns)}")

        # Obtener PKs actuales en la BD
        existing = sb.table(table_name).select(pk).execute()
        existing_pks = {row[pk] for row in existing.data} if existing.data else set()

        # PKs en el nuevo DataFrame
        new_pks = set(df_clean[pk].astype(str).values)
        print(f"[DB] existentes: {len(existing_pks)}, nuevas: {len(new_pks)}, a eliminar: {len(existing_pks - new_pks)}")

        # Eliminar filas que ya no existen
        pks_to_delete = existing_pks - new_pks
        if pks_to_delete:
            for pk_val in pks_to_delete:
                sb.table(table_name).delete().eq(pk, pk_val).execute()

        # Upsert todas las filas del DataFrame
        records = df_clean.to_dict(orient="records")
        # Limpiar NaN/inf que no son JSON-serializables
        records = _clean_records(records)
        if records:
            print(f"[DB] Upserting {len(records)} records. Sample: {records[-1]}")
            # Supabase upsert en lotes de 500
            batch_size = 500
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                resp = sb.table(table_name).upsert(batch).execute()
                print(f"[DB] Upsert batch response: {len(resp.data)} rows returned")

        # Retornar datos frescos
        return leer_hoja(nombre_hoja)

    except Exception as e:
        st.error(f"Error escribiendo en {nombre_hoja}: {str(e)}")
        return None


def _escribir_movimientos(sb: Client, df: pd.DataFrame) -> pd.DataFrame | None:
    """
    Escribe movimientos en la tabla servicios (con mapeo de columnas).
    Solo hace upsert/delete de registros cuyo tipo_servicio es de tipo movimiento.
    """
    try:
        # Renombrar columnas de movimiento → servicio
        df_serv = df.copy()
        df_serv = df_serv.rename(columns=MOV_TO_SERV_COLUMNS)

        pk = "id_servicio"
        if pk not in df_serv.columns:
            return None

        # Asegurar que tipo_servicio está en los valores de movimiento
        tipos_mov = ('montaje', 'desmontaje', 'rotacion', 'aprobacion_reencauche')

        # Obtener los movimientos existentes en servicios
        existing = (sb.table("servicios")
                    .select("id_servicio")
                    .in_("tipo_servicio", list(tipos_mov))
                    .execute())
        existing_pks = {row["id_servicio"] for row in existing.data} if existing.data else set()

        new_pks = set(df_serv[pk].astype(str).values)

        # Eliminar movimientos que ya no existen
        pks_to_delete = existing_pks - new_pks
        if pks_to_delete:
            for pk_val in pks_to_delete:
                sb.table("servicios").delete().eq("id_servicio", pk_val).execute()

        # Preparar registros para upsert
        df_serv = _prepare_for_write(df_serv, "servicios")
        records = _clean_records(df_serv.to_dict(orient="records"))
        if records:
            batch_size = 500
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                sb.table("servicios").upsert(batch).execute()

        return leer_hoja("movimientos")

    except Exception as e:
        st.error(f"Error escribiendo movimientos: {str(e)}")
        return None


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _postprocess(df: pd.DataFrame, nombre_hoja: str) -> pd.DataFrame:
    """Post-procesamiento tras lectura (equivalente a lo que hacía leer_hoja original)."""
    if df.empty:
        return df

    # Normalizar NITs a string (preservando ceros iniciales)
    for col in ['nit', 'nit_cliente']:
        if col in df.columns:
            df[col] = df[col].apply(_normalize_nit)

    # Limpiar clientes_asignados
    if 'clientes_asignados' in df.columns:
        df['clientes_asignados'] = df['clientes_asignados'].apply(_limpiar_clientes_asignados)

    # Normalizar columnas ID a string
    columnas_id = ['id_vehiculo', 'id_llanta', 'id_servicio', 'id_movimiento',
                   'id_alineacion', 'id_usuario', 'placa_vehiculo', 'usuario']
    for col in columnas_id:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: str(x).strip() if pd.notna(x) and str(x).strip() != 'nan' else '')

    # Para movimientos: renombrar columnas de la vista para compatibilidad
    if nombre_hoja == "movimientos":
        rename_back = {v: k for k, v in MOV_TO_SERV_COLUMNS.items()}
        df = df.rename(columns=rename_back)

    return df


def _prepare_for_write(df: pd.DataFrame, nombre_hoja: str) -> pd.DataFrame:
    """Prepara un DataFrame para escritura en Supabase (limpieza de tipos)."""
    import math
    import numpy as np
    df = df.copy()

    # Obtener columnas válidas de la tabla destino
    table_name = TABLE_MAP.get(nombre_hoja, nombre_hoja)
    valid_cols = _get_table_columns(table_name)
    if valid_cols:
        # Solo mantener columnas que existen en la tabla
        df = df[[c for c in df.columns if c in valid_cols]]

    # Reemplazar NaN/NaT/None con None de Python (compatible JSON)
    df = df.replace({np.nan: None, pd.NaT: None})
    df = df.where(df.notna(), None)

    # Preservar NITs como strings exactos (no convertir numéricamente)
    for col in ['nit', 'nit_cliente']:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: str(x).strip() if x is not None else None)

    # Convertir columnas numéricas
    numeric_cols = ['kilometraje', 'kilometraje_inicial', 'kilometraje_actual',
                    'kilometros_totales', 'km_ultimo_montaje', 'precio_vida1',
                    'precio_vida2', 'precio_vida3', 'precio_vida4',
                    'costo_km_vida1', 'costo_km_vida2', 'costo_km_vida3', 'costo_km_vida4',
                    'profundidad_1', 'profundidad_2', 'profundidad_3',
                    'precio_reencauche', 'total_regrabaciones']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Convertir booleanos
    bool_cols = ['balanceo', 'reparacion', 'despinche', 'regrabacion',
                 'torqueo', 'inspeccion', 'rotacion', 'activo']
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].apply(_to_bool)

    # Nivel como int
    if 'nivel' in df.columns:
        df['nivel'] = pd.to_numeric(df['nivel'], errors='coerce').fillna(1).astype(int)

    # Vida como int
    if 'vida' in df.columns:
        df['vida'] = pd.to_numeric(df['vida'], errors='coerce').fillna(1).astype(int)
    if 'vida_actual' in df.columns:
        df['vida_actual'] = pd.to_numeric(df['vida_actual'], errors='coerce').fillna(1).astype(int)

    # frentes: asegurar que sea JSON válido
    if 'frentes' in df.columns:
        df['frentes'] = df['frentes'].apply(_ensure_json_list)

    return df


# Cache de columnas por tabla
_table_columns_cache: dict = {}

# Columnas conocidas como fallback si la tabla está vacía
_KNOWN_COLUMNS = {
    "clientes": {"id_cliente", "nit", "nombre_cliente", "frentes", "fecha_creacion"},
    "vehiculos": {"id_vehiculo", "nit_cliente", "marca", "linea", "tipologia", "placa_vehiculo",
                  "frente", "estado", "kilometraje_inicial", "calculo_kms", "fecha_creacion"},
    "llantas": {"id_llanta", "nit_cliente", "marca_llanta", "referencia", "dimension", "vida_actual",
                "disponibilidad", "kilometros_totales", "km_ultimo_montaje", "total_regrabaciones",
                "placa_actual", "posicion_actual", "estado_reencauche", "precio_vida1", "reencauche1",
                "precio_vida2", "reencauche2", "precio_vida3", "reencauche3", "precio_vida4",
                "costo_km_vida1", "costo_km_vida2", "costo_km_vida3", "costo_km_vida4",
                "fecha_creacion", "fecha_modificacion"},
    "servicios": {"id_servicio", "orden_trabajo", "planilla", "fecha", "id_llanta", "placa_vehiculo",
                  "posicion", "posicion_nueva", "vida", "tipologia", "tipo_servicio", "disponibilidad",
                  "kilometraje", "rotacion", "profundidad_1", "profundidad_2", "profundidad_3",
                  "balanceo", "reparacion", "despinche", "regrabacion", "torqueo", "inspeccion",
                  "insumos", "comentario_fvu", "observaciones", "nueva_disponibilidad",
                  "marca_reencauche", "ref_reencauche", "precio_reencauche", "operario",
                  "usuario_registro", "timestamp"},
    "usuarios": {"id_usuario", "usuario", "password_hash", "nivel", "nombre", "clientes_asignados"},
    "alineaciones": {"id_alineacion", "fecha", "placa_vehiculo", "nit_cliente", "kilometraje",
                     "alineador", "angulo_inicial_izq", "angulo_final_izq",
                     "angulo_inicial_der", "angulo_final_der", "observaciones",
                     "usuario_registro", "timestamp"},
}

def _get_table_columns(table_name: str) -> set | None:
    """Obtiene las columnas de una tabla (cacheado)."""
    if table_name in _table_columns_cache:
        return _table_columns_cache[table_name]
    try:
        sb = get_supabase_client()
        # Leer una fila para obtener las columnas
        resp = sb.table(table_name).select("*").limit(1).execute()
        if resp.data:
            cols = set(resp.data[0].keys())
            _table_columns_cache[table_name] = cols
            return cols
    except:
        pass
    # Fallback a columnas conocidas
    if table_name in _KNOWN_COLUMNS:
        return _KNOWN_COLUMNS[table_name]
    return None


def _normalize_nit(x) -> str:
    """Normaliza NIT a string preservando ceros iniciales. Solo quita .0 de floats."""
    if pd.isna(x) or x is None or x == '':
        return ''
    # Si es float (ej: 1234567890.0), convertir a int para quitar .0
    if isinstance(x, float):
        return str(int(x))
    # Si es int, convertir a string directo
    if isinstance(x, int):
        return str(x)
    # Si es string, preservar tal cual (no hacer int(float()) que pierde ceros)
    s = str(x).strip()
    # Solo quitar .0 si termina en .0 (vino como "1234567890.0")
    if s.endswith('.0') and s[:-2].isdigit():
        return s[:-2]
    return s


def _is_numeric(val) -> bool:
    try:
        float(val)
        return True
    except (ValueError, TypeError):
        return False


def _to_bool(val) -> bool:
    if isinstance(val, bool):
        return val
    if pd.isna(val) or val is None or val == '':
        return False
    s = str(val).strip().lower()
    return s in ('true', '1', 'sí', 'si', 'yes')


def _limpiar_clientes_asignados(valor) -> str:
    if pd.isna(valor) or valor == '' or valor is None:
        return ''
    if isinstance(valor, (int, float)):
        return str(int(valor))
    valor_str = str(valor)
    nits = []
    for nit in valor_str.split(','):
        nit = nit.strip()
        if nit:
            # Preservar el NIT como string, solo quitar .0 si aplica
            nits.append(_normalize_nit(nit))
    return ','.join(nits)


def _clean_records(records: list) -> list:
    """Limpia valores NaN/inf/numpy types de los records para que sean JSON-serializables."""
    import json
    import math
    import numpy as np

    def _sanitize_value(v):
        if v is None:
            return None
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            return None
        if isinstance(v, (np.integer,)):
            return int(v)
        if isinstance(v, (np.floating,)):
            val = float(v)
            return None if (math.isnan(val) or math.isinf(val)) else val
        if isinstance(v, np.bool_):
            return bool(v)
        if isinstance(v, np.ndarray):
            return v.tolist()
        if hasattr(v, 'isoformat'):
            return v.isoformat()
        if isinstance(v, (dict, list)):
            # Recursively sanitize nested structures
            return json.loads(json.dumps(v, default=str))
        return v

    cleaned = []
    for record in records:
        clean = {k: _sanitize_value(v) for k, v in record.items()}
        cleaned.append(clean)
    return cleaned


def _ensure_json_list(val):
    """Asegura que el valor sea una lista JSON válida."""
    import json
    if val is None or (isinstance(val, str) and val.strip() == ''):
        return []
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        try:
            parsed = json.loads(val.replace("'", '"'))
            return parsed if isinstance(parsed, list) else [parsed]
        except:
            return [val]
    return [str(val)]
