import re

keywords_path = "./data/keywords.csv"

class KeywordsFinder(object):
    def __init__(self):
        self.kw = {}

        with open(keywords_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                w_class, w = line.split(",")
                self.kw[w.lower().strip()] = w_class.strip()

    def find_keywords(self, text):
        text = text.lower()

        result = []
        for w in self.kw:
            offsets = [m.start() for m in re.finditer(w, text)]
            for o in offsets:
                result.append({
                    'offset': o,
                    'type': self.kw[w],
                    'content': w
                })
            
        return result