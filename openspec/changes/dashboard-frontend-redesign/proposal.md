# Proposal: Dashboard Frontend Redesign

## Intent

Rediseñar el dashboard principal para mostrar información relevante y enriquecida usando las nuevas APIs del backend (implementadas en el change `dashboard-backend-apis`).

## Scope

### In Scope

1. **Upcoming Matches Widget** — Muestra los próximos 5 partidos con banderas, equipos y fecha usando `GET /api/matches?status=upcoming&limit=5`
2. **My Standing Widget** — Muestra el ranking del usuario en cada grupo usando `GET /api/scores/my-standing`
3. **Activity Feed Widget** — Muestra las últimas actividades del usuario usando `GET /api/activity?limit=10`
4. **Match Distribution Modal** — Muestra la distribución de predicciones para un partido usando `GET /api/matches/<id>/distribution`
5. **Dashboard Layout Redesign** — Reorganizar el dashboard en un layout de grid con los widgets
6. **Nuevos Stores** — `activity.ts`, `scores.ts` (extender `matches.ts` para filtros)
7. **Nuevos Componentes** — `UpcomingMatchesWidget.vue`, `MyStandingWidget.vue`, `ActivityFeedWidget.vue`, `MatchDistributionModal.vue`

### Out of Scope

- Group Detail view (no cambios)
- Leaderboard view (no cambios)
- Matches view (no cambios)
- Predictions view (no cambios)
- History view (no cambios)
- Login view (ya rediseñado previamente)
- Backend changes (ya implementados)

## Business Context

El dashboard actual solo muestra la lista de grupos y botones para crear/unirse. Los usuarios no tienen visibilidad de:
- Próximos partidos relevantes
- Su posición en cada grupo
- Actividad reciente en la plataforma
- Distribución de predicciones de otros usuarios

Este rediseño mejora la experiencia del usuario proporcionando información contextual y social directamente en el dashboard.

## Approach

- Vue 3 + Composition API + Pinia (mismo stack)
- Tailwind v4 con @theme {} y M3 tokens (mismo sistema de diseño)
- Nuevos stores para consumir las nuevas APIs
- Componentes reutilizables y autocontenidos
- Lazy loading de widgets (cargan datos en paralelo)
- Manejo de estados de carga y error en cada widget

## Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Nuevas APIs aún no probadas en frontend | Medium | Implementar con manejo de errores robusto |
| Tailwind v4 token collision | Low | Ya resuelto en change anterior |
| Mobile layout complejo | Low | Usar grid responsive de Tailwind |
| Spanish text throughout | Low | Continuar con español como idioma de UI |

## Success Criteria

- Dashboard muestra todos los widgets correctamente
- Cada widget carga datos de la API correspondiente
- Layout responsive funciona en mobile y desktop
- No regresiones en funcionalidad existente (grupos, create/join)
- Estética consistente con el diseño M3 del login
