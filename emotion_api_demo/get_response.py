from threading import Thread
import time
import requests
import os
import azure.cosmos.cosmos_client as cosmos_client

class Response(Thread):
    def __init__(self, emotion):
        super().__init__()

        config = {
            'ENDPOINT': 'https://homeostasis.documents.azure.com:443/',
            'PRIMARYKEY': 'FBtGnYaiISXps1M1CAXpLyfzbNxbp0HDW2OKxDpieuVagoaMrFPR40CJ0MMjlyEVyNARuDJ5vZyT0NqiPLeeZg==',
            'DATABASE': 'CosmosDatabase',
            'CONTAINER': 'CosmosContainer'
        }

        # Initialize the Cosmos client
        client = cosmos_client.CosmosClient(url_connection=config['ENDPOINT'], auth={
                                            'masterKey': config['PRIMARYKEY']})

        try:
            # All Azure Cosmos resources are addressable via a link
            # This link is constructed from a combination of resource hierachy and 
            # the resource id. 
            # Eg. The link for database with an id of Foo would be dbs/Foo
            print("0")
            database_link = 'dbs/EmotionResponses'
            print("1")

            database = client.ReadDatabase(database_link)
            print('Database with id \'{0}\' was found, it\'s _self is {1}'.format(id, database['_self']))

        except errors.HTTPFailure as e:
            if e.status_code == 404:
                print('A database with id \'{0}\' does not exist'.format(id))
            else: 
                raise
        self.emotion = emotion
        self.key = ""

        # For file debug
        script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
        rel_path = "../logs/debug.log"
        abs_file_path = os.path.join(script_dir, rel_path)

        self.print = open(abs_file_path, "a")
        self.print.write("Hello world!")

    def fetchData(self):
        # Add query code here.
        pass

    def run(self): 
        ## Main function called by Thread.
        headers = dict()
        headers['Ocp-Apim-Subscription-Key'] = self.key
            
        headers['Content-Type'] = 'application/json'
        json = {'emotion': self.emotion}

        result = self.process_request(json, headers, None)

        if result:
            self.print.write("Placeholder.jpg")

        else:
            self.print.write("Error: No result in API response.")

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
            self.print.write("Set {} as the API request URL.".format(url))
            self.print.write("Waiting for the response...")
            response = requests.request('post',
                                        url,
                                        json=json,
                                        headers=headers,
                                        params=params)
            if response.status_code == 429:
                self.print.write("Message: {}".format(response.json()['error']['message']))
                if retries <= max_retries_times:
                    time.sleep(1)
                    retries += 1
                    continue
                else:
                    self.print.write("Error: failed after retrying.")
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
                self.print.write("Error code: {}".format(response.status_code))
                self.print.write("Message: {}".format(response.json()['error']['message']))
            break
        return result

