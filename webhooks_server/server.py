#!/usr/bin/env python3
import os
import json
import hmac
import cherrypy
from bots.starterbot import StarterBot

from devtools import debug

# Web server:
class WebhookServer(object):
    SECRET: str = os.environ.get("SECRET", '')
    BOT: StarterBot

    def __init__(self, bot_url: str) -> None:
        super().__init__()
        self.BOT = StarterBot()

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def webhook(self, *args, **kwargs):
        payload_json = cherrypy.request.json.get("payload", "{}")
        signature = cherrypy.request.headers["X-WEBHOOK-SIGNATURE"]
        self.webhook_called(payload_json, signature)

    # This function will be called each time the webhook endpoint is accessed
    def webhook_called(self, payload_json: str, signature: str):
        expected_signature = hmac.new(
            self.SECRET.encode(), payload_json.encode(), "sha256"
        ).hexdigest()
        if not hmac.compare_digest(expected_signature, signature):
            print("Ignoring request with invalid signature")
            return
        payload = json.loads(payload_json)
        print("Received webhook payload:\n" + json.dumps(payload, indent=4))

        event_name = payload.get("event", {}).get("event_name", "UNKNOWN")
        self.BOT.on_event_received(event_name, payload)


cherrypy.config.update(
    {
        # TODO: uncomment the following line after finishing development
        # 'environment': 'production',
        "server.socket_host": "0.0.0.0",
        "server.socket_port": 8003,
    }
)
