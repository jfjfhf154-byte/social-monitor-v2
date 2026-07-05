import requests
from bs4 import BeautifulSoup
import json
import re

def get_youtube_stats(channel_url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        response = requests.get(channel_url, headers=headers)
        
        match = re.search(r'var ytInitialData = ({.*?});</script>', response.text)
        if match:
            data = json.loads(match.group(1))
            
            try:
                # محاولة الوصول للواجهة الجديدة
                header = data['header']['pageHeaderRenderer']['content']['pageHeaderViewModel']
                metadata = header['metadata']['contentMetadataViewModel']['metadataRows'][1]['metadataParts']
                
                subscribers = metadata[0]['text']['content']
                videos = metadata[1]['text']['content']
                
                return {
                    "subscribers": subscribers,
                    "videos": videos,
                    "error": None
                }
            except (KeyError, IndexError) as e:
                try:
                    # محاولة الوصول للواجهة القديمة
                    header = data['header']['c4TabbedHeaderRenderer']
                    subscribers = header['subscriberCountText']['simpleText']
                    videos = header['videosCountText']['runs'][0]['text']
                    return {
                        "subscribers": subscribers,
                        "videos": videos,
                        "error": None
                    }
                except KeyError:
                    return {"error": "فشل في تحليل هيكل البيانات"}
                
        return {"error": "لم يتم العثور على ytInitialData"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print(get_youtube_stats("https://youtube.com/@taleencute9315"))
