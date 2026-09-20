# Manual básico de usuario

## Sistema Integrado de Llantas (SILL)

**Versión:** 1.0  
**Fecha:** septiembre de 2026  
**Dirigido a:** administradores, supervisores, operarios y administradores de cliente

---

## 1. Objetivo

Este manual explica cómo utilizar las funciones principales de SILL: administrar clientes, vehículos y llantas; registrar servicios, montajes, desmontajes, alineaciones y rotaciones; consultar el estado de la flota; generar reportes y exportar información.

Las opciones visibles dependen del nivel de acceso y de los clientes asignados a cada usuario.

## 2. Acceso al sistema

1. Abra en el navegador la dirección de SILL suministrada por el administrador.
2. Escriba su **Usuario**.
3. Escriba su **Contraseña**.
4. Seleccione **Iniciar Sesión**.

Si aparece el mensaje **Usuario o contraseña incorrectos**, verifique los datos e intente nuevamente. Si el problema continúa, contacte al administrador del sistema.

### Cerrar sesión

Seleccione **Cerrar Sesión** en la barra lateral. Cierre siempre la sesión cuando utilice un equipo compartido.

## 3. Niveles de acceso

| Nivel | Rol | Opciones principales visibles |
|---|---|---|
| 1 | Administrador | Clientes, vehículos, llantas, estado de llantas, servicios, reportes, carga CSV, edición de datos y usuarios |
| 2 | Supervisor | Vehículos, llantas, estado de llantas, servicios, reportes y edición de datos |
| 3 | Operario | Llantas, estado de llantas, servicios y reportes |
| 4 | Admin Cliente | Vehículos, llantas, estado de llantas, servicios y reportes de los clientes asignados |

Los usuarios de nivel 2, 3 y 4 únicamente pueden consultar los clientes que les hayan sido asignados. Si aparece un mensaje de permisos insuficientes, solicite al administrador que revise el nivel y los clientes asignados.

## 4. Navegación general

Después de iniciar sesión encontrará en la barra lateral:

- El nombre del usuario conectado.
- El selector **Menú Principal**.
- La sección **Información de Permisos**.
- El botón **Cerrar Sesión**.

Seleccione una opción del menú para cambiar de módulo. Los formularios muestran un mensaje de confirmación cuando la operación se completa correctamente.

## 5. Gestión de clientes

Esta opción está destinada al administrador.

### Crear un cliente

1. Ingrese a **Gestión de Clientes**.
2. Abra la pestaña **Crear Cliente**.
3. Digite el **NIT** de 10 dígitos, sin puntos ni guiones.
4. Digite el **Nombre del Cliente**.
5. Indique el **Número de Frentes**.
6. Escriba el nombre de cada frente solicitado.
7. Seleccione **Guardar Cliente**.

El sistema no permite guardar un NIT repetido, un nombre vacío o frentes sin nombre.

### Consultar clientes

1. Abra la pestaña **Ver Clientes**.
2. Localice el cliente por nombre o NIT.
3. Despliegue el registro para consultar sus datos y frentes.

## 6. Gestión de vehículos

### Registrar un vehículo

1. Ingrese a **Gestión de Vehículos**.
2. Abra **Registrar Vehículo**.
3. Seleccione el **Cliente**.
4. Complete **Marca**, **Línea**, **Tipología** y **Placa del Vehículo**.
5. Seleccione el **Frente** y el **Estado**.
6. Digite el **Kilometraje Inicial**.
7. Seleccione el método de **Cálculo de Kilómetros**.
8. Deje vacío **ID Vehículo** para que el sistema lo genere automáticamente, salvo que deba conservar un identificador existente.
9. Seleccione **Registrar Vehículo**.

La placa no puede estar registrada previamente.

### Consultar vehículos

Abra la pestaña **Ver Vehículos** para revisar los vehículos asociados a los clientes disponibles para su usuario.

## 7. Gestión de llantas

### Registrar una llanta

1. Ingrese a **Gestión de Llantas**.
2. Abra **Registrar Llanta**.
3. Seleccione el **Cliente** y el **Frente**.
4. Complete **Marca de Llanta**, **Diseño** y **Dimensión**.
5. Deje vacío **ID Llanta** para que el sistema lo genere automáticamente, salvo que deba conservar un identificador existente.
6. Seleccione **Registrar Llanta**.

### Consultar llantas

Abra la pestaña **Ver Llantas** para consultar el inventario disponible para los clientes asignados.

### Consultar el estado de las llantas

Ingrese a **Estado de Llantas** y utilice las siguientes pestañas:

- **Ver Todas:** filtre por cliente, frente o disponibilidad.
- **Aprobar Reencauches:** seleccione las llantas autorizadas e ingrese marca, referencia y precio del reencauche.
- **Análisis de Costos:** consulte y recalcule el costo por kilómetro de una llanta.
- **Asignación de Precios:** registre o actualice los precios por vida de la llanta.

Las opciones de aprobación de reencauches y asignación de precios requieren permisos de administrador.

## 8. Servicios

Ingrese a **Servicios**. El módulo contiene las pestañas **Registro de Servicio**, **Montaje**, **Desmontaje**, **Alineación** y **Rotación Completa**.

### Registrar un servicio

1. Abra **Registro de Servicio**.
2. Ingrese la **Orden de Trabajo** y la **Planilla**, cuando correspondan.
3. Seleccione el **ID Llanta**.
4. Seleccione la **Fecha del Servicio**.
5. Confirme el **Kilometraje** y la **Posición de la llanta**.
6. Registre las profundidades interna, central y externa.
7. Marque los trabajos realizados: balanceo, reparación, despinche, regrabación, torqueo o inspección.
8. Si corresponde, registre los insumos utilizados.
9. Seleccione o escriba el **Operario**.
10. Seleccione **Registrar Servicio**.

Solo se pueden registrar servicios para llantas montadas. La posición es obligatoria.

### Montar una llanta

1. Abra **Montaje**.
2. Ingrese la orden de trabajo y la planilla, cuando correspondan.
3. Seleccione el vehículo.
4. Seleccione una llanta disponible.
5. Digite la posición de montaje.
6. Registre el kilometraje actual del vehículo.
7. Seleccione o escriba el operario.
8. Seleccione **Montar Llanta**.

No utilice una posición que ya esté ocupada. El kilometraje debe ser mayor que cero.

### Desmontar una llanta

1. Abra **Desmontaje**.
2. Ingrese la orden de trabajo y la planilla, cuando correspondan.
3. Seleccione la llanta montada.
4. Seleccione la nueva disponibilidad: **recambio**, **reencauche** o **FVU**.
5. Registre el kilometraje actual del vehículo.
6. Cuando seleccione **FVU**, escriba la razón de fin de vida útil.
7. Seleccione o escriba el operario.
8. Seleccione **Desmontar Llanta**.

### Registrar una alineación

1. Abra **Alineación** y luego **Nueva Alineación**.
2. Ingrese la orden de trabajo y la planilla, cuando correspondan.
3. Seleccione el vehículo.
4. Registre la fecha, el kilometraje y las observaciones.
5. Seleccione o escriba el operario.
6. Seleccione **Registrar Alineación**.

Use **Historial de Alineaciones** para consultar registros anteriores y filtrarlos por vehículo.

### Ejecutar una rotación completa

1. Abra **Rotación Completa**.
2. Ingrese la orden de trabajo y la planilla, cuando correspondan.
3. Seleccione un vehículo activo con al menos dos llantas montadas.
4. Registre el kilometraje actual.
5. En **Asignar nuevas posiciones**, indique la nueva posición de cada llanta.
6. Verifique que no existan posiciones repetidas y que al menos una posición haya cambiado.
7. Seleccione o escriba el operario.
8. Seleccione **Ejecutar Rotación**.

## 9. Reportes y exportación

Ingrese a **Reportes y Análisis** y seleccione la pestaña requerida:

- **Desgaste de Llantas:** muestra la evolución de las profundidades registradas.
- **Servicios por Llanta:** muestra el resumen y detalle de servicios de una llanta.
- **Servicios por Vehículo:** consulta el historial asociado a una placa.
- **Estado de Flota:** presenta métricas generales de vehículos y llantas.
- **Exportar Datos:** permite descargar información en formato CSV.

### Exportar información

1. Abra **Exportar Datos**.
2. Seleccione el conjunto requerido: servicios, llantas, vehículos, clientes o movimientos.
3. Seleccione el botón del archivo CSV que aparece en pantalla.
4. Guarde el archivo en una ubicación autorizada.

Los archivos exportados pueden contener información operativa o personal. No los comparta con personas no autorizadas.

## 10. Corrección y eliminación de datos

Los usuarios autorizados pueden ingresar a **Editar/Eliminar Datos** y seleccionar una de estas pestañas:

- **Vehículos**
- **Llantas**
- **Servicios**
- **Clientes**
- **Movimientos**

Seleccione el registro, modifique los campos necesarios y pulse **Guardar Cambios**. Para eliminarlo, pulse **Eliminar** y confirme la operación cuando el sistema lo solicite.

La eliminación puede afectar historiales y relaciones entre registros. Antes de eliminar información, confirme que seleccionó el registro correcto. Prefiera corregir el registro cuando sea posible.

Los movimientos se generan automáticamente al montar, desmontar, rotar o aprobar el reencauche de una llanta; no se crean desde un formulario independiente.

## 11. Carga de archivos CSV

Esta función está destinada exclusivamente al administrador.

1. Ingrese a **Subir Datos CSV**.
2. Seleccione el **Tipo de Datos**: clientes, vehículos, llantas, servicios o movimientos.
3. Seleccione el archivo CSV.
4. Revise la vista previa.
5. Seleccione **Confirmar y Agregar Datos**.

Utilice **Cancelar** si la estructura o la información no son correctas. Antes de confirmar una carga, verifique encabezados, identificadores, NIT, fechas y valores numéricos.

## 12. Gestión de usuarios

Esta función está destinada exclusivamente al administrador.

### Crear un usuario

1. Ingrese a **Gestión de Usuarios**.
2. Abra **Crear Usuario**.
3. Complete el nombre de usuario, nombre completo y contraseña.
4. Seleccione el nivel de acceso.
5. Para supervisor, operario o admin cliente, asigne al menos un cliente.
6. Seleccione **Crear Usuario**.

### Consultar o modificar usuarios

- Use **Ver Usuarios** para consultar niveles y clientes asignados.
- Use **Editar/Eliminar** para actualizar los datos o retirar un usuario.
- No es posible editar desde esta sección el mismo usuario que tiene la sesión abierta.

Asigne únicamente los permisos y clientes necesarios para las funciones de cada persona.

## 13. Mi perfil

Ingrese a **Mi Perfil** para consultar y actualizar sus datos personales disponibles. Complete los cambios y seleccione **Guardar Cambios**.

## 14. Recomendaciones de uso

- Verifique placa, llanta, posición y kilometraje antes de guardar una operación.
- No cierre ni actualice la pestaña mientras el sistema está guardando información.
- Evite que varias personas modifiquen simultáneamente el mismo registro.
- No comparta su usuario ni contraseña.
- Cierre sesión al terminar.
- Exporte únicamente la información necesaria y protéjala según las políticas de la empresa.

## 15. Solución básica de problemas

### No puedo iniciar sesión

Revise usuario y contraseña. Si el error continúa, solicite al administrador que confirme que el usuario existe y está activo.

### No aparece un cliente o un vehículo

El usuario puede no tener asignado el cliente correspondiente. Solicite al administrador revisar la asignación.

### Aparece “No tienes permisos suficientes”

La acción requiere un nivel de acceso superior. Solicite la operación a un supervisor o administrador.

### No aparece una llanta para montaje

Verifique que la llanta pertenezca al cliente seleccionado y tenga una disponibilidad compatible con montaje.

### No puedo registrar un servicio

Verifique que la llanta esté montada, que la posición esté informada y que el kilometraje sea válido.

### No puedo ejecutar una rotación

Confirme que el vehículo esté activo, tenga al menos dos llantas montadas, no existan posiciones repetidas y haya al menos un cambio de posición.

### El sistema muestra un error de conexión o no carga información

Compruebe la conexión a internet y actualice la página una vez. Si el problema continúa, tome una captura del mensaje, anote la operación que estaba realizando y repórtelo al administrador.

---

**Fin del manual básico de usuario de SILL.**