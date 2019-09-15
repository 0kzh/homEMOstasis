from numpy.random import choice
import random
import os
import requests

class InsultGenerator:
    def __init__(self):
        pass

    def gen_insult(self):
        return self.insult()

    def insult(self):
        r = requests.get('https://evilinsult.com/generate_insult.php?lang=en&type=json')
        return r.json()['insult']