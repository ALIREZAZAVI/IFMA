import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from abc import ABC, abstractmethod
from datetime import datetime , timedelta
from html import unescape


class BaseScraper(ABC):
    def __init__(self, mongo_uri, db_name, collection_name):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.headers  =  { 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    def load_page(self, url):

        
        session = requests.Session()
        response = session.get(url, headers= self.headers)

        if response.status_code == 200:
            return BeautifulSoup(response.content, "html.parser")
        else:
            print(f"Failed to retrieve page: {url} , response : {response.status_code}")
            return None

    @abstractmethod
    def scrape_news(self):
        pass