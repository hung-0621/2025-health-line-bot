from linebot.v3.messaging import (
    TemplateMessage,
    CarouselTemplate,
    CarouselColumn,
    URIAction,
)
from config import config
import urllib.parse

class LineTemplateHandler:
    def __init__(self) -> None:
       self.GYM_IMAGE_PATH = "../assets/images/gym.jpg"
    
    def render_gym_template(self, gyms: list) -> TemplateMessage:
        if not gyms:
            return TemplateMessage(alt_text='找不到健身房', template=CarouselTemplate(columns=[
                CarouselColumn(
                    title='查詢結果',
                    text='抱歉，在您附近找不到任何健身房。',
                    actions=[URIAction(label='重新搜尋', uri='line://nv/location')]
                )
            ]))

        columns = []
        for gym in gyms[:10]:
            # 處理文字長度，避免超過 LINE 的限制
            gym_name = (gym['name'][:37] + '...') if len(gym['name']) > 40 else gym['name']
            gym_vincinity = (gym['vincinity'][:57] + '...') if len(gym['vincinity']) > 60 else gym['vincinity']

            # 動態建立 Google Maps 搜尋 URL
            query = f"{gym['name']} {gym['vincinity']}"
            encoded_query = urllib.parse.quote(query)
            google_map_url = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"

            column = CarouselColumn(
                thumbnail_image_url=self.GYM_IMAGE_PATH,
                title=gym_name,
                text=gym_vincinity,
                actions=[
                    URIAction(
                        label='在地圖上查看',
                        uri=google_map_url
                    )
                ]
            )
            columns.append(column)

        carousel_template = CarouselTemplate(columns=columns)
        return TemplateMessage(alt_text='附近的健身房', template=carousel_template)