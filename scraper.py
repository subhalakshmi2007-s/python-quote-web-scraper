import requests
from bs4 import BeautifulSoup
import json
import time
from collections import Counter

# Website made for practising web scraping
START_URL = "https://quotes.toscrape.com/"
HEADERS = {
    "User-Agent": "BeginnerQuoteScraper/1.0 (learning project)"
}

def get_quotes():
    all_quotes = []
    next_page = START_URL

    while next_page:
        try:
            response = requests.get(next_page, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except requests.RequestException as error:
            print("Could not open the page:", error)
            break

        soup = BeautifulSoup(response.text, "html.parser")

        # Each quote is inside a div with the class 'quote'
        quote_boxes = soup.select("div.quote")

        for box in quote_boxes:
            quote_text = box.select_one("span.text")
            author_name = box.select_one("small.author")
            tag_items = box.select("div.tags a.tag")

            # Check that the important elements are present
            if quote_text and author_name:
                quote = {
                    "quote": quote_text.get_text(strip=True),
                    "author": author_name.get_text(strip=True),
                    "tags": [tag.get_text(strip=True) for tag in tag_items]
                }
                all_quotes.append(quote)

        # Find the Next link. If it is missing, scraping is finished.
        next_button = soup.select_one("li.next a")
        if next_button:
            next_page = "https://quotes.toscrape.com" + next_button.get("href")
            time.sleep(1)
        else:
            next_page = None

    return all_quotes


def save_files(quotes):
    # Save the quotes as JSON
    with open("quotes.json", "w", encoding="utf-8") as file:
        json.dump(quotes, file, indent=2, ensure_ascii=False)

    # Save the same information in a readable text file
    with open("quotes.txt", "w", encoding="utf-8") as file:
        for number, item in enumerate(quotes, start=1):
            file.write(str(number) + ". " + item["quote"] + "\n")
            file.write("   Author: " + item["author"] + "\n")
            file.write("   Tags: " + ", ".join(item["tags"]) + "\n\n")


def show_summary(quotes):
    print("Total quotes collected:", len(quotes))

    if not quotes:
        print("No quotes were collected.")
        return

    authors = Counter(item["author"] for item in quotes)
    tags = Counter(
        tag
        for item in quotes
        for tag in item["tags"]
    )

    print("Most quoted author:", authors.most_common(1)[0][0])

    if tags:
        print("Most common tag:", tags.most_common(1)[0][0])


def main():
    print("Starting quote scraper...")
    quotes = get_quotes()
    save_files(quotes)
    show_summary(quotes)
    print("Finished. Check quotes.json and quotes.txt.")


if __name__ == "__main__":
    main()
