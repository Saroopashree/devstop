# %%
import pandas as pd
import requests
from bs4 import BeautifulSoup

# %%
BASE_URL = "https://www.maybelline.com"
URL = BASE_URL + "/face-makeup/foundation-makeup"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")

# %%
product_list = soup.select("li.shop-all__item")

# %%
data = []

# %%
for product_item in product_list:
    if "article" in product_item["class"]:
        continue

    link = product_item.select_one("a")
    print(link["href"])
    URL = BASE_URL + str(link["href"])
    product = requests.get(URL)
    product_page = BeautifulSoup(product.content, "html.parser")

    title = product_page.select_one(".prod-title__text").text
    name = product_page.select_one(".prod-item__name").text

    description_accordion = product_page.find("div", class_=["accordion", "selected"])
    p_description = description_accordion.select_one("p")
    if p_description:
        description = p_description.text
    else:
        div_description = description_accordion.select_one("div.accordion-content")
        description = div_description.text

    data.append({"title": title, "name": name, "description": description})

# %%
df = pd.DataFrame(data)
df.to_csv("data.csv", index=False)
