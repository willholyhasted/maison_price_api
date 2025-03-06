import unittest
import pandas as pd
from app import calculate_price_per_floor_area


class TestCalculations(unittest.TestCase):
    def test_calculate_price_per_floor_area(self):
        # Create a test DataFrame
        test_df = pd.DataFrame(
            {
                "price_paid": [200000, 300000],
                "total-floor-area": [100, 150],
                "transaction_date": ["20200101", "20210101"],
            }
        )

        # Calculate price per floor area
        result = calculate_price_per_floor_area(test_df)

        # Check if the result has the expected columns
        expected_columns = [
            "year",
            "median",
            "mean",
            "count",
            "std",
            "upper_bound",
            "lower_bound",
        ]
        self.assertListEqual(list(result.columns), expected_columns)

        # Check if the years are correctly extracted
        years = result["year"].tolist()
        self.assertIn(2020, years)
        self.assertIn(2021, years)

        # Check if the calculations are correct
        # For 2020: 200000/100 = 2000
        # For 2021: 300000/150 = 2000
        # Mean should be 2000
        for _, row in result.iterrows():
            self.assertAlmostEqual(row["mean"], 2000, delta=0.1)


if __name__ == "__main__":
    unittest.main()
