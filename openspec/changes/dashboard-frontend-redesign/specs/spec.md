# Spec: Dashboard Frontend Redesign

## 1. upcoming-matches-widget

### Requirements
- El widget DEBE mostrar los próximos 5 partidos obtenidos de `GET /api/matches?status=upcoming&limit=5`
- Cada partido DEBE mostrar: bandera local, nombre local, "vs", bandera visitante, nombre visitante, fecha/hora
- Las banderas DEBEN usar `flag_url` del backend (48px de ancho)
- Si no hay partidos próximos, DEBE mostrar un estado vacío con mensaje "No hay partidos próximos"
- DEBE mostrar un estado de carga mientras se obtienen los datos
- DEBE manejar errores de API mostrando un mensaje de error amigable
- Al hacer click en un partido, DEBE abrir el Match Distribution Modal

### Scenarios

**Scenario: Dashboard loads with upcoming matches**
- Given hay 5 partidos próximos en el backend
- When el dashboard se carga
- Then el widget muestra 5 partidos con banderas, nombres y fechas

**Scenario: No upcoming matches**
- Given no hay partidos próximos
- When el dashboard se carga
- Then el widget muestra "No hay partidos próximos"

**Scenario: API error**
- Given la API de partidos falla
- When el dashboard se carga
- Then el widget muestra un mensaje de error sin romper el resto del dashboard

### Edge Cases
- API retorna menos de 5 partidos → mostrar los que haya
- `flag_url` es null → mostrar un placeholder o solo el código del país
- Fecha en formato ISO → formatear a formato local español

---

## 2. my-standing-widget

### Requirements
- El widget DEBE mostrar el ranking del usuario en cada grupo usando `GET /api/scores/my-standing`
- Cada grupo DEBE mostrar: nombre del grupo, posición (rank), puntos totales, cantidad de miembros
- DEBE mostrar un estado de carga
- Si el usuario no pertenece a ningún grupo, DEBE mostrar un estado vacío
- DEBE manejar errores de API
- DEBE actualizar cuando el usuario se une a un grupo nuevo

### Scenarios

**Scenario: User in multiple groups**
- Given el usuario pertenece a 2 grupos
- When el dashboard se carga
- Then el widget muestra ambos grupos con rank, puntos y miembros

**Scenario: User in no groups**
- Given el usuario no pertenece a ningún grupo
- When el dashboard se carga
- Then el widget muestra un estado vacío o se oculta

**Scenario: User joins a new group**
- Given el usuario se une a un grupo nuevo
- When el dashboard se recarga o el grupo se crea
- Then el widget muestra el nuevo grupo

### Edge Cases
- Rank 1 → destacar con color especial (oro)
- Rank último → mostrar normalmente
- 0 puntos → mostrar "0 pts"
- Grupo con 1 miembro → rank 1

---

## 3. activity-feed-widget

### Requirements
- El widget DEBE mostrar las últimas 10 actividades del usuario usando `GET /api/activity?limit=10`
- DEBE soportar tipos de evento: `group_joined`, `prediction_submitted`
- Cada evento DEBE mostrar: icono según tipo, descripción, timestamp relativo
- `group_joined`: "Te uniste a {group_name}"
- `prediction_submitted`: "Predijiste {home_score}-{away_score} para {match_name}"
- DEBE mostrar un estado de carga
- Si no hay actividades, DEBE mostrar un estado vacío
- DEBE manejar errores de API

### Scenarios

**Scenario: User has activity**
- Given el usuario tiene 3 actividades
- When el dashboard se carga
- Then el widget muestra las 3 actividades con iconos y timestamps

**Scenario: No activity**
- Given el usuario no tiene actividades
- When el dashboard se carga
- Then el widget muestra "No hay actividad reciente"

**Scenario: New activity after prediction**
- Given el usuario envía una predicción
- When se recarga el dashboard
- Then el widget muestra la nueva actividad

### Edge Cases
- Timestamp en formato ISO → formatear a "hace X minutos/horas/días"
- Payload sin `group_name` → mostrar "Grupo desconocido"
- Payload sin scores → mostrar mensaje genérico

---

## 4. match-distribution-modal

### Requirements
- El modal DEBE mostrar la distribución de predicciones para un partido
- DEBE obtener datos de `GET /api/matches/<id>/distribution`
- Si `available: false`, DEBE mostrar mensaje "Las predicciones se mostrarán después del cierre"
- Si `available: true`, DEBE mostrar: total de predicciones, porcentaje de victoria local, empate, victoria visitante
- DEBE mostrar un gráfico visual de barras o donut para los porcentajes
- DEBE tener un botón para cerrar
- DEBE mostrar información del partido: equipos, fecha

### Scenarios

**Scenario: Post-deadline distribution**
- Given un partido pasó la fecha límite y tiene 10 predicciones
- When el usuario abre el modal
- Then muestra las barras con porcentajes: 50% local, 20% empate, 30% visitante

**Scenario: Pre-deadline**
- Given un partido aún no cierra
- When el usuario abre el modal
- Then muestra "Las predicciones se mostrarán después del cierre"

**Scenario: No predictions**
- Given un partido pasó la fecha límite sin predicciones
- When el usuario abre el modal
- Then muestra 0% para todos y "Sin predicciones aún"

### Edge Cases
- Match no existe → mostrar error
- 100% para un resultado → mostrar barra completa
- 1 sola predicción → mostrar 100% para ese resultado

---

## 5. dashboard-layout

### Requirements
- El dashboard DEBE tener un layout de grid responsive
- Desktop: 2 o 3 columnas según el contenido
- Mobile: 1 columna
- DEBE mantener la sección de grupos existente
- DEBE mostrar los widgets en un orden lógico: Upcoming Matches → My Standing → Activity Feed
- DEBE mantener los botones de Create Group y Join Group
- DEBE usar el mismo sistema de diseño M3 (colores, tipografía, espaciado)
- DEBE tener un estado de carga global mientras los widgets cargan

### Layout propuesto

```
Desktop (≥1024px):
┌─────────────────────────────────────────┐
│  Dashboard Header + Create/Join Buttons │
├────────────────────┬────────────────────┤
│  Upcoming Matches  │  My Standing       │
│  (5 partidos)      │  (ranking groups)  │
├────────────────────┴────────────────────┤
│  Activity Feed (10 eventos)           │
├────────────────────┬────────────────────┤
│  My Groups (grid)  │                    │
└────────────────────┴────────────────────┘

Mobile (<768px):
┌─────────────────────────────────────────┐
│  Dashboard Header + Create/Join Buttons │
├─────────────────────────────────────────┤
│  Upcoming Matches                       │
├─────────────────────────────────────────┤
│  My Standing                            │
├─────────────────────────────────────────┤
│  Activity Feed                          │
├─────────────────────────────────────────┤
│  My Groups                              │
└─────────────────────────────────────────┘
```

### Scenarios

**Scenario: Desktop view**
- Given pantalla de 1200px
- When el dashboard se carga
- Then muestra el layout de 2 columnas para widgets

**Scenario: Mobile view**
- Given pantalla de 375px
- When el dashboard se carga
- Then muestra el layout de 1 columna

**Scenario: Loading state**
- Given el dashboard se está cargando
- When el usuario entra
- Then muestra skeletons o spinners en los widgets

### Edge Cases
- Uno de los widgets falla → los otros deben seguir funcionando
- Usuario no autenticado → redirigir a login (ya implementado en router)
