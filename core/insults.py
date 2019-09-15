from numpy.random import choice
import random
import os
import requests

class InsultGenerator:
    def __init__(self):
        pass

    def gen_insult(self):
        formats = [self.steve, self.taunt, self.dad_joke]
        diss = choice(formats, 1, p=[0.0, 0.0, 1.0])[0]()
        return diss

    def taunt(self):
        start = ['Eat grass', 'Get wrecked', 'Bite me', 'Suck on that', 'Go make me a sandwich', 'Take a hike']
        adj_one = ["Lazy", "Stupid", "Insecure", "Idiotic", "Slimy", "Smelly", "Pompous", "Communist", "Pie-eating", "Elitist", "Drug-loving", "Butterface", "Tone deaf", "Ugly", "Creepy"]
        adj_two = ["turd", "butt", "fart", "nut", "Laurier", "puke"]
        noun = ["Steve", "pilot", "canoe", "captain", "pirate", "hammer", "knob", "box", "jockey", "waffle", "goblin", "blossum", "biscuit", "clown", "socket", "monster", "hound", "dragon", "balloon"]
        return random.choice(start) + ", you " + random.choice(adj_one) + " " + random.choice(adj_two) + " " + random.choice(noun)

    def dad_joke(self):
        r = requests.get('https://sv443.net/jokeapi/category/Dark')
        res = r.json()
        if (res['type'] == "twopart"):
            return r.json()['setup'] + ' .... ' + r.json()['delivery']
        else:
            return r.json()['joke']

    def steve(self):
        verbs = ['There is no meaning to our lives. No matter what we do during our time here it all comes to an end anyway. We lose the people we love, the careers we\'ve built, the memories of the things we\'ve done. Everything in the universe tends towards entropy. Smiling increases entropy and speeds up the heat death of the universe. So why smile?',
        'Steve', 'suck', 'throw', 'aim', 'drunk', 'play pong', 'Maintain the safety and wellbeing of countless Harvard John A. Paulson Scool of Engineering and Applied Sciences students in the Active Learning Labs through well run and organized safety training sessions.....']

        return 'You {} like Steve'.format(random.choice(verbs))