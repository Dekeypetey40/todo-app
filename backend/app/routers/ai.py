"""
AI-powered features router.
"""
import os
from fastapi import APIRouter, HTTPException, Request
from openai import OpenAIError
from ..schemas import AIParseRequest, AIParseResponse
from ..services.ai_service import AITaskParser
from ..config import settings
from ..exceptions import ExternalServiceError
from slowapi import Limiter
from slowapi.util import get_remote_address


router = APIRouter(prefix="/api/ai", tags=["AI"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/parse-task", response_model=AIParseResponse)
@limiter.limit(settings.rate_limit_ai_parse)
async def parse_task(request: Request, parse_request: AIParseRequest):
    """
    Parse natural language task description into structured data using AI.
    
    **Rate Limited:** 10 requests per minute per IP address.
    
    This endpoint uses OpenAI GPT-4o-mini to extract:
    - Task title
    - Description (if provided)
    - Priority level (low/medium/high)
    - Due date (supports relative dates like "tomorrow", "next Friday")
    - Suggested tags based on context
    
    ## Example Input
    ```
    "Buy groceries tomorrow evening high priority"
    ```
    
    ## Example Output
    ```json
    {
        "title": "Buy groceries",
        "description": null,
        "priority": "high",
        "due_date": "2026-01-23",
        "suggested_tags": ["shopping", "personal"]
    }
    ```
    
    Raises:
        - 400: Invalid input
        - 429: Rate limit exceeded
        - 500: OpenAI API not configured
        - 503: OpenAI API unavailable
    """
    # Check if API key is configured
    if not settings.openai_api_key or settings.openai_api_key == "your-api-key-here":
        raise HTTPException(
            status_code=500,
            detail="OpenAI API is not configured. Please add OPENAI_API_KEY to your .env file."
        )
    
    try:
        # Initialize the AI parser
        parser = AITaskParser(api_key=settings.openai_api_key, model=settings.openai_model)
        
        # Parse the task
        result = parser.parse_task(parse_request.text)
        
        # Return the structured response
        return AIParseResponse(**result)
        
    except ValueError as e:
        # Invalid input or parsing error
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(e)}"
        )
    except OpenAIError as e:
        # OpenAI API error (rate limit, network, etc.)
        raise ExternalServiceError("OpenAI", "Service temporarily unavailable")
    except Exception as e:
        # Unexpected error - log but don't expose details
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"AI parsing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while parsing your task"
        )


@router.get("/health")
async def ai_health_check():
    """
    Check if AI service is properly configured.
    
    Returns:
        Status information about AI service availability
    """
    api_key = os.getenv("OPENAI_API_KEY")
    is_configured = api_key and api_key != "your-api-key-here"
    
    return {
        "ai_enabled": is_configured,
        "model": "gpt-4o-mini",
        "message": "AI service is configured" if is_configured else "OpenAI API key not configured"
    }
