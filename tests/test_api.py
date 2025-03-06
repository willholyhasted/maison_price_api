import unittest
import json
from app import app
import pandas as pd
from unittest.mock import patch
from epcAPI import query_epc_api
from landRegistryAPI import load_data, parse_data


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch("epcAPI.query_epc_api")
    @patch("landRegistryAPI.load_data")
    @patch("landRegistryAPI.parse_data")
    def test_get_price_timeseries(
        self, mock_parse_data, mock_load_data, mock_query_epc_api
    ):
        # Mock the EPC API response
        epc_df = pd.DataFrame(
            {
                "address": ["123 test street", "456 test avenue"],
                "total-floor-area": [100, 150],
            }
        )
        mock_query_epc_api.return_value = epc_df

        # Mock the Land Registry API response
        mock_load_data.return_value = "mock_data"

        # Mock the parse_data function
        land_registry_df = pd.DataFrame(
            {
                "address": ["123 test street", "456 test avenue"],
                "price_paid": [200000, 300000],
                "transaction_date": ["20200101", "20210101"],
            }
        )
        mock_parse_data.return_value = (land_registry_df, 2)

        # Test the API endpoint
        response = self.app.get("/properties?postcode=SW4+0ES")
        data = json.loads(response.data)

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)

        # Check if the response contains the expected data
        self.assertIn("price_per_floor_area_per_year", data)

        # Check if the years are correctly extracted
        years = [item["year"] for item in data["price_per_floor_area_per_year"]]
        self.assertIn(2020, years)
        self.assertIn(2021, years)

    def test_missing_postcode(self):
        # Test the API endpoint without providing a postcode
        response = self.app.get("/properties")
        data = json.loads(response.data)

        # Check if the response is a bad request
        self.assertEqual(response.status_code, 400)

        # Check if the error message is correct
        self.assertEqual(data["error"], "Postcode is required")

    def test_index_route(self):
        # Test the index route
        response = self.app.get("/")

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
