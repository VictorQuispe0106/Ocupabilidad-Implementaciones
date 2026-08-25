# AGENTS.md - Proyecto Ocupabilidad

## Descripción del Proyecto
Sistema web para el registro diario de horas de ocupabilidad del área de Implementación. Reemplaza el formulario Excel con una interfaz web profesional con gráficas y estadísticas.

## Objetivo
Registrar automáticamente las horas diarias de cada analista en la base de datos SQL Server, y visualizar reportes con gráficas comparativas por mes.

## Stack Tecnológico
- **Backend**: Python 3.14 + Flask
- **Base de Datos**: SQL Server (pymssql)
- **Frontend**: HTML + Bootstrap 5 + Chart.js
- **Scripts CLI**: Python (respaldo)

## Base de Datos
- **Servidor**: `10.200.90.94`
- **Base**: `dashboardocupabilidad`
- **Usuario**: `sa`
- **Tablas principales**:
  - `horasasignadas` - Horas totales por día por analista
  - `operacion` - Actividades individuales (18 min c/u)
  - `analista` - Lista de analistas
  - `areas` - Áreas (filtro: Implementación)
  - `oficina` - Puestos/oficinas
  - `actividadxoficina` - Actividades por oficina

## Estructura del Proyecto
```
OCUPABILIDAD AUTOMATIZACION/
├── app.py                    # Servidor Flask (rutas principales)
├── config.py                 # Configuración (BD, perfil, área filtro)
├── requirements.txt          # Dependencias
├── iniciar_app.bat           # Iniciar servidor + abrir navegador
├── static/
│   ├── css/style.css        # Estilos corporativos
│   └── js/app.js            # Lógica frontend
├── templates/
│   ├── base.html            # Plantilla base
│   ├── index.html           # Dashboard
│   ├── registrar.html       # Formulario registro
│   ├── registros.html       # Ver tablas operacion + horasasignadas
│   ├── verificar.html       # Estado conexión BD
│   └── reportes.html        # Gráficas y estadísticas
├── llenar_horas_automatico.py  # Script CLI original
├── ver_tablas_sql.py           # Script CLI original
└── Formulario de Ocupabilidad v2.xlsm  # Excel original
```

## Comandos Importantes
```bash
# Iniciar app web (recomendado)
iniciar_app.bat

# O manualmente
python app.py

# Abrir en navegador
http://localhost:5000

# Scripts CLI (respaldo)
python llenar_horas_automatico.py --fecha 2026-08-26 --commit
python ver_tablas_sql.py
```

## Configuración Principal (config.py)
```python
# Perfil del analista
PERFIL = {
    "nomanalista": "Victor Quispe Trevejo",
    "nomoficina": "Analista Implementación SGC",
    "nomareas": "Implementación",
}

# Filtro de área para reportes
AREA_FILTRO = "Implementación"

# Horas y actividades
MINUTOS_POR_ACTIVIDAD = 18
HORAS_ASIGNADAS = 8
```

## Funcionalidades
1. **Dashboard** (`/`) - Resumen del día, estadísticas rápidas
2. **Registrar** (`/registrar`) - Formulario para registrar horas (reemplaza Excel)
3. **Registros** (`/registros`) - Ver tablas operacion y horasasignadas
4. **Verificar BD** (`/verificar`) - Estado de conexión y tablas
5. **Reportes** (`/reportes`) - Gráficas por mes de todos los analistas del área

## Restricciones Importantes
- **Solo muestra área de Implementación** en reportes (configurable en `config.py`)
- **fecharegistro = fechatrabajo** (la fecha que el usuario especifica)
- **Modo seguro**: Por defecto simula, no escribe en BD sin confirmar
- **Credenciales en config.py**: No compartir este archivo

## Errores Conocidos y Soluciones
1. **Python no encontrado**: Usar ruta completa o reiniciar terminal después de agregar al PATH
2. **Emojis en terminal**: Ya corregido en scripts CLI (usan [INFO], [ERROR] en vez de emojis)
3. **Calendario desalineado**: Ya corregido (overflow-x: auto)

## Historial de Cambios Importantes
- Se creó app web con Flask
- Se agregarón gráficas Chart.js (barras, donut, líneas, calendario heatmap)
- Se filtró por área de Implementación
- Se corrigieron emojis en scripts CLI
- Se creó iniciar_app.bat con apertura automática de navegador
- Se corrigió alineación del calendario
