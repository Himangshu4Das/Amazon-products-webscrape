from bs4 import BeautifulSoup
import requests
import pandas as pd


# Get product title
def get_name(soup):
    try:
        name_string = soup.find("span", attrs={"id": 'productTitle'}).string.strip()

    except AttributeError:
        name_string = ""

    return name_string


# Get product price
def get_price(soup):
    try:
        price = soup.find("span", attrs={'class': 'a-price-whole'}).text
        try:
            price = float(price.replace(',', ''))
        except:
            price = float(eval(price))

    except AttributeError:
        price = ""

    return price


# Get product ratings
def get_rating(soup):
    try:
        rating = float(soup.find("i", attrs={'class': 'a-icon a-icon-star a-star-4-5'}).string.strip().split("out")[0])

    except AttributeError:

        try:
            rating = float(soup.find("span", attrs={'class': 'a-icon-alt'}).string.strip().split("out")[0])
        except:
            rating = ""

    return rating


# Get number of user reviews
def get_review_count(soup):
    try:
        review_count = int(
            soup.find("span", attrs={'id': 'acrCustomerReviewText'}).string.strip().split(' ')[0].replace(',', ''))

    except AttributeError:
        review_count = ""

    return review_count


# Get description
def get_description(soup):
    try:
        description = soup.find("ul", attrs={"class": 'a-unordered-list a-vertical a-spacing-mini'}).text
    except:
        description = ''

    return description


# Get product description
def get_prod_description(soup):
    try:
        prod_description = soup.find("div", attrs={"id": 'productDescription'}).text.replace('\n', '')
    except:
        prod_description = ''

    return prod_description


# Get ASIN
def get_asin(soup):
    try:
        asin = str(soup.find("input", attrs={"id": "ASIN"})).split("value=")[-1][1:-3]
    except:
        try:
            table = soup.find("table", attrs={"id": "productDetails_detailBullets_sections1"})
            rows = table.find_all('tr')
            values = {"title": [], "value": []}
            for row in rows:
                head = row.find('th').text.strip()
                cols = row.find('td').text.strip()
                values["value"].append(cols)
                values["title"].append(head)

            asin_df = pd.DataFrame(values)
            manufacturer = asin_df[asin_df["title"] == "ASIN"]["value"].iloc[0]
        except:
            try:
                asin_temp = soup.find("div", attrs={"id": "detailBullets_feature_div"})
                asin_temp = asin_temp.find("ul", attrs={
                    "class": "a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list"}).find_all("li")
                for each in asin_temp:
                    values = each.text.split(":")
                    values = [temp.replace("\u200f", '').replace("\u200e", '').strip() for temp in values]
                    if (values[0] == "ASIN"):
                        return (values[-1])
            except:
                asin = ''

    return asin


# Get manufacturer name
def get_manufacturer(soup):
    try:
        table = soup.find("table", attrs={"id": "productDetails_detailBullets_sections1"})
        rows = table.find_all('tr')
        values = {"title": [], "value": []}
        for row in rows:
            head = row.find('th').text.strip()
            cols = row.find('td').text.strip()
            values["value"].append(cols)
            values["title"].append(head)

        manu_df = pd.DataFrame(values)
        manufacturer = manu_df[manu_df["title"] == "Manufacturer"]["value"].iloc[0]
    except:
        try:
            manufacturer = soup.find("div", attrs={"id": "detailBullets_feature_div"})
            manufacturer = manufacturer.find("ul", attrs={
                "class": "a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list"}).find_all("li")
            for each in manufacturer:
                values = each.text.split(":")
                values = [temp.replace("\u200f", '').replace("\u200e", '').strip() for temp in values]
                if (values[0] == "Manufacturer"):
                    return (values[-1])



        except:
            manufacturer = ''

    return manufacturer


HEADERS = ({'User-Agent':
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})
URL = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"

data = {"product_url": [], "product_name": [], "product_price": [], "rating": [], "number_reviews": [],
        "description": [], "product_ASIN": [], "product_description": [], "manufacturer": []}

# Traverse through each page link
for i in range(1, 21):
    print("Fetching products from page {}".format(i))

    # Create url of each search result page ( appending last character with page number )
    url = URL[:-1] + str(i)

    # Traversing inside each url
    webpage = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(webpage.content, "lxml")  # Create soup

    # Find all product list
    links = soup.find_all("a", attrs={'class': 'a-link-normal s-no-outline'})
    links = [("https://www.amazon.in" + link.get('href')) for link in links]  # store links

    # Traverse through each product link.
    for link in links:
        webpage = requests.get(link, headers=HEADERS)
        soup = BeautifulSoup(webpage.content, "lxml")  # Create soup

        data["product_url"].append(link)
        data["product_name"].append(get_name(soup))
        data["product_price"].append(get_price(soup))
        data["rating"].append(get_rating(soup))
        data["number_reviews"].append(get_review_count(soup))

        data["description"].append(get_description(soup))
        data["product_ASIN"].append(get_asin(soup))
        data["product_description"].append(get_prod_description(soup))
        data["manufacturer"].append(get_manufacturer(soup))

# Convert dictionary to dataframe
final = pd.DataFrame.from_dict(data)

# save to csv
final.to_csv("Data.csv")

# Rmove irrelevant products
final = final[final["product_ASIN"]!='']