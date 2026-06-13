# Frontend Specification

## Purpose
UI behavior for displaying a group member's recent finished-match predictions via a bottom sheet.

## Requirements

### Requirement: Avatar Click Trigger

The `LeaderboardTable` component MUST emit a `select-user` event when the user taps a member's avatar. The avatar MUST be clickable for all members, including the current user.

#### Scenario: Avatar tap opens bottom sheet

- GIVEN the leaderboard table is rendered with group members
- WHEN the user taps a member's avatar
- THEN `LeaderboardTable` MUST emit `select-user` with the member's `user_id`
- AND `LeaderboardView` MUST open the `FriendRecentResultsSheet` bottom sheet

#### Scenario: Self-tap is allowed

- GIVEN the current user is viewing their own avatar in the leaderboard
- WHEN the user taps their own avatar
- THEN the bottom sheet MUST open showing the user's own recent history

### Requirement: Bottom Sheet Content

`FriendRecentResultsSheet` MUST render rows of recent finished matches. Each row MUST display the match teams, the user's prediction (or `—`), and the points earned.

#### Scenario: Happy path with 5 matches

- GIVEN the fetched data contains 5 finished matches with predictions
- WHEN the bottom sheet renders
- THEN it MUST display exactly 5 rows
- AND each row MUST show match teams, the prediction, and the points

#### Scenario: Missing prediction

- GIVEN the fetched data contains a match with `prediction: null`
- WHEN the row renders
- THEN the prediction area MUST display `—`
- AND the points MUST display `0`

#### Scenario: Fewer than 5 matches

- GIVEN the fetched data contains only 2 finished matches
- WHEN the bottom sheet renders
- THEN it MUST display exactly 2 rows

### Requirement: Points Color Coding

Points displayed in the bottom sheet MUST use color coding: `3` points in green, `1` point in yellow, and `0` points in red.

#### Scenario: Exact prediction (+3)

- GIVEN a row with `points = 3`
- WHEN the row renders
- THEN the points badge MUST be styled in green

#### Scenario: Outcome prediction (+1)

- GIVEN a row with `points = 1`
- WHEN the row renders
- THEN the points badge MUST be styled in yellow

#### Scenario: Miss or no prediction (+0)

- GIVEN a row with `points = 0`
- WHEN the row renders
- THEN the points badge MUST be styled in red
