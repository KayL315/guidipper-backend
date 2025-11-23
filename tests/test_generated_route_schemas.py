"""
Test cases for generated route schemas validation.
Tests Pydantic schema validation for GeneratedRouteCreate and GeneratedRouteResponse.
"""
import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.generated_route import GeneratedRouteCreate, GeneratedRouteResponse


class TestGeneratedRouteCreate:
    """Test cases for GeneratedRouteCreate schema"""
    
    def test_generated_route_create_valid_data(self):
        """Test GeneratedRouteCreate with valid route text"""
        route = GeneratedRouteCreate(route_text="Day 1: Visit museum, Day 2: Go to park")
        assert route.route_text == "Day 1: Visit museum, Day 2: Go to park"
    
    def test_generated_route_create_empty_string(self):
        """Test GeneratedRouteCreate with empty string"""
        route = GeneratedRouteCreate(route_text="")
        assert route.route_text == ""
    
    def test_generated_route_create_missing_route_text(self):
        """Test GeneratedRouteCreate without route_text field"""
        with pytest.raises(ValidationError):
            GeneratedRouteCreate()
    
    def test_generated_route_create_long_text(self):
        """Test GeneratedRouteCreate with very long text"""
        long_text = "Day 1: " + "Visit location " * 100
        route = GeneratedRouteCreate(route_text=long_text)
        assert len(route.route_text) > 1000
        assert route.route_text.startswith("Day 1:")
    
    def test_generated_route_create_multiline_text(self):
        """Test GeneratedRouteCreate with multiline text"""
        multiline_text = """Day 1: Morning - Breakfast
Afternoon - Museum
Evening - Dinner

Day 2: Morning - Park
Afternoon - Shopping"""
        route = GeneratedRouteCreate(route_text=multiline_text)
        assert "\n" in route.route_text
        assert "Day 1:" in route.route_text
        assert "Day 2:" in route.route_text
    
    def test_generated_route_create_special_characters(self):
        """Test GeneratedRouteCreate with special characters"""
        special_text = "Route: Café → Park (10:00-12:00) & Museum [Free]"
        route = GeneratedRouteCreate(route_text=special_text)
        assert route.route_text == special_text
    
    def test_generated_route_create_unicode_characters(self):
        """Test GeneratedRouteCreate with unicode characters"""
        unicode_text = "路线：第一天参观博物馆，第二天去公园"
        route = GeneratedRouteCreate(route_text=unicode_text)
        assert route.route_text == unicode_text
    
    def test_generated_route_create_whitespace_only(self):
        """Test GeneratedRouteCreate with whitespace only"""
        route = GeneratedRouteCreate(route_text="   \n\t   ")
        assert route.route_text == "   \n\t   "


class TestGeneratedRouteResponse:
    """Test cases for GeneratedRouteResponse schema"""
    
    def test_generated_route_response_valid_data(self):
        """Test GeneratedRouteResponse with valid data"""
        now = datetime.utcnow()
        route = GeneratedRouteResponse(
            id=1,
            user_id=123,
            route_text="Day 1: Visit museum",
            created_at=now
        )
        assert route.id == 1
        assert route.user_id == 123
        assert route.route_text == "Day 1: Visit museum"
        assert route.created_at == now
    
    def test_generated_route_response_missing_id(self):
        """Test GeneratedRouteResponse without id"""
        with pytest.raises(ValidationError):
            GeneratedRouteResponse(
                user_id=123,
                route_text="Test route",
                created_at=datetime.utcnow()
            )
    
    def test_generated_route_response_missing_user_id(self):
        """Test GeneratedRouteResponse without user_id"""
        with pytest.raises(ValidationError):
            GeneratedRouteResponse(
                id=1,
                route_text="Test route",
                created_at=datetime.utcnow()
            )
    
    def test_generated_route_response_missing_route_text(self):
        """Test GeneratedRouteResponse without route_text"""
        with pytest.raises(ValidationError):
            GeneratedRouteResponse(
                id=1,
                user_id=123,
                created_at=datetime.utcnow()
            )
    
    def test_generated_route_response_missing_created_at(self):
        """Test GeneratedRouteResponse without created_at"""
        with pytest.raises(ValidationError):
            GeneratedRouteResponse(
                id=1,
                user_id=123,
                route_text="Test route"
            )
    
    def test_generated_route_response_different_datetime_formats(self):
        """Test GeneratedRouteResponse with different datetime values"""
        datetimes = [
            datetime(2024, 1, 1, 12, 0, 0),
            datetime(2024, 12, 31, 23, 59, 59),
            datetime(2020, 6, 15, 0, 0, 0),
            datetime.utcnow()
        ]
        for dt in datetimes:
            route = GeneratedRouteResponse(
                id=1,
                user_id=123,
                route_text="Test",
                created_at=dt
            )
            assert route.created_at == dt
    
    def test_generated_route_response_different_user_ids(self):
        """Test GeneratedRouteResponse with different user_id values"""
        for user_id in [1, 100, 9999, 0]:
            route = GeneratedRouteResponse(
                id=1,
                user_id=user_id,
                route_text="Test route",
                created_at=datetime.utcnow()
            )
            assert route.user_id == user_id
    
    def test_generated_route_response_different_ids(self):
        """Test GeneratedRouteResponse with different id values"""
        for route_id in [1, 100, 9999]:
            route = GeneratedRouteResponse(
                id=route_id,
                user_id=123,
                route_text="Test route",
                created_at=datetime.utcnow()
            )
            assert route.id == route_id
    
    def test_generated_route_response_empty_route_text(self):
        """Test GeneratedRouteResponse with empty route_text"""
        route = GeneratedRouteResponse(
            id=1,
            user_id=123,
            route_text="",
            created_at=datetime.utcnow()
        )
        assert route.route_text == ""

