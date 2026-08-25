"""
Script para conectarse a la base de datos SQL Server usada por el
Formulario_de_Ocupabilidad_v2.xlsm y listar/consultar sus tablas.

Requiere ejecutarse desde una máquina con acceso de red al servidor
10.200.90.94 (típicamente la red interna de la empresa).

Instalación previa (una sola vez):
    pip install pyodbc
    (además necesitas el driver ODBC de SQL Server instalado en el SO,
     ej. "ODBC Driver 17 for SQL Server")
"""

import pyodbc

# --- Datos de conexión (extraídos del macro VBA "Connect") ---
SERVER   = "10.200.90.94"
DATABASE = "dashboardocupabilidad"
USER     = "sa"
PASSWORD = "Cyber#2025#"

# Cambia el nombre del driver según lo que tengas instalado.
# Si no tienes el driver moderno "ODBC Driver 17/18 for SQL Server",
# usa el genérico que trae Windows por defecto:
DRIVER = "{SQL Server}"
# DRIVER = "{ODBC Driver 17 for SQL Server}"
# DRIVER = "{ODBC Driver 18 for SQL Server}"

CONN_STR = (
    f"DRIVER={DRIVER};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"UID={USER};"
    f"PWD={PASSWORD};"
)


def listar_tablas(cursor):
    """Lista todas las tablas del esquema."""
    cursor.execute("""
        SELECT TABLE_SCHEMA, TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
    """)
    filas = cursor.fetchall()
    print(f"\nSe encontraron {len(filas)} tablas:\n")
    for esquema, tabla in filas:
        print(f"  - {esquema}.{tabla}")
    return [f"{esquema}.{tabla}" for esquema, tabla in filas]


def ver_tabla(cursor, nombre_tabla, top=20):
    """Muestra las primeras N filas de una tabla."""
    print(f"\n--- {nombre_tabla} (primeras {top} filas) ---")
    cursor.execute(f"SELECT TOP {top} * FROM {nombre_tabla}")
    columnas = [col[0] for col in cursor.description]
    print(" | ".join(columnas))
    print("-" * 80)
    for fila in cursor.fetchall():
        print(" | ".join(str(v) for v in fila))


def ver_operacion(cursor, top=50):
    """Muestra el detalle de actividades/tiempos capturado por el formulario,
    con los nombres ya resueltos (join a las tablas catálogo)."""
    print(f"\n--- dbo.operacion (legible, primeras {top} filas) ---")
    sql = f"""
        SELECT TOP {top}
            o.idoperacion,
            a.nomanalista,
            c.nomcelda,
            f.nomoficina,
            d.nomactividad,
            o.frecuencia,
            o.cantminutos,
            o.fechatrabajo,
            o.fecharegistro,
            e.nomturnos,
            g.nomareas
        FROM dbo.operacion o
        INNER JOIN dbo.analista a ON o.idanalista = a.idanalista
        INNER JOIN dbo.celda c    ON o.idcelda    = c.idcelda
        INNER JOIN dbo.oficina f  ON o.idoficina  = f.idoficina
        INNER JOIN dbo.actividad d ON o.idactividad = d.idactividad
        INNER JOIN dbo.turnos e   ON o.idturnos   = e.idturnos
        INNER JOIN dbo.areas g    ON o.idareas    = g.idareas
        ORDER BY o.fechatrabajo DESC, o.idoperacion DESC
    """
    cursor.execute(sql)
    columnas = [col[0] for col in cursor.description]
    print(" | ".join(columnas))
    print("-" * 120)
    for fila in cursor.fetchall():
        print(" | ".join(str(v) for v in fila))


def ver_horasasignadas(cursor, top=50):
    """Muestra las horas totales asignadas por día, con nombres resueltos."""
    print(f"\n--- dbo.horasasignadas (legible, primeras {top} filas) ---")
    sql = f"""
        SELECT TOP {top}
            h.idhoras,
            a.nomanalista,
            c.nomcelda,
            f.nomoficina,
            h.canthoras,
            h.canthorasdecimal,
            h.fechatrabajo,
            h.fecharegistro,
            e.nomturnos,
            g.nomareas
        FROM dbo.horasasignadas h
        INNER JOIN dbo.analista a ON h.idanalista = a.idanalista
        INNER JOIN dbo.celda c    ON h.idcelda    = c.idcelda
        INNER JOIN dbo.oficina f  ON h.idoficina  = f.idoficina
        INNER JOIN dbo.turnos e   ON h.idturnos   = e.idturnos
        INNER JOIN dbo.areas g    ON h.idareas    = g.idareas
        ORDER BY h.fechatrabajo DESC, h.idhoras DESC
    """
    cursor.execute(sql)
    columnas = [col[0] for col in cursor.description]
    print(" | ".join(columnas))
    print("-" * 120)
    for fila in cursor.fetchall():
        print(" | ".join(str(v) for v in fila))


def verificar_xp_cmdshell(cursor):
    """Verifica si el procedimiento extendido xp_cmdshell está habilitado
    en el servidor. Si está en 1, significa que con estas credenciales
    se podrían ejecutar comandos del sistema operativo del servidor
    directamente desde SQL — es un riesgo de seguridad serio."""
    print("\n--- Verificando xp_cmdshell ---")
    cursor.execute("""
        SELECT name, CAST(value AS INT), CAST(value_in_use AS INT)
        FROM sys.configurations
        WHERE name = 'xp_cmdshell'
    """)
    fila = cursor.fetchone()
    if fila is None:
        print("No se pudo leer sys.configurations (¿faltan permisos?).")
        return
    nombre, value, value_in_use = fila
    estado = "HABILITADO ⚠️" if value_in_use == 1 else "deshabilitado"
    print(f"{nombre}: value={value}, value_in_use={value_in_use} -> {estado}")


def main():
    try:
        conn = pyodbc.connect(CONN_STR, timeout=5)
    except pyodbc.Error as e:
        print("No se pudo conectar a la base de datos.")
        print(e)
        return

    cursor = conn.cursor()

    tablas = listar_tablas(cursor)

    verificar_xp_cmdshell(cursor)

    # Tablas conocidas según el macro VBA (analista, celda, actividad,
    # oficina, turnos, areas, actividadxoficina, operacion, horasasignadas).
    # Descomenta / ajusta según lo que quieras inspeccionar:
    #
    # for t in tablas:
    #     ver_tabla(cursor, t)

    # Detalle de actividades/tiempos capturado por el formulario (con nombres)
    ver_operacion(cursor, top=50)

    # Horas totales asignadas por día (con nombres)
    ver_horasasignadas(cursor, top=50)

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
