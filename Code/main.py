import nltk
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT
from whoosh.analysis import StopFilter, LowercaseFilter, RegexTokenizer
from whoosh import scoring
from whoosh.analysis import STOP_WORDS
import os
from whoosh.query import Term, Or, And
from Lemmatizer import Lemmatizer
from SynonymFilter import SynonymFilter
from chatGpt_integration import rerank_wikipedia_pages, rerank_questions_file_answers
from data_parser import result_question, parse_file
from performance import precision_at_1, mean_reciprocal_rank
from utilities import get_synonyms, get_all_categories, get_documents_info
nltk.download('wordnet')

custom_analyzer = RegexTokenizer() | LowercaseFilter() | SynonymFilter() | Lemmatizer() | StopFilter(
    stoplist=STOP_WORDS)

custom_analyzer_query = RegexTokenizer() | LowercaseFilter() | Lemmatizer() | StopFilter(stoplist=STOP_WORDS)

schema = Schema(
    title_original=TEXT(stored=True),
    title=TEXT(analyzer=custom_analyzer, stored=True),
    content=TEXT(analyzer=custom_analyzer),
    category=TEXT(analyzer=custom_analyzer, stored=True)
)

def process_questions_file(file_path, analyzer):
    """
        Processes a text file containing questions and constructs search queries.

        Parameters:
        - file_path (str): The path to the text file containing the questions.
        - analyzer (Analyzer object): An instance of a text analyzer used for processing the text.

        Yields:
        - Generator[str]: A generator that yields query strings for each question.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.read().split('\n\n')
        for block in lines:
            parts = block.strip().split('\n')
            if len(parts) >= 3:
                category, clue, _ = parts[0], parts[1], parts[2]
                query = construct_query(category, clue, analyzer)
                yield query
def preprocess_text(text, analyzer):
    """
        Processes the given text using the specified analyzer and returns the processed text.

        Parameters:
        - text (str): The text to be processed.
        - analyzer (Analyzer object): The text analyzer to be used for processing.

        Returns:
        - str: The processed text as a single string.
    """
    return " ".join([token.text for token in analyzer(text)])

def construct_query(category, clue, analyzer):
    """
        This function processes the category and clue texts, splits them into terms,
        and creates a query by combining these terms with their synonyms. The final
        query is a combination of these terms and their synonyms, joined by logical
        operators ('OR' for terms within the same category/clue, 'AND' between category and clue).

        Parameters:
        - category (str): The category part of the query.
        - clue (str): The clue part of the query.
        - analyzer (Analyzer object): An instance of a text analyzer for processing the text.

        Returns:
        - str: The constructed query string.
    """
    processed_category = preprocess_text(category.lower(), analyzer)
    processed_clue = preprocess_text(clue.lower(), analyzer)

    category_terms = processed_category.split()
    clue_terms = processed_clue.split()

    query_parts = []

    category_group = category_terms[0] + " OR "
    for term in category_terms:
        synonyms = get_synonyms(term)[:2]
        category_group = category_group + " OR ".join(synonyms)

    query_parts.append(f"({category_group})")

    for i in range(0, len(clue_terms)):
        result = clue_terms[i]
        synonyms = get_synonyms(clue_terms[i])[:2]
        if synonyms:
            result = result + " OR " + " OR ".join(synonyms)
        query_parts.append(f"({result})")

    final_query = " AND ".join(query_parts)

    return final_query

def search_index(index, query):
    """
        This function conducts a search on an index using a provided query string.
        The query is first split into its parts, which are then used to create sub-queries.
        These sub-queries are combined and used to search the index.
        The function returns a list of search results, specifically the titles of the
        documents that match the query criteria.

        Parameters:
        - index (Index object): The search index on which to perform the query.
        - query (str): The query string used for searching the index.

        Returns:
        - list: A list of titles from the documents that match the query.
    """
    with index.searcher(weighting=scoring.TF_IDF()) as searcher:
        parts = query.split(" AND ")
        all_res = []
        first_part_words = parts[0][1:-1].split(" OR ")
        category_term = first_part_words[0]
        parts_to_sort = parts[1:]
        parts_to_sort.sort(key=lambda part: len(part), reverse=True)
        sorted_parts = [parts[0]] + parts_to_sort
        seen_titles = set()

        while sorted_parts and len(all_res) <= 10:
            sub_queries = []
            for part in sorted_parts:
                words = part[1:-1].split(" OR ")
                if part is sorted_parts[0]:
                    term_objects = [Term("category", category_term)]
                    words.insert(0, category_term)
                else:
                    term_objects = [Term(field, word) for word in words for field in ['content', 'title']]
                sub_query = Or(term_objects)
                sub_queries.append(sub_query)

            final_query = And(sub_queries)
            print(final_query)
            results = searcher.search(final_query, limit=10, terms=True)

            sorted_parts.pop()

            # for result in results:
            #     title = result['title_original']
            #     if len(title.split()) <= 20:
            #         all_res.append(title)
            for result in results:
                title = result['title_original']
                if len(title.split()) <= 20 and title not in seen_titles:  # Check if title is not in seen_titles
                    all_res.append(title)
                    seen_titles.add(title)

        return all_res[:10]


def run_tests(questions_file_path, index):
    """
        This function iterates over a file of questions, each consisting of a
        category and a clue. It constructs a query for each question, searches
        the index, and then checks if the search results match the expected answer.
        The function counts and prints the number of correct answers found.

        Parameters:
        - questions_file_path (str): The path to the file containing the questions.
        - index (Index object): The search index to be used for running the tests.
    """
    i = 0
    nr = 0
    correct_answers = result_question(questions_file_path)
    all_results = []
    correct = []
    for query in process_questions_file(questions_file_path, custom_analyzer_query):
        print("Initial query: " + str(query))
        answers = search_index(index, query)
        print("Top 10 answers: " + str(answers))
        correct_answer = result_question(questions_file_path)[i]
        if '|' in correct_answer:
            splitted = correct_answer.split('|')
            for split in splitted:
                if split in answers:
                    nr += 1
        elif correct_answer in answers:
            nr += 1
            correct.append(i)

        all_results.append(answers)
        print("Total correct answers: " + str(nr))
        print('\n')
        i += 1
    print("Final correct answers: " + str(nr))
    print("Precision at 1: "+ str(precision_at_1(correct_answers, all_results)))
    print("MRR: "+ str(mean_reciprocal_rank(correct_answers, all_results)))
    print("List of questions with correct answers returned by system: " + str(correct))
    print(all_results)

def run_query(index):
    """
        This function prompts the user to enter a category and a clue. It then
        constructs a query using these inputs and performs a search on the provided
        index. The results of the search are printed to the console.

        Parameters:
        - index (Index object): The search index on which the query is to be performed.
    """
    category = input("Enter category: ")
    clue = input("Enter clue: ")

    query = construct_query(category, clue, custom_analyzer_query)
    answers = search_index(index, query)

    if answers:
        print("Answers found:")
        for answer in answers:
            print(answer)
    else:
        print("No answers found.")



if __name__ == '__main__':
    dataset_dir = "wiki-subset-20140602"
    indexdir = "indexdir2"
    if not os.path.exists(indexdir):
        # If index does not exist, we should create it. Please wait until commit is done
        print("Create index. Wait until commit is done!")
        os.mkdir(indexdir)
        index = create_in(indexdir, schema)
        writer = index.writer()
        for filename in os.listdir(dataset_dir):
            print(filename)
            with open(os.path.join(dataset_dir, filename), 'r', encoding='utf-8') as file:
                file_content = file.read()
                for title, content, category in parse_file(file_content):
                    writer.add_document(title_original=title, title=title, content=content, category=category)
        writer.commit()
        print("INDEX COMMITED")
    else:
        # if index exist, we can open it to make a search
        print("Index exists\n")
        index = open_dir(indexdir)
        questions_file_path = "questions.txt"
        index = open_dir(indexdir)

        while True:
            print("\nChoose an option:")
            print("1: Run tests from questions file")
            print("2: Enter a custom query")
            print("3: Rerank titles from questions file with ChatGPT")
            print("4: Exit")
            choice = input("Enter your choice (1, 2, 3 or 4): ")
            if choice == '1':
                run_tests(questions_file_path, index)
            elif choice == '2':
                run_query(index)
            elif choice == '3':
                rerank_questions_file_answers(questions_file_path)
            elif choice == '4':
                print("Exiting program.")
                break
            else:
                print("Invalid choice, please try again.")


