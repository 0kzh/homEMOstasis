from threading import Thread
import time
import requests
import azure.cosmos.errors as errors
from os import path
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.documents as documents


config = {
    'ENDPOINT': 'https://homeostasis.documents.azure.com:443/',
    'PRIMARYKEY': 'FBtGnYaiISXps1M1CAXpLyfzbNxbp0HDW2OKxDpieuVagoaMrFPR40CJ0MMjlyEVyNARuDJ5vZyT0NqiPLeeZg==',
    'DATABASE': 'CosmosDatabase',
    'CONTAINER': 'CosmosContainer'
}

positive = ['happiness', 'surprise']
negative = ['anger', 'sadness', 'contempt', 'disgust']

def fetchData(mode):
    
    if mode in negative:
        mode = "negative"
    else: 
        mode = "positive"

    client = cosmos_client.CosmosClient(url_connection=config['ENDPOINT'], auth={
                                        'masterKey': config['PRIMARYKEY']})
    query1 = 'SELECT c.messages FROM c WHERE c.emotion = ' + r'"' + mode + r'"'
    print(query1)

    # this part is used for getting insult messages    
    try:
        query = {'query': query1}
        options = {}
        options['enableCrossPartitionQuery'] = True
        message = "Document(s) found by query: "
        results = list(client.QueryItems('dbs/EmotionResponses/colls/Items', query, options))
        print(message)
        for doc in results:
            print(doc)
        return results
    except errors.HTTPFailure as e:
        if e.status_code == 404:
            print("Document doesn't exist")
        elif e.status_code == 400:
            # Can occur when we are trying to query on excluded paths
            print("Bad Request exception occured: ", e)
            pass
        else:
            raise
    finally:
        print()