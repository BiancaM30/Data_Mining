from whoosh.analysis import Filter, Token
from nltk.corpus import wordnet

class SynonymFilter(Filter):
    def __call__(self, tokens):
        for token in tokens:
            yield token
            for syn in wordnet.synsets(token.text):
                for lemma in syn.lemmas():
                    synonym = lemma.name().replace('_', ' ')
                    if synonym != token.text:
                        # applied on query
                        yield Token(text=synonym, boost=token.boost, stopped=token.stopped, removestops=token.removestops, mode=token.mode)
                        # applied on indexing
                        # yield Token(text=synonym, pos=token.pos, boost=token.boost, stopped=token.stopped, removestops=token.removestops, mode=token.mode)

