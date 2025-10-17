import logging
from flask import Flask, request, abort, send_from_directory
from linebot.v3.exceptions import InvalidSignatureError

from handlers.line_handler import handler

app = Flask(__name__)

app.logger.setLevel(logging.INFO)

# 靜態檔案路由
@app.route("/static/<path:filename>")
def static_files(path):
    return send_from_directory('assets', path)

# LINE Webhook 路由
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

if __name__ == "__main__":
    app.run()