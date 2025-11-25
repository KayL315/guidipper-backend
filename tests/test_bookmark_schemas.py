"""
Test cases for bookmark schemas validation.
Tests Pydantic schema validation for BookmarkBase, BookmarkCreate, and BookmarkResponse.
"""
import pytest
from pydantic import ValidationError
from app.schemas.bookmark import BookmarkBase, BookmarkCreate, BookmarkResponse


class TestBookmarkBase:
    """Test cases for BookmarkBase schema"""
    
    def test_bookmark_base_valid_data(self):
        """Test BookmarkBase with all required fields"""
        bookmark = BookmarkBase(
            title="Test Location",
            address="123 Main St",
            latitude=40.7128,
            longitude=-74.0060
        )
        assert bookmark.title == "Test Location"
        assert bookmark.address == "123 Main St"
        assert bookmark.latitude == 40.7128
        assert bookmark.longitude == -74.0060
    
    def test_bookmark_base_with_optional_fields(self):
        """Test BookmarkBase with optional category and google_maps_url"""
        bookmark = BookmarkBase(
            title="Test Location",
            address="123 Main St",
            latitude=40.7128,
            longitude=-74.0060,
            category="restaurant",
            google_maps_url="https://maps.google.com/?q=123+Main+St"
        )
        assert bookmark.category == "restaurant"
        assert bookmark.google_maps_url == "https://maps.google.com/?q=123+Main+St"
    
    def test_bookmark_base_missing_title(self):
        """Test BookmarkBase without title"""
        with pytest.raises(ValidationError):
            BookmarkBase(
                address="123 Main St",
                latitude=40.7128,
                longitude=-74.0060
            )
    
    def test_bookmark_base_missing_address(self):
        """Test BookmarkBase without address"""
        with pytest.raises(ValidationError):
            BookmarkBase(
                title="Test Location",
                latitude=40.7128,
                longitude=-74.0060
            )
    
    def test_bookmark_base_missing_latitude(self):
        """Test BookmarkBase without latitude"""
        with pytest.raises(ValidationError):
            BookmarkBase(
                title="Test Location",
                address="123 Main St",
                longitude=-74.0060
            )
    
    def test_bookmark_base_missing_longitude(self):
        """Test BookmarkBase without longitude"""
        with pytest.raises(ValidationError):
            BookmarkBase(
                title="Test Location",
                address="123 Main St",
                latitude=40.7128
            )
    
    def test_bookmark_base_empty_strings(self):
        """Test BookmarkBase with empty strings"""
        bookmark = BookmarkBase(
            title="",
            address="",
            latitude=0.0,
            longitude=0.0
        )
        assert bookmark.title == ""
        assert bookmark.address == ""
    
    def test_bookmark_base_extreme_coordinates(self):
        """Test BookmarkBase with extreme coordinate values"""
        bookmark = BookmarkBase(
            title="North Pole",
            address="Arctic",
            latitude=90.0,
            longitude=0.0
        )
        assert bookmark.latitude == 90.0
        
        bookmark2 = BookmarkBase(
            title="South Pole",
            address="Antarctica",
            latitude=-90.0,
            longitude=180.0
        )
        assert bookmark2.latitude == -90.0
        assert bookmark2.longitude == 180.0


class TestBookmarkCreate:
    """Test cases for BookmarkCreate schema"""
    
    def test_bookmark_create_valid_data(self):
        """Test BookmarkCreate with valid data"""
        bookmark = BookmarkCreate(
            title="New Location",
            address="456 Oak Ave",
            latitude=34.0522,
            longitude=-118.2437
        )
        assert bookmark.title == "New Location"
        assert bookmark.address == "456 Oak Ave"
        assert bookmark.latitude == 34.0522
        assert bookmark.longitude == -118.2437
    
    def test_bookmark_create_inherits_from_base(self):
        """Test that BookmarkCreate has all BookmarkBase fields"""
        bookmark = BookmarkCreate(
            title="Test",
            address="Test Address",
            latitude=0.0,
            longitude=0.0,
            category="test",
            google_maps_url="https://test.com"
        )
        assert bookmark.category == "test"
        assert bookmark.google_maps_url == "https://test.com"
    
    def test_bookmark_create_with_optional_fields(self):
        """Test BookmarkCreate with optional fields"""
        bookmark = BookmarkCreate(
            title="Restaurant",
            address="789 Food St",
            latitude=25.7617,
            longitude=-80.1918,
            category="dining",
            google_maps_url="https://maps.google.com"
        )
        assert bookmark.category == "dining"


class TestBookmarkResponse:
    """Test cases for BookmarkResponse schema"""
    
    def test_bookmark_response_valid_data(self):
        """Test BookmarkResponse with valid data"""
        bookmark = BookmarkResponse(
            id=1,
            title="Saved Location",
            address="321 Pine St",
            latitude=41.8781,
            longitude=-87.6298
        )
        assert bookmark.id == 1
        assert bookmark.title == "Saved Location"
        assert bookmark.address == "321 Pine St"
        assert bookmark.latitude == 41.8781
        assert bookmark.longitude == -87.6298
    
    def test_bookmark_response_missing_id(self):
        """Test BookmarkResponse without id"""
        with pytest.raises(ValidationError):
            BookmarkResponse(
                title="Test",
                address="Test Address",
                latitude=0.0,
                longitude=0.0
            )
    
    def test_bookmark_response_with_optional_fields(self):
        """Test BookmarkResponse with optional fields"""
        bookmark = BookmarkResponse(
            id=5,
            title="Museum",
            address="100 Art Blvd",
            latitude=37.7749,
            longitude=-122.4194,
            category="attraction",
            google_maps_url="https://maps.google.com/museum"
        )
        assert bookmark.id == 5
        assert bookmark.category == "attraction"
    
    def test_bookmark_response_different_id_types(self):
        """Test BookmarkResponse with different id values"""
        for bookmark_id in [1, 100, 9999, 0]:
            bookmark = BookmarkResponse(
                id=bookmark_id,
                title="Test",
                address="Test",
                latitude=0.0,
                longitude=0.0
            )
            assert bookmark.id == bookmark_id
    
    def test_bookmark_response_float_coordinates(self):
        """Test BookmarkResponse with precise float coordinates"""
        bookmark = BookmarkResponse(
            id=10,
            title="Precise Location",
            address="Exact Spot",
            latitude=40.712776,
            longitude=-74.005974
        )
        assert bookmark.latitude == 40.712776
        assert bookmark.longitude == -74.005974

