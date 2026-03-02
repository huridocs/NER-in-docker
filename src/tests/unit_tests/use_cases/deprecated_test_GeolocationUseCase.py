from unittest import TestCase
from ner_in_docker.use_cases.GetGeolocationUseCase import GetGeolocationUseCase


class TestGetGeolocationUseCase(TestCase):
    def setUp(self):
        self.use_case = GetGeolocationUseCase()

    def test_get_coordinates_success(self):
        location_name = "New York City"

        result = self.use_case.get_coordinates(location_name)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], float)
        self.assertIsInstance(result[1], float)

        self.assertAlmostEqual(result[0], 40.7128, delta=1.0)
        self.assertAlmostEqual(result[1], -74.0060, delta=1.0)

    def test_get_coordinates_not_found(self):
        location_name = "NonExistentCity12345XYZ"

        result = self.use_case.get_coordinates(location_name)

        self.assertIsNone(result)

    def test_get_coordinates_empty_string(self):
        location_name = ""

        result = self.use_case.get_coordinates(location_name)

        self.assertIsNone(result)

    def test_get_coordinates_whitespace_only(self):
        location_name = "   \t\n  "

        result = self.use_case.get_coordinates(location_name)

        self.assertIsNone(result)

    def test_get_coordinates_multiple_calls(self):
        locations = ["New York", "London", "Tokyo"]

        for location in locations:
            result = self.use_case.get_coordinates(location)

            self.assertIsNotNone(result)
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)
            self.assertIsInstance(result[0], float)
            self.assertIsInstance(result[1], float)

    def test_get_coordinates_with_special_characters(self):
        location_name = "Paris, France"

        result = self.use_case.get_coordinates(location_name)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], float)
        self.assertIsInstance(result[1], float)
        self.assertAlmostEqual(result[0], 48.8566, delta=1.0)
        self.assertAlmostEqual(result[1], 2.3522, delta=1.0)

    def test_get_coordinates_very_long_location_name(self):
        location_name = "San Francisco, California, United States"

        result = self.use_case.get_coordinates(location_name)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], float)
        self.assertIsInstance(result[1], float)
        self.assertAlmostEqual(result[0], 37.7793, delta=1.0)
        self.assertAlmostEqual(result[1], -122.4193, delta=1.0)

    def test_none_location_name(self):
        location_name = None

        result = self.use_case.get_coordinates(location_name)

        self.assertIsNone(result)
