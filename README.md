# Simulación de Transacciones en PostgreSQL

## Introducción teórica

## Transacciones anidadas y Savepoints  
Las transacciones permiten ejecutar varias operaciones como una sola unidad lógica, garantizando que los cambios en la base de datos sean consistentes.

Los savepoints permiten definir puntos intermedios dentro de una transacción, lo cual es importante porque en sistemas reales no siempre todo falla o todo funciona.  
Gracias a ellos, es posible realizar un rollback parcial sin cancelar toda la operación, evitando perder trabajo ya validado.



## Deadlocks  
Un deadlock ocurre cuando dos transacciones se bloquean mutuamente al intentar acceder a recursos en orden diferente, generando una espera circular.

Este problema es común en sistemas concurrentes donde múltiples usuarios acceden y modifican datos al mismo tiempo.  
Su importancia radica en que puede detener completamente un sistema si no es detectado y manejado correctamente.


## Timeouts  
Un timeout limita el tiempo máximo de ejecución de una transacción. Si se excede, la operación se cancela automáticamente.

Esto es importante porque evita que consultas mal optimizadas o bloqueos prolongados afecten el rendimiento general del sistema y de otros usuarios.


# Escenario del sistema

Se simula un sistema de reservas turísticas compuesto por:

- Vuelo (descuento de asiento disponible)
- Hotel (descuento de habitación disponible)
- Transporte (descuento de vehículo disponible)

### Regla del sistema:
Si el hotel no tiene disponibilidad:

- Se realiza rollback al savepoint del vuelo  
- Se ejecuta una transacción de compensación (cancelación del vuelo)

Este comportamiento simula sistemas reales donde no basta con fallar la operación, sino que también se deben revertir cambios ya realizados para mantener consistencia.

# Cómo ejecutar el proyecto
### 1. Clonar el repositorio
```sql
git clone https://github.com/EmiNava1409/Transacciones_anidadas.git
cd Transacciones_anidadas
```

### 2. Instalar dependencias
```sql
pip install psycopg2-binary
```

### 3. Configurar la base de datos en PostgreSQL
Antes de ejecutar el proyecto, asegúrate de tener creada la base de datos:
```sql
Nombre de la base de datos: viajes
Usuario: postgres
Contraseña: root
Host: localhost
Puerto: 5432
```
Verifica que estos datos coincidan con los que están en el código Python.

### 4. Ejecutar el programa
```sql
python main.py
```


### 5. Verificar resultados
Puedes revisar el funcionamiento en:
- Consola (transacciones, commits, rollbacks)
- pgAdmin (cambios en las tablas de la base de datos)


# Explicación del código

### Conexión a la base de datos  
Se utiliza `psycopg2` para la conexión a PostgreSQL con `autocommit = False`.
Esto es importante porque permite controlar manualmente cuándo se confirma o se revierte una transacción, lo cual es clave para implementar savepoints y rollback.


## Flujo de la transacción  
1. BEGIN  
2. Validación de cliente  
3. SAVEPOINT 1 (vuelo)  
4. Validación de hotel  
5. SAVEPOINT 2 (hotel)  
6. Reserva de transporte  
7. COMMIT  

Este flujo representa una transacción real de sistemas de reservas, donde cada paso depende del anterior.


## Manejo de errores  
- Si falla el hotel → rollback al savepoint del vuelo  
- Si ocurre un error general → rollback total de la transacción  
Esto permite mantener la consistencia de los datos, evitando estados intermedios inválidos como vuelos reservados sin hotel asociado.


## Deadlock  
Se simulan dos transacciones concurrentes que acceden a recursos en orden inverso, generando bloqueo entre ellas.
Este caso representa un problema real en bases de datos multiusuario, donde el orden de acceso a los recursos es crítico.


## Timeout  
Se configura en PostgreSQL:

```sql
SET statement_timeout = '5000';
```
Si una operación excede el tiempo límite, la transacción se cancela automáticamente.
Esto protege al sistema de consultas bloqueantes o demasiado costosas que podrían afectar a otros usuarios. 

------

# Preguntas de reflexión
### 1. ¿Por qué es importante usar savepoints en transacciones largas? ¿Qué problema resuelven?

Los savepoints son importantes porque permiten dividir una transacción en partes y realizar rollback parcial sin cancelar toda la operación.
Esto es fundamental en sistemas reales donde una falla en una etapa no debería invalidar todo el proceso completo.

### 2. En el escenario de reserva, ¿qué pasaría si no usáramos savepoints y el hotel no tuviera cupo? ¿Cómo afectaría a la consistencia de los datos?

Si no existieran savepoints, al fallar la reserva del hotel se tendría que hacer rollback completo de toda la transacción, incluyendo el vuelo ya reservado.
Esto afectaría la consistencia porque el sistema perdería control sobre operaciones parciales ya válidas, generando ineficiencia y posibles inconsistencias en el negocio.

### 3. ¿Cómo se produce un deadlock en una base de datos? Explica el ejemplo implementado y cómo se resolvió.

Un deadlock ocurre cuando dos transacciones intentan acceder a recursos bloqueados por la otra en orden inverso.

Esto genera una espera circular sin fin, donde ninguna transacción puede continuar.
En PostgreSQL, el sistema detecta automáticamente el deadlock y finaliza una de las transacciones para liberar los recursos.

### 4. ¿Qué estrategias de mitigación existen para evitar deadlocks en sistemas concurrentes?

Las principales estrategias son:
- Mantener un orden consistente de acceso a tablas
- Reducir el tiempo de las transacciones
- Evitar bloqueos innecesarios
- Usar índices adecuados para mejorar el acceso a datos
- Implementar reintentos automáticos en caso de fallo

### 5. ¿Qué sucede cuando una transacción alcanza el timeout? ¿Cómo afecta al usuario final y qué mecanismos se pueden implementar para manejar esta situación?

- Cuando una transacción alcanza el timeout, el sistema la cancela automáticamente para evitar bloqueos prolongados.
- Esto puede afectar al usuario final porque la operación no se completa, obligándolo a reintentar.

Para manejarlo correctamente se pueden implementar mecanismos como:
- Mensajes de error claros
- Reintentos automáticos
- Optimización de consultas
- Ajuste del tiempo de timeout según la carga del sistema

-----
# Conclusión

Este proyecto permite comprender el manejo de transacciones en PostgreSQL aplicando savepoints, control de concurrencia mediante deadlocks y protección del sistema mediante timeouts.
Estos mecanismos son fundamentales en sistemas reales, ya que garantizan consistencia, estabilidad y rendimiento en entornos con múltiples usuarios.

# Evidencias
### Imagen 1: Reserva exitosa + SAVEPOINT
<img width="893" height="300" alt="image" src="https://github.com/user-attachments/assets/ad145665-ec93-4c7a-8798-bdf06faec6ad" />


### Imagen 2: Deadlock
<img width="973" height="256" alt="image" src="https://github.com/user-attachments/assets/0b9d1238-c021-477c-a1dc-86d691d39ec2" />


### Imagen 3: Timeout
<img width="1007" height="95" alt="image" src="https://github.com/user-attachments/assets/e2423611-7fad-4f44-b8a7-2915b4c7c795" />


### Imagen 4: Resultado completo
<img width="1000" height="700" alt="image" src="https://github.com/user-attachments/assets/e4c265b4-ea73-4127-b42b-588e12b0f2c2" />




