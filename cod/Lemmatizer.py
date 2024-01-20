import nltk
from whoosh.analysis import Filter, RegexTokenizer, LowercaseFilter, StopFilter, STOP_WORDS

# nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer

from whoosh.analysis import Token

from whoosh.analysis import Token

class Lemmatizer(Filter):
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()

    def __call__(self, tokens):
        for t in tokens:
            lemmatized_text = self.lemmatizer.lemmatize(t.text)
            # applied on query
            yield Token(text=lemmatized_text, boost=t.boost, stopped=t.stopped, removestops=t.removestops, mode=t.mode)
            # applied on indexing
            # yield Token(text=lemmatized_text, pos=t.pos, boost=t.boost, stopped=t.stopped, removestops=t.removestops, mode=t.mode)
