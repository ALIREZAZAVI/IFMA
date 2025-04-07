import requests
from bs4 import BeautifulSoup



def scrape_news_topic_1():
    headers  =  { 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    url = "https://www.forexlive.com/"
    response = requests.get(url ,  headers= headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all("div", class_="article-list__item-wrapper")
    title =  articles[0].find('h3' , 'article-slot__title')
    link = title.find("a")["href"]
    article_url = link if link.startswith("http") else url + link
    response = requests.get(article_url ,  headers= headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    tag = soup.find("a", class_="article-header__category-section").text.strip() 


   
    print(title.text.strip())
   
    description = soup.find("li", class_='tldr__item').text.strip()
   
    news = []
    print(description)

    
    summary = "Ahhhhhhhh....."

    news.append({
        "title":title.text.strip(),
        "description": description,
        "link": link,
        "tag": "tag",
        "summary": summary,
        'url' :url + link,
        "source": ' Forex live ',

        
    })

    return news
