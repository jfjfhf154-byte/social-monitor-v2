import os
import json
import time
import logging
import datetime
import threading
from flask import Flask
from dotenv import load_dotenv

# Import trackers from separate files
from youtube_tracker import YouTubeTracker
from instagram_tracker import InstagramTracker
from tiktok_tracker import TikTokTracker
from roblox_tracker import RobloxTracker
from telegram_tracker import TelegramTracker
from pinterest_tracker import PinterestTracker
from image_generator import ImageGenerator

# Load environment variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ROBLOX_COOKIE = os.getenv("ROBLOX_COOKIE")

# Data file for persistence
DATA_FILE = "data.json"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flask app for Render health check
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Social Tracker Bot is running!", 200

class SocialBot:
    def __init__(self):
        self.image_gen = ImageGenerator()
        
        # Initialize trackers
        self.trackers = {
            "YouTube": YouTubeTracker("https://youtube.com/@taleencute9315?si=qoCGN_AouM3DVcRb"),
            "Instagram": InstagramTracker("tulyx_v"),
            "TikTok": TikTokTracker("tulyx_v"),
            "Roblox": RobloxTracker("qad4s", ROBLOX_COOKIE),
            "Telegram": TelegramTracker("tulyx_v"),
            "Pinterest": PinterestTracker("tulyx_v")
        }
        
        self.last_data = self.load_data()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_data(self, data):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def send_notification(self, platform, change_text):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        image_path = self.image_gen.generate_notification_image(platform, change_text, timestamp)
        
        # Send via Telegram API
        import requests
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        with open(image_path, 'rb') as photo:
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'caption': f"🚨 تحديث جديد في {platform}!\n📝 {change_text}\n⏰ {timestamp}"
            }
            files = {'photo': photo}
            try:
                response = requests.post(url, data=payload, files=files)
                if response.status_code == 200:
                    logger.info(f"Notification sent for {platform}")
                else:
                    logger.error(f"Failed to send notification: {response.text}")
            except Exception as e:
                logger.error(f"Error sending telegram notification: {e}")

    def check_for_changes(self):
        logger.info("Checking for changes...")
        new_all_data = {}
        
        for platform, tracker in self.trackers.items():
            try:
                current_data = tracker.get_data()
                if not current_data or "error" in current_data and current_data["error"]:
                    logger.warning(f"Skipping {platform} due to error: {current_data.get('error')}")
                    continue
                
                if platform in self.last_data:
                    changes = tracker.compare(self.last_data[platform], current_data)
                    if changes:
                        for change in changes:
                            self.send_notification(platform, change)
                
                new_all_data[platform] = current_data
            except Exception as e:
                logger.error(f"Error tracking {platform}: {e}")
        
        # Update persistence
        if new_all_data:
            self.last_data.update(new_all_data)
            self.save_data(self.last_data)

    def run_loop(self):
        logger.info("Monitoring loop started...")
        # Initial run
        self.check_for_changes()
        
        while True:
            # Check every 15 minutes
            time.sleep(900)
            self.check_for_changes()

def start_bot_thread():
    bot = SocialBot()
    bot.run_loop()

if __name__ == "__main__":
    # Start monitoring in background
    t = threading.Thread(target=start_bot_thread)
    t.daemon = True
    t.start()
    
    # Start Flask for Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
