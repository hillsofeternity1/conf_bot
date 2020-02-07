from .histograms import Dictogram
import random
from collections import deque
import re


class MarkovChain:
    def __init__(self, text=str()):
        self.length = 25
        self.text = text
        self.text_list = None
        self._prepare_list()
        self.model = self._gen_model()

    def _prepare_list(self):
        if isinstance(self.text, str):
            self._clean_text()
            self.text_list = self.text.split()
        else:
            raise TypeError

    def _clean_text(self):
        text = self.text.replace('—','')
        text = self.text.replace('«','')
        text = self.text.replace('»','')
        text = self.text.replace('(','')
        text = self.text.replace(')','')
        text = self.text.replace('.','')
        text = self.text.replace(',','')
        self.text = text
        print(self.text)

    def _gen_model(self):
        data = self.text_list
        if data is None:
            raise TypeError
        markov_model = dict()
        for i in range(0, len(data)-1):
            if data[i] in markov_model:
                markov_model[data[i]].update([data[i+1]])
            else:
                markov_model[data[i]] = Dictogram([data[i+1]])
        return markov_model

    def _generate_random_start(self):
        model = self.model
        # Чтобы сгенерировать любое начальное слово, раскомментируйте строку:
        return random.choice(list(model.keys()))

        # Чтобы сгенерировать "правильное" начальное слово, используйте код ниже:
        # Правильные начальные слова - это те, что являлись началом предложений в корпусе
        if 'END' in model:
            seed_word = 'END'
            while seed_word == 'END':
                seed_word = model['END'].return_weighted_random_word()
            return seed_word
        return random.choice(list(model.keys()))


    def generate_random_sentence(self):
        markov_model = self.model
        length = self.length if len(self.text_list) > self.length else len(self.text_list) - 1
        current_word = self._generate_random_start()
        sentence = [current_word]
        for i in range(0, length):
            try:
                current_dictogram = markov_model[current_word]
                random_weighted_word = current_dictogram.return_weighted_random_word()
                current_word = random_weighted_word
                sentence.append(current_word)
            except KeyError:
                pass
        sentence[0] = sentence[0].capitalize()
        return ' '.join(sentence) + '.'
