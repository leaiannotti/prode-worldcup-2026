# League Detail Specification

## Purpose

Defines inline prize editing and collapsible audit history behavior in the league detail modal.

## Requirements

### Requirement: Inline prize editing

The modal SHALL render editable text inputs for each prize rank (1st, 2nd, 3rd). All members SHALL see the edit UI.

#### Scenario: Member opens modal

- GIVEN a member views a league detail modal
- THEN prize fields are editable inputs pre-filled with current values

#### Scenario: Empty prizes

- GIVEN a group has no prizes
- THEN the inputs are empty and editable

### Requirement: Save flow

On save, the frontend SHALL call `PATCH /api/groups/:id/prizes` with changed values only. On success, local state updates and the modal stays open.

#### Scenario: Successful save

- GIVEN member edited 1st prize to "Asado"
- WHEN they click save
- THEN `patchPrizes` is called with `{ first: "Asado" }`
- AND local group state updates and a success indicator is shown

#### Scenario: Validation error

- GIVEN member enters a prize longer than 200 characters
- WHEN they click save
- THEN the PATCH returns `422` and the error is displayed inline

#### Scenario: No-op save

- GIVEN member saves prizes identical to current values
- WHEN they click save
- THEN the request succeeds but no activity events are generated

### Requirement: Collapsible audit history

The modal SHALL contain a collapsible "Ver historial" section below prizes. It SHALL be collapsed by default.

#### Scenario: Toggle history

- GIVEN the modal is open with history collapsed
- WHEN user clicks "Ver historial"
- THEN the section expands and fetches last 10 `prize_changed` events

#### Scenario: Collapse history

- GIVEN the history section is expanded
- WHEN user clicks again
- THEN the section collapses

### Requirement: Audit message formatting

Audit lines SHALL follow: `{Actor} cambió el {rank}° premio de «{previous}» a «{new}» — {relative_time}`. If `actor_is_admin` is true, append `(admin)` to the actor name.

#### Scenario: Regular member change

- GIVEN a `prize_changed` event with `actor_is_admin: false`
- WHEN the line is rendered
- THEN it shows "Juan cambió el 1° premio de «Pizza» a «Asado» — hace 2 días"

#### Scenario: Admin change

- GIVEN a `prize_changed` event with `actor_is_admin: true`
- WHEN the line is rendered
- THEN it shows "Lea (admin) cambió el 1° premio de «Pizza» a «Asado» — hace 2 días"

### Requirement: Dead code removal

The frontend SHALL remove the unused `setPrizes` action and all references.

#### Scenario: No dead references

- GIVEN a codebase search for `setPrizes`
- THEN no imports or calls exist outside the store definition
