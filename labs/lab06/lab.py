# lab.py


import os
import pandas as pd
import numpy as np

np.set_printoptions(legacy="1.21")
import requests
import bs4
import lxml


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def question1():
    """
    NOTE: You do NOT need to do anything with this function.
    The function for this question makes sure you
    have a correctly named HTML file in the right
    place. Note: This does NOT check if the supplementary files
    needed for your page are there!
    """
    # Don't change this function body!
    # No Python required; create the HTML file.
    return


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------


def extract_book_links(text):
    soup = bs4.BeautifulSoup(text, features="lxml")
    books = soup.find_all("article", class_="product_pod")
    
    links = []
    rating_map = {
        "One": 1, "Two": 2, "Three": 3,
        "Four": 4, "Five": 5
    }
    
    for book in books:
        rating_class = book.find("p", class_="star-rating")["class"]
        rating_word = rating_class[1]
        
        price_text = book.find("p", class_="price_color").text
        price = float(price_text.replace("£", "").replace("Â", ""))
        
        if rating_map[rating_word] >= 4 and price < 50:
            relative_link = book.find("h3").find("a")["href"]
            cleaned = relative_link.replace("../../../catalogue/", "")
            links.append(cleaned)
    
    return links


def get_product_info(text, categories):
    soup = bs4.BeautifulSoup(text, features="lxml")
    
    breadcrumb = soup.find("ul", class_="breadcrumb")
    category = breadcrumb.find_all("a")[2].text
    
    if category not in categories:
        return None
    
    table = soup.find("table", class_="table table-striped")
    rows = table.find_all("tr")
    
    product_info = {}
    
    for row in rows:
        key = row.find("th").text
        value = row.find("td").text
        product_info[key] = value
    
    rating_class = soup.find("p", class_="star-rating")["class"]
    rating = rating_class[1]
    
    description_tag = soup.find("meta", attrs={"name": "description"})
    description = description_tag["content"].strip() if description_tag else ""
    
    title = soup.find("h1").text
    
    product_info["Category"] = category
    product_info["Rating"] = rating
    product_info["Description"] = description
    product_info["Title"] = title
    
    return product_info


def scrape_books(k, categories): 
    all_books = []
    
    for page in range(1, k + 1):
        page_url = f"http://books.toscrape.com/catalogue/page-{page}.html"
        response = requests.get(page_url)
        
        links = extract_book_links(response.text)
        
        for link in links:
            full_url = "http://books.toscrape.com/catalogue/" + link
            book_response = requests.get(full_url)
            book_info = get_product_info(book_response.text, categories)
            
            if book_info is not None:
                all_books.append(book_info)
    
    return pd.DataFrame(all_books)


# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


def stock_history(symbol, year, month):
    api_key = "uahC2tUbgH7BuEjSOkZwvl7V3q9AB6E0"
    
    url = (
        f"https://financialmodelingprep.com/api/v3/historical-price-full/"
        f"{symbol}?apikey={api_key}"
    )
    
    response = requests.get(url)
    data = response.json()
    
    history = pd.DataFrame(data["historical"])
    
    history = history[
        history["date"].str.startswith(f"{year}-{str(month).zfill(2)}")
    ].reset_index(drop=True)
    
    history = history[
        ['date', 'open', 'high', 'low', 'close',
         'adjClose', 'volume', 'unadjustedVolume',
         'change', 'changePercent']
    ]
    
    return history


def stock_stats(history):
    start_price = history.iloc[-1]["open"]
    end_price = history.iloc[0]["close"]
    
    percent_change = ((end_price - start_price) / start_price) * 100
    
    avg_price = (history["high"] + history["low"]) / 2
    total_volume = (history["volume"] * avg_price).sum() / 1e9
    
    percent_str = f"{percent_change:+.2f}%"
    volume_str = f"{total_volume:.2f}B"
    
    return (percent_str, volume_str)


# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def get_comments(storyid): 
    base_url = "https://hacker-news.firebaseio.com/v0/item/{}.json"
    
    response = requests.get(base_url.format(storyid))
    story = response.json()
    
    comments = []
    
    def dfs(comment_id):
        res = requests.get(base_url.format(comment_id))
        comment = res.json()
        
        if comment is None:
            return
        
        if comment.get("dead", False):
            return
        
        comments.append({
            "id": comment.get("id"),
            "by": comment.get("by"),
            "text": comment.get("text"),
            "parent": comment.get("parent"),
            "time": pd.to_datetime(comment.get("time"), unit="s")
        })
        
        for child_id in comment.get("kids", []):
            dfs(child_id)
    
    for top_comment_id in story.get("kids", []):
        dfs(top_comment_id)
    
    return pd.DataFrame(comments)


history = stock_history("AAPL", 2019, 2)
stats = stock_stats(history)
history_hidden = stock_history("AAPL", 2023, 12)
stats_hidden = stock_stats(history_hidden)