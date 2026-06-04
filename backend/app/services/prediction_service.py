"""Prediction service - business logic for predictions."""
from datetime import datetime
from app.extensions import db
from app.models import Prediction, Match, User, PredictionGroup


def submit_prediction(user_id: str, match_id: int, group_id: str, home_score: int, away_score: int) -> Prediction:
    """Submit or update a prediction for a match in a group.
    
    Args:
        user_id: User ID
        match_id: Match ID
        group_id: Prediction group ID
        home_score: Predicted home team score (must be >= 0)
        away_score: Predicted away team score (must be >= 0)
    
    Returns:
        Updated or created Prediction object
    
    Raises:
        ValueError: If deadline has passed
    """
    # Get match to check deadline
    match = Match.query.get(match_id)
    if not match:
        raise ValueError("match_not_found")
    
    # Check deadline (>= deadline means frozen, use naive UTC comparison)
    now = datetime.utcnow()
    if now >= match.deadline_utc:
        raise ValueError("prediction_locked")
    
    # Check if prediction exists
    prediction = Prediction.query.filter_by(
        user_id=user_id,
        match_id=match_id,
        group_id=group_id
    ).first()
    
    if prediction:
        # Update existing
        prediction.home_score = home_score
        prediction.away_score = away_score
        prediction.submitted_at = datetime.utcnow()
    else:
        # Create new
        prediction = Prediction(
            user_id=user_id,
            match_id=match_id,
            group_id=group_id,
            home_score=home_score,
            away_score=away_score
        )
        db.session.add(prediction)
    
    db.session.commit()
    return prediction
