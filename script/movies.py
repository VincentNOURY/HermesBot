"""
Movies module is used to retreive infos from and add a film to overseerr.

Args:
    overseerr_url: Url of the overseerr serverr
    plex_token: The token of your plex account
    logger: An instance of the logger module
    messenger: An instance of the messenger module
"""

import sys
import json
import requests


class Movies:
    """
    Movies module is used to retreive infos from and add a film to overseerr.

    Args:
        overseerr_url: Url of the overseerr serverr
        plex_token: The token of your plex account
        logger: An instance of the logger module
        messenger: An instance of the messenger module
    """

    def __init__(
        self,
        overseerr_url: str,
        plex_token: str,
        logger,
        messenger
    ):
        """
        Movies module is used to retreive infos from and add a film to
        overseerr.

        Args:
            overseerr_url: Url of the overseerr serverr
            plex_token: The token of your plex account
            logger: An instance of the logger module
            messenger: An instance of the messenger module
        """

        self.overseerr_url = overseerr_url
        self.plex_token = plex_token
        self.log = logger.log
        self.messenger = messenger

        self.infos = {'title':       None,
                      'description': None,
                      'media_id':    None,
                      'media_type':  None,
                      'poster':      None}

        self.session = requests.Session()

        self.connect()

    def get_title(self):
        """
        Returns the title of the last movie searched.

        Args:
            None

        Returns:
            self.infos['title']: The title of the last movie searched.
        """

        return self.infos['title']

    def get_description(self):
        """
        Returns the description of the last movie searched.

        Args:
            None

        Returns:
            self.infos['description']: The description of the last movie
                                       searched.
        """

        return self.infos['description']

    def get_media_id(self):
        """
        Returns the media id of the last movie searched.

        Args:
            None

        Returns:
            self.infos['media_id']: The media id of the last movie searched.
        """

        return self.infos['media_id']

    def get_media_type(self):
        """
        Returns the media type of the last movie searched.

        Args:
            None

        Returns:
            self.infos['media_type']: The media type of the last movie
                                      searched.
        """

        return self.infos['media_type']

    def get_poster(self):
        """
        Returns the poster of the last movie searched.

        Args:
            None

        Returns:
            self.infos['poster']: The poster of the last movie searched.
        """

        return self.infos['poster']

    def connect(self):
        """
        Connects to the overseerr server (sets the session
        necessary for the requests).

        Args:
            None

        Returns:
            None
        """

        self.log('none', "Logging in ...")
        payload = {"authToken": self.plex_token}
        headers = {"accept": "application/json"}

        req = self.session.post(self.overseerr_url + "/auth/plex",
                                headers=headers, json=payload)
        if req.status_code == 200:
            self.log('none', "Logged in")
        else:
            self.log('error', "You are not logged in please check your token")
            self.log('error', req.text)
            sys.exit()

    def search_movie(self, movie_name: str, i=0):
        """
        Searches for a movie with its name.

        Args:
            movie_name: Name of the movie to search.
            i: index at which the search should start
                (used if the result sent before is not the right one).

        Returns:
            Integer: index of the last movie found or -1 if no movie is found.
        """

        url = f"{self.overseerr_url}/search?query={movie_name}&page=1"
        req = self.session.get(url=url)
        if req.status_code == 200:
            json_result = json.loads(req.text)
            results = json_result['results']
            if results:
                for index, result in enumerate(results):
                    if index >= i and result['mediaType'] == 'movie':
                        i = index
                        break

                if self.movie_treatment(results[i]):
                    self.log('error', "Treatment failed")
                    return -1
                return i
        self.log('error', "Couldn't get a response from the server")
        return -1

    def movie_treatment(self, result):
        """
        Gets all the infos from a given movie.

        Args:
            result: Name of the movie to search.

        Returns:
            String: Returns if there are no results and None if there are.
        """

        if result:
            self.log('trace', result)

            title = result['originalTitle']
            description = result['overview']
            if not description:
                description = "Nothing found"
            poster_path = result['posterPath']
            media_type = result['mediaType']

            media_id = result['id']

            if media_id is not None:
                media_id = int(media_id)
            poster_path = "https://image.tmdb.org/t/p/w600_and_h900_bestv2" + \
                          poster_path

            poster = self.session.get(poster_path).content

            self.infos['title'] = title
            self.infos['description'] = description
            self.infos['media_id'] = media_id
            self.infos['media_type'] = media_type
            self.infos['poster'] = poster
            return None
        self.log('error', "No results")
        self.infos['title'] = None
        self.infos['description'] = None
        self.infos['media_id'] = None
        self.infos['media_type'] = None
        self.infos['poster'] = None
        return "No results"

    def add_movie(self, media_type, media_id, root_folder):
        """
        Searches for a movie with its name.

        Args:
            media_type: Type of media.
            media_id: Tmdb / tvdb id of a given media.
            root_folder: root_folder of Plex.

        Returns:
            String: A string ment to be outputed to represent the action
                    performed regarding the status of that particular movie.
        """

        url = self.overseerr_url + "/request"

        payload = {
          "mediaType": media_type,
          "mediaId": media_id,
          # "tvdbId": tvdb_id,
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

        headers = {"accept": "application/json"}

        req = self.session.post(url=url, headers=headers, json=payload)
        if req.status_code == 201:
            self.log('debug', "movie added")
            self.log('trace', req.text)
            return "Movie added"
        if req.status_code == 500:
            self.log('debug', "Movie already available")
            return "Movie already available"
        if req.status_code == 409:
            self.log('debug', "Already asked")
            return "Already asked"
        self.log('error', f"status code {req.status_code} : {req.text}")
        return "An error as occured, can't add movie"
