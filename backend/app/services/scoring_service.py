"""Scoring service - calculate and record prediction scores."""
from datetime import datetime
from app.models import Prediction, PredictionScore, Match


def calculate_score(predicted_home: int, predicted_away: int, actual_home: int, actual_away: int) -> tuple[int, str]:
    """Calculate points for a prediction based on actual result.
    
    Scoring rules:
    - 3 points: exact score match
    - 1 point: correct outcome (win/draw/loss) but wrong score
    - 0 points: wrong outcome
    
    Args:
        predicted_home: Predicted home score
        predicted_away: Predicted away score
        actual_home: Actual home score
        actual_away: Actual away score
    
    Returns:
        Tuple of (points, score_type) where score_type is "exact", "outcome", or "miss"
    """
    # Check exact match
    if predicted_home == actual_home and predicted_away == actual_away:
        return (3, "exact")
    
    # Check outcome (win/draw/loss)
    predicted_outcome = predicted_home - predicted_away
    actual_outcome = actual_home - actual_away
    
    # Normalize to sign: >0 = home win, 0 = draw, <0 = away win
    predicted_sign = 1 if predicted_outcome > 0 else (-1 if predicted_outcome < 0 else 0)
    actual_sign = 1 if actual_outcome > 0 else (-1 if actual_outcome < 0 else 0)
    
    if predicted_sign == actual_sign:
        return (1, "outcome")
    
    return (0, "miss")


def score_match(match_id: int, home_score: int, away_score: int, session) -> None:
    """Score all predictions for a match across all groups.
    
    This is idempotent: re-running with the same scores updates existing rows
    via ON CONFLICT DO UPDATE.
    
    Args:
        match_id: Match ID
        home_score: Actual home team score
        away_score: Actual away team score
        session: SQLAlchemy session
    """
    # Get match info for activity payload
    match = Match.query.get(match_id)
    home_code = match.home_team.code if match else "?"
    away_code = match.away_team.code if match else "?"

    # Get all predictions for this match
    predictions = Prediction.query.filter_by(match_id=match_id).all()

    from app.services.activity_service import emit_event

    for prediction in predictions:
        # Calculate score for this prediction
        points, score_type = calculate_score(
            prediction.home_score,
            prediction.away_score,
            home_score,
            away_score
        )

        # Check if score already exists
        existing_score = PredictionScore.query.filter_by(prediction_id=prediction.id).first()

        if existing_score:
            existing_score.points = points
            existing_score.score_type = score_type
            existing_score.calculated_at = datetime.utcnow()
        else:
            score = PredictionScore(
                prediction_id=prediction.id,
                points=points,
                score_type=score_type
            )
            session.add(score)

        # Emit score_calculated event (best-effort)
        emit_event(
            user_id=prediction.user_id,
            event_type="score_calculated",
            match_id=match_id,
            payload={
                "points": points,
                "score_type": score_type,
                "home_team": home_code,
                "away_team": away_code,
                "actual_home": home_score,
                "actual_away": away_score,
                "predicted_home": prediction.home_score,
                "predicted_away": prediction.away_score,
            },
        )

    session.commit()
