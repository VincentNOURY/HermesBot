import requests
import json

class Movies:

    def __init__(
        self,
        #API_KEY : str,
        overseerr_url : str,
        #connection_endpoint : str,
        PLEX_TOKEN : str,
        logger,
        messenger
    ):

        #self.API_KEY = API_KEY
        self.overseerr_url = overseerr_url
        self.connection_endpoint = "/auth/plex"
        self.PLEX_TOKEN = PLEX_TOKEN
        self.HEADERS = {"accept" : "application/json"}

        self.log = logger.log

        self.title = None
        self.description = None
        self.media_id = None
        self.media_type = None
        self.poster = None

        self.session = requests.Session()
        self.messenger = messenger;

        self.connect()

    def get_title(self):
        return self.title

    def get_description(self):
        return self.description

    def get_media_id(self):
        return self.media_id

    def get_media_type(self):
        return self.media_type

    def get_poster(self):
        return self.poster


    def connect(self):
        self.log('none', "Logging in ...")
        payload = {"authToken" : self.PLEX_TOKEN}

        req = self.session.post(self.overseerr_url + self.connection_endpoint,
            headers = self.HEADERS, json = payload)
        if req.status_code == 200:
            self.log('none', "Logged in")
        else:
            self.log('error', "You are not logged in please check your token")
            self.log('error', req.text)
            raise

    def search_movie(self, movie_name, channel_id):
        url = f"{self.overseerr_url}/search?query={movie_name}&page=1"
        req = self.session.get(url = url)
        if req.status_code == 200:
            json_result = json.loads(req.text)
            results = json_result['results']

            if results:
                self.log('trace', results[0])

                title = results[0]['originalTitle']
                description = results[0]['overview']
                if not description:
                    description = "Nothing found"
                poster_path = results[0]['posterPath']
                media_type = results[0]['mediaType']

                media_id = results[0]['id']

                if media_id != None: media_id = int(media_id)


                poster = self.session.get(f"https://image.tmdb.org/t/p/w600_and_h900_bestv2{poster_path}").content

                self.title = title
                self.description = description
                self.media_id = media_id
                self.media_type = media_type
                self.poster = poster
            else:
                self.messenger.send_message(channel_id, "No results")
                self.log('error', "No results")
                self.title = None
                self.description = None
                self.media_id = None
                self.media_type = None
                self.poster = None
        else:
            self.log('error', "Couldn't get a response from the server")
            raise

    def add_movie(self, media_type, media_id, root_folder):
        url = self.overseerr_url + "/request"

        payload = {
          "mediaType": media_type,
          "mediaId": media_id,
          #"tvdbId": tvdb_id,
          "seasons": [
            0
          ],
          "is4k": False,
          "serverId": 0,
          "profileId": 0,
          "rootFolder": root_folder,
          "languageProfileId": 0,
          "userId": 0
        }

        req = self.session.post(url = url, headers = self.HEADERS, json = payload)
        if req.status_code == 201:
            self.log('debug', "movie added")
            self.log('trace', req.text)
            return "Movie added"
        elif req.status_code == 500:
            self.log('debug', "Movie already available")
            return "Movie already available"
        elif req.status_code == 409:
            self.log('debug', "Already asked")
            return "Already asked"
        else:
            self.log('error', f"status code {req.status_code} : {req.text}")
