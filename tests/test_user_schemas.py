"""
Test cases for user schemas validation.
Tests Pydantic schema validation for UserCreate, UserLogin, UserResponse, and TokenResponse.
"""
import pytest
from pydantic import ValidationError, EmailStr
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse


class TestUserCreate:
    """Test cases for UserCreate schema"""
    
    def test_user_create_valid_data(self):
        """Test UserCreate with valid email and password"""
        user_data = UserCreate(email="test@example.com", password="password123")
        assert user_data.email == "test@example.com"
        assert user_data.password == "password123"
    
    def test_user_create_invalid_email_format(self):
        """Test UserCreate with invalid email format"""
        with pytest.raises(ValidationError):
            UserCreate(email="invalid_email", password="password123")
    
    def test_user_create_missing_email(self):
        """Test UserCreate without email field"""
        with pytest.raises(ValidationError):
            UserCreate(password="password123")
    
    def test_user_create_missing_password(self):
        """Test UserCreate without password field"""
        with pytest.raises(ValidationError):
            UserCreate(email="test@example.com")
    
    def test_user_create_empty_password(self):
        """Test UserCreate with empty password (should be allowed)"""
        user_data = UserCreate(email="test@example.com", password="")
        assert user_data.password == ""
    
    def test_user_create_valid_email_variations(self):
        """Test UserCreate with various valid email formats"""
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "user123@example-domain.com"
        ]
        for email in valid_emails:
            user_data = UserCreate(email=email, password="password123")
            assert user_data.email == email


class TestUserLogin:
    """Test cases for UserLogin schema"""
    
    def test_user_login_valid_data(self):
        """Test UserLogin with valid email and password"""
        login_data = UserLogin(email="test@example.com", password="password123")
        assert login_data.email == "test@example.com"
        assert login_data.password == "password123"
    
    def test_user_login_invalid_email_format(self):
        """Test UserLogin with invalid email format"""
        with pytest.raises(ValidationError):
            UserLogin(email="not_an_email", password="password123")
    
    def test_user_login_missing_email(self):
        """Test UserLogin without email field"""
        with pytest.raises(ValidationError):
            UserLogin(password="password123")
    
    def test_user_login_missing_password(self):
        """Test UserLogin without password field"""
        with pytest.raises(ValidationError):
            UserLogin(email="test@example.com")
    
    def test_user_login_empty_password(self):
        """Test UserLogin with empty password"""
        login_data = UserLogin(email="test@example.com", password="")
        assert login_data.password == ""


class TestUserResponse:
    """Test cases for UserResponse schema"""
    
    def test_user_response_valid_data(self):
        """Test UserResponse with valid data"""
        user_response = UserResponse(
            id=1,
            email="test@example.com",
            username="testuser"
        )
        assert user_response.id == 1
        assert user_response.email == "test@example.com"
        assert user_response.username == "testuser"
    
    def test_user_response_without_username(self):
        """Test UserResponse without username (optional field)"""
        user_response = UserResponse(
            id=1,
            email="test@example.com"
        )
        assert user_response.id == 1
        assert user_response.email == "test@example.com"
        assert user_response.username is None
    
    def test_user_response_missing_id(self):
        """Test UserResponse without id field"""
        with pytest.raises(ValidationError):
            UserResponse(email="test@example.com")
    
    def test_user_response_missing_email(self):
        """Test UserResponse without email field"""
        with pytest.raises(ValidationError):
            UserResponse(id=1)
    
    def test_user_response_invalid_email_format(self):
        """Test UserResponse with invalid email format"""
        with pytest.raises(ValidationError):
            UserResponse(id=1, email="invalid_email")
    
    def test_user_response_with_empty_bookmarks(self):
        """Test UserResponse with empty bookmarks list"""
        user_response = UserResponse(
            id=1,
            email="test@example.com",
            bookmarks=[]
        )
        assert user_response.bookmarks == []
    
    def test_user_response_with_bookmarks(self):
        """Test UserResponse with bookmarks"""
        from app.schemas.bookmark import BookmarkResponse
        bookmark = BookmarkResponse(
            id=1,
            title="Test Bookmark",
            address="123 Test St",
            latitude=40.7128,
            longitude=-74.0060
        )
        user_response = UserResponse(
            id=1,
            email="test@example.com",
            bookmarks=[bookmark]
        )
        assert len(user_response.bookmarks) == 1
        assert user_response.bookmarks[0].id == 1


class TestTokenResponse:
    """Test cases for TokenResponse schema"""
    
    def test_token_response_valid_data(self):
        """Test TokenResponse with valid data"""
        user = UserResponse(id=1, email="test@example.com")
        token_response = TokenResponse(
            access_token="test_token_123",
            token_type="bearer",
            user=user
        )
        assert token_response.access_token == "test_token_123"
        assert token_response.token_type == "bearer"
        assert token_response.user.id == 1
        assert token_response.user.email == "test@example.com"
    
    def test_token_response_missing_access_token(self):
        """Test TokenResponse without access_token"""
        user = UserResponse(id=1, email="test@example.com")
        with pytest.raises(ValidationError):
            TokenResponse(token_type="bearer", user=user)
    
    def test_token_response_missing_token_type(self):
        """Test TokenResponse without token_type"""
        user = UserResponse(id=1, email="test@example.com")
        with pytest.raises(ValidationError):
            TokenResponse(access_token="test_token", user=user)
    
    def test_token_response_missing_user(self):
        """Test TokenResponse without user"""
        with pytest.raises(ValidationError):
            TokenResponse(access_token="test_token", token_type="bearer")
    
    def test_token_response_different_token_types(self):
        """Test TokenResponse with different token types"""
        user = UserResponse(id=1, email="test@example.com")
        token_types = ["bearer", "Bearer", "BEARER"]
        for token_type in token_types:
            token_response = TokenResponse(
                access_token="test_token",
                token_type=token_type,
                user=user
            )
            assert token_response.token_type == token_type

