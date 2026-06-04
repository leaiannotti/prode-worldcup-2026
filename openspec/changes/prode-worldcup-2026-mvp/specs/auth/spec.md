# Auth Specification

## Purpose

Manages user identity via Google OAuth 2.0 Authorization Code Flow + PKCE. Issues a JWT stored in an httpOnly cookie. Protects all non-public endpoints.

## Requirements

### Requirement: Google OAuth Login

The system MUST redirect unauthenticated users to Google's OAuth consent screen when they access the login endpoint. On successful callback, the system MUST create or update a user record (upsert by Google `sub`) and issue a signed JWT stored in an httpOnly, Secure, SameSite=Lax cookie.

#### Scenario: Successful login

- GIVEN a visitor navigates to `GET /api/auth/login`
- WHEN Google returns a valid authorization code at `GET /api/auth/callback`
- THEN the system upserts the user (email, name, picture) and returns a 302 redirect to the frontend with the JWT cookie set

#### Scenario: OAuth callback with invalid state

- GIVEN a callback arrives at `GET /api/auth/callback`
- WHEN the `state` parameter does not match the server-stored nonce
- THEN the system returns HTTP 400 and does NOT set a cookie

#### Scenario: Repeat login (existing user)

- GIVEN a user has logged in before (user row exists)
- WHEN they complete the OAuth flow again
- THEN the system updates `name`, `picture`, `last_login_at` and issues a fresh JWT without creating a duplicate user row

---

### Requirement: JWT Session Validation

The system MUST validate the JWT on every protected endpoint. A missing, expired, or tampered token MUST yield HTTP 401.

#### Scenario: Valid JWT on protected endpoint

- GIVEN a request carries a valid, non-expired JWT cookie
- WHEN the endpoint is called
- THEN the system resolves `current_user` and processes the request normally

#### Scenario: Expired JWT

- GIVEN a request carries a JWT whose `exp` claim is in the past
- WHEN the endpoint is called
- THEN the system returns HTTP 401 `{"error": "token_expired"}`

#### Scenario: Tampered JWT signature

- GIVEN a request carries a JWT with a modified payload
- WHEN the endpoint is called
- THEN signature verification fails and the system returns HTTP 401

---

### Requirement: Logout

The system MUST clear the JWT cookie on logout.

#### Scenario: Successful logout

- GIVEN a user holds a valid session
- WHEN they call `POST /api/auth/logout`
- THEN the system clears the cookie and returns HTTP 200

---

## API Contract

| Method | Path | Auth | Response |
|--------|------|------|----------|
| GET | `/api/auth/login` | None | 302 → Google |
| GET | `/api/auth/callback` | None | 302 → frontend + cookie |
| POST | `/api/auth/logout` | JWT | 200 `{}` |
| GET | `/api/auth/me` | JWT | 200 `{id, email, name, picture}` |

## Data Constraints

- `users.google_sub`: unique, NOT NULL
- `users.email`: unique, NOT NULL
- JWT expiry: 7 days
- Cookie flags: `httpOnly=true`, `Secure=true`, `SameSite=Lax`
