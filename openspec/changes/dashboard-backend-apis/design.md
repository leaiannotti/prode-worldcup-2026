# Design: Dashboard Backend APIs

## Implementation Order

1. team-identity (migration 1)
2. match-filtering (no migration, depends on team-identity for serialization)
3. my-standing (no migration)
4. prediction-distribution (no migration)
5. activity-feed (migration 2, depends on migration 1)

---

## 1. match-filtering

### File Changes
| File | Change |
|------|--------|
| `backend/app/blueprints/matches.py` | Add `status` and `limit` query param handling to `list_matches()` |

### Route Change

```python
# In list_matches(), after existing group/date filters:

VALID_STATUSES = {"upcoming": "scheduled", "scheduled": "scheduled",
                  "in_progress": "in_progress", "finished": "finished"}

status_filter = request.args.get("status")
if status_filter:
    mapped = VALID_STATUSES.get(status_filter.lower())
    if not mapped:
        return jsonify({"error": "invalid_status"}), 400
    query = query.filter(Match.status == mapped)

limit_param = request.args.get("limit")
if limit_param:
    try:
        limit_val = int(limit_param)
        if limit_val <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "invalid_limit"}), 400
    matches = query.order_by(Match.kickoff_utc.asc()).limit(limit_val).all()
else:
    matches = query.order_by(Match.kickoff_utc.asc()).all()
```

### Error Handling
- Invalid status → 400 `{"error": "invalid_status"}`
- Invalid limit → 400 `{"error": "invalid_limit"}`

---

## 2. team-identity

### Model Changes

| File | Change |
|------|--------|
| `backend/app/models/team.py` | Add `name` and `flag_url` columns to `Team` |

```python
class Team(db.Model):
    # ... existing fields ...
    name = db.Column(db.String(100), nullable=False, server_default="")
    flag_url = db.Column(db.String(500), nullable=True)
```

### Migration

New file: `backend/migrations/versions/<timestamp>_add_team_identity.py`

```python
def upgrade():
    op.add_column('teams', sa.Column('name', sa.String(100), nullable=False, server_default=''))
    op.add_column('teams', sa.Column('flag_url', sa.String(500), nullable=True))

def downgrade():
    op.drop_column('teams', 'flag_url')
    op.drop_column('teams', 'name')
```

### FIFA→ISO2 Mapping (in seed.py)

```python
FIFA_TO_ISO2 = {
    "ARG": "ar", "AUS": "au", "BRA": "br", "CAN": "ca", "CHI": "cl",
    "CHN": "cn", "CMR": "cm", "COL": "co", "CRC": "cr", "CRO": "hr",
    "DEN": "dk", "ECU": "ec", "EGY": "eg", "ENG": "gb-eng", "ESP": "es",
    "FRA": "fr", "GER": "de", "GHA": "gh", "IRN": "ir", "ITA": "it",
    "JAM": "jm", "JPN": "jp", "KOR": "kr", "KSA": "sa", "MAR": "ma",
    "MEX": "mx", "NED": "nl", "NGA": "ng", "NZL": "nz", "PAN": "pa",
    "PAR": "py", "PER": "pe", "POL": "pl", "POR": "pt", "QAT": "qa",
    "RSA": "za", "RUS": "ru", "SCO": "gb-sct", "SEN": "sn", "SRB": "rs",
    "SUI": "ch", "TUN": "tn", "URU": "uy", "USA": "us", "WAL": "gb-wls",
    "CIV": "ci", "ALG": "dz", "NOR": "no", "SWE": "se",
}

def get_flag_url(fifa_code: str) -> str | None:
    iso2 = FIFA_TO_ISO2.get(fifa_code)
    if not iso2:
        print(f"WARNING: No ISO2 mapping for {fifa_code}")
        return None
    return f"https://flagcdn.com/w80/{iso2}.png"
```

### Seed Changes

| File | Change |
|------|--------|
| `backend/app/seed.py` | Populate `name` from JSON, `flag_url` from mapping |
| `backend/app/json_loader.py` | Return `name` field (already present in JSON) |

### Serialization Changes

| File | Change |
|------|--------|
| `backend/app/blueprints/matches.py` | Add `name` and `flag_url` to team sub-objects |

```python
# In both list_matches() and get_match():
"home_team": {
    "id": m.home_team.id,
    "code": m.home_team.code,
    "name": m.home_team.name,
    "flag_url": m.home_team.flag_url,
},
```

---

## 3. my-standing

### File Changes

| File | Change |
|------|--------|
| `backend/app/blueprints/scores.py` | Add `my_standing()` route |
| `backend/app/schemas/score.py` | Add `MyStandingItem` Pydantic model |

### Endpoint

`GET /api/scores/my-standing` — no query params

### Query Strategy

```python
@scores_bp.route("/my-standing", methods=["GET"])
@jwt_required
def my_standing():
    user_id = g.current_user.id

    # 1. Get all groups user belongs to
    memberships = GroupMembership.query.filter_by(user_id=user_id).all()

    results = []
    for membership in memberships:
        group = PredictionGroup.query.get(membership.group_id)
        member_count = GroupMembership.query.filter_by(group_id=group.id).count()

        # 2. Aggregate points for ALL members in this group (one query per group)
        member_points = (
            db.session.query(
                Prediction.user_id,
                func.coalesce(func.sum(PredictionScore.points), 0).label("total")
            )
            .outerjoin(PredictionScore)
            .filter(Prediction.group_id == group.id)
            .group_by(Prediction.user_id)
            .all()
        )

        # Build sorted list, find user's rank
        points_map = {uid: total for uid, total in member_points}
        # Include members with 0 predictions
        all_members = GroupMembership.query.filter_by(group_id=group.id).all()
        sorted_members = sorted(
            [(m.user_id, points_map.get(m.user_id, 0)) for m in all_members],
            key=lambda x: (-x[1], x[0])
        )

        # Compute rank with ties
        user_rank = 1
        user_total = points_map.get(user_id, 0)
        for i, (uid, pts) in enumerate(sorted_members):
            if uid == user_id:
                # Count how many are strictly above
                user_rank = sum(1 for _, p in sorted_members if p > user_total) + 1
                break

        results.append({
            "group_id": group.id,
            "group_name": group.name,
            "rank": user_rank,
            "total_points": user_total,
            "member_count": member_count,
        })

    return jsonify(results), 200
```

### Schema

```python
class MyStandingItem(BaseModel):
    group_id: str
    group_name: str
    rank: int
    total_points: int
    member_count: int
```

---

## 4. prediction-distribution

### File Changes

| File | Change |
|------|--------|
| `backend/app/blueprints/matches.py` | Add `get_distribution()` route |

### Endpoint

`GET /api/matches/<int:match_id>/distribution`

### Query Strategy

```python
@bp.route("/<int:match_id>/distribution", methods=["GET"])
@jwt_required
def get_distribution(match_id):
    match = Match.query.get(match_id)
    if not match:
        return jsonify({"error": "not_found"}), 404

    now = datetime.utcnow()
    if now < match.deadline_utc:
        return jsonify({"available": False, "reason": "pre_deadline"}), 200

    # Deduplicate: one vote per (user_id, match_id)
    # Use a subquery to get distinct predictions
    subq = (
        db.session.query(
            Prediction.user_id,
            Prediction.home_score,
            Prediction.away_score
        )
        .filter(Prediction.match_id == match_id)
        .distinct(Prediction.user_id)
        .subquery()
    )

    # Aggregate outcomes
    total = db.session.query(func.count()).select_from(subq).scalar() or 0

    if total == 0:
        return jsonify({
            "available": True,
            "match_id": match_id,
            "home_win_pct": 0,
            "draw_pct": 0,
            "away_win_pct": 0,
            "total_predictions": 0,
        }), 200

    home_wins = db.session.query(func.count()).select_from(subq).filter(
        subq.c.home_score > subq.c.away_score
    ).scalar() or 0

    draws = db.session.query(func.count()).select_from(subq).filter(
        subq.c.home_score == subq.c.away_score
    ).scalar() or 0

    away_wins = total - home_wins - draws

    return jsonify({
        "available": True,
        "match_id": match_id,
        "home_win_pct": round(home_wins / total * 100, 1),
        "draw_pct": round(draws / total * 100, 1),
        "away_win_pct": round(away_wins / total * 100, 1),
        "total_predictions": total,
    }), 200
```

### Privacy Gate
- Before `deadline_utc` → `{"available": false, "reason": "pre_deadline"}`
- NOT a 403 — avoids auth confusion

---

## 5. activity-feed

### New Model

| File | Change |
|------|--------|
| `backend/app/models/activity.py` | New `ActivityEvent` model |
| `backend/app/models/__init__.py` | Import `ActivityEvent` |

```python
import uuid
from datetime import datetime, timezone
from app.extensions import db

class ActivityEvent(db.Model):
    __tablename__ = "activity_events"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    event_type = db.Column(db.String(50), nullable=False, index=True)
    group_id = db.Column(db.String(36), db.ForeignKey("prediction_groups.id"), nullable=True)
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id"), nullable=True)
    payload = db.Column(db.JSON, nullable=True)
    occurred_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
```

### Migration

New file: `backend/migrations/versions/<timestamp>_add_activity_events.py`

- `down_revision` MUST point to the team-identity migration
- Creates `activity_events` table with indexes on `user_id`, `event_type`, `occurred_at`

### Blueprint

| File | Change |
|------|--------|
| `backend/app/blueprints/activity.py` | New blueprint |
| `backend/app/__init__.py` | Register blueprint |

```python
bp = Blueprint("activity", __name__, url_prefix="/api/activity")

@bp.route("", methods=["GET"])
@jwt_required
def list_activity():
    user_id = g.current_user.id
    limit = min(int(request.args.get("limit", 20)), 50)
    if limit <= 0:
        return jsonify({"error": "invalid_limit"}), 400

    cursor = request.args.get("cursor")

    query = ActivityEvent.query.filter_by(user_id=user_id)

    if cursor:
        try:
            cursor_dt = datetime.fromisoformat(cursor)
            query = query.filter(ActivityEvent.occurred_at < cursor_dt)
        except ValueError:
            return jsonify({"error": "invalid_cursor"}), 400

    events = query.order_by(ActivityEvent.occurred_at.desc()).limit(limit + 1).all()

    has_more = len(events) > limit
    events = events[:limit]

    next_cursor = events[-1].occurred_at.isoformat() if has_more and events else None

    return jsonify({
        "events": [{
            "id": e.id,
            "event_type": e.event_type,
            "group_id": e.group_id,
            "match_id": e.match_id,
            "payload": e.payload,
            "occurred_at": e.occurred_at.isoformat() + "Z",
        } for e in events],
        "next_cursor": next_cursor,
    }), 200
```

### Event Writer Helper

```python
# In a shared location, e.g. app/services/activity_service.py
def emit_event(user_id, event_type, group_id=None, match_id=None, payload=None):
    """Best-effort event write. Never raises."""
    try:
        event = ActivityEvent(
            user_id=user_id,
            event_type=event_type,
            group_id=group_id,
            match_id=match_id,
            payload=payload,
        )
        db.session.add(event)
        db.session.flush()  # Write but don't commit — let the caller's commit handle it
    except Exception:
        db.session.rollback()  # Rollback only the event, not the parent transaction
        import traceback
        traceback.print_exc()
```

### Instrumentation Points

| File | Where | Event |
|------|-------|-------|
| `backend/app/blueprints/groups.py` | After `db.session.commit()` in `join_group()` | `emit_event(user_id, "group_joined", group_id=group.id, payload={"group_name": group.name})` |
| `backend/app/blueprints/predictions.py` | After `db.session.commit()` in `submit_prediction()` | `emit_event(user_id, "prediction_submitted", group_id=group_id, match_id=match_id, payload={"home_score": ..., "away_score": ...})` |

**Important**: `emit_event` uses `flush()` not `commit()`, so it participates in the parent transaction. If the parent action rolls back, the event rolls back too (correct). If the event fails, we catch the exception and rollback only the event add.

---

## Test Plan

| Feature | Test File | Key Tests |
|---------|-----------|-----------|
| match-filtering | `tests/test_matches.py` | Status filter, limit, combined, invalid params |
| team-identity | `tests/test_teams.py` | Model fields, serialization, migration |
| my-standing | `tests/test_scores.py` | Multiple groups, no groups, ties, auth |
| prediction-distribution | `tests/test_distribution.py` | Post-deadline, pre-deadline, dedup, empty, 404 |
| activity-feed | `tests/test_activity.py` | Events created, pagination, failure isolation, auth |

---

## Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| FIFA→ISO2 mapping gaps | Medium | `flag_url` nullable; seed logs warnings; manual curation of 48 codes |
| Activity `flush()` vs `commit()` semantics | High | Test that parent action succeeds when event write fails |
| `DISTINCT ON` not available in SQLite (tests) | Medium | Use subquery with `GROUP BY user_id` instead for portability |
| my-standing N+1 at group level | Low | Acceptable for <20 groups per user; optimize with window functions if needed |
| Migration ordering | Low | Enforce via `down_revision` chain in Alembic |
