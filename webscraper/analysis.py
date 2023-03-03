import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

"""
Before I begin, a few questions:
    - How often should I check a city's craigslist page? (what is the highest frequency with the least number of redundant records?)
    - Is there a noticeable trend in housing prices?
    - What trends exist in the data that are worth more discussion and consideration?
    - What machine learning implementations are applicable to this and which methods or insights would benefit the most people?
    - What can be gained by aggregating the craigslist data to the state level of Colorado? What is lost?


Step 1. -- DONE!
    Establish a valid data collection rate ("most frequent, least redundancy")
    
    First, I'll have to figure out how many records are redundant between two separate collection dates.
        Naive approach: Scrape data on two different dates, load in data, pd.DataFrame().duplicated().sum()
    
    Optimal data collection rate:
        As often as I care to! :D I would rather have data over a long period of time instead of a lot of data over a short period. 
            Light experimentation with the Denver dataset collected 1 day apart found about 30% of records were novel and not redundant records. Despite the rate of new records, it wouldn't be feasible or necessary to collect all of this information to create worthwhile analysis.
        
Step 2.
    Prepare dataset for analysis. 
    
    Using denver_results as a template, create an approach for cleaning and typecasting data into the correct shapes and types. Then prepare all datasets.

Step 3.
    Aggregate data into a Colorado dataset.

Step 4.
    Dashboards in Tableau

Step 5.
    Hosted on GitHub Pages
"""

def format_price(item) -> str:
    if isinstance(item, float):
        return item
    return item.replace("$", "").replace(",", "")

def get_br_num(item) -> str:
    if isinstance(item, float):
        return item
    return item.replace("br", "")

def missing_to_na(item):
    if isinstance(item, float):
        return item
    return item.replace("missing", "0")

def br_to_na(item) -> str:
    if isinstance(item, float):
        return item
    return item.replace("br", "0")

denver = "../data/denver_results_28-09-2022.csv"
boulder = "../data/boulder_results_28-09-2022.csv"

denver_df = pd.read_csv(denver)
boulder_df = pd.read_csv(boulder)

denver_df.columns = boulder_df.columns

# print(den_df1.shape)
# print(den_df2.shape)

# print(den_df1.columns)
# print(den_df2.columns)

# print()
# print(denver_df.isna().sum())
# print()
# print(boulder_df.isna().sum())

# print(denver_df.shape)
# print(boulder_df.shape)

merged = denver_df.merge(boulder_df, how='left', right_index=False)
# practice = merged[["home_size(ft2)", "price", "bedrooms"]]
redundant_count = merged.duplicated().sum()
redundant_percent = redundant_count / 3000
original_percent = 1 - redundant_percent

print(f"Number of redundant items: {redundant_count}")
print(f"Percentage of redundant items: {redundant_percent:.3%}")
print(f"Percentage of records were original: {original_percent:.3%}")
# print(f"Records were collected 1 day apart.")
print()
print()

outreach_listing = merged.drop(["Unnamed: 0", "time"], axis=1)
outreach_listing = outreach_listing.replace("missing", np.nan)
outreach_listing.loc[:, "price"] = outreach_listing["price"].apply(format_price)
outreach_listing.loc[:, "bedrooms"] = outreach_listing["bedrooms"].apply(get_br_num)
outreach_listing.loc[:, "home_size(ft2)"] = outreach_listing["home_size(ft2)"].apply(br_to_na)
outreach_listing = outreach_listing.dropna(axis=0, subset=["price", "bedrooms"])
outreach_listing.loc[:, "home_size(ft2)"] = outreach_listing["home_size(ft2)"].astype(int)    # Need to make this type-castable for sorting later
outreach_listing.loc[:, "price"] = outreach_listing["price"].astype(int)
# print(outreach_listing.columns)

outreach_listing = outreach_listing[
    (outreach_listing["price"] > 1) & 
    (outreach_listing["price"] < 2000)
    ] \
    .sort_values(["price", "home_size(ft2)"], ascending=[True, False])

print(outreach_listing.columns)
outreach_listing = outreach_listing.drop_duplicates(subset=["title"], keep="first")

print(outreach_listing.iloc[:40, 2:])
outreach_listing.to_csv("../data/outreach_listing.csv")

# br_na = lambda s: "0" if "br" in s or "missing" in s else s

# def br_na(string: str) -> str:
#     if "br" in string or "missing" in string:
#         return "0"
#     else:
#         return string


# missing_to_zero = lambda m: m.replace("missing", "0")

# practice = practice.replace("missing", "0")
# practice.loc[:, "home_size(ft2)"] = practice["home_size(ft2)"].apply(br_na).astype(int)
# practice.loc[:, "price"] = practice["price"].apply(format_price).astype(int)
# practice = practice.replace("0", practice.median())
# practice = practice.replace(0, practice.median())

# # print(practice.info())

# print(practice.corr())
# plt.show()
