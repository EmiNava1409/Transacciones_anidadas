import psycopg2
import threading
import time

# Conexión Base

def nueva_conexion():
    return psycopg2.connect(
        database="viajes_turismo",
        user="emilia",
        password="root",
        host="localhost",
        port="5432"
    )

# Reserva con SavePoint
def crear_reserva(id_vuelo, id_hotel, id_transporte):
    conn = nueva_conexion()
    cur = conn.cursor()

    try:
        print("\n INICIANDO RESERVA COMPLETA")

        cur.execute("BEGIN;")
        cur.execute("SET statement_timeout = '5000';")

        # Vuelo
        print("Reservando vuelo...")
        cur.execute("SELECT asientos_disponibles FROM vuelos WHERE id_vuelo = %s FOR UPDATE;", (id_vuelo,))
        vuelo = cur.fetchone()

        if not vuelo or vuelo[0] <= 0:
            raise Exception("No hay vuelos disponibles")

        cur.execute("""
            UPDATE vuelos
            SET asientos_disponibles = asientos_disponibles - 1
            WHERE id_vuelo = %s
        """, (id_vuelo,))

        cur.execute("SAVEPOINT sp_vuelo;")
        print("💾 SAVEPOINT sp_vuelo creado")

        # Hotel
        print("Reservando hotel...")
        cur.execute("SELECT habitaciones_disponibles FROM hoteles WHERE id_hotel = %s FOR UPDATE;", (id_hotel,))
        hotel = cur.fetchone()

        if not hotel or hotel[0] <= 0:
            print("⚠ Hotel sin disponibilidad → rollback a vuelo")
            cur.execute("ROLLBACK TO SAVEPOINT sp_vuelo;")

            cur.execute("""
                UPDATE vuelos
                SET asientos_disponibles = asientos_disponibles + 1
                WHERE id_vuelo = %s
            """, (id_vuelo,))

            raise Exception("Reserva cancelada en hotel")

        cur.execute("""
            UPDATE hoteles
            SET habitaciones_disponibles = habitaciones_disponibles - 1
            WHERE id_hotel = %s
        """, (id_hotel,))

        cur.execute("SAVEPOINT sp_hotel;")
        print("💾 SAVEPOINT sp_hotel creado")

        # Transporte
        print("Reservando transporte...")
        cur.execute("SELECT vehiculos_disponibles FROM transportes WHERE id_transporte = %s FOR UPDATE;", (id_transporte,))
        t = cur.fetchone()

        if not t or t[0] <= 0:
            print("Transporte no disponible → rollback a hotel")
            cur.execute("ROLLBACK TO SAVEPOINT sp_hotel;")
            raise Exception("Reserva cancelada en transporte")

        cur.execute("""
            UPDATE transportes
            SET vehiculos_disponibles = vehiculos_disponibles - 1
            WHERE id_transporte = %s
        """, (id_transporte,))

        conn.commit()
        print("RESERVA COMPLETADA CON ÉXITO")

    except Exception as e:
        conn.rollback()
        print("ERROR:", e)

    finally:
        cur.close()
        conn.close()

# Ejemplo con DeadLock
def deadlock_1():
    conn = nueva_conexion()
    cur = conn.cursor()
    conn.autocommit = False

    try:
        print("\n T1 bloquea vuelos")
        cur.execute("SELECT * FROM vuelos WHERE id_vuelo = 1 FOR UPDATE;")
        time.sleep(5)

        print(" T1 intenta hoteles")
        cur.execute("SELECT * FROM hoteles WHERE id_hotel = 1 FOR UPDATE;")

        conn.commit()

    except Exception as e:
        print("💥 DEADLOCK T1:", e)
        conn.rollback()

    finally:
        conn.close()


def deadlock_2():
    conn = nueva_conexion()
    cur = conn.cursor()
    conn.autocommit = False

    try:
        print("\n T2 bloquea hoteles")
        cur.execute("SELECT * FROM hoteles WHERE id_hotel = 1 FOR UPDATE;")
        time.sleep(5)

        print(" T2 intenta vuelos")
        cur.execute("SELECT * FROM vuelos WHERE id_vuelo = 1 FOR UPDATE;")

        conn.commit()

    except Exception as e:
        print("💥 DEADLOCK T2:", e)
        conn.rollback()

    finally:
        conn.close()


def simular_deadlock():
    t1 = threading.Thread(target=deadlock_1)
    t2 = threading.Thread(target=deadlock_2)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

# TimeOut
def transaccion_lenta():
    conn = nueva_conexion()
    cur = conn.cursor()
    conn.autocommit = False

    try:
        print("\n T1 operación lenta")
        cur.execute("SELECT pg_sleep(8);")
        conn.commit()

    except Exception as e:
        print(" ERROR T1:", e)
        conn.rollback()

    finally:
        conn.close()


def transaccion_intenta():
    time.sleep(2)

    conn = nueva_conexion()
    cur = conn.cursor()
    conn.autocommit = False

    try:
        print(" T2 intenta acceder")
        cur.execute("SET statement_timeout = '3000';")
        cur.execute("SELECT pg_sleep(6);")
        conn.commit()

    except Exception as e:
        print(" TIMEOUT:", e)
        conn.rollback()

    finally:
        conn.close()


def simular_timeout():
    t1 = threading.Thread(target=transaccion_lenta)
    t2 = threading.Thread(target=transaccion_intenta)

    t1.start()
    t2.start()

    t1.join()
    t2.join()


if __name__ == "__main__":
    print("\n==============================")
    print("   SISTEMA DE RESERVAS SQL")
    print("==============================")

    crear_reserva(1, 1, 1)
    simular_deadlock()
    simular_timeout()