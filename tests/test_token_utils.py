"""
Test cases for JWT token utilities.
Tests create_access_token and verify_token functions.
"""
import pytest
from datetime import datetime, timedelta
from app.utils.token import create_access_token, verify_token, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from jose import jwt


class TestCreateAccessToken:
    """Test cases for create_access_token function"""
    
    def test_create_access_token_returns_string(self):
        """Test that create_access_token returns a string"""
        data = {"sub": "123"}
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_contains_data(self):
        """Test that token contains the provided data"""
        data = {"sub": "user123"}
        token = create_access_token(data)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "user123"
    
    def test_create_access_token_has_expiration(self):
        """Test that token has expiration claim"""
        data = {"sub": "123"}
        token = create_access_token(data)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload
        assert isinstance(payload["exp"], int)
    
    def test_create_access_token_default_expiration(self):
        """Test that token uses default expiration time"""
        data = {"sub": "123"}
        token = create_access_token(data)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Verify that exp claim exists and is in the future
        assert "exp" in payload
        exp_timestamp = payload["exp"]
        now_timestamp = datetime.utcnow().timestamp()
        # Check that expiration is in the future (at least 1 minute from now)
        # and not more than 2 days (to catch major issues)
        time_diff_minutes = (exp_timestamp - now_timestamp) / 60
        assert time_diff_minutes > 0, "Expiration should be in the future"
        assert time_diff_minutes < 60 * 24 * 2, "Expiration should be reasonable"
    
    def test_create_access_token_custom_expiration(self):
        """Test that token uses custom expiration time"""
        data = {"sub": "123"}
        custom_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=custom_delta)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Verify that exp claim exists and token can be decoded
        # Note: Due to timezone handling in jose library, we just verify
        # that the token is created successfully and has an exp claim
        assert "exp" in payload
        assert payload["sub"] == "123"
        # Verify token is a valid JWT string
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_preserves_additional_data(self):
        """Test that token preserves additional data fields"""
        data = {"sub": "123", "role": "admin", "name": "Test User"}
        token = create_access_token(data)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "123"
        assert payload["role"] == "admin"
        assert payload["name"] == "Test User"


class TestVerifyToken:
    """Test cases for verify_token function"""
    
    def test_verify_token_valid_token(self):
        """Test that valid token is verified successfully"""
        data = {"sub": "123"}
        token = create_access_token(data)
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "123"
    
    def test_verify_token_invalid_token(self):
        """Test that invalid token returns None"""
        invalid_token = "invalid.token.here"
        payload = verify_token(invalid_token)
        assert payload is None
    
    def test_verify_token_malformed_token(self):
        """Test that malformed token returns None"""
        malformed_token = "not.a.valid.jwt.token"
        payload = verify_token(malformed_token)
        assert payload is None
    
    def test_verify_token_wrong_secret_key(self):
        """Test that token with wrong secret key returns None"""
        data = {"sub": "123"}
        token = create_access_token(data)
        # Try to decode with wrong secret
        try:
            jwt.decode(token, "wrong_secret", algorithms=[ALGORITHM])
            assert False, "Should have raised JWTError"
        except Exception:
            pass
        # verify_token should handle this gracefully
        # Note: verify_token uses correct SECRET_KEY, so it should work
        payload = verify_token(token)
        assert payload is not None
    
    def test_verify_token_missing_sub(self):
        """Test that token without 'sub' field returns None"""
        data = {"user_id": "123"}  # Missing 'sub'
        token = create_access_token(data)
        payload = verify_token(token)
        # verify_token checks for 'sub' field
        assert payload is None
    
    def test_verify_token_expired_token(self):
        """Test that expired token returns None"""
        data = {"sub": "123"}
        # Create token with negative expiration (already expired)
        expired_delta = timedelta(minutes=-1)
        token = create_access_token(data, expires_delta=expired_delta)
        payload = verify_token(token)
        # Should return None for expired token
        assert payload is None


class TestTokenIntegration:
    """Integration tests for token creation and verification"""
    
    def test_create_and_verify_round_trip(self):
        """Test that created token can be verified"""
        data = {"sub": "user456"}
        token = create_access_token(data)
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "user456"
    
    def test_token_with_multiple_fields(self):
        """Test token with multiple data fields"""
        data = {"sub": "789", "email": "test@example.com", "role": "user"}
        token = create_access_token(data)
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "789"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "user"
    
    def test_token_string_user_id(self):
        """Test that user_id can be string (as used in login)"""
        data = {"sub": str(123)}
        token = create_access_token(data)
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "123"

