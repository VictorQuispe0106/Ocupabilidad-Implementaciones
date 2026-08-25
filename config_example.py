# -*- coding: utf-8 -*-
"""
EJEMPLO DE CONFIGURACION - Copiar este archivo como config.py
y reemplazar los valores reales.
"""

# ============================================================================
# CONFIGURACION DE BASE DE DATOS
# ============================================================================
DB_CONFIG = {
    "server": "TU_SERVIDOR",
    "user": "TU_USUARIO",
    "password": "TU_PASSWORD",
    "database": "TU_BASE_DATOS",
}

# ============================================================================
# PERFIL DEL ANALISTA
# ============================================================================
PERFIL = {
    "nomanalista": "Tu Nombre",
    "nomcelda": "No aplica",
    "nomoficina": "Tu Puesto",
    "nomturnos": "Oficina",
    "nomareas": "Tu Area",
}

# Filtro de area para reportes (solo mostrar analistas de esta area)
AREA_FILTRO = "Tu Area"

# ============================================================================
# CONFIGURACION DE ACTIVIDADES
# ============================================================================
MINUTOS_POR_ACTIVIDAD = 18
FRECUENCIA_POR_ACTIVIDAD = 1
HORAS_ASIGNADAS = 8
HORAS_ASIGNADAS_DECIMAL = 8.0

# ============================================================================
# RUTAS DE ARCHIVOS
# ============================================================================
EXCEL_PATH = "Formulario de Ocupabilidad v2.xlsm"
CELDAS_FECHA_EXCEL = {
    "2_Validacion": "E16",
    "3_Registro": "E14",
}

# ============================================================================
# CONFIGURACION DE LA APLICACION WEB
# ============================================================================
APP_CONFIG = {
    "host": "127.0.0.1",
    "port": 5000,
    "debug": True,
}
