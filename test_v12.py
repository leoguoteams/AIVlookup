import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import os
import json
from api_manager import APIManager, KeyObfuscator
from matcher_logic import MatcherLogic

class MockAPIManager(APIManager):
    def __init__(self, api_key):
        self.api_key = api_key

    def get_embeddings(self, texts):
        return np.random.rand(len(texts), 1536)

    def get_llm_response(self, prompt):
        return '{"index": 0, "score": 85}'

class TestV12Integration(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_key_123"
        self.api_mgr = MockAPIManager(self.api_key)
        self.matcher = MatcherLogic(self.api_mgr, score_threshold=30)
        self.test_b_data = [
            ("C001", "Apple iPhone 13", "128GB", "6.1 inch"),
            ("C002", "Samsung Galaxy S21", "256GB", "6.2 inch"),
            ("C003", "Google Pixel 6", "128GB", "6.4 inch")
        ]
        self.test_b_embs = np.random.rand(len(self.test_b_data), 1536)

    def test_key_obfuscation(self):
        original = "my_secret_key_123"
        obfuscated = KeyObfuscator.obfuscate(original)
        self.assertNotEqual(original, obfuscated)
        self.assertEqual(KeyObfuscator.deobfuscate(obfuscated), original)

    def test_confidence_grading(self):
        self.assertEqual(self.matcher.get_confidence_grade(95), "High")
        self.assertEqual(self.matcher.get_confidence_grade(75), "Medium")
        self.assertEqual(self.matcher.get_confidence_grade(40), "Low")

    def test_match_logic_flow(self):
        a_text = "iPhone 13 128GB"
        result = self.matcher.match_single_item(a_text, self.test_b_data, self.test_b_embs)
        self.assertEqual(result[0], "C001")
        self.assertEqual(result[4], 85)
        self.assertEqual(result[6], "High")
        self.assertEqual(result[7], "Matched")

    def test_global_cache(self):
        a_text = "Pixel 6"
        self.matcher.match_single_item(a_text, self.test_b_data, self.test_b_embs)
        with patch.object(self.api_mgr, 'get_embeddings', side_effect=Exception("API should not be called!")):
            result = self.matcher.match_single_item(a_text, self.test_b_data, self.test_b_embs)
            self.assertEqual(result[7], "Cached")

    def tearDown(self):
        if os.path.exists("global_match_cache.json"):
            os.remove("global_match_cache.json")

if __name__ == "__main__":
    unittest.main()
