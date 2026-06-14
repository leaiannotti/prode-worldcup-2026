# Release Testing Checklist — post v1.1.0

Checklist para testear localmente todos los cambios incorporados después del tag `v1.1.0`, antes de sacar la próxima versión.

## Cómo usarla

1. Levantar backend y frontend en local.
2. Ir sección por sección.
3. Marcar cada item cuando esté verificado manualmente o por test automatizado.
4. Si algo falla, anotar el bug debajo de la sección correspondiente antes de seguir.

> Base comparada: `v1.1.0` → `main` actual, incluyendo PR #110.

---

## 1. PWA / installability — PRs #98, #99

- [x] Chrome Desktop: aparece botón "Instalar app" en la barra.
- [ ] Chrome Android: aparece prompt "Agregar a pantalla de inicio".
- [ ] Safari iOS: "Compartir → Agregar a pantalla de inicio" funciona.
- [ ] Iconos 192, 512 y maskable se ven nítidos, sin pixelado.
- [ ] Splash screen muestra logo Prode Argentina 2026 con color correcto.
- [ ] Apple touch icon se ve bien en iOS.
- [ ] Favicon 16x16, 32x32 e `.ico` cargan bien.
- [ ] Modo offline básico: abrir la app sin internet muestra la última pantalla cacheada.
- [ ] Auth cacheada no se rompe entre sesiones.
- [ ] Lighthouse PWA score >= 90.

## 2. App version, changelog y What's New — PR #97

- [x] `GET /api/version` devuelve la versión actual desde `VERSION`. (verificado: test_version.py)
- [x] `GET /api/changelog` devuelve JSON con entradas formateadas. (verificado: test_version.py)
- [x] El perfil muestra la versión actual de la app.
- [ ] El modal "What's New" aparece la primera vez después de un bump de versión.
- [ ] El modal no vuelve a aparecer después de cerrarlo.
- [ ] El estado de cierre del modal se persiste en `localStorage`.
- [ ] El modal renderiza correctamente las entradas del changelog.
- [x] `scripts/release.sh` bloquea el bump si no hay entrada en `CHANGELOG.md`. (verificado: lectura de script)
- [x] `scripts/_validate_changelog.py` falla con changelog inválido. (verificado: ejecución manual, exit 2)
- [x] `scripts/_validate_changelog.py` pasa con changelog válido. (verificado: ejecución manual, exit 0)

## 3. Editable prizes + audit — PRs #105, #106, #107, #108

### 3.1 Backend: edición de premios — PR #105

- [x] `PATCH /api/groups/:id/prizes` permite editar premios a cualquier miembro del grupo. (verificado: test_groups.py)
- [x] `PATCH /api/groups/:id/prizes` permite editar premios a un admin global aunque no sea miembro del grupo. (verificado: test_groups.py)
- [x] `PATCH /api/groups/:id/prizes` devuelve `403` para un usuario que no es miembro ni admin global. (verificado: test_groups.py)
- [x] El endpoint edita premios por rank. (verificado: test_groups.py)
- [x] La respuesta devuelve array `changed` con los cambios reales. (verificado: test_groups.py)
- [x] Los premios quedan persistidos correctamente en DB. (verificado: test_groups.py)
- [x] Se genera un evento `prize_changed` por cada rank modificado. (verificado: test_groups.py)

### 3.2 Activity filters — PR #106

- [x] `GET /api/activity?group_id=X` filtra solo eventos de ese grupo. (verificado: test_activity.py)
- [x] `GET /api/activity?event_type=prize_changed` filtra por tipo de evento. (verificado: test_activity.py)
- [x] `GET /api/activity?limit=N` respeta el límite. (verificado: test_activity.py)
- [x] La combinación `group_id + event_type + limit` funciona. (verificado: test_activity.py)
- [x] `limit` negativo no crashea. (verificado: test_activity.py, devuelve 400)
- [x] `group_id` inexistente devuelve una respuesta controlada. (verificado: test_activity.py, devuelve 403)
- [x] `event_type` desconocido devuelve vacío o error claro. (verificado: test_activity.py, devuelve [] con 200)
- [x] Un usuario que no es miembro del grupo no ve eventos de ese grupo. (verificado: test_activity.py)

### 3.3 Frontend stores — PR #107

- [x] `activity.fetchActivity(limit)` sigue funcionando con argumento positional. (verificado: activity.test.ts)
- [x] `activity.fetchActivity({ groupId, eventType, limit })` funciona. (verificado: activity.test.ts)
- [x] `groups.patchPrizes()` hace el `PATCH` correcto. (verificado: groups.test.ts)
- [x] `groups.patchPrizes()` actualiza el estado local esperado. (verificado: groups.test.ts)
- [x] No queda ninguna llamada al viejo `setPrizes`. (verificado: grep en frontend)

### 3.4 Frontend UI — PR #108

- [x] En `LeagueDetailModal`, un admin ve botón para editar premios. (verificado: LeagueDetailModal.test.ts)
- [ ] En `LeagueDetailModal`, un no-admin no ve botón de edición.
- [x] El modo edición muestra contador de caracteres por premio. (verificado: LeagueDetailModal.test.ts)
- [x] Guardar premios refresca el modal con los nuevos valores. (verificado: LeagueDetailModal.test.ts)
- [x] El historial colapsable de auditoría se abre y cierra correctamente. (verificado: LeagueDetailModal.test.ts)
- [x] El historial renderiza eventos `prize_changed` correctamente. (verificado: LeagueDetailModal.test.ts)
- [ ] `NavBar` muestra eventos `prize_changed` con indicador de admin.
- [x] Todos los strings nuevos existen en español. (verificado: es.json + LeagueDetailModal.test.ts)
- [ ] Todos los strings nuevos existen en inglés. (verificado: en.json presente, no testeado)

### 3.5 Regression: `actor_name`

- [x] `GET /api/activity` devuelve `actor_name` en el root del evento. (verificado: test_activity.py)
- [x] `actor_name` no depende de estar dentro de `payload`. (verificado: test_activity.py)
- [x] El frontend lee `actor_name` desde el lugar correcto. (verificado: activity.test.ts + LeagueDetailModal.test.ts)
- [x] El nombre del admin aparece correctamente en eventos de auditoría. (verificado: LeagueDetailModal.test.ts)
- [x] Eventos viejos o incompletos no rompen el render. (verificado: activity.test.ts fallback)

## 4. Friend recent results — PRs #101, #102

### 4.1 Backend

- [x] El endpoint de recent history devuelve datos de miembros de la liga. (verificado: test_leaderboard.py)
- [x] Un usuario que no es miembro no puede ver datos de esa liga. (verificado: test_leaderboard.py)
- [x] La respuesta incluye todos los campos necesarios para la UI. (verificado: test_leaderboard.py)
- [x] La respuesta maneja usuarios sin resultados recientes. (verificado: test_leaderboard.py)

### 4.2 Frontend

- [x] Click en avatar dentro de `LeaderboardTable` abre el sheet.
- [x] Click en avatar dentro de standings de `GruposView` abre el sheet.
- [ ] El `BottomSheet` se cierra con swipe-down.
- [x] El `BottomSheet` se cierra con tap fuera.
- [x] El header muestra nombre y avatar del amigo.
- [x] La tabla muestra últimos partidos y puntos.
- [x] Los colores de puntos coinciden con `PointsDrawer`.
- [ ] Hay loading state durante el fetch.
- [ ] Hay error state si falla el fetch.

## 5. i18n quick wins — PR #95

- [x] `HistoryView`: switch ES/EN traduce todo, sin strings hardcodeados.
- [x] `LeaderboardView`: switch ES/EN traduce todo, sin strings hardcodeados.
- [x] `PredictionsView`: switch ES/EN traduce todo, sin strings hardcodeados.
- [x] `GruposView`: switch ES/EN traduce todo, sin strings hardcodeados.
- [x] `GroupDetailView`: switch ES/EN traduce todo, sin strings hardcodeados.
- [x] `MatchCard`: switch ES/EN traduce todo, sin strings hardcodeados.
- [x] `MatchCountdownBadge`: switch ES/EN traduce todo, sin strings hardcodeados.
- [x] `RecentMatchesWidget`: switch ES/EN traduce todo, sin strings hardcodeados.
- [x] Flujo de predicciones mantiene textos localizados.

## 6. Admin / prediction score buttons: double-tap zoom fix — PR #110

PR #110 soluciona zoom por doble tap en mobile agregando `touch-manipulation` a botones `+` y `-` de score.

Archivos tocados:

- `frontend/src/views/AdminView.vue`
- `frontend/src/components/PredictionModal.vue`

### 6.1 Admin result modal

- [x] Mobile Safari iOS: tap rápido repetido en `+` de home score no hace zoom.
- [x] Mobile Safari iOS: tap rápido repetido en `-` de home score no hace zoom.
- [x] Mobile Safari iOS: tap rápido repetido en `+` de away score no hace zoom.
- [x] Mobile Safari iOS: tap rápido repetido en `-` de away score no hace zoom.
- [x] Mobile Chrome Android: tap rápido repetido en botones `+` y `-` no hace zoom.
- [ ] Desktop: click normal en `+` y `-` sigue funcionando.
- [ ] El score se actualiza correctamente con cada tap.
- [ ] Guardar resultado sigue funcionando.
- [ ] Cancelar/cerrar modal sigue funcionando.

### 6.2 Prediction modal

- [x] Mobile Safari iOS: tap rápido repetido en botones `+` y `-` no hace zoom.
- [x] Mobile Chrome Android: tap rápido repetido en botones `+` y `-` no hace zoom.
- [x] Desktop: click normal en `+` y `-` sigue funcionando.
- [x] El score de predicción se actualiza correctamente con cada tap.
- [x] Guardar predicción sigue funcionando.
- [x] Cerrar modal sigue funcionando.

## 7. Fixes varios

- [x] `MyStandingWidget`: con más de 4 ligas, el widget tiene altura máxima.
- [x] `MyStandingWidget`: con más de 4 ligas, aparece scroll interno y no rompe layout.
- [x] Deadline de predicciones respeta la business rule de offset de 1 hora. (verificado: test_predictions.py, test_seed.py, test_matches.py, test_distribution.py)
- [x] `npm run typecheck` pasa sin errores preexistentes. (verificado: `npx vue-tsc --noEmit`)

## 8. Smoke tests generales

- [x] Login con email funciona.
- [x] Login con Google OAuth funciona.
- [x] Crear liga funciona.
- [ ] Unirse a liga con invite code funciona.
- [ ] Invite code sigue siendo case-insensitive.
- [x] El botón/UI de eliminar liga no se muestra en `LeagueDetailModal`. (verificado: LeagueDetailModal.test.ts)
- [ ] Si se decide mantener el endpoint `DELETE /api/groups/:id`, endurecer backend para admin global únicamente.
- [ ] Cargar predicción para partido próximo funciona.
- [ ] Ver leaderboard de una liga funciona.
- [ ] Admin panel sigue funcionando.
- [ ] Community insights carga correctamente.
- [x] `/health` responde `200`. (verificado: test_health.py)
- [x] CORS funciona desde el dominio configurado. (verificado: test_cors.py)

## 9. Pre-release técnico

- [x] Tests frontend pasan completos. (verificado: vitest run, 40 passed)
- [x] Tests backend pasan completos. (verificado: pytest, 170 passed)
- [x] Build de producción del frontend pasa sin warnings críticos. (verificado: vite build, 0 errores)
- [ ] Migraciones corren limpio en una DB fresh.
- [ ] `VERSION` está bumpado a la próxima versión.
- [ ] `CHANGELOG.md` tiene entrada para la próxima versión.
- [x] El release script valida correctamente la entrada del changelog. (verificado: ejecución manual del validator)

## Bugs encontrados durante testing

Anotar acá cualquier bug nuevo encontrado mientras se recorre la checklist.

| Fecha | Sección | Bug | Severidad | Estado |
|-------|---------|-----|-----------|--------|
| 2026-06-14 | 7 Fixes / typecheck | `vue-tsc --noEmit` error TS6133 en `FriendRecentResultsSheet.vue:158`: 'props' declarado pero nunca leído | WARNING | Corregido |
| 2026-06-14 | 8 Smoke / delete league | Se removió la UI de eliminar liga del modal. El endpoint backend todavía permite borrar a cualquier miembro con `membership.role == "admin"` si se llama directo por API. | HIGH | Mitigado en UI / backend pendiente |
