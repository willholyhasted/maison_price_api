import requests
import pandas as pd
import numpy as np
import json

API_URL = "https://landregistry.data.gov.uk/data/ppi/transaction-record.json"

"https://landregistry.data.gov.uk/data/ppi/transaction-record.html?_page=0&transactionId=&newBuild=&transactionDate=&min-transactionDate=2024-01-01&max-transactionDate=2024-12-02&pricePaid=&min-pricePaid=&max-pricePaid=&type.label=&estateType.prefLabel=&hasTransaction=&propertyAddress.county=&propertyAddress.district=&propertyAddress.locality=&propertyAddress.paon=&propertyAddress.postcode=&propertyAddress.saon=&propertyAddress.street=&propertyAddress.town=&propertyAddress.type.=&propertyType.prefLabel=&recordStatus.prefLabel=&transactionCategory.prefLabel="
"https://landregistry.data.gov.uk/data/ppi/transaction-record.html?_page=0&min-pricePaid=&propertyAddress.district=&recordStatus.prefLabel=&propertyAddress.county=&propertyAddress.town=&transactionDate=&transactionId=&newBuild=&propertyAddress.type.=&transactionCategory.prefLabel=&min-transactionDate=2024-01-01&max-pricePaid=&hasTransaction=&propertyType.prefLabel=&max-transactionDate=2024-12-02&propertyAddress.street=&type.label=&propertyAddress.paon=&propertyAddress.postcode=&propertyAddress.saon=&pricePaid=&estateType.prefLabel=&propertyAddress.locality=&_pageSize=50"

"https://landregistry.data.gov.uk/data/ppi/transaction-record.html?_page=0&_pageSize=50&transactionId=&newBuild=&transactionDate=&min-transactionDate=0022-02-01&max-transactionDate=2024-12-02&pricePaid=&min-pricePaid=&max-pricePaid=&type.label=&estateType.prefLabel=&hasTransaction=&propertyAddress.county=&propertyAddress.district=&propertyAddress.locality=&propertyAddress.paon=&propertyAddress.postcode=SW4+0ES&propertyAddress.saon=&propertyAddress.street=&propertyAddress.town=&propertyAddress.type.=&propertyType.prefLabel=&recordStatus.prefLabel=&transactionCategory.prefLabel="

#API call returns a dictionary, where we care about the key "result"
#This is in turn another dictionary, where we care about "items"
#items is itself a list of property transactions.
#Each transaction is a dictionary with the following keys
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
#There appear to be 10 observations as the maximum number of observations per request

def load_data():
    transactions = []
    print("Loading data......")
    for i in range(0, 100):
        print(f"Calling from page {i}")
        # params = {
        #     "_page" : f"{i}",
        #     "min-transactionDate" : "2000-12-01",
        #     "max-transactionDate" : "2024-12-31",
        #     "propertyAddress.postcode" : "SW1A 1AA",
        #     "propertyAddress.town": "LONDON",
        #     "_pageSize": "200"
        # }

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
            "propertyAddress.postcode": "SW4 0ES",
            "propertyAddress.saon": "",
            "propertyAddress.street": "",
            "propertyAddress.town": "",
            "propertyAddress.type.": "",
            "propertyType.prefLabel": "",
            "recordStatus.prefLabel": "",
            "transactionCategory.prefLabel": ""
        }

        response = requests.get(API_URL, params=params)
        print(f"Generated URL: {response.url}")

        if response.status_code != 200:
            break
        items = response.json().get('result').get('items')
        if len(items) == 0:
            break
        transactions.extend(items)

    #data = pd.DataFrame(transactions)
    return transactions

def parse_data(list):
        # Create lists to store the transaction details
        transactions = []

        # Extract all information from each transaction
        for item in list:
            transaction = {
                # Transaction details
                'transaction_id': item['transactionId'],
                'transaction_date': item['transactionDate'],
                'price_paid': item['pricePaid'],
                'new_build': item['newBuild'],

                # Property type and estate type
                'property_type': item['propertyType']['label'][0]['_value'],
                'estate_type': item['estateType']['label'][0]['_value'],

                # Address components
                'paon': item['propertyAddress']['paon'],
                'saon': item['propertyAddress'].get('saon', ''),  # Optional field
                'street': item['propertyAddress']['street'],
                'locality': item['propertyAddress'].get('locality', ''),  # Optional field
                'town': item['propertyAddress']['town'],
                'district': item['propertyAddress']['district'],
                'county': item['propertyAddress']['county'],
                'postcode': item['propertyAddress']['postcode'],

                # Record status and transaction category
                'record_status': item['recordStatus']['label'][0]['_value'],
                'transaction_category': item['transactionCategory']['label'][0]['_value'],

                # Full address (combined)
                'full_address': f"{item['propertyAddress'].get('saon', '')} {item['propertyAddress']['paon']} {item['propertyAddress']['street']}".strip(),

                # Reference URLs
                #'transaction_ref': item['hasTransaction'],
                #'about_ref': item['_about']
            }
            transactions.append(transaction)

        # Create DataFrame
        df = pd.DataFrame(transactions)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'], format='%a, %d %b %Y')
        df['transaction_date'] = df['transaction_date'].dt.strftime('%Y%m%d')

        # Count total transactions
        total_transactions = len(transactions)

        return df, total_transactions


if __name__ == "__main__":
    data = load_data()
    df, n = parse_data(data)
    print(n)
    print(np.shape(df))
    print(df.head())
    df.to_csv('transactions.csv', index=False)


