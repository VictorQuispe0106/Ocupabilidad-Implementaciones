# Sistema de Ocupabilidad - Interfaz Web

Aplicación web para el registro diario de horas de ocupabilidad. Reemplaza el formulario Excel con una interfaz visual profesional.

## Características

- ✅ **Registro de Horas**: Formulario fácil para registrar horas diarias
- ✅ **Ver Registros**: Tabla con historial de registros
- ✅ **Verificar BD**: Estado de conexión y tablas disponibles
- ✅ **Reportes**: Estadísticas y gráficas de actividades
- ✅ **Modo Seguro**: Simulación antes de guardar (dry-run)

## Requisitos Previos

- Python 3.8 o superior
- Acceso a la base de datos SQL Server (red interna)

## Instalación

1. **Clonar o descargar el proyecto**

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar** (opcional):
   - Editar `config.py` para cambiar perfil, horas, o configuración de BD

## Uso

### Opción 1: Interfaz Web (Recomendado)

1. **Iniciar el servidor**:
   ```bash
   python app.py
   ```

2. **Abrir en navegador**:
   ```
   http://localhost:5000
   ```

3. **Usar la interfaz**:
   - **Dashboard**: Resumen y accesos rápidos
   - **Registrar**: Formulario para registrar horas
   - **Registros**: Ver historial
   - **Verificar BD**: Estado de conexión
   - **Reportes**: Estadísticas y gráficas

### Opción 2: Scripts CLI (Respaldo)

Los scripts originales se mantienen para uso por terminal:

```bash
# Simulación (dry-run)
python llenar_horas_automatico.py

# Guardar en BD
python llenar_horas_automatico.py --commit

# Fecha específica
python llenar_horas_automatico.py --fecha 2026-08-25 --commit

# Ver tablas
python ver_tablas_sql.py
```

## Estructura del Proyecto

```
OCUPABILIDAD AUTOMATIZACION/
├── app.py                          # Servidor Flask principal
├── config.py                       # Configuración centralizada
├── requirements.txt                # Dependencias
├── static/
│   ├── css/style.css              # Estilos corporativos
│   └── js/app.js                  # Lógica del frontend
├── templates/
│   ├── base.html                  # Plantilla base
│   ├── index.html                 # Dashboard
│   ├── registrar.html             # Formulario de registro
│   ├── registros.html             # Ver registros
│   ├── verificar.html             # Verificar BD
│   └── reportes.html              # Reportes
├── llenar_horas_automatico.py     # Script CLI (respaldo)
├── ver_tablas_sql.py              # Script CLI (respaldo)
└── Formulario de Ocupabilidad v2.xlsm  # Excel original
```

## Configuración

Editar `config.py` para cambiar:

- **DB_CONFIG**: Conexión a la base de datos
- **PERFIL**: Datos del analista
- **MINUTOS_POR_ACTIVIDAD**: Tiempo por actividad (default: 18)
- **HORAS_ASIGNADAS**: Horas diarias (default: 8)
- **APP_CONFIG**: Puerto y modo de la app web

## Seguridad

- ⚠️ **Credenciales**: Están en `config.py` (no compartir este archivo)
- ⚠️ **Modo Seguro**: Por defecto, la app opera en simulación
- ⚠️ **Base de datos**: Producción - cualquier cambio es irreversible

## Solución de Problemas

### No conecta a la BD
- Verificar que estés en la red interna de la empresa
- Verificar que el servidor SQL esté activo: `10.200.90.94`
- Verificar credenciales en `config.py`

### Error al instalar pymssql
```bash
# En Windows, puede necesitar Visual C++ Build Tools
pip install pymssql --no-cache-dir
```

### Puerto 5000 en uso
Cambiar en `config.py`:
```python
APP_CONFIG = {
    "port": 5001,  # u otro puerto
    ...
}
```

## Desarrollo

Para desarrolladores que quieran modificar la aplicación:

- **Backend**: `app.py` (Flask)
- **Frontend**: `templates/` (Jinja2) + `static/` (CSS/JS)
- **Estilos**: `static/css/style.css`
- **Lógica JS**: `static/js/app.js`

## Licencia

Proyecto interno - Uso exclusivo del equipo.
