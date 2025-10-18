import os, logging, json
from flask import Flask, request, abort, jsonify, render_template, send_from_directory
from linebot.v3.exceptions import InvalidSignatureError
from handlers.line_handler import handler
from config import config

app = Flask(__name__)

app.logger.setLevel(logging.INFO)


# --- 前端頁面路由 ---
@app.route("/form")
def form_page():
    liff_id_form = config.LIFF_ID_FORM
    return render_template("html/form.html", liff_id=liff_id_form)


# 取得問卷題目路由
@app.route("/api/questions/<category>", methods=["GET"])
def get_questions(category):
    json_path = os.path.join(app.root_path, "assets", "json", "form_question.json")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            all_questions = json.load(f)
        for cat_data in all_questions:
            # 使用 category 進行比對
            if cat_data.get("category") == category:
                return jsonify(cat_data)
        return jsonify({"error": f"Category '{category}' not found."}), 404
    except FileNotFoundError:
        return jsonify({"error": "Question file not found."}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to decode JSON file."}), 500


# 表單提交處理路由
@app.route("/submit-form", methods=["POST"])
def submit_form():
    data = request.json
    app.logger.info(f"Received form submission: {data}")
    return jsonify({"status": "success", "message": "資料已成功提交！"})


# LINE Webhook 路由
@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        abort(400)

    return "OK"


if __name__ == "__main__":
    app.run()
