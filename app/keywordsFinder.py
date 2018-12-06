import re

keywords_path = "./data/keywords.csv"
lexicons_path = "./data/lexicons_compiled.csv"

class KeywordsFinder(object):
    def __init__(self):
        self.kw = {}

        with open(keywords_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                w_class, w = line.split(",")
                self.kw[w.lower().strip()] = w_class.strip()

        with open(lexicons_path, 'r') as f:
            lines = f.readlines()
            for line in lines[1:]:
                w, emotion, color, orientation, sentiment, subjectivity, source = line.split(",")
                if subjectivity == "strong":
                    self.kw[w.lower().strip()] = "subjectivity"

    def find_keywords(self, text):
        text = text.lower()

        result = []
        for w in self.kw:
            # TODO: find words in subset of words, not in whole text
            # I added spaces to find words, not part of other words
            offsets = [m.start() for m in re.finditer(" %s " % w, text)]
            for o in offsets:
                result.append({
                    'offset': o + 1,
                    'type': self.kw[w],
                    'content': w
                })
            
        return result