import googlemaps
import logging
from config import config


class GymService:
    def __init__(self):
        self.GOOGLE_MAPS_API_KEY = config.GOOGLE_MAPS_API_KEY
        if not self.GOOGLE_MAPS_API_KEY:
            logging.error("Google Maps API key is not configured.")
            raise ValueError("Google Maps API key is missing.")
        self.gmaps = googlemaps.Client(key=self.GOOGLE_MAPS_API_KEY)

    # 找附近的健身房
    def find_nearby_gyms(
        self, latitude: float, longitude: float, radius: int
    ) -> list | None:
        user_location = (latitude, longitude)

        try:
            places_result = self.gmaps.places_nearby(
                location=user_location,
                keyword="健身房",
                radius=radius,
                language="zh-TW",
            )
            
            if not places_result or places_result.get('status') != 'OK' or 'results' not in places_result:
                logging.warning(f"Google Maps API did not return valid results. Status: {places_result.get('status')}")
                return None
                
            gyms = []
            for place in places_result.get("results", []):
                gym = {
                    "name": place.get("name", "未知健身房"),
                    "vincinity": place.get("vicinity", "地址未知"),
                }
                gyms.append(gym)

            return gyms

        except Exception as e:
            logging.error(f"Google Maps API error: {e}")
            return None
