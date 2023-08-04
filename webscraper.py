import requests
from bs4 import BeautifulSoup
import pandas as pd

# Base URL of your website
base_url = 'https://www.atascosacdj.com/searchnew.aspx?pt={}'

# Page number
page_num = 1

# List to store the data
data = []

while True:
    # Form the URL for the current page
    url = base_url.format(page_num)

    # Send HTTP request to the specified URL and save the response from the server in a response object called r
    r = requests.get(url)

    # Create a BeautifulSoup object and specify the parser
    soup = BeautifulSoup(r.text, 'html.parser')

    # Find all 'span' tags with class 'vehicle-title__year', 'vehicle-title__make-model', and 'vehicle-title__trim'
    years = soup.find_all('span', class_='vehicle-title__year')
    make_models = soup.find_all('span', class_='vehicle-title__make-model')
    trims = soup.find_all('span', class_='vehicle-title__trim')

    # Find all 'span' tags with class 'priceBlocItemPriceValue'
    prices = soup.find_all('span', class_='priceBlocItemPriceValue')

    # Initialize lists to store the MSRPs and sales prices
    msrps = []
    sales_prices = []

    # Iterate over the list of 'span' tags and identify each one as an MSRP or sales price
    for price in prices:
        # Find the preceding label
        label = price.find_previous('span', class_='priceBlocItemPriceLabel')

        # Use the label's text to identify whether the price is an MSRP or sales price
        if "MSRP" in label.text:
            msrps.append(price)
        elif "ALLWAYS ONE SIMPLE PRICE" in label.text:
            sales_prices.append(price)

    # Check if there are any vehicles on the current page
    if not years or not make_models or not trims or not msrps or not sales_prices:
        break  # Exit the loop if there are no vehicles

    # Iterate over the lists of 'span' tags and extract the text within each tag
    for year, make_model, trim, msrp, sales_price in zip(years, make_models, trims, msrps, sales_prices):
        year = year.text
        make, model = make_model.text.split(' ', 1)  # This assumes the make is always a single word
        trim = trim.text
        msrp = msrp.text
        sales_price = sales_price.text
        price_difference = float(msrp.replace(',', '').replace('$', '')) - float(sales_price.replace(',', '').replace('$', ''))

        data.append([year, make, model, trim, msrp, sales_price, price_difference])

    # Increment the page number for the next iteration
    page_num += 1

# Create DataFrame
df = pd.DataFrame(data, columns=['Year', 'Make', 'Model', 'Trim', 'MSRP', 'Sales Price', 'Price Difference'])

# Save data to CSV
df.to_csv('vehicles.csv', index=False)
