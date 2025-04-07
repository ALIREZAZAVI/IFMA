import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_news_topic_2():
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    }
    base_url = "https://www.myfxbook.com"
    url = f"{base_url}/news"

    try:
        # Fetch the main news page
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the first news article
        first_news = soup.select_one("h2.news-top-title a")
        if not first_news:
            print("No news link found.")
            return None

        # Extract the link and fix if relative
        link = first_news['href']
        article_url = link if link.startswith("http") else urljoin(base_url, link)

        # Fetch the specific news article page
        news_response = requests.get(article_url, headers=headers)
        news_response.raise_for_status()
        news_soup = BeautifulSoup(news_response.text, 'html.parser')

        # Extract title
        title_element = news_soup.select_one("div.col-xs-12 h1")
        title = title_element.text.strip() if title_element else "Title not found"

        # Extract description
        description_element = news_soup.find("p")
        description = description_element.text.strip() if description_element else "Description not available"

        # Extract tag (if available)
        tag_element = news_soup.select_one("div.tags a")
        tag = tag_element.text.strip() if tag_element else "No tag"

        # Add a summary
        summary = f"Breaking news from {base_url}, covering forex and market updates."

        # Prepare the news object
        news = [{
            "title": title,
            "description": description,
            "link": article_url,
            "tag": tag,
            "summary": summary,
            "url": article_url,
            "source": "MyFxBook"
        }]

        return news

    except requests.exceptions.RequestException as e:
        print(f"HTTP request error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
if __name__ == "__main__":
    news = scrape_news_topic_2()
    if news:
        print(news)
