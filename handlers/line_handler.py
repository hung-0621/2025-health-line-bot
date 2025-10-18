import json, logging
from linebot import LineBotApi
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
line_bot_api = LineBotApi(config.ACCESS_TOKEN)

REPLY_MESSAGE_FILE_PATH = "assets/json/reply_message.json"


# 輔助函式：回覆訊息
def _reply_message(reply_token: str, messages: list):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(reply_token=reply_token, messages=messages)
        )


# 輔助函式：取得回復訊息
def _get_reply_message(title: str, file_path: str = REPLY_MESSAGE_FILE_PATH) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reply_data_list = json.load(f)
            
            # 3. 迭代列表，尋找相符的 title
            for item in reply_data_list:
                if item.get("title") == title:
                    return item.get("message", "訊息內容不存在。") # 回傳對應的 message
            
            # 如果迴圈結束後都沒找到
            logging.warning(f"Title '{title}' not found in {file_path}")
            return "抱歉，找不到對應的說明文字。"

    except FileNotFoundError:
        logging.error(f"Reply message file not found at: {file_path}")
        return "功能異常：找不到回覆訊息檔案，請回報管理員。"
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from file: {file_path}")
        return "功能異常：回覆訊息檔案格式錯誤，請回報管理員。"
    except Exception as e:
        logging.error(f"An unexpected error occurred in _get_reply_message: {e}")
        return "功能發生未知錯誤，請回報管理員。"


# 處理文字訊息
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_text = event.message.text
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)
    user_name = profile.display_name
    
    # 訊息處理邏輯
    if user_text == "*操作說明*":
        reply_text = _get_reply_message(title="*操作說明*")
    elif user_text == "*健康評估*":
        liff_url = f"https://liff.line.me/{config.LIFF_ID}"
        reply_text = _get_reply_message(title="*健康評估*") + liff_url + "\n"
    else:
        ai_service = AIService()
        reply_text = ai_service.generate_response(user_text)

    _reply_message(event.reply_token, [TextMessage(text=reply_text)])


# 處理位置訊息
@handler.add(MessageEvent, message=LocationMessageContent)
def handle_location(event):
    latitude = event.message.latitude
    longitude = event.message.longitude
    radius = 500  # 搜尋半徑，單位為公尺

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
