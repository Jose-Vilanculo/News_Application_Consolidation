import os
import json
from requests_oauthlib import OAuth1Session


class Tweet():

    _instance = None
    TOKEN_FILE = "twitter_token.json"

    CONSUMER_KEY = 'Enter Consumer Key Here'
    CONSUMER_SECRET = 'Enter Consumer Secret Here'

    TWITTER_SUPPORTED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif'}

    def __new__(cls):
        """This code will determine whether a class instance of Tweet exists.

        Returns:
            If it does exist , it returns the current instance,
            if it doesn't, a new instance will be created and returned.
        """
        if cls._instance is None:
            cls._instance = super(Tweet, cls).__new__(cls)
            cls._instance.authenticate()

        return cls._instance

    def authenticate(self):
        """
        Authenticate with the Twitter API using OAuth1.

        Behavior:
            - If an access token file exists, it loads credentials from it.
            - If not, it initiates the OAuth flow:
                - Fetches request token
                - Prompts user to authorize via a browser link
                - Exchanges verifier PIN for an access token
                - Saves the token to disk for reuse

        Side Effects:
            - Sets `self.oauth` to an authenticated OAuth1Session.
            - Writes token data to `self.TOKEN_FILE`.

        Raises:
            ValueError: If consumer key/secret is invalid.
            Exception: On failure during any request or user input step.
        """

        # Check first if token file already exists
        if os.path.exists(self.TOKEN_FILE):
            with open(self.TOKEN_FILE, "r") as f:
                token_data = json.load(f)
                print("loaded access token from file.")
                # Make the request object
                self.oauth = OAuth1Session(
                    self.CONSUMER_KEY,
                    client_secret=self.CONSUMER_SECRET,
                    resource_owner_key=token_data["oauth_token"],
                    resource_owner_secret=token_data["oauth_token_secret"]
                )
                response = self.oauth.get(
                    "https://api.twitter.com/1.1/account"
                    "/verify_credentials.json"
                )
                print(response.json())  # Shows which user is authenticated

                return

        # Start OAuth process from scratch
        print("Authenticating with Twitter...")
        # Get request token
        request_token_url = (
            "https://api.twitter.com/oauth/request_token"
            "?oauth_callback=oob&x_auth_access_type=write"
        )
        oauth = OAuth1Session(
            self.CONSUMER_KEY,
            client_secret=self.CONSUMER_SECRET
        )

        try:
            fetch_response = oauth.fetch_request_token(request_token_url)
        except ValueError:
            print(
                "There may have been an issue with the consumer_key"
                " or consumer_secret you entered"
            )

        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")
        print(f"Got OAuth token: {resource_owner_key}")

        # Get authorization
        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauth.authorization_url(base_authorization_url)
        print(f"Please go here and authorize: {authorization_url}")
        verifier = input("Paste the PIN here: ")

        # Get the access token
        access_token_url = "https://api.twitter.com/oauth/access_token"
        oauth = OAuth1Session(
            self.CONSUMER_KEY,
            client_secret=self.CONSUMER_SECRET,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier,
        )
        oauth_token = oauth.fetch_access_token(access_token_url)

        access_token = oauth_token.get("oauth_token")
        access_token_secret = oauth_token.get("oauth_token_secret")

        # Save in file for future use
        with open(self.TOKEN_FILE, "w") as f:
            json.dump({
                "oauth_token": access_token,
                "oauth_token_secret": access_token_secret
            }, f)
        print("Access token saved for future use.")

        # Make the request object
        self.oauth = OAuth1Session(
            self.CONSUMER_KEY,
            client_secret=self.CONSUMER_SECRET,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret
        )

    def make_tweet(self, text):
        """
        Post a tweet to the Twitter API.

        Args:
            text (str): The main tweet content
            (will be trimmed to 280 characters).

        Returns:
            None

        Behavior:
            - Posts the tweet via Twitter API v2.
            - Handles errors silently, logging them to console.

        Raises:
            RuntimeError: If authentication was not completed.
            Exception: If tweet submission fails.
        """
        # twitter api only allows 280 characters
        tweet_data = {"text": text.strip()[:280]}

        try:
            if not hasattr(self, 'oauth') or not self.oauth:
                raise RuntimeError("Twitter OAuth session is not initialized.")

            # Making the request
            response = self.oauth.post(
                "https://api.twitter.com/2/tweets",
                json=tweet_data,
            )

            if response.status_code != 201:
                raise Exception(
                    "request returned an error: {} - {}".format(
                        response.status_code, response.text
                    )
                )
        except Exception as e:
            print(f"[Tweet] Exception while sending tweet: {e}")
            return

        print("Response code: {}".format(response.text))

        # Saving the response as JSON
        json_response = response.json()
        print(json.dumps(json_response, indent=4, sort_keys=True))
