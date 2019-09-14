from threading import Thread
import time
import requests



class Response(Thread):
    def __init__(self, emotion, output):
        super().__init__()
        self.emotion = emotion
        self.key = ""
        self.output = output ## Not caring about deadlock references for now.

    def run(self): 
        ## Main function called by Thread.
        headers = dict()
        headers['Ocp-Apim-Subscription-Key'] = self.key
            
        headers['Content-Type'] = 'application/json'
        json = {'emotion': self.emotion}

        result = self.process_request(json, headers, None)

        if result:
            self.output("Placeholder.jpg")

        else:
            self.output("Error: No result in API response.")
    def process_request(self, json, headers, params):
        """(Pulled from request_emotions) Request the API server.

        Parameters:
        -----------
        json: Used when processing images from its URL. See API Documentation
        headers: Used to pass the key information and the data type request
        """

        max_retries_times = 10
        retries = 0
        result = None

        while True:
            url = 'https://facial-expression-detector.cognitiveservices.azure.com/face/v1.0/detect?returnFaceAttributes=emotion,smile'
            self.output("Set {} as the API request URL.".format(url))
            self.output("Waiting for the response...")
            response = requests.request('post',
                                        url,
                                        json=json,
                                        headers=headers,
                                        params=params)
            if response.status_code == 429:
                self.output("Message: {}".format(response.json()['error']['message']))
                if retries <= max_retries_times:
                    time.sleep(1)
                    retries += 1
                    continue
                else:
                    self.output("Error: failed after retrying.")
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
                self.output("Error code: {}".format(response.status_code))
                self.output("Message: {}".format(response.json()['error']['message']))
            break
        return result

        