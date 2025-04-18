from openai import OpenAI
import logging
import json
import os
from typing import Dict, List, Any, Optional

logger = logging.getLogger("vocAIyze.LLM")

class LLM:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.knowledge_base = self.load_knowledge_base()
        logger.info("LLM initialized")

    def load_knowledge_base(self) -> dict:
        kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
        try:
            if os.path.exists(kb_path):
                with open(kb_path, 'r') as f:
                    return json.load(f)
            else:
                # Default knowledge base if file doesn't exist
                default_kb = {
                    "finding_leads": "Use LinkedIn and industry events to find potential leads.",
                    "communicating_effectively": "Listen actively and address customer needs.",
                    "converting_leads": "Follow up promptly and provide clear value propositions."
                }
                # Save default knowledge base
                with open(kb_path, 'w') as f:
                    json.dump(default_kb, f, indent=2)
                return default_kb
        except Exception as e:
            logger.error(f"Error loading knowledge base: {str(e)}")
            return {}

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",  # Using the more capable GPT-4 model
                messages=[
                    {"role": "system", "content": "You are an AI assistant for business professionals. Provide helpful, accurate, and concise responses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7,
                n=1,
                stop=None
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"Sorry, I encountered an error while processing your request. Please try again later."

    def analyze_text(self, text: str) -> dict:
        try:
            prompt = f"""Analyze the following text and provide insights on:
            1. Main topics
            2. Sentiment
            3. Key action items (if any)
            
            Text: {text}
            
            Format your response as JSON with keys 'topics', 'sentiment', and 'action_items'.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Try to parse as JSON, but handle plain text responses
            try:
                return json.loads(analysis_text)
            except json.JSONDecodeError:
                # If not valid JSON, return as structured dict
                return {
                    "topics": [analysis_text],
                    "sentiment": "unknown",
                    "action_items": []
                }
        except Exception as e:
            logger.error(f"Error analyzing text: {str(e)}")
            return {"error": str(e)}

    def detect_unreliable_promises(self, text: str) -> bool:
        prompt = f"Does the following text contain unrealistic or unreliable promises? Answer with 'yes' or 'no' only.\n\nText: {text}"
        try:
            response = self.generate(prompt).lower()
            return "yes" in response[:5]  # Check first few characters for "yes"
        except Exception as e:
            logger.error(f"Error detecting promises: {str(e)}")
            return False

    def detect_exaggerations(self, text: str) -> bool:
        prompt = f"Does the following text contain exaggerations or hyperbole? Answer with 'yes' or 'no' only.\n\nText: {text}"
        try:
            response = self.generate(prompt).lower()
            return "yes" in response[:5]  # Check first few characters for "yes"
        except Exception as e:
            logger.error(f"Error detecting exaggerations: {str(e)}")
            return False

    def summarize_todos(self, conversation: str) -> list:
        prompt = f"""Extract all action items or to-dos from this conversation. 
        Format as a JSON array of strings, with each item being a specific task.
        
        Conversation: {conversation}"""
        
        try:
            response = self.generate(prompt)
            # Try to parse as JSON
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # If not valid JSON, try to extract as list
                return [item.strip() for item in response.split('\n') if item.strip()]
        except Exception as e:
            logger.error(f"Error summarizing todos: {str(e)}")
            return []

    def query_knowledge_base(self, scenario: str) -> str:
        """Query the knowledge base for relevant information based on a scenario"""
        try:
            # Find the most relevant key in the knowledge base
            prompt = f"""Given the following scenario, which of these knowledge categories is most relevant?
            
            Scenario: {scenario}
            
            Categories:
            {', '.join(self.knowledge_base.keys())}
            
            Return only the category name, nothing else."""
            
            category = self.generate(prompt)
            
            # Clean up the response to match knowledge base keys
            for key in self.knowledge_base:
                if key.lower() in category.lower():
                    return self.knowledge_base[key]
                    
            # If no direct match, return the most general advice
            return "I don't have specific information about this scenario in my knowledge base."
        except Exception as e:
            logger.error(f"Error querying knowledge base: {str(e)}")
            return "Unable to access knowledge base at this time."

    def schedule_follow_up(self, client_name: str, date: str) -> str:
        # Simulate scheduling a follow-up
        logger.info(f"Scheduling follow-up with {client_name} on {date}")
        return f"Follow-up scheduled with {client_name} on {date}."

    def send_email(self, recipient: str, subject: str, body: str) -> str:
        # Simulate sending an email
        logger.info(f"Email to {recipient}: {subject}")
        return f"Email sent to {recipient} with subject '{subject}'."

    def update_crm(self, client_name: str, update_info: str) -> str:
        # Simulate updating CRM
        logger.info(f"CRM update for {client_name}: {update_info}")
        return f"CRM updated for {client_name} with: {update_info}"