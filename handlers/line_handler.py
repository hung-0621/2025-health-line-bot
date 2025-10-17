import json, logging
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent, LocationMessageContent
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from config import config
from services.AI_service import AIService
from services.eat_service import EatService
from services.gym_service import GymService
from services.life_service import LifeService
from services.mental_service import MentalHealthService
from utils.handle_line_template import LineTemplateHandler

configuration = Configuration(access_token=config.ACCESS_TOKEN)
handler = WebhookHandler(config.CHANNEL_SECRET)
line_template_handler = LineTemplateHandler()

INSTRUCTION_FILE_PATH = "assets/json/instruction.json" 


# 輔助函式：回覆訊息
def _reply_message(reply_token: str, messages: list):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(reply_token=reply_token, messages=messages)
        )


# 輔助函式：取得回復訊息
def _get_reply_message(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            instruction_data = json.load(f)
            reply_text = instruction_data["message"]
    except FileNotFoundError:
        reply_text = "功能異常，請回報管理員。"
    return reply_text


# 處理文字訊息
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_text = event.message.text
    reply_text = _get_reply_message(user_text)
    # todo 訊息處理邏輯
    if user_text == "操作說明":
        reply_text = _get_reply_message(INSTRUCTION_FILE_PATH)
    else:
        reply_text = "not implemented yet"

    _reply_message(event.reply_token, [TextMessage(text=reply_text)])


# 處理位置訊息
@handler.add(MessageEvent, message=LocationMessageContent)
def handle_location(event):
    latitude = event.message.latitude
    longitude = event.message.longitude
    radius = 100  # 搜尋半徑，單位為公尺

    gym_service = GymService()
    gyms = gym_service.find_nearby_gyms(latitude, longitude, radius)
    
    if not gyms:
        reply_text = "抱歉，找不到附近的健身房。"
        _reply_message(event.reply_token, [TextMessage(text=reply_text)])
        logging.info(f"No gyms found near ({latitude}, {longitude})")
        return
    else:
        carousel_template_message = line_template_handler.render_gym_template(gyms)

    if not carousel_template_message:
        reply_text = "抱歉，找不到合適的健身房資訊。"
    else:
        _reply_message(event.reply_token, [carousel_template_message])
