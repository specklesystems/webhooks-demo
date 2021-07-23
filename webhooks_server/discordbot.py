import os
import json
import base64
import requests
from urllib.parse import quote
from specklepy.api import client
from specklepy.api.client import SpeckleClient
from devtools import debug

COLOURS = {
    "speckle blue": 295163,
    "spark": 119293,
    "futures": 9011703,
    "funk": 6771167,
    "majestic": 2960090,
    "lightning": 14204694,
    "data yellow": 16508501,
    "twist": 6872905,
    "mantis": 2266732,
    "flavour": 12999895,
    "environment": 11469515,
    "red": 16532034,
}


class DiscordBot(object):
    DISCORD_URL: str = ""
    SPECKLE_LOGO: str = "https://avatars.githubusercontent.com/u/65039012?s=200&v=4"

    def __init__(self, url: str) -> None:
        self.DISCORD_URL = url

    def on_event_received(self, event, payload):
        method = getattr(self, f"on_{event}", None)
        if not method:
            print(f"Event {event} not supported.")
            return

        method(
            payload["server"],
            payload["user"],
            payload["stream"],
            payload["webhook"],
            payload["event"].get("data", {}),
        )

    def get_message_template(self):
        return {
            "username": "Speckle",
            "avatar_url": self.SPECKLE_LOGO,
            "embeds": [
                {
                    "author": {
                        "name": "speckle user",
                        "url": "",
                        "icon_url": self.SPECKLE_LOGO,
                    },
                    "title": "",
                    "url": "",
                    "description": "",
                    "color": 295163,
                    "image": {"url": None},
                }
            ],
            "files": [],
        }

    def add_author(self, msg, user_info, server_url):
        avatar = user_info["avatar"]
        if avatar and not avatar.startswith("http"):
            type = avatar[5:].split(";")[0]
            filename = f"avatar.{type.split('/')[1]}"
            msg["files"].append(
                (
                    "file",
                    (
                        filename,
                        (base64.b64decode(avatar.split(",")[1])),
                        type,
                    ),
                )
            )
            avatar = f"attachment://{filename}"

        msg["embeds"][0]["author"].update(
            {
                "name": user_info["name"],
                "url": f"{server_url}/profile/{user_info['id']}",
                "icon_url": avatar or self.SPECKLE_LOGO,
            }
        )

    def send_to_discord(self, message: str):
        files = message.pop("files")
        debug(message)
        files.append(("payload_json", (None, json.dumps(message))))
        res = requests.post(self.DISCORD_URL, files=files)
        debug(res)

    def on_stream_update(
        self, server_info, user_info, stream_info, webhook_info, event_info
    ):
        server_url = server_info["canonicalUrl"].rstrip("/")
        msg = self.get_message_template()
        msg["embeds"][0].update(
            {
                "title": f"Stream Updated: [{stream_info['name']}]",
                "url": f"{server_url}/streams/{stream_info['id']}",
                "description": f"{user_info['name']} updated stream `{stream_info['id']}`",
                "color": COLOURS["speckle blue"],
                "fields": [
                    {
                        "name": "Old",
                        "value": f"**Name:** {event_info['old']['name']}\n**Description:** {event_info['old']['description'] if len(event_info['old']['description']) < 30 else event_info['old']['description'][:30] + '...'}\n**Is Public:** {event_info['old']['isPublic']}",
                        "inline": True,
                    },
                    {
                        "name": "Updated",
                        "value": f"**Name:** {event_info['new']['name']}\n**Description:** {event_info['new']['description'] if len(event_info['new']['description']) < 30 else event_info['new']['description'][:30] + '...'}\n**Is Public:** {event_info['new']['isPublic']}",
                        "inline": True,
                    },
                ],
                "image": {"url": f"{server_url}/preview/{stream_info['id']}"},
            }
        )
        self.add_author(msg, user_info, server_url)
        self.send_to_discord(msg)

    # def on_stream_permissions_add(
    #     self, server_info, user_info, stream_info, webhook_info, event_info
    # ):
    #     msg = self.get_message_template()

    # def on_stream_permissions_remove(
    #     self, server_info, user_info, stream_info, webhook_info, event_info
    # ):
    #     msg = self.get_message_template()

    def on_commit_create(
        self, server_info, user_info, stream_info, webhook_info, event_info
    ):
        server_url = server_info["canonicalUrl"].rstrip("/")

        commit_id = event_info["id"]
        commit_info = event_info["commit"]

        client = SpeckleClient(host=server_url, use_ssl=False)
        client.authenticate(os.environ.get("SPECKLE_TOKEN"))
        commit_obj = client.object.get(stream_info["id"], commit_info["objectId"])
        obj_count = getattr(commit_obj, "totalChildrenCount", "_unknown_")

        msg = self.get_message_template()
        msg["embeds"][0].update(
            {
                "title": f"Commit Created on {stream_info['name']}/{commit_info['branchName']}",
                "url": f"{server_url}/streams/{stream_info['id']}/commits/{commit_id}",
                "description": f"{user_info['name']} created a new commit `{commit_id}`",
                "color": COLOURS["futures"],
                "fields": [
                    {
                        "name": "Message",
                        "value": commit_info["message"] or "_No message provided_",
                    },
                    {
                        "name": "Source",
                        "value": commit_info["sourceApplication"] or "_unknown_",
                    },
                    {"name": "Object Count", "value": obj_count},
                    {"name": "Object Id", "value": commit_info["objectId"]},
                ],
            }
        )
        self.add_author(msg, user_info, server_url)
        self.send_to_discord(msg)

    def on_commit_update(
        self, server_info, user_info, stream_info, webhook_info, event_info
    ):
        server_url = server_info["canonicalUrl"].rstrip("/")

        commit_info = event_info["old"]

        msg = self.get_message_template()
        msg["embeds"][0].update(
            {
                "title": f"Commit Updated on [{stream_info['name']}]/{commit_info['branchName']}",
                "url": f"{server_url}/streams/{stream_info['id']}/commits/{commit_info['id']}",
                "description": f"{user_info['name']} updated  commit `{commit_info['id']}` on branch {commit_info['branchName']}",
                "color": COLOURS["spark"],
                "fields": [
                    {
                        "name": "Old",
                        "value": f"{commit_info['message']}",
                        "inline": True,
                    },
                    {
                        "name": "Updated",
                        "value": f"{event_info['new']['message']}",
                        "inline": True,
                    },
                ],
                "image": {
                    "url": None
                    if commit_info["branchName"] == "globals"
                    else f"{server_url}/preview/{stream_info['id']}/commits/{commit_info['id']}"
                },
            }
        )
        self.add_author(msg, user_info, server_url)
        self.send_to_discord(msg)

    def on_branch_create(
        self, server_info, user_info, stream_info, webhook_info, event_info
    ):
        server_url = server_info["canonicalUrl"].rstrip("/")
        branch = event_info["branch"]
        msg = self.get_message_template()
        msg["embeds"][0].update(
            {
                "title": f"Branch Created: [{stream_info['name']}]/{branch['name']}",
                "url": f"{server_url}/streams/{stream_info['id']}/branches/{quote(branch['name'])}",
                "description": f"{user_info['name']} created branch `{branch['id']}` on stream _{stream_info['name']}_ (`{stream_info['id']}`)",
                "color": COLOURS["twist"],
                "fields": [
                    {
                        "name": "Name",
                        "value": branch["name"],
                    },
                    {
                        "name": "Description",
                        "value": branch["description"]
                        or "_No branch description given_",
                    },
                ],
            }
        )
        self.add_author(msg, user_info, server_url)
        self.send_to_discord(msg)

    def on_branch_update(
        self, server_info, user_info, stream_info, webhook_info, event_info
    ):
        server_url = server_info["canonicalUrl"].rstrip("/")
        branch = event_info["new"]
        msg = self.get_message_template()
        msg["embeds"][0].update(
            {
                "title": f"Branch Updated: [{stream_info['name']}]/{branch['name']}",
                "url": f"{server_url}/streams/{stream_info['id']}/branches/{quote(branch['name'])}",
                "description": f"{user_info['name']} updated branch `{branch['id']}` on stream _{stream_info['name']}_ (`{stream_info['id']}`)",
                "color": COLOURS["mantis"],
                "fields": [
                    {
                        "name": "Old",
                        "value": f"**Name:** {event_info['old']['name']}\n**Description:** {event_info['old']['description']}",
                        "inline": True,
                    },
                    {
                        "name": "Updated",
                        "value": f"**Name:** {branch['name']}\n**Description:** {branch['description']}",
                        "inline": True,
                    },
                ],
            }
        )
        self.add_author(msg, user_info, server_url)
        self.send_to_discord(msg)

    def on_branch_delete(
        self, server_info, user_info, stream_info, webhook_info, event_info
    ):
        server_url = server_info["canonicalUrl"].rstrip("/")
        branch = event_info["branch"]
        msg = self.get_message_template()
        msg["embeds"][0].update(
            {
                "title": f"Branch Deleted: [{stream_info['name']}]/{branch['name']}",
                "url": f"{server_url}/streams/{stream_info['id']}/branches",
                "description": f"{user_info['name']} deleted branch `{branch['id']}` on stream _{stream_info['name']}_ (`{stream_info['id']}`)",
                "color": COLOURS["red"],
            }
        )
        self.add_author(msg, user_info, server_url)
        self.send_to_discord(msg)
