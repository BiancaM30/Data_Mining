from whoosh import query
from nltk.corpus import wordnet
from whoosh.index import open_dir
from whoosh.query import Term


def get_synonyms(term):
    """
        Retrieves a list of synonyms for a given term using the WordNet lexical database.
        It returns a list of unique synonyms, excluding the original term itself.

        Parameters:
        - term (str): The term for which synonyms are to be found.

        Returns:
        - list: A list of synonym strings for the given term.
    """
    synonyms = set()
    for synset in wordnet.synsets(term):
        for lemma in synset.lemmas():
            synonym = lemma.name().replace('_', ' ').lower()
            if synonym != term:
                synonyms.add(synonym)
    return list(synonyms)


def get_all_categories(index):
    """
        Retrieves all unique categories from the documents in the given search index.

        Parameters:
        - index (Index object): The search index from which to retrieve categories.

        Returns:
        - set: A set of unique category strings found in the index.
    """
    with index.searcher() as searcher:
        all_documents_query = query.Every()
        results = searcher.search(all_documents_query)
        categories = set()
        for result in results:
            if 'category' in result:
                category_list = result['category'].split(',')
                categories.update(category.strip() for category in category_list)
                print(f"Document ID: {result.docnum}, Categories: {category_list}")
        return categories


def get_documents_info(index_dir):
    """
        Retrieves all document titles along with their categories from the search index directory.

        Parameters:
        - index_dir (str): The directory where the search index is located.

        Returns:
        - list of tuples: A list where each tuple in the list is structured as (title, categories), where 'title' is a string
        representing the title of the document, and 'categories' is a string representing the
        concatenated categories of the document.
    """
    documents_info = []
    index = open_dir(index_dir)

    with index.searcher() as searcher:
        for doc in searcher.all_stored_fields():
            title = doc.get("title_original", "")
            categories = doc.get("category", "")
            documents_info.append((title, categories))

    return documents_info


def category_exists(index, category):
    """
        Checks if a given category exists in any document within the search index.

        Parameters:
        - index (Index object): The search index to query.
        - category (str): The category to search for in the index.

        Returns:
        - bool: True if the category exists in the index, False otherwise.
    """
    with index.searcher() as searcher:
        category_query = Term("category", category)
        results = searcher.search(category_query)
        return len(results) > 0
