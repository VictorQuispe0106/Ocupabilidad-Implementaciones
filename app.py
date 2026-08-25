# -*- coding: utf-8 -*-
"""
Aplicación Web de Ocupabilidad - Interfaz visual para gestionar registros diarios.
Reemplaza el formulario Excel con una interfaz web profesional.
"""

from flask import Flask, render_template, request, jsonify
import pymssql
import datetime
import os

from config import DB_CONFIG, PERFIL, MINUTOS_POR_ACTIVIDAD, FRECUENCIA_POR_ACTIVIDAD
from config import HORAS_ASIGNADAS, HORAS_ASIGNADAS_DECIMAL, EXCEL_PATH, CELDAS_FECHA_EXCEL, APP_CONFIG, AREA_FILTRO

app = Flask(__name__)


# ============================================================================
# FUNCIONES DE BASE DE DATOS
# ============================================================================

def conectar_bd():
    """Establece conexión con la base de datos SQL Server."""
    try:
        conn = pymssql.connect(
            server=DB_CONFIG["server"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
        )
        return conn
    except Exception as e:
        print(f"Error al conectar a la BD: {e}")
        return None


def obtener_id(cursor, tabla, col_id, col_nombre, col_estado, valor):
    """Busca el id de un valor en una tabla de referencia."""
    sql = f"SELECT {col_id} FROM {tabla} WHERE {col_nombre} = %s AND {col_estado} = '1'"
    cursor.execute(sql, (valor,))
    fila = cursor.fetchone()
    if not fila:
        raise ValueError(f"No se encontró '{valor}' en la tabla {tabla}")
    return fila[0]


def obtener_actividades_oficina(cursor, idoficina):
    """Obtiene las actividades asignadas a la oficina/puesto."""
    cursor.execute(
        "SELECT idactividad, nomactividad FROM actividadxoficina WHERE idoficina = %s",
        (idoficina,),
    )
    return cursor.fetchall()


def obtener_operaciones_existentes(cursor, idanalista, idcelda, idoficina, idturnos, idareas, fecha):
    """Obtiene los registros 'operacion' ya guardados para ese día."""
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


# ============================================================================
# RUTAS PRINCIPALES
# ============================================================================

@app.route("/")
def index():
    """Página principal - Dashboard."""
    return render_template("index.html", perfil=PERFIL)


@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    """Formulario para registrar horas diarias."""
    mensaje = None
    tipo_mensaje = None

    if request.method == "POST":
        try:
            fecha_str = request.form.get("fecha")
            commit = request.form.get("commit") == "true"

            if not fecha_str:
                fecha = datetime.date.today()
            else:
                fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()

            fecha_registro = fecha

            conn = conectar_bd()
            if not conn:
                raise Exception("No se pudo conectar a la base de datos")

            cursor = conn.cursor()

            # Obtener IDs
            idanalista = obtener_id(cursor, "analista", "idanalista", "nomanalista", "estanalista", PERFIL["nomanalista"])
            idcelda = obtener_id(cursor, "celda", "idcelda", "nomcelda", "estcelda", PERFIL["nomcelda"])
            idoficina = obtener_id(cursor, "oficina", "idoficina", "nomoficina", "estoficina", PERFIL["nomoficina"])
            idturnos = obtener_id(cursor, "turnos", "idturnos", "nomturnos", "estturnos", PERFIL["nomturnos"])
            idareas = obtener_id(cursor, "areas", "idareas", "nomareas", "estareas", PERFIL["nomareas"])

            # Obtener actividades
            actividades = obtener_actividades_oficina(cursor, idoficina)
            if not actividades:
                raise ValueError(f"No hay actividades configuradas para '{PERFIL['nomoficina']}'")

            # Verificar si ya existen registros
            existentes = obtener_operaciones_existentes(cursor, idanalista, idcelda, idoficina, idturnos, idareas, fecha)

            if existentes:
                if len(existentes) != len(actividades):
                    raise ValueError(f"Registros existentes ({len(existentes)}) no coinciden con actividades ({len(actividades)})")

                # Actualizar registros existentes
                for (idoperacion, _), (idactividad_nuevo, nomact) in zip(existentes, actividades):
                    cursor.execute(
                        "UPDATE operacion SET idactividad=%s, frecuencia=%s, cantminutos=%s, fecharegistro=%s WHERE idoperacion=%s",
                        (idactividad_nuevo, FRECUENCIA_POR_ACTIVIDAD, MINUTOS_POR_ACTIVIDAD, fecha_registro, idoperacion),
                    )

                # Actualizar horas asignadas
                cursor.execute(
                    "UPDATE horasasignadas SET canthoras=%s, canthorasdecimal=%s, fecharegistro=%s WHERE idanalista=%s AND idcelda=%s AND idoficina=%s AND fechatrabajo=%s",
                    (HORAS_ASIGNADAS, HORAS_ASIGNADAS_DECIMAL, fecha_registro, idanalista, idcelda, idoficina, fecha),
                )
                accion = "actualizado"
            else:
                # Insertar nuevos registros
                for idactividad, nomact in actividades:
                    cursor.execute(
                        "INSERT INTO operacion (idcelda, idoficina, idanalista, idactividad, frecuencia, cantminutos, fechatrabajo, fecharegistro, idturnos, idareas) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (idcelda, idoficina, idanalista, idactividad, FRECUENCIA_POR_ACTIVIDAD, MINUTOS_POR_ACTIVIDAD, fecha, fecha_registro, idturnos, idareas),
                    )

                # Insertar horas asignadas
                cursor.execute(
                    "INSERT INTO horasasignadas (idanalista, idcelda, idoficina, canthoras, fechatrabajo, fecharegistro, canthorasdecimal, idturnos, idareas) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (idanalista, idcelda, idoficina, HORAS_ASIGNADAS, fecha, fecha_registro, HORAS_ASIGNADAS_DECIMAL, idturnos, idareas),
                )
                accion = "registrado"

            if commit:
                conn.commit()
                tipo_mensaje = "success"
                mensaje = f"✅ Datos {accion} correctamente para el {fecha}"
            else:
                tipo_mensaje = "warning"
                mensaje = f"ℹ️ Simulación completada. Para guardar, marca la casilla de confirmación."

            cursor.close()
            conn.close()

        except Exception as e:
            tipo_mensaje = "danger"
            mensaje = f"❌ Error: {str(e)}"

    return render_template("registrar.html", perfil=PERFIL, mensaje=mensaje, tipo_mensaje=tipo_mensaje)


@app.route("/registros")
def registros():
    """Ver registros existentes en la base de datos."""
    datos_operacion = []
    datos_horas = []
    try:
        conn = conectar_bd()
        if conn:
            cursor = conn.cursor()
            
            # Consulta de operacion (actividades)
            cursor.execute(
                """
                SELECT TOP 100
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
                FROM operacion o
                INNER JOIN analista a ON o.idanalista = a.idanalista
                INNER JOIN celda c ON o.idcelda = c.idcelda
                INNER JOIN oficina f ON o.idoficina = f.idoficina
                INNER JOIN actividad d ON o.idactividad = d.idactividad
                INNER JOIN turnos e ON o.idturnos = e.idturnos
                INNER JOIN areas g ON o.idareas = g.idareas
                ORDER BY o.fechatrabajo DESC, o.idoperacion DESC
                """
            )
            datos_operacion = cursor.fetchall()
            
            # Consulta de horasasignadas
            cursor.execute(
                """
                SELECT TOP 100
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
                FROM horasasignadas h
                INNER JOIN analista a ON h.idanalista = a.idanalista
                INNER JOIN celda c ON h.idcelda = c.idcelda
                INNER JOIN oficina f ON h.idoficina = f.idoficina
                INNER JOIN turnos e ON h.idturnos = e.idturnos
                INNER JOIN areas g ON h.idareas = g.idareas
                ORDER BY h.fechatrabajo DESC, h.idhoras DESC
                """
            )
            datos_horas = cursor.fetchall()
            
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Error al obtener registros: {e}")

    return render_template("registros.html", datos_operacion=datos_operacion, datos_horas=datos_horas)


@app.route("/verificar")
def verificar():
    """Verificar conexión a la base de datos."""
    estado = {
        "conexion": False,
        "mensaje": "",
        "tablas": [],
        "xp_cmdshell": {"value": 0, "value_in_use": 0, "estado": "desconocido"},
    }

    try:
        conn = conectar_bd()
        if conn:
            estado["conexion"] = True
            estado["mensaje"] = "Conexión exitosa a la base de datos"
            cursor = conn.cursor()

            # Listar tablas
            cursor.execute(
                "SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME"
            )
            estado["tablas"] = [f"{esquema}.{tabla}" for esquema, tabla in cursor.fetchall()]

            # Verificar xp_cmdshell
            cursor.execute(
                "SELECT name, CAST(value AS INT), CAST(value_in_use AS INT) FROM sys.configurations WHERE name = 'xp_cmdshell'"
            )
            fila = cursor.fetchone()
            if fila:
                estado["xp_cmdshell"] = {
                    "value": fila[1],
                    "value_in_use": fila[2],
                    "estado": "HABILITADO ⚠️" if fila[2] == 1 else "deshabilitado",
                }

            cursor.close()
            conn.close()
        else:
            estado["mensaje"] = "No se pudo conectar a la base de datos"
    except Exception as e:
        estado["mensaje"] = f"Error: {str(e)}"

    return render_template("verificar.html", estado=estado)


@app.route("/reportes")
def reportes():
    """Reportes y estadísticas con selector de mes/año."""
    mes = request.args.get("mes", datetime.date.today().month, type=int)
    anio = request.args.get("anio", datetime.date.today().year, type=int)
    
    datos = []
    datos_horas = []
    try:
        conn = conectar_bd()
        if conn:
            cursor = conn.cursor()
            
            # Datos de operacion (actividades) para el mes seleccionado - solo área Implementación
            cursor.execute(
                """
                SELECT 
                    a.nomanalista,
                    f.nomoficina,
                    d.nomactividad,
                    SUM(o.cantminutos) as total_minutos,
                    COUNT(*) as num_registros,
                    o.fechatrabajo
                FROM operacion o
                INNER JOIN analista a ON o.idanalista = a.idanalista
                INNER JOIN oficina f ON o.idoficina = f.idoficina
                INNER JOIN actividad d ON o.idactividad = d.idactividad
                INNER JOIN areas ar ON o.idareas = ar.idareas
                WHERE MONTH(o.fechatrabajo) = %s AND YEAR(o.fechatrabajo) = %s
                  AND ar.nomareas = %s
                GROUP BY a.nomanalista, f.nomoficina, d.nomactividad, o.fechatrabajo
                ORDER BY a.nomanalista, o.fechatrabajo
                """,
                (mes, anio, AREA_FILTRO),
            )
            datos = cursor.fetchall()
            
            # Datos de horasasignadas para el mes seleccionado - solo área Implementación
            cursor.execute(
                """
                SELECT 
                    a.nomanalista,
                    h.canthoras,
                    h.fechatrabajo
                FROM horasasignadas h
                INNER JOIN analista a ON h.idanalista = a.idanalista
                INNER JOIN areas ar ON h.idareas = ar.idareas
                WHERE MONTH(h.fechatrabajo) = %s AND YEAR(h.fechatrabajo) = %s
                  AND ar.nomareas = %s
                ORDER BY a.nomanalista, h.fechatrabajo
                """,
                (mes, anio, AREA_FILTRO),
            )
            datos_horas = cursor.fetchall()
            
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Error al obtener reportes: {e}")

    return render_template(
        "reportes.html",
        datos=datos,
        datos_horas=datos_horas,
        mes_seleccionado=mes,
        anio_seleccionado=anio,
    )


# ============================================================================
# API ENDPOINTS (para AJAX)
# ============================================================================

@app.route("/api/verificar-conexion", methods=["POST"])
def api_verificar_conexion():
    """API para verificar conexión a la base de datos."""
    try:
        conn = conectar_bd()
        if conn:
            conn.close()
            return jsonify({"success": True, "message": "Conexión exitosa"})
        else:
            return jsonify({"success": False, "message": "No se pudo conectar"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/estadisticas", methods=["GET"])
def api_estadisticas():
    """API para obtener estadísticas del dashboard."""
    try:
        conn = conectar_bd()
        if conn:
            cursor = conn.cursor()

            # Total registros hoy
            cursor.execute(
                "SELECT COUNT(*) FROM operacion WHERE fechatrabajo = %s",
                (datetime.date.today(),),
            )
            total_hoy = cursor.fetchone()[0]

            # Total registros este mes
            primer_dia_mes = datetime.date.today().replace(day=1)
            cursor.execute(
                "SELECT COUNT(*) FROM operacion WHERE fechatrabajo >= %s",
                (primer_dia_mes,),
            )
            total_mes = cursor.fetchone()[0]

            # Total horas este mes
            cursor.execute(
                "SELECT ISNULL(SUM(canthoras), 0) FROM horasasignadas WHERE fechatrabajo >= %s",
                (primer_dia_mes,),
            )
            horas_mes = cursor.fetchone()[0]

            cursor.close()
            conn.close()

            return jsonify({
                "success": True,
                "total_hoy": total_hoy,
                "total_mes": total_mes,
                "horas_mes": float(horas_mes),
            })
        else:
            return jsonify({"success": False, "message": "No se pudo conectar a la BD"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/estadisticas-mes", methods=["GET"])
def api_estadisticas_mes():
    """API para obtener estadísticas de un mes específico por analista (solo área Implementación)."""
    mes = request.args.get("mes", datetime.date.today().month, type=int)
    anio = request.args.get("anio", datetime.date.today().year, type=int)
    
    try:
        conn = conectar_bd()
        if conn:
            cursor = conn.cursor()
            
            # Obtener días del mes
            import calendar
            dias_del_mes = calendar.monthrange(anio, mes)[1]
            
            # Horas por analista en el mes - solo área Implementación
            cursor.execute(
                """
                SELECT 
                    a.nomanalista,
                    COUNT(DISTINCT h.fechatrabajo) as dias_registrados,
                    ISNULL(SUM(h.canthoras), 0) as total_horas
                FROM horasasignadas h
                INNER JOIN analista a ON h.idanalista = a.idanalista
                INNER JOIN areas ar ON h.idareas = ar.idareas
                WHERE MONTH(h.fechatrabajo) = %s AND YEAR(h.fechatrabajo) = %s
                  AND ar.nomareas = %s
                GROUP BY a.nomanalista
                ORDER BY total_horas DESC
                """,
                (mes, anio, AREA_FILTRO),
            )
            analistas = []
            total_horas = 0
            total_dias = 0
            
            for row in cursor.fetchall():
                horas = float(row[2])
                dias = row[1]
                total_horas += horas
                total_dias += dias
                analistas.append({
                    "nombre": row[0],
                    "dias_registrados": dias,
                    "total_horas": horas,
                })
            
            # Calcular porcentajes
            for a in analistas:
                a["porcentaje"] = round((a["total_horas"] / total_horas * 100) if total_horas > 0 else 0, 1)
                a["promedio_dia"] = round(a["total_horas"] / a["dias_registrados"], 1) if a["dias_registrados"] > 0 else 0
                a["cumplimiento"] = round((a["dias_registrados"] / dias_del_mes * 100), 1)
            
            # Evolución diaria por analista - solo área Implementación
            cursor.execute(
                """
                SELECT 
                    a.nomanalista,
                    DAY(h.fechatrabajo) as dia,
                    h.canthoras
                FROM horasasignadas h
                INNER JOIN analista a ON h.idanalista = a.idanalista
                INNER JOIN areas ar ON h.idareas = ar.idareas
                WHERE MONTH(h.fechatrabajo) = %s AND YEAR(h.fechatrabajo) = %s
                  AND ar.nomareas = %s
                ORDER BY a.nomanalista, h.fechatrabajo
                """,
                (mes, anio, AREA_FILTRO),
            )
            evolucion = {}
            for row in cursor.fetchall():
                nombre = row[0]
                if nombre not in evolucion:
                    evolucion[nombre] = {}
                evolucion[nombre][row[1]] = float(row[2])
            
            cursor.close()
            conn.close()
            
            meses_nombre = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                           "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            
            return jsonify({
                "success": True,
                "mes": meses_nombre[mes],
                "anio": anio,
                "dias_del_mes": dias_del_mes,
                "analistas": analistas,
                "total_horas": total_horas,
                "total_dias": total_dias,
                "evolucion": evolucion,
            })
        else:
            return jsonify({"success": False, "message": "No se pudo conectar a la BD"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  APLICACIÓN WEB DE OCUPABILIDAD")
    print("=" * 60)
    print(f"  Servidor: http://{APP_CONFIG['host']}:{APP_CONFIG['port']}")
    print(f"  Modo: {'Desarrollo' if APP_CONFIG['debug'] else 'Producción'}")
    print("=" * 60)
    print("\n  Presiona Ctrl+C para detener el servidor\n")

    app.run(
        host=APP_CONFIG["host"],
        port=APP_CONFIG["port"],
        debug=APP_CONFIG["debug"],
    )
