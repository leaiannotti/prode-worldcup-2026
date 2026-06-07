# Tasks: Dashboard Frontend Redesign

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 400–500 |
| 400-line budget risk | Medium |
| Chained PRs recommended | No (within budget) |
| Suggested split | Single PR |
| Delivery strategy | ask-always (but within budget) |

---

## Phase 1: Stores

- [ ] 1.1 Create `frontend/src/stores/scores.ts` with `MyStandingItem` interface, `useScoresStore` with `fetchMyStanding()` action
- [ ] 1.2 Create `frontend/src/stores/activity.ts` with `ActivityEvent` interface, `useActivityStore` with `fetchActivity()` action
- [ ] 1.3 Extend `frontend/src/stores/matches.ts` — add `status` and `limit` to `MatchFilters`, update `fetchMatches()` to append query params
- [ ] 1.4 Verify stores compile correctly (run `npm run build` or `npx vue-tsc --noEmit`)

---

## Phase 2: Widgets

- [ ] 2.1 Create `frontend/src/components/UpcomingMatchesWidget.vue` — fetch upcoming matches on mount, show list with flags, handle empty/error/loading states
- [ ] 2.2 Create `frontend/src/components/MyStandingWidget.vue` — fetch my-standing on mount, show rank cards, handle empty/error/loading states
- [ ] 2.3 Create `frontend/src/components/ActivityFeedWidget.vue` — fetch activity on mount, show event list with icons, handle empty/error/loading states
- [ ] 2.4 Verify all 3 widgets render correctly in isolation (Storybook or manual test)

---

## Phase 3: Modal

- [ ] 3.1 Create `frontend/src/components/MatchDistributionModal.vue` — accept `isOpen`, `matchId`, `match` props, fetch distribution on open, show bars/pre-deadline/error states
- [ ] 3.2 Verify modal opens/closes correctly, shows distribution data for a known match

---

## Phase 4: Dashboard Integration

- [ ] 4.1 Update `frontend/src/views/DashboardView.vue` — import widgets, add grid layout, wire up `openDistribution` handler
- [ ] 4.2 Update DashboardView Spanish text (replace English UI copy with Spanish)
- [ ] 4.3 Verify responsive layout works on desktop (≥1024px) and mobile (375px)
- [ ] 4.4 Verify existing group cards still work (create, join, list)

---

## Phase 5: Testing & Polish

- [ ] 5.1 Run `npm run build` — verify no TypeScript errors
- [ ] 5.2 Run `npm run dev` — smoke test the dashboard visually
- [ ] 5.3 Check console for API errors or warnings
- [ ] 5.4 Verify no Tailwind v4 class collisions (e.g., `p-md`, `gap-lg` should be `p-4`, `gap-6`)
- [ ] 5.5 Run `npm run lint` if available

---

## Phase 6: Backend Integration (Manual)

- [ ] 6.1 Start backend (`flask run`) and frontend (`npm run dev`) together
- [ ] 6.2 Log in, verify dashboard loads with widgets
- [ ] 6.3 Verify upcoming matches widget shows real data
- [ ] 6.4 Verify my-standing widget shows real data
- [ ] 6.5 Verify activity feed shows real data (or empty state if no activity)
- [ ] 6.6 Click on a match, verify distribution modal opens
- [ ] 6.7 Create a group, verify dashboard refreshes
- [ ] 6.8 Join a group, verify my-standing updates

---

## Acceptance Criteria

- [ ] Dashboard shows 3 widgets: Upcoming Matches, My Standing, Activity Feed
- [ ] Each widget loads data from the correct API endpoint
- [ ] Layout is responsive (1 col mobile, 2 col desktop)
- [ ] Match distribution modal works when clicking a match
- [ ] All text in Spanish
- [ ] No TypeScript errors
- [ ] No console errors
- [ ] Existing functionality (groups) still works
