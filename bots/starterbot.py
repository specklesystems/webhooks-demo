from specklepy.api.wrapper import StreamWrapper
from devtools import debug


class StarterBot(object):
    def __init__(self) -> None:
        # set some additional class attrs if you need them here
        pass

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

    def on_commit_create(
        self, server_info, user_info, stream_info, webhook_info, event_info
    ):
        server_url = server_info["canonicalUrl"].rstrip("/")
        commit_id = event_info["id"]
        commit_info = event_info["commit"]

        wrapper = StreamWrapper(f"{server_url}/streams/{stream_info['id']}")
        client = wrapper.get_client()
        commit_obj = client.object.get(stream_info["id"], commit_info["objectId"])

    # def on_stream_update(
    #     self, server_info, user_info, stream_info, webhook_info, event_info
    # ):
    #     pass

    # def on_branch_update(
    #     self, server_info, user_info, stream_info, webhook_info, event_info
    # ):
    #     pass

    # def on_branch_delete(
    #     self, server_info, user_info, stream_info, webhook_info, event_info
    # ):
    #     pass
