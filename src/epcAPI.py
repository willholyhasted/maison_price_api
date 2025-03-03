# This file queries the Energy Performance Certificate API from the Department for Levelling Up, Housing and Communities
# The API data is updated daily at the end of each working day

import requests
from base64 import b64encode
from dotenv import load_dotenv
from src.postcodes import split_string
import pandas as pd
import os

load_dotenv()


# "/info" endpoint will return two values
# latestDate: the date of the most recent energy certificate
# updatedDate: the date of the last update


def last_updated():
    url = "https://epc.opendatacommunities.org/api/v1/info"
    response = requests.get(url)

    if response.status_code != 200:
        print("An error occured")

    data = response.json()

    print(data)


def create_auth_header():
    """Create the Basic Auth header from username and password."""
    username = os.getenv("USERNAME")
    api_key = os.getenv("API_KEY")
    credentials = f"{username}:{api_key}"
    encoded_credentials = b64encode(credentials.encode("utf-8")).decode("utf-8")
    return f"Basic {encoded_credentials}"


def query_epc_api(postcode, n=2):
    """Query the EPC API with Basic Auth."""
    base_url = "https://epc.opendatacommunities.org/api/v1/domestic/search"

    headers = {"Accept": "application/json", "Authorization": create_auth_header()}
    all_data = []
    i = 0
    postcode = split_string(postcode, n)
    search_after = None
    search = True
    while search:
        postcode = postcode.replace(" ", "").upper()
        params = {"postcode": postcode, "size": 5000}
        if i > 0:
            params["search-after"] = search_after

        try:
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()
            # print(f"Generated URL: {response.url}")
            search_after = response.headers.get("X-Next-Search-After")

            if search_after is None:
                search = False

            # Get the data from the response
            rows = response.json().get("rows", [])

            # Add all rows to our collection
            all_data.extend(rows)

            print(f"Collected {len(rows)} records for postcode {postcode}")
            print(f"Total records collected so far: {len(all_data)}")
            i = i + 1

        except requests.exceptions.RequestException as e:
            search = False
            print(f"Error processing postcode {postcode}: {e}")

    test_response = requests.get(
        base_url,
        headers=headers,
        params={"postcode": postcode.replace(" ", "").upper(), "size": 1},
    )
    column_names = test_response.json()["column-names"]

    # Create the final DataFrame
    df = pd.DataFrame(all_data, columns=column_names)
    print(f"Final DataFrame created with {len(df)} rows and {len(df.columns)} columns")

    # Convert lodgement-date to datetime for comparison
    df["lodgement-date"] = pd.to_datetime(df["lodgement-date"])

    # Sort by lodgement date (newest first) and keep first occurrence of each building reference
    df = df.sort_values("lodgement-date", ascending=False)
    # df = df.drop_duplicates(subset="building-reference-number", keep="first")
    df["lodgement-date"] = df["lodgement-date"].dropna()
    df["total-floor-area"] = df["total-floor-area"].dropna()

    # Select and clean required columns
    df = df[["postcode", "total-floor-area", "address"]]

    # Clean the ADDRESS column
    df["address"] = df["address"].str.replace(r"[.,]", "", regex=True)
    # df["address"] = df["address"].str.replace(" ", "")
    df["address"] = df["address"].str.lower()
    df["address"] = df["address"].str.strip()
    df["address"] = df["address"].str.replace(r"\s+", " ", regex=True)

    return df


def main():
    # Example usage
    print("Test")
    postcode = "SW4"  # Example postcode
    results = query_epc_api(postcode, 1)
    results.to_csv("epc_data.csv", index=False)


if __name__ == "__main__":
    main()
