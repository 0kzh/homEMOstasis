# store for current emotion
emotion = 'neutral'

def set_emotion(val):
    global emotion 
    emotion = val

def get_emotion():
    global emotion
    return emotion