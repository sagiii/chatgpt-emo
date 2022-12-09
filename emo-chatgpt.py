"""
Emo Platform API python example connecting emo to GPTChat.
references:
https://github.com/mmabrouk/chatgpt-wrapper
https://platform-api.bocco.me/api-docs/#overview

Expected environment variables:
EMO_PLATFORM_API_REFRESH_TOKEN : Please refer to platform api doc
EMO_PLATFORM_API_ACCESS_TOKEN : Please refer to platform api doc
EMO_ROOM_NAME : Name string of target room
"""


import http.server
import json
import os
from chatgpt_wrapper import ChatGPT
from emo_platform import Client, EmoPlatformError, WebHook
from pyngrok import ngrok

bot = ChatGPT()

PORT = 8000
http_tunnel = ngrok.connect(PORT)

client = Client()
client.create_webhook_setting(WebHook(http_tunnel.public_url))
client.register_webhook_event(["message.received"])

rooms_list = client.get_rooms_list()
room_name = os.environ['EMO_ROOM_NAME']
room_uuid = next((item for item in rooms_list.dict()['rooms'] if item["name"] == room_name))['uuid']
print("Found a room. uuid = {}, name = {}.".format(room_uuid, room_name))
room = client.create_room_client(room_uuid)


@client.event("message.received")
def message_callback(body):
    print("message received")
    data = body.dict()
    # check if a message is from a room of interest
    if data['uuid'] != room_uuid:
        print("message is from another room. discard: {}".format(data))
        return
    # check if message is from emo
    if data['data']['message']['user']['uuid'] != room_uuid:
        print("message is not from emo. ignore: {}".format(data))
        return
    # extract message text from data
    from_emo = data['data']['message']['message']['ja']
    print("from emo = {}".format(from_emo))
    if len(from_emo) == 0:
        print("message is too short. ignore: {}".format(from_emo))
        return
    # FIXME : better be done asynchronously??
    # send text to bot
    print("will ask ChatGPT")
    from_bot = bot.ask(from_emo)
    print("response = {}".format(from_bot))
    # send response to emo
    EMO_MESSAGE_MAX_LENGTH = 250
    from_bot_chunks = [from_bot[i : i + EMO_MESSAGE_MAX_LENGTH] for i in range(0, len(from_bot), EMO_MESSAGE_MAX_LENGTH)]
    print("chunks = {}".format(from_bot_chunks))
    print("will send response to emo")
    for chunk in from_bot_chunks:
        room.send_msg(chunk)


secret_key = client.start_webhook_event()


# define localserver
class Handler(http.server.BaseHTTPRequestHandler):
    def _send_status(self, status):
        self.send_response(status)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()

    def do_POST(self):
        # check secret_key
        if not secret_key == self.headers["X-Platform-Api-Secret"]:
            self._send_status(401)
            return

        content_len = int(self.headers["content-length"])
        request_body = json.loads(self.rfile.read(content_len).decode("utf-8"))

        try:
            cb_func, emo_webhook_body = client.get_cb_func(request_body)
        except EmoPlatformError:
            self._send_status(501)
            return

        cb_func(emo_webhook_body)

        self._send_status(200)


# launch local server
with http.server.HTTPServer(("", 8000), Handler) as httpd:
    httpd.serve_forever()

# FIXME: need to diconnect ngrok??
