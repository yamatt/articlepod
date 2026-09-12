import unittest
from datetime import UTC, datetime

from articlepod.__main__ import generate_now
from articlepod.article import generate_slug


class TestEpisode(unittest.TestCase):
    def test_slug_generation(self):
        # Example test for slug generation
        test_datetime = datetime(2024, 6, 1, 12, 0, 0, tzinfo=UTC)
        test_title = "Test Episode-!"
        expected_slug = "2024-06-01T12-00-00-test-episode--"
        generated_slug = generate_slug(test_title, test_datetime)
        self.assertEqual(generated_slug, expected_slug)

    def test_generate_now_is_timezone_aware(self):
        now = generate_now()
        self.assertIsNotNone(now.tzinfo)
        self.assertEqual(now.utcoffset(), UTC.utcoffset(now))
