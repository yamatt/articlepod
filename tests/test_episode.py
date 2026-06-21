import unittest

from datetime import datetime

from src.articlepod.episode import generate_slug, generate_script

class TestEpisode(unittest.TestCase):
    def test_slug_generation(self):
        # Example test for slug generation
        test_datetime = datetime(2024, 6, 1, 12, 0, 0)
        test_title = "Test Episode"
        expected_slug = "2024-06-01T12-00-00-test-episode"
        generated_slug = generate_slug(test_title, test_datetime)
        self.assertEqual(generated_slug, expected_slug)
