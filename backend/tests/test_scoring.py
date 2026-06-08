"""Tests for scoring service and webhook."""
import pytest
import json
import hmac
import hashlib
from datetime import datetime, timedelta
from time import time


class TestScoringService:
    """Unit tests for scoring calculation."""
    
    def test_calculate_score_exact_match_returns_3(self):
        """calculate_score with exact match returns 3 points."""
        from app.services.scoring_service import calculate_score
        
        points, score_type = calculate_score(2, 1, 2, 1)
        assert points == 3
        assert score_type == "exact"
    
    def test_calculate_score_correct_outcome_wrong_score_returns_1(self):
        """calculate_score with correct outcome but wrong score returns 1 point."""
        from app.services.scoring_service import calculate_score
        
        # Predicted home win 3-0, actual home win 2-1
        points, score_type = calculate_score(3, 0, 2, 1)
        assert points == 1
        assert score_type == "outcome"
    
    def test_calculate_score_wrong_outcome_returns_0(self):
        """calculate_score with wrong outcome returns 0 points."""
        from app.services.scoring_service import calculate_score
        
        # Predicted away win 0-1, actual home win 2-1
        points, score_type = calculate_score(0, 1, 2, 1)
        assert points == 0
        assert score_type == "miss"
    
    def test_calculate_score_draw_exact_returns_3(self):
        """calculate_score with draw exact match returns 3 points."""
        from app.services.scoring_service import calculate_score
        
        points, score_type = calculate_score(1, 1, 1, 1)
        assert points == 3
        assert score_type == "exact"
    
    def test_calculate_score_draw_prediction_actual_draw_returns_1(self):
        """calculate_score with predicted draw, actual draw returns 1 (outcome correct)."""
        from app.services.scoring_service import calculate_score
        
        # Predicted 0-0 draw, actual 2-2 draw
        points, score_type = calculate_score(0, 0, 2, 2)
        assert points == 1
        assert score_type == "outcome"
    
    def test_score_match_creates_prediction_scores(self, app, db_session, seed_matches, seed_user):
        """score_match creates prediction_scores for match."""
        from app.services.scoring_service import score_match
        from app.models import PredictionGroup, GroupMembership, Prediction, PredictionScore
        
        with app.app_context():
            # Setup: create group, add user, create prediction
            group = PredictionGroup(name="Test", invite_code="ABC", creator_id=seed_user.id)
            db_session.add(group)
            db_session.commit()
            
            membership = GroupMembership(user_id=seed_user.id, group_id=group.id)
            db_session.add(membership)
            db_session.commit()
            
            match = seed_matches[0]
            pred = Prediction(user_id=seed_user.id, match_id=match.id, home_score=2, away_score=1)
            db_session.add(pred)
            db_session.commit()
            
            # Score the match
            score_match(match.id, 2, 1, db_session)
            
            # Verify PredictionScore created
            score = PredictionScore.query.filter_by(prediction_id=pred.id).first()
            assert score is not None
            assert score.points == 3
            assert score.score_type == "exact"
    
    def test_score_match_idempotent_no_duplicates(self, app, db_session, seed_matches, seed_user):
        """score_match is idempotent - re-run creates no duplicates."""
        from app.services.scoring_service import score_match
        from app.models import PredictionGroup, GroupMembership, Prediction, PredictionScore
        
        with app.app_context():
            # Setup
            group = PredictionGroup(name="Test", invite_code="ABC", creator_id=seed_user.id)
            db_session.add(group)
            db_session.commit()
            
            membership = GroupMembership(user_id=seed_user.id, group_id=group.id)
            db_session.add(membership)
            db_session.commit()
            
            match = seed_matches[0]
            pred = Prediction(user_id=seed_user.id, match_id=match.id, home_score=2, away_score=1)
            db_session.add(pred)
            db_session.commit()
            
            # Score once
            score_match(match.id, 2, 1, db_session)
            score1 = PredictionScore.query.filter_by(prediction_id=pred.id).first()
            score_id_1 = score1.id
            
            # Score again (idempotent)
            score_match(match.id, 2, 1, db_session)
            score2 = PredictionScore.query.filter_by(prediction_id=pred.id).first()
            score_id_2 = score2.id
            
            # Should be same row
            assert score_id_1 == score_id_2
            # Count should be 1
            count = PredictionScore.query.filter_by(prediction_id=pred.id).count()
            assert count == 1


class TestWebhookService:
    """Tests for webhook signature verification."""
    
    def test_verify_webhook_signature_valid_returns_true(self):
        """verify_webhook_signature with valid HMAC returns True."""
        from app.services.webhook_service import verify_webhook_signature
        
        secret = "test-secret"
        payload = '{"match_id": 1, "home_score": 2, "away_score": 1}'
        ts = str(int(time()))
        
        # Calculate expected signature
        msg = f"{ts}.{payload}".encode()
        sig_hex = hmac.new(secret.encode(), msg, hashlib.sha256).hexdigest()
        sig_header = f"t={ts},v1={sig_hex}"
        
        result = verify_webhook_signature(payload, sig_header, secret, max_age=300)
        assert result is True
    
    def test_verify_webhook_signature_invalid_returns_false(self):
        """verify_webhook_signature with invalid HMAC returns False."""
        from app.services.webhook_service import verify_webhook_signature
        
        secret = "test-secret"
        payload = '{"match_id": 1, "home_score": 2, "away_score": 1}'
        ts = str(int(time()))
        
        # Wrong signature
        sig_header = f"t={ts},v1=invalidsignature"
        
        result = verify_webhook_signature(payload, sig_header, secret, max_age=300)
        assert result is False
    
    def test_verify_webhook_signature_stale_returns_false(self):
        """verify_webhook_signature with stale timestamp returns False."""
        from app.services.webhook_service import verify_webhook_signature
        
        secret = "test-secret"
        payload = '{"match_id": 1, "home_score": 2, "away_score": 1}'
        # 10 minutes old (max_age=300 is 5 minutes)
        old_ts = str(int(time()) - 600)
        
        msg = f"{old_ts}.{payload}".encode()
        sig_hex = hmac.new(secret.encode(), msg, hashlib.sha256).hexdigest()
        sig_header = f"t={old_ts},v1={sig_hex}"
        
        result = verify_webhook_signature(payload, sig_header, secret, max_age=300)
        assert result is False
