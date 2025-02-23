# This file queries the Energy Performance Certificate API from the Department for Levelling Up, Housing and Communities
# The API data is updated daily at the end of each working day

import requests
from base64 import b64encode
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import json
import pandas as pd

load_dotenv()

API_KEY = "292e0ff993a5314c9ffd25a3b44d7de0ded0776e"
USERNAME = "willholyhasted@gmail.com"

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
    credentials = f"{USERNAME}:{API_KEY}"
    encoded_credentials = b64encode(credentials.encode("utf-8")).decode("utf-8")
    return f"Basic {encoded_credentials}"


def query_epc_api(postcode=""):
    """Query the EPC API with Basic Auth."""
    base_url = "https://epc.opendatacommunities.org/api/v1/domestic/search"

    headers = {"Accept": "application/json", "Authorization": create_auth_header()}
    if postcode:
        postcode = postcode.replace(" ", "").upper()

    params = {"postcode": postcode, "size": 5000}

    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        print(f"Generated URL: {response.url}")
        results = response.json()

        df = pd.DataFrame(
            response.json()["rows"], columns=response.json()["column-names"]
        )

        df = df[["postcode", "total-floor-area", "address"]]

        # Clean the ADDRESS column
        df["address"] = df["address"].str.replace(r"[.,]", "", regex=True)
        df["address"] = df["address"].str.replace(
            " ", ""
        )  # Remove commas and full stops
        df["address"] = df["address"].str.lower()  # Convert to lower case
        df["address"] = df["address"].str.strip()  # Remove leading/trailing whitespace
        df["address"] = df["address"].str.replace(
            r"\s+", " ", regex=True
        )  # Replace multiple spaces with a single space

        return df
    except requests.exceptions.RequestException as e:
        raise e


def main():
    # Example usage
    postcode = "SW4 0ES"  # Example postcode
    results = query_epc_api(postcode)

    print(results.head())


if __name__ == "__main__":
    main()
