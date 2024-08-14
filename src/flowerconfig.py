import os

auth_provider = "flower.views.auth.GithubLoginHandler"
auth = os.environ.get("FLOWER_AUTH", "joeriddles10@gmail.com")
oauth2_key = os.environ["FLOWER_OAUTH2_KEY"]
oauth2_secret = os.environ["FLOWER_OAUTH2_SECRET"]
oauth2_redirect_uri = os.environ.get("FLOWER_OAUTH2_REDIRECT_URI", "http://localhost:5555/login")
port = os.environ.get("FLOWER_PORT", "5555")
