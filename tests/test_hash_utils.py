"""
Test cases for password hashing utilities.
Tests hash_password and verify_password functions.
"""
import pytest
from app.utils.hash import hash_password, verify_password


class TestHashPassword:
    """Test cases for hash_password function"""
    
    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string"""
        password = "test_password_123"
        hashed = hash_password(password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_hash_password_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes"""
        password1 = "password1"
        password2 = "password2"
        hash1 = hash_password(password1)
        hash2 = hash_password(password2)
        assert hash1 != hash2
    
    def test_hash_password_same_password_different_hashes(self):
        """Test that same password produces different hashes (salt)"""
        password = "same_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        # Bcrypt uses salt, so same password should produce different hashes
        assert hash1 != hash2
    
    def test_hash_password_empty_string(self):
        """Test hashing empty string"""
        hashed = hash_password("")
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_hash_password_special_characters(self):
        """Test hashing password with special characters"""
        password = "p@ssw0rd!#$%^&*()"
        hashed = hash_password(password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0


class TestVerifyPassword:
    """Test cases for verify_password function"""
    
    def test_verify_password_correct_password(self):
        """Test that correct password is verified successfully"""
        password = "test_password_123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect_password(self):
        """Test that incorrect password is rejected"""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty_password(self):
        """Test verification of empty password"""
        password = ""
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
        assert verify_password("non_empty", hashed) is False
    
    def test_verify_password_case_sensitive(self):
        """Test that password verification is case sensitive"""
        password = "TestPassword"
        hashed = hash_password(password)
        assert verify_password("TestPassword", hashed) is True
        assert verify_password("testpassword", hashed) is False
        assert verify_password("TESTPASSWORD", hashed) is False
    
    def test_verify_password_special_characters(self):
        """Test verification with special characters"""
        password = "p@ssw0rd!#$%^&*()"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
        assert verify_password("p@ssw0rd!#$%^&*()", hashed) is True
    
    def test_verify_password_long_password(self):
        """Test verification with long password"""
        # Note: bcrypt truncates passwords to 72 bytes, so we test with 70 chars
        # to ensure the full password is hashed and verified
        password = "a" * 70
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
        assert verify_password(password + "x", hashed) is False


class TestHashPasswordIntegration:
    """Integration tests for hash and verify functions"""
    
    def test_hash_and_verify_round_trip(self):
        """Test that hashing and verifying works together"""
        password = "integration_test_password"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
    
    def test_multiple_hash_verify_cycles(self):
        """Test multiple hash and verify cycles"""
        passwords = ["pass1", "pass2", "pass3", "pass4", "pass5"]
        for password in passwords:
            hashed = hash_password(password)
            assert verify_password(password, hashed) is True
            assert verify_password(password + "wrong", hashed) is False

