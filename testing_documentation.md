# Testing Documentation

## Testing Strategy

This project uses **unit testing** as the primary testing strategy, focusing on testing individual components in isolation without external dependencies. The testing approach emphasizes:

1. **Deterministic Testing**: All tests produce predictable results without relying on external services or random data
2. **Isolation**: Each test is independent and can run in any order
3. **No Third-Party Dependencies**: Tests avoid calling external APIs (e.g., OpenAI, Google Maps) to prevent costs and ensure reliability
4. **Schema Validation**: Extensive testing of Pydantic schemas to ensure data validation works correctly
5. **Utility Function Testing**: Core utility functions (hashing, token generation) are thoroughly tested

### Test Organization

Tests are organized into 5 main test files:
- `test_hash_utils.py`: Password hashing and verification utilities
- `test_token_utils.py`: JWT token creation and verification
- `test_user_schemas.py`: User-related Pydantic schema validation
- `test_bookmark_schemas.py`: Bookmark-related Pydantic schema validation
- `test_generated_route_schemas.py`: Generated route-related Pydantic schema validation

## Scope of Testing

1. **Password Hashing Utilities** (`app/utils/hash.py`)
   - Password hashing functionality
   - Password verification
   - Edge cases (empty passwords, special characters, long passwords)
   - Security properties (salt usage, case sensitivity)

2. **JWT Token Utilities** (`app/utils/token.py`)
   - Token creation with various data payloads
   - Token verification
   - Expiration handling
   - Invalid token handling

3. **User Schemas** (`app/schemas/user.py`)
   - UserCreate schema validation
   - UserLogin schema validation
   - UserResponse schema validation
   - TokenResponse schema validation
   - Email format validation
   - Required field validation

4. **Bookmark Schemas** (`app/schemas/bookmark.py`)
   - BookmarkBase schema validation
   - BookmarkCreate schema validation
   - BookmarkResponse schema validation
   - Coordinate validation
   - Optional field handling

5. **Generated Route Schemas** (`app/schemas/generated_route.py`)
   - GeneratedRouteCreate schema validation
   - GeneratedRouteResponse schema validation
   - Datetime handling
   - Text field validation

### What is NOT Tested

**Third-Party Integrations**: No tests for OpenAI API calls or other external services



## Testing Environment

### Prerequisites

- Python 3.8 or higher
- pytest (testing framework)
- All project dependencies from `requirements.txt`

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
pip install pytest
```

2. Run all tests:
```bash
pytest tests/
```

3. Run specific test file:
```bash
pytest tests/test_hash_utils.py
```

4. Run with verbose output:
```bash
pytest tests/ -v
```

5. Run with coverage (if pytest-cov is installed):
```bash
pytest tests/ --cov=app
```



## All Tests Performed

### Test File: `test_hash_utils.py`

#### Test Class: `TestHashPassword`

1. **test_hash_password_returns_string**
   - **Brief description**: Verifies that `hash_password` returns a non-empty string
   - **Expected result**: Function returns a string with length > 0
   - **Observed result**: ✅ Pass - Returns bcrypt hash string

2. **test_hash_password_different_passwords_different_hashes**
   - **Brief description**: Ensures different passwords produce different hashes
   - **Expected result**: Hash of "password1" ≠ hash of "password2"
   - **Observed result**: ✅ Pass - Different passwords produce different hashes

3. **test_hash_password_same_password_different_hashes**
   - **Brief description**: Verifies that same password produces different hashes due to salt
   - **Expected result**: Two hashes of same password are different
   - **Observed result**: ✅ Pass - Bcrypt uses salt, producing different hashes

4. **test_hash_password_empty_string**
   - **Brief description**: Tests hashing of empty password string
   - **Expected result**: Returns valid hash string
   - **Observed result**: ✅ Pass - Empty string is hashed successfully

5. **test_hash_password_special_characters**
   - **Brief description**: Tests hashing password with special characters
   - **Expected result**: Returns valid hash string
   - **Observed result**: ✅ Pass - Special characters handled correctly

#### Test Class: `TestVerifyPassword`

6. **test_verify_password_correct_password**
   - **Brief description**: Verifies correct password matches its hash
   - **Expected result**: `verify_password` returns `True` for correct password
   - **Observed result**: ✅ Pass - Correct password verified successfully

7. **test_verify_password_incorrect_password**
   - **Brief description**: Verifies incorrect password is rejected
   - **Expected result**: `verify_password` returns `False` for wrong password
   - **Observed result**: ✅ Pass - Incorrect password rejected

8. **test_verify_password_empty_password**
   - **Brief description**: Tests verification of empty password
   - **Expected result**: Empty password matches its hash, non-empty doesn't
   - **Observed result**: ✅ Pass - Empty password verification works

9. **test_verify_password_case_sensitive**
   - **Brief description**: Verifies password verification is case sensitive
   - **Expected result**: "TestPassword" ≠ "testpassword" ≠ "TESTPASSWORD"
   - **Observed result**: ✅ Pass - Case sensitivity enforced

10. **test_verify_password_special_characters**
    - **Brief description**: Tests verification with special characters
    - **Expected result**: Password with special chars verified correctly
    - **Observed result**: ✅ Pass - Special characters handled correctly

11. **test_verify_password_long_password**
    - **Brief description**: Tests verification with very long password (1000 chars)
    - **Expected result**: Long password verified correctly
    - **Observed result**: ✅ Pass - Long passwords handled correctly

#### Test Class: `TestHashPasswordIntegration`

12. **test_hash_and_verify_round_trip**
    - **Brief description**: Integration test for hash and verify cycle
    - **Expected result**: Hashed password can be verified
    - **Observed result**: ✅ Pass - Round trip works correctly

13. **test_multiple_hash_verify_cycles**
    - **Brief description**: Tests multiple hash/verify cycles with different passwords
    - **Expected result**: All passwords hash and verify correctly
    - **Observed result**: ✅ Pass - Multiple cycles work correctly

---

### Test File: `test_token_utils.py`

#### Test Class: `TestCreateAccessToken`

14. **test_create_access_token_returns_string**
    - **Brief description**: Verifies token creation returns a string
    - **Expected result**: Returns non-empty string
    - **Observed result**: ✅ Pass - Returns JWT token string

15. **test_create_access_token_contains_data**
    - **Brief description**: Verifies token contains provided data
    - **Expected result**: Decoded token contains original data
    - **Observed result**: ✅ Pass - Data preserved in token

16. **test_create_access_token_has_expiration**
    - **Brief description**: Verifies token has expiration claim
    - **Expected result**: Token payload contains "exp" field
    - **Observed result**: ✅ Pass - Expiration claim present

17. **test_create_access_token_default_expiration**
    - **Brief description**: Verifies that token has expiration claim and is in reasonable range
    - **Expected result**: Token has "exp" claim and expiration is in the future
    - **Observed result**: ✅ Pass - Expiration claim present and valid

18. **test_create_access_token_custom_expiration**
    - **Brief description**: Tests custom expiration time parameter
    - **Expected result**: Token created successfully with exp claim when custom delta provided
    - **Observed result**: ✅ Pass - Custom expiration parameter works correctly

19. **test_create_access_token_preserves_additional_data**
    - **Brief description**: Verifies additional data fields are preserved
    - **Expected result**: All fields (sub, role, name) in decoded token
    - **Observed result**: ✅ Pass - Additional fields preserved

#### Test Class: `TestVerifyToken`

20. **test_verify_token_valid_token**
    - **Brief description**: Verifies valid token is verified successfully
    - **Expected result**: Returns payload with correct data
    - **Observed result**: ✅ Pass - Valid token verified

21. **test_verify_token_invalid_token**
    - **Brief description**: Tests invalid token handling
    - **Expected result**: Returns `None` for invalid token
    - **Observed result**: ✅ Pass - Invalid token returns None

22. **test_verify_token_malformed_token**
    - **Brief description**: Tests malformed token handling
    - **Expected result**: Returns `None` for malformed token
    - **Observed result**: ✅ Pass - Malformed token handled gracefully

23. **test_verify_token_wrong_secret_key**
    - **Brief description**: Tests token with wrong secret key
    - **Expected result**: Should raise JWTError when decoded with wrong secret
    - **Observed result**: ✅ Pass - Wrong secret raises error

24. **test_verify_token_missing_sub**
    - **Brief description**: Tests token without required "sub" field
    - **Expected result**: Returns `None` (verify_token checks for "sub")
    - **Observed result**: ✅ Pass - Missing "sub" returns None

25. **test_verify_token_expired_token**
    - **Brief description**: Tests expired token handling
    - **Expected result**: Returns `None` for expired token
    - **Observed result**: ✅ Pass - Expired token returns None

#### Test Class: `TestTokenIntegration`

26. **test_create_and_verify_round_trip**
    - **Brief description**: Integration test for token creation and verification
    - **Expected result**: Created token can be verified
    - **Observed result**: ✅ Pass - Round trip works correctly

27. **test_token_with_multiple_fields**
    - **Brief description**: Tests token with multiple data fields
    - **Expected result**: All fields preserved and accessible
    - **Observed result**: ✅ Pass - Multiple fields work correctly

28. **test_token_string_user_id**
    - **Brief description**: Tests token with string user ID (as used in login)
    - **Expected result**: String user ID works correctly
    - **Observed result**: ✅ Pass - String user ID handled correctly

---

### Test File: `test_user_schemas.py`

#### Test Class: `TestUserCreate`

29. **test_user_create_valid_data**
    - **Brief description**: Tests UserCreate with valid email and password
    - **Expected result**: Schema accepts valid data
    - **Observed result**: ✅ Pass - Valid data accepted

30. **test_user_create_invalid_email_format**
    - **Brief description**: Tests UserCreate with invalid email format
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Invalid email rejected

31. **test_user_create_missing_email**
    - **Brief description**: Tests UserCreate without email field
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Missing email rejected

32. **test_user_create_missing_password**
    - **Brief description**: Tests UserCreate without password field
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Missing password rejected

33. **test_user_create_empty_password**
    - **Brief description**: Tests UserCreate with empty password
    - **Expected result**: Empty password accepted (validation allows it)
    - **Observed result**: ✅ Pass - Empty password accepted

34. **test_user_create_valid_email_variations**
    - **Brief description**: Tests various valid email formats
    - **Expected result**: All valid email formats accepted
    - **Observed result**: ✅ Pass - Valid emails accepted

#### Test Class: `TestUserLogin`

35. **test_user_login_valid_data**
    - **Brief description**: Tests UserLogin with valid data
    - **Expected result**: Schema accepts valid data
    - **Observed result**: ✅ Pass - Valid login data accepted

36. **test_user_login_invalid_email_format**
    - **Brief description**: Tests UserLogin with invalid email
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Invalid email rejected

37. **test_user_login_missing_email**
    - **Brief description**: Tests UserLogin without email
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Missing email rejected

38. **test_user_login_missing_password**
    - **Brief description**: Tests UserLogin without password
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Missing password rejected

39. **test_user_login_empty_password**
    - **Brief description**: Tests UserLogin with empty password
    - **Expected result**: Empty password accepted
    - **Observed result**: ✅ Pass - Empty password accepted

#### Test Class: `TestUserResponse`

40. **test_user_response_valid_data**
    - **Brief description**: Tests UserResponse with valid data
    - **Expected result**: Schema accepts valid data
    - **Observed result**: ✅ Pass - Valid response data accepted

41. **test_user_response_without_username**
    - **Brief description**: Tests UserResponse without optional username
    - **Expected result**: Username is None
    - **Observed result**: ✅ Pass - Optional username works

42. **test_user_response_missing_id**
    - **Brief description**: Tests UserResponse without id
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Missing id rejected

43. **test_user_response_missing_email**
    - **Brief description**: Tests UserResponse without email
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Missing email rejected

44. **test_user_response_invalid_email_format**
    - **Brief description**: Tests UserResponse with invalid email
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Invalid email rejected

45. **test_user_response_with_empty_bookmarks**
    - **Brief description**: Tests UserResponse with empty bookmarks list
    - **Expected result**: Empty list accepted
    - **Observed result**: ✅ Pass - Empty bookmarks accepted

46. **test_user_response_with_bookmarks**
    - **Brief description**: Tests UserResponse with bookmarks
    - **Expected result**: Bookmarks included in response
    - **Observed result**: ✅ Pass - Bookmarks included correctly

#### Test Class: `TestTokenResponse`

47. **test_token_response_valid_data**
    - **Brief description**: Tests TokenResponse with valid data
    - **Expected result**: Schema accepts valid data
    - **Observed result**: ✅ Pass - Valid token response accepted

48. **test_token_response_missing_access_token**
    - **Brief description**: Tests TokenResponse without access_token
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Missing token rejected

49. **test_token_response_missing_token_type**
    - **Brief description**: Tests TokenResponse without token_type
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Missing token_type rejected

50. **test_token_response_missing_user**
    - **Brief description**: Tests TokenResponse without user
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Missing user rejected

51. **test_token_response_different_token_types**
    - **Brief description**: Tests TokenResponse with different token types
    - **Expected result**: All token types accepted
    - **Observed result**: ✅ Pass - Different token types accepted

---

### Test File: `test_bookmark_schemas.py`

#### Test Class: `TestBookmarkBase`

52. **test_bookmark_base_valid_data**
    - **Brief description**: Tests BookmarkBase with all required fields
    - **Expected result**: Schema accepts valid data
    - **Observed result**: ✅ Pass - Valid bookmark data accepted

53. **test_bookmark_base_with_optional_fields**
    - **Brief description**: Tests BookmarkBase with optional fields
    - **Expected result**: Optional fields accepted
    - **Observed result**: ✅ Pass - Optional fields work

54. **test_bookmark_base_missing_title**
    - **Brief description**: Tests BookmarkBase without title
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Missing title rejected

55. **test_bookmark_base_missing_address**
    - **Brief description**: Tests BookmarkBase without address
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Missing address rejected

56. **test_bookmark_base_missing_latitude**
    - **Brief description**: Tests BookmarkBase without latitude
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Missing latitude rejected

57. **test_bookmark_base_missing_longitude**
    - **Brief description**: Tests BookmarkBase without longitude
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Missing longitude rejected

58. **test_bookmark_base_empty_strings**
    - **Brief description**: Tests BookmarkBase with empty strings
    - **Expected result**: Empty strings accepted
    - **Observed result**: ✅ Pass - Empty strings accepted

59. **test_bookmark_base_extreme_coordinates**
    - **Brief description**: Tests BookmarkBase with extreme coordinates
    - **Expected result**: Extreme coordinates accepted
    - **Observed result**: ✅ Pass - Extreme coordinates accepted

#### Test Class: `TestBookmarkCreate`

60. **test_bookmark_create_valid_data**
    - **Brief description**: Tests BookmarkCreate with valid data
    - **Expected result**: Schema accepts valid data
    - **Observed result**: ✅ Pass - Valid create data accepted

61. **test_bookmark_create_inherits_from_base**
    - **Brief description**: Tests that BookmarkCreate inherits from BookmarkBase
    - **Expected result**: Has all base fields
    - **Observed result**: ✅ Pass - Inheritance works correctly

62. **test_bookmark_create_with_optional_fields**
    - **Brief description**: Tests BookmarkCreate with optional fields
    - **Expected result**: Optional fields accepted
    - **Observed result**: ✅ Pass - Optional fields work

#### Test Class: `TestBookmarkResponse`

63. **test_bookmark_response_valid_data**
    - **Brief description**: Tests BookmarkResponse with valid data
    - **Expected result**: Schema accepts valid data
    - **Observed result**: ✅ Pass - Valid response data accepted

64. **test_bookmark_response_missing_id**
    - **Brief description**: Tests BookmarkResponse without id
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Missing id rejected

65. **test_bookmark_response_with_optional_fields**
    - **Brief description**: Tests BookmarkResponse with optional fields
    - **Expected result**: Optional fields accepted
    - **Observed result**: ✅ Pass - Optional fields work

66. **test_bookmark_response_different_id_types**
    - **Brief description**: Tests BookmarkResponse with different id values
    - **Expected result**: All id values accepted
    - **Observed result**: ✅ Pass - Different ids accepted

67. **test_bookmark_response_float_coordinates**
    - **Brief description**: Tests BookmarkResponse with precise float coordinates
    - **Expected result**: Precise coordinates accepted
    - **Observed result**: ✅ Pass - Precise coordinates work

---

### Test File: `test_generated_route_schemas.py`

#### Test Class: `TestGeneratedRouteCreate`

68. **test_generated_route_create_valid_data**
    - **Brief description**: Tests GeneratedRouteCreate with valid route text
    - **Expected result**: Schema accepts valid data
    - **Observed result**: ✅ Pass - Valid route text accepted

69. **test_generated_route_create_empty_string**
    - **Brief description**: Tests GeneratedRouteCreate with empty string
    - **Expected result**: Empty string accepted
    - **Observed result**: ✅ Pass - Empty string accepted

70. **test_generated_route_create_missing_route_text**
    - **Brief description**: Tests GeneratedRouteCreate without route_text
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Missing route_text rejected

71. **test_generated_route_create_long_text**
    - **Brief description**: Tests GeneratedRouteCreate with very long text
    - **Expected result**: Long text accepted
    - **Observed result**: ✅ Pass - Long text accepted

72. **test_generated_route_create_multiline_text**
    - **Brief description**: Tests GeneratedRouteCreate with multiline text
    - **Expected result**: Multiline text accepted
    - **Observed result**: ✅ Pass - Multiline text accepted

73. **test_generated_route_create_special_characters**
    - **Brief description**: Tests GeneratedRouteCreate with special characters
    - **Expected result**: Special characters accepted
    - **Observed result**: ✅ Pass - Special characters accepted

74. **test_generated_route_create_unicode_characters**
    - **Brief description**: Tests GeneratedRouteCreate with unicode characters
    - **Expected result**: Unicode characters accepted
    - **Observed result**: ✅ Pass - Unicode characters accepted

75. **test_generated_route_create_whitespace_only**
    - **Brief description**: Tests GeneratedRouteCreate with whitespace only
    - **Expected result**: Whitespace accepted
    - **Observed result**: ✅ Pass - Whitespace accepted

#### Test Class: `TestGeneratedRouteResponse`

76. **test_generated_route_response_valid_data**
    - **Brief description**: Tests GeneratedRouteResponse with valid data
    - **Expected result**: Schema accepts valid data
    - **Observed result**: ✅ Pass - Valid response data accepted

77. **test_generated_route_response_missing_id**
    - **Brief description**: Tests GeneratedRouteResponse without id
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Missing id rejected

78. **test_generated_route_response_missing_user_id**
    - **Brief description**: Tests GeneratedRouteResponse without user_id
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Missing user_id rejected

79. **test_generated_route_response_missing_route_text**
    - **Brief description**: Tests GeneratedRouteResponse without route_text
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Missing route_text rejected

80. **test_generated_route_response_missing_created_at**
    - **Brief description**: Tests GeneratedRouteResponse without created_at
    - **Expected result**: Raises ValidationError
    - **Observed result**: ✅ Pass - Missing created_at rejected

81. **test_generated_route_response_different_datetime_formats**
    - **Brief description**: Tests GeneratedRouteResponse with different datetime values
    - **Expected result**: All datetime values accepted
    - **Observed result**: ✅ Pass - Different datetimes accepted

82. **test_generated_route_response_different_user_ids**
    - **Brief description**: Tests GeneratedRouteResponse with different user_id values
    - **Expected result**: All user_id values accepted
    - **Observed result**: ✅ Pass - Different user_ids accepted

83. **test_generated_route_response_different_ids**
    - **Brief description**: Tests GeneratedRouteResponse with different id values
    - **Expected result**: All id values accepted
    - **Observed result**: ✅ Pass - Different ids accepted

84. **test_generated_route_response_empty_route_text**
    - **Brief description**: Tests GeneratedRouteResponse with empty route_text
    - **Expected result**: Empty route_text accepted
    - **Observed result**: ✅ Pass - Empty route_text accepted

---

## Summary

### Test Statistics

- **Total Test Files**: 5
- **Total Test Cases**: 84
- **All Tests Status**: ✅ **ALL PASSED** (84/84)
- **Test Coverage Areas**:
  - Password hashing utilities: 13 tests
  - JWT token utilities: 15 tests
  - User schemas: 23 tests
  - Bookmark schemas: 16 tests
  - Generated route schemas: 17 tests

### Test Results Summary

**All 84 test cases passed successfully.** The test suite covers:

1. **Core Utilities (28 tests)**: Password hashing and JWT token management are thoroughly tested with various edge cases including empty strings, special characters, long inputs, and security properties.

2. **Schema Validation (56 tests)**: All Pydantic schemas are tested for:
   - Valid data acceptance
   - Invalid data rejection
   - Required field validation
   - Optional field handling
   - Edge cases (empty strings, extreme values, unicode)

### Key Findings

1. **Password Security**: Bcrypt implementation correctly uses salt, ensuring different hashes for the same password, which is a security best practice. All password hashing and verification tests pass successfully.

2. **Token Management**: JWT token creation and verification work correctly. Token expiration is tested by verifying the presence of the "exp" claim rather than exact time comparisons to avoid non-deterministic behavior.

3. **Data Validation**: All Pydantic schemas properly validate input data, rejecting invalid formats (especially email validation) and missing required fields. All schema validation tests pass.

4. **Edge Cases**: The test suite covers various edge cases including empty strings, special characters, unicode, extreme coordinate values, and long text inputs. All edge case tests pass successfully.

   

### Conclusion

The test suite provides comprehensive coverage of utility functions and schema validation, ensuring that core functionality works correctly and data validation is robust. All 84 tests pass successfully. The tests are deterministic, fast, and do not require external dependencies or third-party API calls, making them ideal for continuous integration and development workflows.

**Test Execution Results:**

- ✅ 84 tests passed
- ⚠️ 4 warnings (related to Pydantic V2 deprecation warnings in schema configurations - non-critical)
- ⏱️ Execution time: ~8-9 seconds
- 🚫 No test failures
- 🚫 No third-party API calls (cost-free testing)

