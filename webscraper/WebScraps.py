from bs4 import BeautifulSoup, Tag
import pandas as pd
import requests
import time
from typing import Optional
import re
from datetime import date

HTTPHeaders = dict[str, str]

"""
A (more) generalized web scraper. Meant to provide basic web scraping functionality while also being extendable by any programmer users.
"""


class Scraps(object):
    def __init__(self, URL: str, headers: HTTPHeaders = None):
        self.URL = URL
        self.headers = headers

    # Returns a response object a given URL
    def get_response(self, URL: str = None, headers: HTTPHeaders = None) -> requests.Response:
        # To prevent spamming
        time.sleep(10.0)
        if URL is None:
            URL = self.URL
        elif headers is None:
            headers = self.headers

        elif URL is not None and headers is not None:
            self.response = requests.get(URL, headers)

        self.response = requests.get(url=self.URL, headers=self.headers)
        return self.response

    # Returns a BeautifulSoup object from response
    def make_soup(self, response_content, parser: str = None) -> BeautifulSoup:
        VALID_PARSERS = {"lxml", "html5lib", "html.parser"}

        if parser not in VALID_PARSERS and parser is not None:
            raise ValueError(
                f"Invalid parser specified. Supported parsers: {VALID_PARSERS}")
        elif parser is None:
            print(
                "It's recommended to specify a parser, but BeautifulSoup can make a decent guess automatically.")

        if isinstance(response_content, requests.Response):
            raise TypeError(
                "Expected response content. Did you accidentally return the response object instead of its contents? Please try again.")

        self.soup = BeautifulSoup(response_content, parser)
        return self.soup

    # Find all occurences of <Tag>
    def list_from_tag(self, tag: str, css_class: str = None) -> list[Tag]:
        # css_class parameter also accepts multiple class names contained within one string.
        if isinstance(css_class, str):
            return self.soup.find_all(tag, {"class": css_class})
        else:
            return self.soup.find_all(tag)

    # Clears object content
    def reset_content(self):
        raise NotImplementedError()


####################################################################################################################################################################################################################################################################################################################################################################################################### Craigslist Project Beginning ######################################################################################################################################################################
######################################################################################################################################################################

def clean_text(text: str) -> str:
    return re.sub(r"[\n\(\)\-\$]\s{2,}", "", text).strip().replace("ft2", "")


def extract_bedrooms(text: str) -> str:
    br_match = re.match(r"\d+br", text)

    if "br" in text.lower():
        return clean_text(br_match.group(0))
    else:
        return "missing"


def try_parse(tag: Optional[Tag]) -> Tag:
    if isinstance(tag, str):
        return clean_text(tag)
    elif isinstance(tag, Tag):
        return clean_text(tag.text)
    elif tag is None:
        return "missing"
    else:
        return clean_text(tag)


# Proof-of-Concept application
def main(city: str, headers: HTTPHeaders):
    """
    Tags and CSS Classes of interest
    For each listing in apartments:
    ("time") :: time of listing publishing
    ("a", {"class": "result-title"}) :: contains title and href
        ("span", {"class": "result-price"}) :: price in USD ($)
        ("span", {"class": "housing"}) :: contains n-br and n-ft^2
        ("span", {"class": "result-hood"}) :: Sometimes neighborhood, sometimes address

    Craigslist pagination Ref: https://stackoverflow.com/questions/52951066/how-do-you-move-to-a-new-page-when-web-scraping-with-beautifulsoup
    """
    # Scraping craigslist
    base_url = f"https://{city}.craigslist.org"
    s = Scraps(base_url, headers)

    # Hacky pagination for craigslist
    next_page_urls = []
    next_page_urls.append(base_url + "/search/hhh?")
    data = []

    # While there are next page links,
    # continue looping over listing details
    while len(next_page_urls) > 0:
        print(next_page_urls)

        # Pops the first next_page_url
        # and assigns it the Scraps instance's URL attribute
        s.URL = next_page_urls.pop(0)
        resp = s.get_response()
        soup = s.make_soup(resp.text, "html.parser")

        next_page = soup.find("a", {"class": "button next"})["href"]

        # Searches for the next page
        if next_page:
            next_page_urls.append(base_url + next_page)

        # Collects specified data from each results
        listings = s.list_from_tag("li", "result-row")
        for listing in listings:
            fields = {
                "title": listing.find("a", {"class": "result-title"}),
                "link": listing.find("a", {"class": "result-title"})["href"],
                "time": listing.find("time")["title"],
                "price": listing.find("span", {"class": "result-price"}),
                "home_size(ft2)": listing.find("span", {"class": "housing"}),
                "bedrooms": listing.find("span", {"class": "housing"}),
                "neighborhood": listing.find("span", {"class": "result-hood"})
            }

            # Loops over each each desired item of data in fields
            # Fills in missing values with "missing" string
            for field in fields:

                if field == "home_size(ft2)":
                    fields["home_size(ft2)"] = re.sub(
                        "\d+br\s+", "", try_parse(fields["home_size(ft2)"]))

                elif field == "bedrooms":
                    fields["bedrooms"] = extract_bedrooms(
                        try_parse(fields["bedrooms"]))

                else:
                    fields[field] = try_parse(fields[field])

            data.append(fields)

    # Next create a pandas DataFrame
    df = pd.DataFrame(data)

    # Then convert data to_parquet()
    file_path = f"../data/link/{city}_results_{date.today().strftime('%m-%d-%Y')}.csv"
    print(file_path)
    df.to_csv(file_path)



if __name__ == "__main__":
    cities = ["denver", "boulder", "cosprings", "pueblo", "eastco", "westslope", "fortcollins", "rockies"]
    # cities = ["kansascity", "lawrence"]

    # searching for all housing listings
    headers = {
        #     # "query":"apartment",
        # "sort":"price",
        "bundleDuplicates": "1",
        #     # "min_price":"",
        "max_price":"1100",
        "availabilityMode": "0",
        #     # "pets_dog":"1",
        "sale_date": "all+dates"
    }
    for city in cities:
        main(city, headers)
