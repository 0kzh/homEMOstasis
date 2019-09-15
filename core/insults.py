from numpy.random import choice
import random
import os
import requests
from query import fetchData
import core.emotion as e

class InsultGenerator:
    def __init__(self):
        pass

    def gen_insult(self):
        return self.insult()

    def insult(self):
        #r = requests.get('https://evilinsult.com/generate_insult.php?lang=en&type=json')
        r = fetchData(e.get_emotion)
        list_res = r[0].get('messages')
        size = len(list_res)
        ran_num = random.randint(0, size-1)
        print("hello: " + list_res[ran_num].get('msg'))
        return list_res[ran_num].get('msg')
        #return r.json()['insult']