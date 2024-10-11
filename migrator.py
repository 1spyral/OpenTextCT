from selenium import webdriver # pip install selenium
from bs4 import BeautifulSoup # pip install beautifulsoup4
import json

# Selenium options
options = webdriver.ChromeOptions()
options.add_argument("--headless")

# Links to read from and write to
input_url = "https://www.microfocus.com/en-us/products?trial=true"
output_url = "products.json"

# Fetch the webpage and return its content
# Note: originally tried using requests module, but the page needs JavaScript to load the product items
def fetch(url):
    driver = webdriver.Chrome(options = options)

    driver.get(url)
    html_content = driver.page_source
    driver.quit()

    return html_content

# Parse the content of the webpage and return the products
def parse(content):
    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    # Find all the products
    products = soup.find_all("div", class_ = "uk-card")
    
    return products

# On the microfocus website, the links are relative, so we need to globalize them
def globalize(link):
    if link.startswith("/"):
        # Append the website domain to the link
        return "https://www.microfocus.com" + link
    # The company also provides email links, which we don't globalize
    return link

# Return a JSON object of the product
# Output format:
# {
#     name
#     starting_letter
#     description
#     demo_url
#     support_url
#     community_url
# }
def jsonify(product):
    # Name exists as text in the h3 tag
    name = product.find("h3", class_ = "uk-card-title").text
    starting_letter = name[0].upper()
    # The description always lies in the paragraph tag
    description = product.find("p").text
    # The demo URL can exist as either a "Request a demo" or "Get free trial" button
    demo_url = []
    for link in product.find("div", class_ = "cta-section").find_all("a"):
        if "demo" in link.string.lower() or "free trial" in link.string.lower():
            demo_url.append(globalize(link["href"]))
    # The support and community URLs are provided in the product footer
    support_url = ""
    community_url = ""
    for link in product.find("div", class_ = "footer").find_all("a"):
        if "support" in link.string.lower() and "href" in link.attrs:
            support_url = globalize(link["href"])
        elif "community" in link.string.lower() and "href" in link.attrs:
            community_url = globalize(link["href"])
    return {
        "name": name,
        "starting_letter": starting_letter,
        "description": description,
        "demo_url": demo_url,
        "support_url": support_url,
        "community_url": community_url
    }

# Main function
def main():
    products = list(parse(fetch(input_url)))
    # JSONify each product
    json_products = [jsonify(product) for product in products]

    # Write the JSON object to a file
    with open(output_url, "w") as file:
        json.dump(json_products, file, indent = 4)


if __name__ == "__main__":
    main()
