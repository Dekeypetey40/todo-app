"""
Tests for AI task parsing endpoint.
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestAIParseTask:
    """Tests for the AI task parsing endpoint."""
    
    @patch('app.routers.ai.os.getenv')
    @patch('app.routers.ai.AITaskParser')
    def test_parse_task_success(self, mock_parser_class, mock_getenv):
        """Test successful task parsing with AI."""
        # Setup mocks
        mock_getenv.return_value = "test-api-key"
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_task.return_value = {
            'title': 'Buy groceries',
            'description': 'Get milk and bread',
            'priority': 'high',
            'due_date': '2026-01-23',
            'suggested_tags': ['shopping', 'personal']
        }
        
        # Make request
        response = client.post(
            '/api/ai/parse-task',
            json={'text': 'Buy groceries tomorrow high priority'}
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data['title'] == 'Buy groceries'
        assert data['description'] == 'Get milk and bread'
        assert data['priority'] == 'high'
        assert data['due_date'] == '2026-01-23'
        assert data['suggested_tags'] == ['shopping', 'personal']
        
        # Verify parser was called correctly
        mock_parser.parse_task.assert_called_once_with('Buy groceries tomorrow high priority')
    
    @patch('app.routers.ai.os.getenv')
    def test_parse_task_no_api_key(self, mock_getenv):
        """Test parsing fails when API key is not configured."""
        mock_getenv.return_value = None
        
        response = client.post(
            '/api/ai/parse-task',
            json={'text': 'Buy groceries tomorrow'}
        )
        
        assert response.status_code == 500
        assert 'not configured' in response.json()['detail'].lower()
    
    @patch('app.routers.ai.os.getenv')
    def test_parse_task_placeholder_api_key(self, mock_getenv):
        """Test parsing fails when API key is still the placeholder."""
        mock_getenv.return_value = "your-api-key-here"
        
        response = client.post(
            '/api/ai/parse-task',
            json={'text': 'Buy groceries tomorrow'}
        )
        
        assert response.status_code == 500
        assert 'not configured' in response.json()['detail'].lower()
    
    def test_parse_task_empty_text(self):
        """Test parsing fails with empty input."""
        response = client.post(
            '/api/ai/parse-task',
            json={'text': ''}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_parse_task_whitespace_only(self):
        """Test parsing fails with whitespace-only input."""
        response = client.post(
            '/api/ai/parse-task',
            json={'text': '   '}
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('app.routers.ai.os.getenv')
    @patch('app.routers.ai.AITaskParser')
    def test_parse_task_value_error(self, mock_parser_class, mock_getenv):
        """Test handling of ValueError from parser."""
        mock_getenv.return_value = "test-api-key"
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_task.side_effect = ValueError("Invalid input format")
        
        response = client.post(
            '/api/ai/parse-task',
            json={'text': 'Invalid input'}
        )
        
        assert response.status_code == 400
        assert 'invalid input' in response.json()['detail'].lower()
    
    @patch('app.routers.ai.os.getenv')
    @patch('app.routers.ai.AITaskParser')
    def test_parse_task_openai_error(self, mock_parser_class, mock_getenv):
        """Test handling of OpenAI API errors."""
        from openai import OpenAIError
        
        mock_getenv.return_value = "test-api-key"
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_task.side_effect = OpenAIError("API rate limit exceeded")
        
        response = client.post(
            '/api/ai/parse-task',
            json={'text': 'Buy groceries'}
        )
        
        assert response.status_code == 503
        assert 'unavailable' in response.json()['detail'].lower()
    
    @patch('app.routers.ai.os.getenv')
    @patch('app.routers.ai.AITaskParser')
    def test_parse_task_unexpected_error(self, mock_parser_class, mock_getenv):
        """Test handling of unexpected errors."""
        mock_getenv.return_value = "test-api-key"
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_task.side_effect = Exception("Unexpected error")
        
        response = client.post(
            '/api/ai/parse-task',
            json={'text': 'Buy groceries'}
        )
        
        assert response.status_code == 500
        assert 'unexpected error' in response.json()['detail'].lower()
    
    def test_parse_task_long_text(self):
        """Test parsing with text at maximum length."""
        long_text = 'a' * 500
        
        response = client.post(
            '/api/ai/parse-task',
            json={'text': long_text}
        )
        
        # Should pass validation (500 is the max)
        assert response.status_code in [200, 500, 503]  # Depends on API key config
    
    def test_parse_task_too_long_text(self):
        """Test parsing fails with text exceeding maximum length."""
        too_long_text = 'a' * 501
        
        response = client.post(
            '/api/ai/parse-task',
            json={'text': too_long_text}
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('app.routers.ai.os.getenv')
    @patch('app.routers.ai.AITaskParser')
    def test_parse_task_minimal_response(self, mock_parser_class, mock_getenv):
        """Test parsing with minimal AI response (only required fields)."""
        mock_getenv.return_value = "test-api-key"
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_task.return_value = {
            'title': 'Call mom',
            'description': None,
            'priority': 'medium',
            'due_date': None,
            'suggested_tags': []
        }
        
        response = client.post(
            '/api/ai/parse-task',
            json={'text': 'Call mom'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['title'] == 'Call mom'
        assert data['description'] is None
        assert data['priority'] == 'medium'
        assert data['due_date'] is None
        assert data['suggested_tags'] == []


class TestAIHealthCheck:
    """Tests for the AI health check endpoint."""
    
    @patch('app.routers.ai.os.getenv')
    def test_health_check_configured(self, mock_getenv):
        """Test health check when AI is configured."""
        mock_getenv.return_value = "test-api-key"
        
        response = client.get('/api/ai/health')
        
        assert response.status_code == 200
        data = response.json()
        assert data['ai_enabled'] is True
        assert data['model'] == 'gpt-4o-mini'
        assert 'configured' in data['message'].lower()
    
    @patch('app.routers.ai.os.getenv')
    def test_health_check_not_configured(self, mock_getenv):
        """Test health check when AI is not configured."""
        mock_getenv.return_value = None
        
        response = client.get('/api/ai/health')
        
        assert response.status_code == 200
        data = response.json()
        assert data['ai_enabled'] is False
        assert 'not configured' in data['message'].lower()
    
    @patch('app.routers.ai.os.getenv')
    def test_health_check_placeholder_key(self, mock_getenv):
        """Test health check with placeholder API key."""
        mock_getenv.return_value = "your-api-key-here"
        
        response = client.get('/api/ai/health')
        
        assert response.status_code == 200
        data = response.json()
        assert data['ai_enabled'] is False
        assert 'not configured' in data['message'].lower()


class TestAIServiceUnit:
    """Unit tests for the AITaskParser service."""
    
    def test_parser_initialization(self):
        """Test AITaskParser initialization."""
        from app.services.ai_service import AITaskParser
        
        parser = AITaskParser(api_key="test-key", model="gpt-4o-mini")
        assert parser.model == "gpt-4o-mini"
    
    def test_parser_empty_input(self):
        """Test parser rejects empty input."""
        from app.services.ai_service import AITaskParser
        
        parser = AITaskParser(api_key="test-key")
        
        with pytest.raises(ValueError, match="cannot be empty"):
            parser.parse_task("")
    
    def test_parser_whitespace_input(self):
        """Test parser rejects whitespace-only input."""
        from app.services.ai_service import AITaskParser
        
        parser = AITaskParser(api_key="test-key")
        
        with pytest.raises(ValueError, match="cannot be empty"):
            parser.parse_task("   ")
    
    def test_validate_priority_valid(self):
        """Test priority validation with valid values."""
        from app.services.ai_service import AITaskParser
        
        parser = AITaskParser(api_key="test-key")
        
        assert parser._validate_priority("low") == "low"
        assert parser._validate_priority("medium") == "medium"
        assert parser._validate_priority("high") == "high"
        assert parser._validate_priority("HIGH") == "high"  # Case insensitive
    
    def test_validate_priority_invalid(self):
        """Test priority validation with invalid values defaults to medium."""
        from app.services.ai_service import AITaskParser
        
        parser = AITaskParser(api_key="test-key")
        
        assert parser._validate_priority("urgent") == "medium"
        assert parser._validate_priority("invalid") == "medium"
        assert parser._validate_priority("") == "medium"
    
    def test_validate_date_valid(self):
        """Test date validation with valid dates."""
        from app.services.ai_service import AITaskParser
        
        parser = AITaskParser(api_key="test-key")
        
        assert parser._validate_date("2026-01-23") == "2026-01-23"
        assert parser._validate_date("2026-12-31") == "2026-12-31"
    
    def test_validate_date_invalid(self):
        """Test date validation with invalid dates returns None."""
        from app.services.ai_service import AITaskParser
        
        parser = AITaskParser(api_key="test-key")
        
        assert parser._validate_date("invalid-date") is None
        assert parser._validate_date("2026-13-01") is None  # Invalid month
        assert parser._validate_date("2026-01-32") is None  # Invalid day
        assert parser._validate_date(None) is None
        assert parser._validate_date("null") is None
    
    def test_validate_tags_valid(self):
        """Test tag validation with valid tags."""
        from app.services.ai_service import AITaskParser
        
        parser = AITaskParser(api_key="test-key")
        
        tags = parser._validate_tags(["work", "urgent", "project"])
        assert tags == ["work", "urgent", "project"]
    
    def test_validate_tags_normalization(self):
        """Test tag normalization (lowercase, trim)."""
        from app.services.ai_service import AITaskParser
        
        parser = AITaskParser(api_key="test-key")
        
        tags = parser._validate_tags(["Work", " URGENT ", "Project"])
        assert tags == ["work", "urgent", "project"]
    
    def test_validate_tags_duplicates(self):
        """Test tag validation removes duplicates."""
        from app.services.ai_service import AITaskParser
        
        parser = AITaskParser(api_key="test-key")
        
        tags = parser._validate_tags(["work", "work", "urgent"])
        assert tags == ["work", "urgent"]
    
    def test_validate_tags_max_limit(self):
        """Test tag validation limits to 5 tags."""
        from app.services.ai_service import AITaskParser
        
        parser = AITaskParser(api_key="test-key")
        
        tags = parser._validate_tags(["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7"])
        assert len(tags) == 5
        assert tags == ["tag1", "tag2", "tag3", "tag4", "tag5"]
    
    def test_validate_tags_empty_and_invalid(self):
        """Test tag validation filters out empty/invalid tags."""
        from app.services.ai_service import AITaskParser
        
        parser = AITaskParser(api_key="test-key")
        
        tags = parser._validate_tags(["work", "", "  ", "urgent", None, 123])
        assert tags == ["work", "urgent"]
    
    def test_validate_tags_non_list(self):
        """Test tag validation with non-list input returns empty list."""
        from app.services.ai_service import AITaskParser
        
        parser = AITaskParser(api_key="test-key")
        
        assert parser._validate_tags("not a list") == []
        assert parser._validate_tags(None) == []
        assert parser._validate_tags(123) == []
