import requests
import pandas as pd
import numpy as np
import json
from src.postcodes import find_postcodes

API_URL = "https://landregistry.data.gov.uk/data/ppi/transaction-record.json"

"https://landregistry.data.gov.uk/data/ppi/transaction-record.html?_page=0&transactionId=&newBuild=&transactionDate=&min-transactionDate=2024-01-01&max-transactionDate=2024-12-02&pricePaid=&min-pricePaid=&max-pricePaid=&type.label=&estateType.prefLabel=&hasTransaction=&propertyAddress.county=&propertyAddress.district=&propertyAddress.locality=&propertyAddress.paon=&propertyAddress.postcode=&propertyAddress.saon=&propertyAddress.street=&propertyAddress.town=&propertyAddress.type.=&propertyType.prefLabel=&recordStatus.prefLabel=&transactionCategory.prefLabel="
"https://landregistry.data.gov.uk/data/ppi/transaction-record.html?_page=0&min-pricePaid=&propertyAddress.district=&recordStatus.prefLabel=&propertyAddress.county=&propertyAddress.town=&transactionDate=&transactionId=&newBuild=&propertyAddress.type.=&transactionCategory.prefLabel=&min-transactionDate=2024-01-01&max-pricePaid=&hasTransaction=&propertyType.prefLabel=&max-transactionDate=2024-12-02&propertyAddress.street=&type.label=&propertyAddress.paon=&propertyAddress.postcode=&propertyAddress.saon=&pricePaid=&estateType.prefLabel=&propertyAddress.locality=&_pageSize=50"

"https://landregistry.data.gov.uk/data/ppi/transaction-record.html?_page=0&_pageSize=50&transactionId=&newBuild=&transactionDate=&min-transactionDate=0022-02-01&max-transactionDate=2024-12-02&pricePaid=&min-pricePaid=&max-pricePaid=&type.label=&estateType.prefLabel=&hasTransaction=&propertyAddress.county=&propertyAddress.district=&propertyAddress.locality=&propertyAddress.paon=&propertyAddress.postcode=SW4+0ES&propertyAddress.saon=&propertyAddress.street=&propertyAddress.town=&propertyAddress.type.=&propertyType.prefLabel=&recordStatus.prefLabel=&transactionCategory.prefLabel="

# API call returns a dictionary, where we care about the key "result"
# This is in turn another dictionary, where we care about "items"
# items is itself a list of property transactions.
# Each transaction is a dictionary with the following keys
"""
_about
estateType
hasTransaction
newBuild
pricePaid
propertyAddress
propertyType
recordStatus
transactionCategory
transactionDate
transactionId
type
"""
# There appear to be 10 observations as the maximum number of observations per request


def load_data(postcode, n=3):

    try:
        postcodes_list = find_postcodes(postcode, n)
    except Exception as e:
        return e
    print("The postcodes list is: ", postcodes_list)
    transactions = []
    print("Loading data......")
    for postcode_i in postcodes_list:
        for i in range(0, 100):
            params = {
                "_page": i,
                "_pageSize": 200,
                "transactionId": "",
                "newBuild": "",
                "transactionDate": "",
                "min-transactionDate": "0022-02-01",
                "max-transactionDate": "2024-12-02",
                "pricePaid": "",
                "min-pricePaid": "",
                "max-pricePaid": "",
                "type.label": "",
                "estateType.prefLabel": "",
                "hasTransaction": "",
                "propertyAddress.county": "",
                "propertyAddress.district": "",
                "propertyAddress.locality": "",
                "propertyAddress.paon": "",
                "propertyAddress.postcode": postcode_i,
                "propertyAddress.saon": "",
                "propertyAddress.street": "",
                "propertyAddress.town": "",
                "propertyAddress.type.": "",
                "propertyType.prefLabel": "",
                "recordStatus.prefLabel": "",
                "transactionCategory.prefLabel": "",
            }

            response = requests.get(API_URL, params=params)
            print(f"Generated URL: {response.url}")

            if response.status_code != 200:
                break
            items = response.json().get("result").get("items")
            if len(items) == 0:
                break
            transactions.extend(items)

    # data = pd.DataFrame(transactions)
    return transactions


def parse_data(transactions_list):
    # Create lists to store the transaction details
    transactions = []
    print("The transactions list is: ", transactions_list)
    # Extract all information from each transaction
    for item in transactions_list:
        transaction = {
            # Transaction details
            "transaction_id": item.get("transactionId", None),
            "transaction_date": item.get("transactionDate", None),
            "price_paid": item.get("pricePaid", None),
            "new_build": item.get("newBuild", None),
            # Property type and estate type
            "property_type": item.get("propertyType", {})
            .get("label", [{}])[0]
            .get("_value", None),
            "estate_type": item.get("estateType", {})
            .get("label", [{}])[0]
            .get("_value", None),
            # Address components
            "paon": item.get("propertyAddress", {}).get("paon", None),
            "saon": item.get("propertyAddress", {}).get("saon", ""),
            "street": item.get("propertyAddress", {}).get("street", None),
            "locality": item.get("propertyAddress", {}).get("locality", ""),
            "town": item.get("propertyAddress", {}).get("town", None),
            "district": item.get("propertyAddress", {}).get("district", None),
            "county": item.get("propertyAddress", {}).get("county", None),
            "postcode": item.get("propertyAddress", {}).get("postcode", None),
            # Record status and transaction category
            "record_status": item.get("recordStatus", {})
            .get("label", [{}])[0]
            .get("_value", None),
            "transaction_category": item.get("transactionCategory", {})
            .get("label", [{}])[0]
            .get("_value", None),
        }

        transaction["address"] = (
            f"{transaction.get('saon', '')} {transaction['paon']} {transaction['street']}".replace(
                ".", ""
            )
            .replace(",", "")
            # .replace(" ", "")
            .lower()
            .strip()
        )

        transactions.append(transaction)

    # Create DataFrame
    df = pd.DataFrame(transactions)

    # Convert dates only for non-null values
    if "transaction_date" in df.columns:
        mask = df["transaction_date"].notna()
        df.loc[mask, "transaction_date"] = pd.to_datetime(
            df.loc[mask, "transaction_date"], format="%a, %d %b %Y"
        ).dt.strftime("%Y%m%d")

    # Count total transactions
    total_transactions = len(transactions)

    return df, total_transactions


if __name__ == "__main__":
    data = load_data("SW4 0ES", n=2)
    df, n = parse_data(data)
    print(n)
    print(np.shape(df))
    print(df.head())
    # df.to_csv("transactions.csv", index=False)
