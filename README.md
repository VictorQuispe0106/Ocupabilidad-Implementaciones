# Ocupabilidad - Sistema de Registro de Horas

Sistema web para el registro y seguimiento diario de horas de ocupabilidad del área de Implementación. Interfaz profesional con gráficas estadísticas y reportes por mes.

---

## Características

- **Registro de Horas** - Formulario web para registrar horas diarias
- **Ver Registros** - Consulta de tablas `horasasignadas` y `operacion`
- **Verificar BD** - Estado de conexión y tablas disponibles
- **Reportes** - Gráficas comparativas por mes y por analista
- **Modo Seguro** - Simulación antes de guardar (dry-run)

## Gráficas Incluidas

| Gráfica | Descripción |
|---------|-------------|
| Horas por Analista | Barras verticales con total de horas |
| Días que Llenó | Barras horizontales (días registrados vs días del mes) |
| Distribución Donut | Porcentaje de horas por analista |
| Evolución Diaria | Líneas comparativas día a día |
| Calendario Heatmap | Vista tipo GitHub (completo/incompleto/sin registro) |

---

## Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| Backend | Python 3.14 + Flask |
| Base de Datos | SQL Server (pymssql) |
| Frontend | HTML + Bootstrap 5 |
| Gráficas | Chart.js |

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/VictorQuispe0106/Ocupabilidad-Implementaciones.git
cd Ocupabilidad-Implementaciones
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar

```bash
# Copiar el archivo de ejemplo
cp config_example.py config.py
```

Editar `config.py` con tus datos:

```python
DB_CONFIG = {
    "server": "TU_SERVIDOR",
    "user": "TU_USUARIO",
    "password": "TU_PASSWORD",
    "database": "TU_BASE_DATOS",
}

PERFIL = {
    "nomanalista": "Tu Nombre",
    "nomoficina": "Tu Puesto",
    "nomareas": "Tu Area",
}

AREA_FILTRO = "Tu Area"
```

### 4. Iniciar la aplicación

```bash
# Windows (doble clic en iniciar_app.bat)
iniciar_app.bat

# O manualmente
python app.py
```

### 5. Abrir en navegador

```
http://localhost:5000
```

---

## Estructura del Proyecto

```
├── app.py                    # Servidor Flask
├── config.py                 # Configuración (no se sube a GitHub)
├── config_example.py         # Ejemplo de configuración
├── requirements.txt          # Dependencias
├── iniciar_app.bat           # Iniciar servidor + navegador
├── static/
│   ├── css/style.css        # Estilos corporativos
│   └── js/app.js            # Lógica frontend
├── templates/
│   ├── base.html            # Plantilla base
│   ├── index.html           # Dashboard
│   ├── registrar.html       # Formulario de registro
│   ├── registros.html       # Ver tablas
│   ├── verificar.html       # Verificar BD
│   └── reportes.html        # Gráficas y estadísticas
├── AGENTS.md                # Documentación para IA
├── README.md                # Este archivo
└── .gitignore               # Archivos excluidos
```

---

## Páginas Disponibles

| Ruta | Descripción |
|------|-------------|
| `/` | Dashboard principal con resumen |
| `/registrar` | Formulario para registrar horas |
| `/registros` | Tabla de operacion y horasasignadas |
| `/verificar` | Estado de conexión a la BD |
| `/reportes` | Gráficas y estadísticas por mes |

---

## Configuración

| Variable | Descripción | Default |
|----------|-------------|---------|
| `AREA_FILTRO` | Filtra analistas por área | `"Implementación"` |
| `MINUTOS_POR_ACTIVIDAD` | Minutos por actividad | `18` |
| `HORAS_ASIGNADAS` | Horas diarias | `8` |
| `APP_CONFIG["port"]` | Puerto del servidor | `5000` |

---

## Seguridad

- `config.py` contiene credenciales y **no se sube a GitHub**
- `.gitignore` protege archivos sensibles
- Modo seguro: por defecto solo simula (dry-run)

---

## Solución de Problemas

| Problema | Solución |
|----------|----------|
| Python no encontrado | Reiniciar terminal después de instalar |
| Puerto 5000 en uso | Cambiar `APP_CONFIG["port"]` en config.py |
| No conecta a BD | Verificar red interna y credenciales |
| Error pymssql | `pip install pymssql --no-cache-dir` |

---

## Licencia

Uso interno - Área de Implementación
