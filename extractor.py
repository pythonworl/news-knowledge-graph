"""
Apple Pie Recipe
1. Preheat oven to 425 degrees F (220 degrees C).
2. Melt butter in a saucepan. Stir in flour to form a paste. Add water, white sugar, and brown sugar, and bring to a boil. Reduce temperature and let simmer.
3. Place the bottom crust in your pan. Fill with apples, mounded slightly. Cover with a lattice work crust. Gently pour the sugar and butter liquid over the crust. Pour slowly so that it does not run off.
4. Bake 15 minutes in the preheated oven. Reduce the temperature to 350 degrees F (175 degrees C). Continue baking for 35 to 45 minutes, until apples are soft.
"""

import os
import json
from google import genai
from google.genai import types
from models import ExtractionResult, Person, Relationship

# Ensure you have set the GEMINI_API_KEY environment variable.
# For example: os.environ["GEMINI_API_KEY"] = "your_key"

def extract_knowledge(article_text: str, article_url: str) -> ExtractionResult:
    """
    Extracts people and relationships from article text using Gemini.
    """
    client = genai.Client()
    
    prompt = f"""
    You are an expert entity resolution and knowledge extraction AI.
    Read the following news article and extract:
    1. People mentioned in the article, including the author. Use their full canonical name as ID (e.g. "Sam Altman" instead of "Altman").
    2. Relationships between these people. This must be a directed edge (source, target) with a relationship type, a short explanation, and a quote/sentence from the text that proves it.
    
    Article URL for provenance: {article_url}
    
    Article Text:
    {article_text}
    """
    
    # Define the response schema explicitly to match ExtractionResult
    # For google-genai, we use `response_schema`.
    
    schema = {
        "type": "OBJECT",
        "properties": {
            "people": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "id": {"type": "STRING", "description": "Canonical full name of the person"},
                        "name": {"type": "STRING", "description": "Display name of the person"}
                    },
                    "required": ["id", "name"]
                }
            },
            "relationships": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "source": {"type": "STRING", "description": "ID of the source person"},
                        "target": {"type": "STRING", "description": "ID of the target person"},
                        "type": {"type": "STRING", "description": "Short relationship type (e.g. 'criticizes', 'partners with')"},
                        "explanation": {"type": "STRING", "description": "Short natural language explanation"},
                        "provenance": {"type": "STRING", "description": "Quote or sentence from the article that justifies the relationship"}
                    },
                    "required": ["source", "target", "type", "explanation", "provenance"]
                }
            }
        },
        "required": ["people", "relationships"]
    }

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )
        
        # Parse the JSON response
        data = json.loads(response.text)
        
        people = [Person(**p) for p in data.get("people", [])]
        relationships = [Relationship(**r) for r in data.get("relationships", [])]
        
        return ExtractionResult(people=people, relationships=relationships)
    except Exception as e:
        print(f"Error extracting knowledge: {e}")
        return ExtractionResult(people=[], relationships=[])
