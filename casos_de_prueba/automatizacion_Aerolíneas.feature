Feature: API de Automatización de Aerolíneas
  Como usuario quiero poder gestionar aerolíneas, vuelos y reservas
  Para automatizar los procesos de una aerolínea

  # --- Auth ---

  Scenario: Registro exitoso de usuario
    Given que envío un request POST a "/auth/signup"
    And contiene: email, password, full_name
    When ejecuto la petición
    Then la respuesta debe tener status 200
    And la respuesta debe incluir un campo "id"
    And la respuesta debe incluir un campo "email" con valor "nuevo@example.com"

  Scenario: Registro falla por email ya registrado
    Given que envío un request POST a "/auth/signup"
    And contiene: email, password, full_name
    When ejecuto la petición
    Then la respuesta debe tener status 400
    And la respuesta debe incluir un campo "detail" con valor "Email already registered"

  # --- Airlines ---

  Scenario: Crear una nueva aerolínea exitosamente
    Given que tengo los siguientes datos válidos de una aerolínea:
      | name         | country | logo         | slogan        | head_quaters | website  | established |
      | Sky Airlines | USA     | sky-logo.png | Fly with us   | New York     | sky.com  | 1990-01-01 |
    When envío una solicitud POST a "/airlines"
    Then el código de respuesta debe ser 201
    And la respuesta debe contener el ID de la aerolínea creada
    And la respuesta debe contener el nombre "Sky Airlines"

  Scenario: Intentar crear aerolínea con datos inválidos
    Given que tengo los siguientes datos inválidos de una aerolínea:
      | name | country | established   |
      |      | USA     | fecha-invalida|
    When envío una solicitud POST a "/airlines"
    Then el código de respuesta debe ser 400
    And la respuesta debe contener un mensaje de error

  Scenario: Obtener todas las aerolíneas
    Given que existen aerolíneas en el sistema
    When envío una solicitud GET a "/airlines"
    Then el código de respuesta debe ser 200
    And la respuesta debe ser un array de aerolíneas
    And cada aerolínea debe incluir id, name y country

  Scenario: Obtener una aerolínea específica por ID
    Given que existe una aerolínea con ID "123"
    When envío una solicitud GET a "/airlines/123"
    Then el código de respuesta debe ser 200
    And la respuesta debe contener los detalles de la aerolínea

  Scenario: Intentar obtener aerolínea inexistente
    Given que no existe una aerolínea con ID "999"
    When envío una solicitud GET a "/airlines/999"
    Then el código de respuesta debe ser 404

  Scenario: Actualizar una aerolínea existente
    Given que existe una aerolínea con ID "123"
    And que tengo los siguientes datos actualizados:
      | name        | slogan         |
      | Sky Air 2.0 | Better flights |
    When envío una solicitud PUT a "/airlines/123"
    Then el código de respuesta debe ser 200
    And la respuesta debe contener los datos actualizados

  Scenario: Eliminar una aerolínea
    Given que existe una aerolínea con ID "123"
    When envío una solicitud DELETE a "/airlines/123"
    Then el código de respuesta debe ser 200
    And la aerolínea debe ser eliminada del sistema

  # --- Flights ---

  Scenario: Crear un nuevo vuelo exitosamente
    Given que existe una aerolínea con ID "123"
    And que tengo los siguientes datos válidos de un vuelo:
      | name   | from | to   | departure | arrival | duration | stops | price  |
      | SKY123 | JFK  | LAX  | 08:00     | 11:30   | 3.5      | 0     | 299.99 |
    When envío una solicitud POST a "/flights"
    Then el código de respuesta debe ser 201
    And la respuesta debe contener el ID del vuelo creado

  Scenario: Crear vuelo con aerolínea inexistente
    Given que no existe una aerolínea con ID "999"
    And que tengo datos de vuelo asociados a la aerolínea "999"
    When envío una solicitud POST a "/flights"
    Then el código de respuesta debe ser 400

  Scenario: Obtener todos los vuelos
    Given que existen vuelos en el sistema
    When envío una solicitud GET a "/flights"
    Then el código de respuesta debe ser 200
    And la respuesta debe ser un array de vuelos

  Scenario: Obtener vuelos con filtros
    Given que existen vuelos de JFK a LAX
    When envío una solicitud GET a "/flights?from=JFK&to=LAX"
    Then el código de respuesta debe ser 200
    And todos los vuelos en la respuesta deben tener from="JFK" y to="LAX"

  Scenario: Obtener un vuelo específico
    Given que existe un vuelo con ID "FL456"
    When envío una solicitud GET a "/flights/FL456"
    Then el código de respuesta debe ser 200
    And la respuesta debe contener los detalles completos del vuelo

  # --- Bookings ---

  Scenario: Crear una reserva exitosa
    Given que existe un vuelo con ID "FL456"
    And que tengo los siguientes datos válidos de pasajero:
      | name | email          | seat | class   |
      | John | john@email.com | 15A  | economy |
    When envío una solicitud POST a "/bookings"
    Then el código de respuesta debe ser 201
    And la respuesta debe contener el ID de la reserva
    And la respuesta debe contener el estado "confirmed"

  Scenario: Crear reserva para vuelo inexistente
    Given que no existe un vuelo con ID "FL999"
    And que tengo datos de reserva para el vuelo "FL999"
    When envío una solicitud POST a "/bookings"
    Then el código de respuesta debe ser 400

  Scenario: Obtener todas las reservas
    Given que existen reservas en el sistema
    When envío una solicitud GET a "/bookings"
    Then el código de respuesta debe ser 200
    And la respuesta debe ser un array de reservas

  Scenario: Obtener una reserva específica
    Given que existe una reserva con ID "BK789"
    When envío una solicitud GET a "/bookings/BK789"
    Then el código de respuesta debe ser 200
    And la respuesta debe contener los detalles de la reserva

  Scenario: Cancelar una reserva
    Given que existe una reserva con ID "BK789" con estado "confirmed"
    When envío una solicitud DELETE a "/bookings/BK789"
    Then el código de respuesta debe ser 200
    And la reserva debe cambiar su estado a "cancelled"

  Scenario: Intentar cancelar reserva ya cancelada
    Given que existe una reserva con ID "BK789" con estado "cancelled"
    When envío una solicitud DELETE a "/bookings/BK789"
    Then el código de respuesta debe ser 400

  # --- Search & Validation ---

  Scenario: Buscar vuelos por fechas
    Given que existen vuelos para la fecha "2024-03-15"
    When envío una solicitud GET a "/flights?date=2024-03-15"
    Then el código de respuesta debe ser 200
    And todos los vuelos deben ser para la fecha especificada

  Scenario: Buscar vuelos por rango de precios
    Given que existen vuelos entre $200 y $500
    When envío una solicitud GET a "/flights?minPrice=200&maxPrice=500"
    Then el código de respuesta debe ser 200
    And todos los vuelos deben tener un precio entre 200 y 500

  Scenario: Validar formato de fechas en creación de aerolínea
    Given que intento crear una aerolínea con fecha establecida inválida:
      | established |
      | 2024-13-45  |
    When envío una solicitud POST a "/airlines"
    Then el código de respuesta debe ser 400
    And el mensaje debe indicar error en el formato de fecha

  Scenario: Validar campos requeridos en creación de vuelo
    Given que intento crear un vuelo sin campos requeridos:
      | name | from | to |
      |      | JFK  |    |
    When envío una solicitud POST a "/flights"
    Then el código de respuesta debe ser 400
    And el mensaje debe indicar los campos faltantes
