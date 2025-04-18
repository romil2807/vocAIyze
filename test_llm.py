import os
import unittest
from unittest.mock import patch
from llm import LLM

class TestLLM(unittest.TestCase):

    def test_integration_with_openai_api(self):
        # Setup
        api_key = os.getenv('OPENAI_API_KEY')
        llm_instance = LLM(api_key)

        # Test
        prompt = "2+2=? Only output the result and nothing else."
        response = llm_instance.generate(prompt)
        
        # Assert
        self.assertIsInstance(response, str)  # Check if response is a string
        self.assertTrue(len(response) > 0)    # Check if response is not empty

if __name__ == '__main__':
    unittest.main()
