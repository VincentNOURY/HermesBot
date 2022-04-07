import requests

class Movies:

    def __init__(self, API_KEY, overseerr_url):
        self.API_KEY = API_KEY
        self.overseerr_url = overseerr_url

    def search_movie(self, movie_name):
        url = f"{self.overseerr_url}/search?query={movie_name}"
        req = requests.get(url = url)
