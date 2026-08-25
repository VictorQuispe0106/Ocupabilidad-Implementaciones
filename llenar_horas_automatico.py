# -*- coding: utf-8 -*-
"""
Llena automáticamente el registro DIARIO de ocupabilidad:
  1. Actualiza la fecha en el archivo Excel local (por si lo quieres abrir).
  2. Inserta (o actualiza, si ya existe) el registro del día DIRECTO en la
     base de datos SQL Server, replicando exactamente lo que hace el botón
     "Guardar" del macro, pero sin abrir Excel.

⚠️ IMPORTANTE - LEE ANTES DE USAR ⚠️
- Corre SIEMPRE primero sin el flag --commit (modo simulación). Revisa la
  salida con calma. Recién cuando confirmes que los datos son correctos,
  vuelve a correrlo con --commit para que escriba de verdad en la BD.
- Usa credenciales de administrador ("sa") de la base de datos. Un error
  aquí escribe directo en producción. No se puede deshacer un --commit.
- No se probó contra tu servidor real (no tengo acceso de red a tu base
  interna desde este entorno). Pruébalo tú mismo con cuidado, e
  idealmente primero contra una fecha de prueba / ambiente de pruebas si
  tu empresa tiene uno.

Uso:
    python llenar_horas_automatico.py                  -> simula (dry-run), fecha = hoy
    python llenar_horas_automatico.py --commit          -> ejecuta de verdad, fecha = hoy
    python llenar_horas_automatico.py --fecha 2026-08-20 --commit
"""

import sys
import argparse
import datetime
import openpyxl
import pymssql

# ============================================================================
# CONFIGURACIÓN — ajusta esto a tu caso (una sola vez)
# ============================================================================

DB_CONFIG = {
    "server": "10.200.90.94",
    "user": "sa",
    "password": "Cyber#2025#",
    "database": "dashboardocupabilidad",
}

# Tu perfil (igual a lo que hoy escribes a mano en 2_Validacion / 3_Registro)
PERFIL = {
    "nomanalista": "Victor Quispe Trevejo",
    "nomcelda": "No aplica",
    "nomoficina": "Analista Implementación SGC",  # esto es el campo "Puesto"
    "nomturnos": "Oficina",
    "nomareas": "Implementación",
}

# Cuántos minutos asignar a CADA actividad del día (igual para todas, como
# está hoy en el archivo: 18 minutos cada una)
MINUTOS_POR_ACTIVIDAD = 18
FRECUENCIA_POR_ACTIVIDAD = 1

# Horas asignadas del día (campo "Horas asignadas")
HORAS_ASIGNADAS = 8
HORAS_ASIGNADAS_DECIMAL = 8.0

# Ruta del Excel local que también se actualiza (opcional, solo referencia)
EXCEL_PATH = "Formulario_de_Ocupabilidad_v2.xlsm"
CELDAS_FECHA_EXCEL = {
    "2_Validacion": "E16",
    "3_Registro": "E14",
}

# ============================================================================


def conectar_bd():
    return pymssql.connect(
        server=DB_CONFIG["server"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
    )


def obtener_id(cursor, tabla, col_id, col_nombre, col_estado, valor):
    """Busca el id de un valor en una tabla de referencia (analista, celda, oficina, turnos, areas)."""
    sql = f"SELECT {col_id} FROM {tabla} WHERE {col_nombre} = %s AND {col_estado} = '1'"
    cursor.execute(sql, (valor,))
    fila = cursor.fetchone()
    if not fila:
        raise ValueError(f"No se encontró '{valor}' en la tabla {tabla} (columna {col_nombre}).")
    return fila[0]


def obtener_actividades_oficina(cursor, idoficina):
    """Actividades asignadas a la oficina/puesto (tabla actividadxoficina, misma lógica que 'auxiliar2')."""
    cursor.execute(
        "SELECT idactividad, nomactividad FROM actividadxoficina WHERE idoficina = %s",
        (idoficina,),
    )
    return cursor.fetchall()


def obtener_operaciones_existentes(cursor, idanalista, idcelda, idoficina, idturnos, idareas, fecha):
    """Registros 'operacion' ya guardados para ese día (misma lógica que QueryValidar)."""
    cursor.execute(
        """
        SELECT idoperacion, idactividad
        FROM operacion
        WHERE idanalista = %s AND idcelda = %s AND idoficina = %s
          AND idturnos = %s AND idareas = %s AND fechatrabajo = %s
        ORDER BY idoperacion
        """,
        (idanalista, idcelda, idoficina, idturnos, idareas, fecha),
    )
    return cursor.fetchall()


def actualizar_excel_local(ruta_excel, fecha):
    try:
        wb = openpyxl.load_workbook(ruta_excel, keep_vba=True)
    except FileNotFoundError:
        print(f"  (aviso: no se encontró '{ruta_excel}', se omite la actualización de Excel)")
        return
    for hoja, celda in CELDAS_FECHA_EXCEL.items():
        if hoja in wb.sheetnames:
            wb[hoja][celda] = fecha
    wb.save(ruta_excel)
    print(f"  Excel local actualizado: {ruta_excel}")


def preparar_plan(cursor, fecha):
    """Calcula qué se va a insertar/actualizar, sin tocar la base todavía."""
    idanalista = obtener_id(cursor, "analista", "idanalista", "nomanalista", "estanalista", PERFIL["nomanalista"])
    idcelda = obtener_id(cursor, "celda", "idcelda", "nomcelda", "estcelda", PERFIL["nomcelda"])
    idoficina = obtener_id(cursor, "oficina", "idoficina", "nomoficina", "estoficina", PERFIL["nomoficina"])
    idturnos = obtener_id(cursor, "turnos", "idturnos", "nomturnos", "estturnos", PERFIL["nomturnos"])
    idareas = obtener_id(cursor, "areas", "idareas", "nomareas", "estareas", PERFIL["nomareas"])

    actividades = obtener_actividades_oficina(cursor, idoficina)
    if not actividades:
        raise ValueError(f"No hay actividades configuradas para la oficina/puesto '{PERFIL['nomoficina']}'.")

    existentes = obtener_operaciones_existentes(cursor, idanalista, idcelda, idoficina, idturnos, idareas, fecha)

    return {
        "idanalista": idanalista,
        "idcelda": idcelda,
        "idoficina": idoficina,
        "idturnos": idturnos,
        "idareas": idareas,
        "actividades": actividades,
        "existentes": existentes,
    }


def ejecutar_plan(cursor, plan, fecha, fecha_registro, commit_real):
    modo = "ACTUALIZAR" if plan["existentes"] else "INSERTAR"
    print(f"\n  Modo: {modo}  |  Fecha trabajo: {fecha}  |  Fecha registro: {fecha_registro}  "
          f"|  Actividades: {len(plan['actividades'])}")

    if plan["existentes"]:
        if len(plan["existentes"]) != len(plan["actividades"]):
            raise ValueError(
                f"El número de registros existentes ({len(plan['existentes'])}) no coincide con el "
                f"número de actividades de la oficina ({len(plan['actividades'])}). "
                "Deteniendo por seguridad: revisa manualmente en Excel antes de forzar esto."
            )
        for (idoperacion, _idactividad_actual), (idactividad_nuevo, nomact) in zip(
            plan["existentes"], plan["actividades"]
        ):
            print(f"    UPDATE operacion idoperacion={idoperacion} -> {nomact} "
                  f"({FRECUENCIA_POR_ACTIVIDAD}x, {MINUTOS_POR_ACTIVIDAD} min)")
            if commit_real:
                cursor.execute(
                    "UPDATE operacion SET idactividad=%s, frecuencia=%s, cantminutos=%s, fecharegistro=%s "
                    "WHERE idoperacion=%s",
                    (idactividad_nuevo, FRECUENCIA_POR_ACTIVIDAD, MINUTOS_POR_ACTIVIDAD, fecha_registro, idoperacion),
                )
        print(f"    UPDATE horasasignadas -> {HORAS_ASIGNADAS} h ({HORAS_ASIGNADAS_DECIMAL})")
        if commit_real:
            cursor.execute(
                "UPDATE horasasignadas SET canthoras=%s, canthorasdecimal=%s, fecharegistro=%s "
                "WHERE idanalista=%s AND idcelda=%s AND idoficina=%s AND fechatrabajo=%s",
                (HORAS_ASIGNADAS, HORAS_ASIGNADAS_DECIMAL, fecha_registro,
                 plan["idanalista"], plan["idcelda"], plan["idoficina"], fecha),
            )
    else:
        for idactividad, nomact in plan["actividades"]:
            print(f"    INSERT operacion -> {nomact} ({FRECUENCIA_POR_ACTIVIDAD}x, {MINUTOS_POR_ACTIVIDAD} min)")
            if commit_real:
                cursor.execute(
                    "INSERT INTO operacion "
                    "(idcelda, idoficina, idanalista, idactividad, frecuencia, cantminutos, "
                    " fechatrabajo, fecharegistro, idturnos, idareas) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (plan["idcelda"], plan["idoficina"], plan["idanalista"], idactividad,
                     FRECUENCIA_POR_ACTIVIDAD, MINUTOS_POR_ACTIVIDAD, fecha, fecha_registro,
                     plan["idturnos"], plan["idareas"]),
                )
        print(f"    INSERT horasasignadas -> {HORAS_ASIGNADAS} h ({HORAS_ASIGNADAS_DECIMAL})")
        if commit_real:
            cursor.execute(
                "INSERT INTO horasasignadas "
                "(idanalista, idcelda, idoficina, canthoras, fechatrabajo, fecharegistro, "
                " canthorasdecimal, idturnos, idareas) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (plan["idanalista"], plan["idcelda"], plan["idoficina"], HORAS_ASIGNADAS,
                 fecha, fecha_registro, HORAS_ASIGNADAS_DECIMAL, plan["idturnos"], plan["idareas"]),
            )


def main():
    parser = argparse.ArgumentParser(description="Registro diario automático de ocupabilidad")
    parser.add_argument("--fecha", help="Fecha a registrar (YYYY-MM-DD). Por defecto: hoy.")
    parser.add_argument("--commit", action="store_true",
                         help="Escribe de verdad en la base de datos. Sin esto, solo simula (dry-run).")
    parser.add_argument("--excel", default=EXCEL_PATH, help="Ruta del archivo Excel local a actualizar.")
    parser.add_argument("--sin-excel", action="store_true", help="No tocar el archivo Excel local.")
    args = parser.parse_args()

    if args.fecha:
        fecha = datetime.datetime.strptime(args.fecha, "%Y-%m-%d").date()
        # Si se especifica --fecha explícitamente, se usa esa misma fecha
        # también como fecha de registro (en vez de la fecha del sistema).
        fecha_registro = fecha
    else:
        fecha = datetime.date.today()
        fecha_registro = fecha

    print(f"{'MODO SIMULACIÓN (dry-run)' if not args.commit else 'MODO REAL — SE VA A ESCRIBIR EN LA BASE DE DATOS'}")
    print(f"Fecha trabajo: {fecha}  |  Fecha registro: {fecha_registro}")

    if not args.sin_excel:
        actualizar_excel_local(args.excel, fecha)

    try:
        conn = conectar_bd()
    except Exception as e:
        print(f"\n[ERROR] No se pudo conectar a la base de datos: {e}")
        sys.exit(1)

    try:
        cursor = conn.cursor()
        plan = preparar_plan(cursor, fecha)
        ejecutar_plan(cursor, plan, fecha, fecha_registro, commit_real=args.commit)

        if args.commit:
            conn.commit()
            print("\n[OK] Datos guardados en la base de datos.")
        else:
            print("\n[INFO] Esto fue una simulacion, no se escribio nada. "
                  "Si se ve correcto, vuelve a correr con --commit.")
    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Error, no se guardo nada (rollback aplicado): {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
