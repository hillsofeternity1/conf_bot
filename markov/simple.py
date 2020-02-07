import random
from collections import deque
import re

class Dictogram(dict):
    def __init__(self, iterable=None):
        super(Dictogram, self).__init__()
        self.types = 0  
        self.tokens = 0  
        if iterable:
            self.update(iterable)

    def update(self, iterable):
        for item in iterable:
            if item in self:
                self[item] += 1
                self.tokens += 1
            else:
                self[item] = 1
                self.types += 1
                self.tokens += 1

    def count(self, item):
        if item in self:
            return self[item]
        return 0

    def return_random_word(self):
        random_key = random.sample(self, 1)
        return random_key[0]

    def return_weighted_random_word(self):
        random_int = random.randint(0, self.tokens-1)
        index = 0
        list_of_keys = list(self.keys())
        for i in range(0, self.types):
            index += self[list_of_keys[i]]
            if(index > random_int):
                return list_of_keys[i]

def get():
    def generate_random_start(model):
        if 'END' in model:
            seed_word = 'END'
            while seed_word == 'END':
                seed_word = model['END'].return_weighted_random_word()
            return seed_word
        return random.choice(list(model.keys()))


    def generate_random_sentence(length, markov_model):
        current_word = generate_random_start(markov_model)
        sentence = [current_word]
        for i in range(0, length):
            current_dictogram = markov_model[current_word]
            random_weighted_word = current_dictogram.return_weighted_random_word()
            current_word = random_weighted_word
            sentence.append(current_word)
        sentence[0] = sentence[0].capitalize()
        return ' '.join(sentence) + '.'
        return sentence

    def make_markov_model(data):
        markov_model = dict()

        for i in range(0, len(data)-1):
            if data[i] in markov_model:
                markov_model[data[i]].update([data[i+1]])
            else:
                markov_model[data[i]] = Dictogram([data[i+1]])
        return markov_model

    text = """
    Олег Соколов, преподававший в СПбГУ, в ноябре был задержан в Петербурге, 
    в его рюкзаке обнаружили две отпиленные женские руки. Соколов признался, 
    что убил и расчленил свою бывшую студентку Анастасию Ещенко, с которой 
    его связывали близкие отношения. Адвокат Соколова Александр Почуев заявлял, 
    что не исключает «и версию самооговора» его подзащитного и иные версии 
    преступления, «вплоть до мистических»."""

# simple cleanup
    text = text.replace('—','')
    text = text.replace('«','')
    text = text.replace('»','')
    text = text.replace('(','')
    text = text.replace(')','')
    text = "START " + text
    text = text.replace('.', ' END')

    text_list = text.split()
    model = make_markov_model(text_list)

    generated = generate_random_sentence(50, model)
    generated = generated.replace(' END', '.')
    print(generated)
