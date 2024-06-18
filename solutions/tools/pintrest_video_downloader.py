import os
import re
import cv2
import json
import requests
import urllib.request
from config import Config

CAPTURE_FRAME_RATE = 1000

class Pinterest:
    def __init__(self, url):
        self.url = url

    def is_url_valid(self):
        if re.match(r'(^http(s)?://)?(www.)?pinterest.\w+/pin/[\w\-?]+', self.url):
            return True
        return False

    def get_page_content(self):
        content = requests.get(self.url).text
        return content

    def is_a_video(self):
        if "video-snippet" in self.get_page_content():
            return True
        return False

    def get_media_link(self):
        if self.is_url_valid():
            try:
                if self.is_a_video():
                    match = re.findall(r'<script data-test-id="video-snippet".+?</script>', self.get_page_content())
                    j = json.loads(match[0].replace('<script data-test-id="video-snippet" type="application/ld+json">', "").replace("</script>", ""))
                    return {"type": "video", "link": j["contentUrl"], "success": True}
                else:
                    match = re.findall(r'<script data-test-id="leaf-snippet".+?</script>', self.get_page_content())
                    j = json.loads(match[0].replace('<script data-test-id="leaf-snippet" type="application/ld+json">', "").replace("</script>", ""))
                    return {"type": "image", "link": j["image"], "success": True}
            except:
                return {"type": "", "link": "", "success": False}
        else:
            return {"type": "", "link": "", "success": False}



def download_pinterest_video(url, save_with_name)-> bool:
    p = Pinterest(url)
    response = p.get_media_link()
    if(response['type']=="video" and response['success']==True):
        urllib.request.urlretrieve(response['link'], save_with_name)
        return True
    else:
        return False


def process_video_file(url, save_with_name)->bool:
    is_dowloaded_successfully = download_pinterest_video(url, save_with_name)
    if(is_dowloaded_successfully):
        cap = cv2.VideoCapture(save_with_name)
        if not cap.isOpened():
            print("Error: Unable to open video file.")
            return False

        try:
            if not os.path.exists(Config.SAVE_VIDEO_FILE_IN_FOLDER_NAME):
                os.makedirs(Config.SAVE_VIDEO_FILE_IN_FOLDER_NAME)
        except OSError:
            print ('Error: Creating directory of data')
            return False
        
        currentFrame = 0
        while(True):
            cap.set(cv2.CAP_PROP_POS_MSEC, currentFrame * Config.VIDEO_CAPTURE_FRAME_RATE)
            # Capture frame-by-frame
            ret, frame = cap.read()
            if ret:
                # Saves image of the current frame in jpg file
                name = Config.SAVE_VIDEO_FILE_ON_ROOT_PATH + Config.SAVE_FILE_NAME_WITH_HEAD + str(currentFrame) + '.jpg'
                print ('Creating...' + name)
                cv2.imwrite(name, frame)
                # To stop duplicate images
                currentFrame += 1
            else:
                break

        cap.release()
        cv2.destroyAllWindows()
        return True
