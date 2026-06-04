# Prediction Groups Specification

## Purpose

Manages the lifecycle of named prediction groups. Users create or join groups via invite code. Each group configures prize descriptions for top-3 finishers.

## Requirements

### Requirement: Create Prediction Group

The system MUST allow an authenticated user to create a prediction group with a unique name. The creator MUST automatically become the first member with the `owner` role. The system MUST generate a short, random, URL-safe invite code (6–8 chars, uppercase alphanumeric).

#### Scenario: Successful group creation

- GIVEN an authenticated user submits `POST /api/groups` with `{"name": "Oficina"}`
- WHEN the name is not already taken
- THEN a group is created, the creator is added as owner, an invite code is generated, and HTTP 201 is returned with the group object

#### Scenario: Duplicate group name

- GIVEN a group named "Oficina" already exists
- WHEN a user submits `POST /api/groups` with the same name
- THEN the system returns HTTP 409 `{"error": "group_name_taken"}`

#### Scenario: Missing name field

- GIVEN a user submits `POST /api/groups` with an empty body
- WHEN the request is validated
- THEN the system returns HTTP 422 with field-level validation errors

---

### Requirement: Join Group via Invite Code

The system MUST allow an authenticated user to join an existing group using a valid invite code. The system MUST prevent duplicate memberships.

#### Scenario: Successful join

- GIVEN a user provides a valid 6–8 char invite code
- WHEN they call `POST /api/groups/join` with `{"invite_code": "ABC123"}`
- THEN a `group_membership` record is created and HTTP 200 is returned with the group object

#### Scenario: Already a member

- GIVEN a user is already a member of the group referenced by the invite code
- WHEN they attempt to join again
- THEN the system returns HTTP 409 `{"error": "already_a_member"}`

#### Scenario: Invalid invite code

- GIVEN a user submits an invite code that matches no group
- WHEN the lookup is performed
- THEN the system returns HTTP 404 `{"error": "group_not_found"}`

---

### Requirement: List Group Members

The system MUST return all members of a prediction group when requested by a member of that group.

#### Scenario: Member lists members

- GIVEN user A is a member of group G
- WHEN they call `GET /api/groups/{group_id}/members`
- THEN the system returns a list of `{user_id, name, picture, role, joined_at}`

#### Scenario: Non-member access denied

- GIVEN user B is NOT a member of group G
- WHEN they call `GET /api/groups/{group_id}/members`
- THEN the system returns HTTP 403

---

### Requirement: Configure Group Prizes

The system MUST allow the group owner to set prize descriptions for rank 1, 2, and 3. Each prize MUST be a non-empty string of ≤255 chars.

#### Scenario: Owner sets prizes

- GIVEN a group owner submits `PUT /api/groups/{group_id}/prizes` with ranks 1–3
- WHEN all descriptions are valid
- THEN the prize_tiers are upserted and HTTP 200 is returned

#### Scenario: Non-owner attempts to set prizes

- GIVEN a non-owner member calls the prize endpoint
- WHEN the request is validated
- THEN the system returns HTTP 403

---

## API Contract

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/groups` | JWT | Create group |
| POST | `/api/groups/join` | JWT | Join via invite code |
| GET | `/api/groups` | JWT | List caller's groups |
| GET | `/api/groups/{id}` | JWT (member) | Group detail |
| GET | `/api/groups/{id}/members` | JWT (member) | Member list |
| PUT | `/api/groups/{id}/prizes` | JWT (owner) | Set prize tiers |

## Data Constraints

- `prediction_groups.name`: NOT NULL, UNIQUE, 1–100 chars
- `prediction_groups.invite_code`: NOT NULL, UNIQUE, 6–8 chars
- `group_memberships`: UNIQUE on `(group_id, user_id)`
- `prize_tiers.rank`: values 1, 2, 3 only; UNIQUE on `(group_id, rank)`
- `prize_tiers.description`: NOT NULL, 1–255 chars
