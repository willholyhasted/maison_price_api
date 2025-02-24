from flask import Flask, request, jsonify, render_template
from src.epcAPI import query_epc_api
from src.landRegistryAPI import load_data, parse_data
import pandas as pd
from fuzzywuzzy import process
import numpy as np

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/properties", methods=["GET"])
def get_properties():
    postcode = request.args.get("postcode")
    n = int(request.args.get("n"))
    if n is None:
        n = 3
    if not postcode:
        return jsonify({"error": "Postcode is required"}), 400

    # Query EPC API
    try:
        epc_df = query_epc_api(postcode, n)
    except Exception as e:
        return jsonify({"Error querying EPC API": str(e)}), 500

    # Query Land Registry API
    land_registry_data = load_data(postcode, n)
    land_registry_df, total_transactions = parse_data(land_registry_data)
    print(
        "Land Registry Addresses: have length ", np.shape(land_registry_df["address"])
    )
    # print(land_registry_df["address"])
    print("EPC Addresses: have length ", np.shape(epc_df["address"]))
    # print(epc_df["address"])

    # Merge the DataFrames on the address column using an inner join
    merged_df = pd.merge(
        epc_df,
        land_registry_df,
        on="address",
        how="inner",
        suffixes=("_epc", "_land_registry"),
    )

    print("Merged DataFrame has length ", np.shape(merged_df["address"]))
    price_per_floor_area_per_year = calculate_price_per_floor_area(merged_df)

    # Combine results
    combined_results = {
        # "merged_data": merged_df.to_dict(orient='records'),
        "price_per_floor_area_per_year": price_per_floor_area_per_year.to_dict(
            orient="records"
        ),
    }

    # merged_df.to_csv("results.csv", index=False)
    # price_per_floor_area_per_year.to_csv(
    #    "price_per_floor_area_per_year.csv", index=False
    # )  # Save to CSV if needed
    return jsonify(combined_results)


def calculate_price_per_floor_area(merged_df):
    merged_df["price_paid"] = pd.to_numeric(merged_df["price_paid"], errors="coerce")
    merged_df["total-floor-area"] = pd.to_numeric(
        merged_df["total-floor-area"], errors="coerce"
    )

    # Calculate price per floor area
    merged_df["price_per_floor_area"] = (
        merged_df["price_paid"] / merged_df["total-floor-area"]
    )

    # Extract year from transaction date
    merged_df["year"] = pd.to_datetime(
        merged_df["transaction_date"], format="%Y%m%d"
    ).dt.year

    # Group by year and calculate average price per floor area
    price_per_floor_area_per_year = (
        merged_df.groupby("year")["price_per_floor_area"].mean().reset_index()
    )

    # Rename columns for clarity
    price_per_floor_area_per_year.columns = ["year", "price_per_floor_area"]

    return price_per_floor_area_per_year


def fuzzy_merge(df1, df2, key1, key2, threshold=80):
    matches = []
    for address in df1[key1]:
        match, score = process.extractOne(address, df2[key2])
        if score >= threshold:
            matches.append((address, match))
    return matches


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5055)
