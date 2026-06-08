"""Prediction service - business logic for predictions."""
from datetime import datetime
from app.extensions import db
from app.models import Prediction, Match


def submit_prediction(user_id: str, match_id: int, home_score: int, away_score: int) -> Prediction:
    """Submit or update a prediction for a match.

    One prediction per user per match, valid across all groups.

    Raises ValueError("prediction_locked") if now >= match.deadline_utc.
    Raises ValueError("match_not_found") if match doesn't exist.
    """
    match = Match.query.get(match_id)
    if not match:
        raise ValueError("match_not_found")

    if datetime.utcnow() >= match.deadline_utc:
        raise ValueError("prediction_locked")

    # Upsert: one prediction per user per match
    prediction = Prediction.query.filter_by(
        user_id=user_id,
        match_id=match_id,
    ).first()

    if prediction:
        prediction.home_score = home_score
        prediction.away_score = away_score
        prediction.submitted_at = datetime.utcnow()
    else:
        prediction = Prediction(
            user_id=user_id,
            match_id=match_id,
            home_score=home_score,
            away_score=away_score,
        )
        db.session.add(prediction)

    db.session.commit()
    return prediction
