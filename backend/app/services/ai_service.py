"""
AI service for natural language task parsing using OpenAI.
"""
import json
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from openai import OpenAI, OpenAIError


class AITaskParser:
    """
    Natural language task parser using OpenAI GPT-4o-mini.
    
    Extracts structured task data from conversational input.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize the AI task parser.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-4o-mini for cost efficiency)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def parse_task(self, user_input: str) -> Dict:
        """
        Parse natural language input into structured task data.
        
        Args:
            user_input: Natural language task description
            
        Returns:
            Dictionary containing:
                - title: str (required)
                - description: Optional[str]
                - priority: str (low/medium/high)
                - due_date: Optional[str] (YYYY-MM-DD format)
                - suggested_tags: List[str]
                
        Raises:
            ValueError: If input is empty or invalid
            OpenAIError: If API call fails
        """
        if not user_input or not user_input.strip():
            raise ValueError("Task input cannot be empty")
        
        today = datetime.now().date()
        
        # Construct the prompt
        system_message = (
            "You are a task parsing assistant that extracts structured data "
            "from natural language task descriptions. Always respond with valid JSON."
        )
        
        user_message = f"""Parse this task: "{user_input.strip()}"

Today's date: {today.isoformat()}

Extract and return ONLY valid JSON with this exact structure:
{{
  "title": "concise task title (50 chars max)",
  "description": "optional details if provided or null",
  "priority": "low|medium|high",
  "due_date": "YYYY-MM-DD or null",
  "suggested_tags": ["tag1", "tag2"]
}}

Rules:
- Parse relative dates (tomorrow, next week, Friday, etc.) to absolute dates
- Infer priority from words like "urgent", "important", "high priority", "asap"
- Default priority: "medium" if not specified
- Extract implicit categories/contexts as suggested tags (e.g., "work", "personal", "home")
- Keep title concise and actionable
- If description can be inferred from context, include it briefly
- Return empty array for suggested_tags if none are obvious
"""
        
        try:
            # Call OpenAI API with JSON mode
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,  # Lower temperature for consistent, predictable results
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            result = json.loads(response.choices[0].message.content)
            
            # Validate and normalize the response
            normalized_result = self._validate_and_normalize(result)
            
            return normalized_result
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
        except OpenAIError as e:
            raise OpenAIError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error during task parsing: {str(e)}")
    
    def _validate_and_normalize(self, result: Dict) -> Dict:
        """
        Validate and normalize the AI response.
        
        Args:
            result: Raw AI response dictionary
            
        Returns:
            Validated and normalized dictionary
        """
        # Ensure required fields exist
        if 'title' not in result or not result['title']:
            raise ValueError("AI response missing required 'title' field")
        
        # Normalize the result
        normalized = {
            'title': str(result['title']).strip()[:200],  # Enforce max length
            'description': str(result.get('description', '')).strip() if result.get('description') else None,
            'priority': self._validate_priority(result.get('priority', 'medium')),
            'due_date': self._validate_date(result.get('due_date')),
            'suggested_tags': self._validate_tags(result.get('suggested_tags', []))
        }
        
        return normalized
    
    def _validate_priority(self, priority: str) -> str:
        """
        Validate and normalize priority value.
        
        Args:
            priority: Priority string from AI
            
        Returns:
            Valid priority (low/medium/high)
        """
        valid_priorities = ['low', 'medium', 'high']
        normalized = str(priority).lower().strip()
        
        if normalized in valid_priorities:
            return normalized
        
        # Default to medium if invalid
        return 'medium'
    
    def _validate_date(self, date_str: Optional[str]) -> Optional[str]:
        """
        Validate date format.
        
        Args:
            date_str: Date string from AI (YYYY-MM-DD or None)
            
        Returns:
            Valid date string or None
        """
        if not date_str or date_str == 'null':
            return None
        
        try:
            # Validate date format
            datetime.strptime(str(date_str), '%Y-%m-%d')
            return str(date_str)
        except ValueError:
            # Invalid date format, return None
            return None
    
    def _validate_tags(self, tags: List) -> List[str]:
        """
        Validate and normalize tag list.
        
        Args:
            tags: List of tag names from AI
            
        Returns:
            List of valid, normalized tag names
        """
        if not isinstance(tags, list):
            return []
        
        # Normalize tags: lowercase, strip whitespace, limit length
        normalized_tags = []
        for tag in tags:
            if isinstance(tag, str) and tag.strip():
                normalized_tag = tag.strip().lower()[:50]
                if normalized_tag and normalized_tag not in normalized_tags:
                    normalized_tags.append(normalized_tag)
        
        return normalized_tags[:5]  # Limit to 5 tags max
