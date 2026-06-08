# Business Rules — Prode World Cup 2026

## 1. Predicciones

- Cada usuario hace **1 predicción por partido** (marcador exacto: goles local y visitante).
- La predicción **no está ligada a un grupo** — vale para todos los grupos en los que el usuario participa.
- **Deadline:** la predicción cierra **1 hora antes del kickoff**. Pasado ese momento, no se puede crear ni modificar.
- Si un usuario **no predijo** un partido, suma **0 puntos** para ese partido.

## 2. Puntuación

| Resultado | Puntos |
|---|---|
| Acertó victoria / empate / derrota (resultado) | 1 punto |
| Acertó el marcador exacto | 3 puntos |
| No predijo o se equivocó | 0 puntos |

- El marcador exacto otorga 3 puntos (no 1+3, solo 3).
- Los puntos se calculan **por partido**, al momento en que el admin carga el resultado.
- El historial de puntos ya calculados **no se modifica** al recalcular un partido.

## 3. Ligas (anteriormente "Grupos de usuario")

- Cualquier usuario autenticado puede **crear una liga**.
- El creador de la liga es automáticamente su **admin**.
- Las ligas son **privadas**: el acceso es solo por código de invitación generado al crear la liga.
- Al crear una liga se configuran los **premios para los 3 primeros puestos** (descripción libre, ej: "Pizza para el ganador").
- Las ligas sirven exclusivamente para **rankear y comparar** puntajes entre sus miembros.
- En el código interno y la DB se sigue usando el término `group`/`PredictionGroup` por compatibilidad.

## 4. Ranking

- Los puntos son **globales por usuario** — una predicción acertada suma 1 o 3 puntos una sola vez, independientemente de en cuántas ligas participe el usuario.
- El ranking de cada liga ordena a sus miembros por sus puntos globales acumulados.
- Un usuario puede estar primero en una liga y tercero en otra, pero sus puntos totales son los mismos en ambas.
- El **total de puntos** que se muestra en el header es la suma real de todos los `PredictionScore` del usuario, sin duplicar por liga.

## 5. Administración

- Existe un **rol de admin global**, asignado manualmente en la base de datos.
- El admin global accede a una página `/admin` donde puede:
  - Cargar el resultado final de un partido (goles local y visitante).
  - Al guardar el resultado, se dispara el cálculo de puntos para ese partido para todos los usuarios que predijeron.
- Por ahora, el único admin es `leandro.iannotti87@gmail.com`.

## 6. Dashboard — Widgets de partidos

- **Próximos Partidos:** partidos con `status=scheduled` Y `deadline > ahora`, ordenados por kickoff ASC, límite 5.
- **Partidos Finalizados:** partidos con `deadline < ahora`, ordenados por kickoff DESC, límite 4. Incluye dos sub-estados:
  - `status=finished`: muestra resultado, predicción del usuario y puntos obtenidos.
  - `status=scheduled` con deadline pasado: muestra "Procesando resultado..." — el admin aún no cargó el resultado.

## 7. Integraciones futuras

- **Webhook de resultados:** se integrará un webhook externo que actualizará los resultados automáticamente. El flujo de cálculo de puntos debe ser el mismo que el del admin manual.

## 8. Bugs / inconsistencias conocidas a corregir

- [ ] `deadline_utc` en la DB está calculado como `kickoff - 24h`. Debe ser `kickoff - 1h`.
- [ ] El modal de predicción tiene un selector de grupo que no corresponde (la predicción es por usuario, no por grupo).
