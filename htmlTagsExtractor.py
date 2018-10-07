from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def _my_hack_init(self, text):
        self.text = text
        self.prepared_text = ''
        self.html_tags_offsets = []
        self.raw_text = ''
        self.prev_text_end = 0
    
    def handle_data(self, data):
        
        text_start = self.getpos()[1]
        text_end = text_start + len(data)
        
        # TODO: there are some encoding problem, try to parse this:
        # https://wiki.swap.online/decentralized-exchange-of-bitcoins-for-altcoins-right-in-the-browser-live-demo
        # if self.text[text_start: text_end] != data:
        #     print(self.text[text_start: text_end], '|||', data)
        #     print((len(self.raw_text), self.text[self.prev_text_end: text_start]))
        #     print()
        
        self.html_tags_offsets.append((len(self.raw_text), self.text[self.prev_text_end: text_start]))
        self.prev_text_end = text_end
        self.raw_text += self.text[text_start: text_end]  # can't use 'data' - encoding problem

def extract_tags(html_string):
    # removing '\n', '\t', '  '
    html_string = ' '.join(html_string.split())

    parser = MyHTMLParser()
    parser._my_hack_init(html_string)
    parser.feed(html_string)
    return (parser.html_tags_offsets, parser.raw_text)