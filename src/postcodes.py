import pandas as pd


"""
This function will returns a list of all postcodes within the partial postcode 

@ param postcode: a string with a full postcode, with a space
i.e. - "SW6 9EP"

@ return: a list of all postcodes that match the partial postcode
"""


def find_postcodes(postcode, n):
    if len(postcode) > 4 and " " in postcode:
        postcode_partial = split_string(postcode, n=n)
        print("The partial postcode is: ", postcode_partial)
    else:
        return Exception("Error: Postcode is too short or does not contain a space")

    # Load the postcodes data
    postcodes_df = pd.read_csv("data/postcodes.csv")

    # Filter the postcodes that match the partial postcode

    postcodes_df["partial_postcode"] = postcodes_df["postcode"].apply(split_string, n=n)

    print(
        "We found the following partial postcodes: ",
        postcodes_df["partial_postcode"].unique(),
    )

    postcodes_df = postcodes_df[postcodes_df["partial_postcode"] == postcode_partial]

    postcodes_list = postcodes_df["postcode"].tolist()

    if len(postcodes_list) == 0:
        print("No matching postcodes found")
        return Exception("Error: No matching postcodes found")
    else:
        print(postcodes_list)
        return postcodes_list


def split_string(text, n):
    space_index = text.index(" ")
    if space_index + n + 1 < len(text):
        return text[: space_index + n + 1]
    else:
        return text
