import requests
from dotenv import load_dotenv
import os
load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

print(NEWS_API_KEY)
url = f'https://newsapi.org/v2/everything?q=Ahmedabad&apiKey={NEWS_API_KEY}'
response = requests.get(url)
print("URL:", url)
print("Status Code:", response.status_code)
print("Response:", response.text)

    
