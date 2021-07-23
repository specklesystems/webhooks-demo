import os
import cherrypy
from webhooks_server.server import WebhookServer


def main():
    cherrypy.quickstart(WebhookServer(os.environ.get("DISCORD_URL")))


if __name__ == "__main__":
    main()
