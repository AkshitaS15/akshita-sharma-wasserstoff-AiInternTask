# src/web_search_service.py
import requests

def web_search(query):
    try:
        url = f"https://www.google.com/search?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return "Search performed. Results might be at the url: " + url
    except requests.exceptions.RequestException as e:
        print(f"Web search error: {e}")
        return None