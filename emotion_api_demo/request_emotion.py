"""Define the thread of requesting the result from Emotion API."""

import time
from threading import Thread
import requests
from emotion_api_demo import get_response, queue as que

class RequestEmotion(Thread):
    """The class to request result from Emotion API."""
    def __init__(self, key, mode, source, plot, print_func):
        """Parameters
        ----------

        * key : (str)
            The key for Emotion API.

        * mode : (str)
            `local` for local raw image and `url` for URL online image.

        * source : (str)
            The link to the source (for either local or URL online).

        * plot : (ResultImg)
            The object of ResultImg to render result image.

        * print_func : (func)
            The function to print additional info.
        """
        super().__init__()
        self.key = key
        self.mode = mode
        self.source = source
        self.plot = plot
        self.print = print_func
    def run(self): ## Main function called by Thread.
        headers = dict()
        headers['Ocp-Apim-Subscription-Key'] = self.key
        if self.mode == 'url':
            headers['Content-Type'] = 'application/json'
            json = {'url': self.source}
            data, params = None, None
        else: 
            data = self.source
            headers['Content-Type'] = 'application/octet-stream'
            json, params = None, None
        result = self.process_request(json, data, headers, params)
        if result:
            self.print(result)
            emodict = result[0]["faceAttributes"]["emotion"]
            emotion = max(emodict, key=emodict.get)
            self.print(emotion)
            response = get_response.Response(emotion)

            # Call this on main thread:
            que.runOnMain(self.plot.draw_labels(result))
            
            # Start new thread to query for response given emotion. 
            response.start()

        else:
            self.print("Error: No result in API response.")

    def process_request(self, json, data, headers, params):
        """Request the API server.

        Parameters:
        -----------
        json: Used when processing images from its URL. See API Documentation
        data: Used when processing image read from disk. See API Documentation
        headers: Used to pass the key information and the data type request
        """

        max_retries_times = 10
        retries = 0
        result = None

        while True:
            url = 'https://facial-expression-detector.cognitiveservices.azure.com/face/v1.0/detect?returnFaceAttributes=emotion,smile'
            self.print("Set {} as the API request URL.".format(url))
            self.print("Waiting for the response...")
            response = requests.request('post',
                                        url,
                                        json=json,
                                        data=data,
                                        headers=headers,
                                        params=params)
            if response.status_code == 429:
                self.print("Message: {}".format(response.json()['error']['message']))
                if retries <= max_retries_times:
                    time.sleep(1)
                    retries += 1
                    continue
                else:
                    self.print("Error: failed after retrying.")
                    break
            elif response.status_code == 200 or response.status_code == 201:
                if 'content-length' in response.headers and int(response.headers['content-length']) == 0:
                    result = None
                elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):
                    if 'application/json' in response.headers['content-type'].lower():
                        result = response.json() if response.content else None
                    elif 'image' in response.headers['content-type'].lower():
                        result = response.content
            else:
                self.print("Error code: {}".format(response.status_code))
                self.print("Message: {}".format(response.json()['error']['message']))
            break
        return result
