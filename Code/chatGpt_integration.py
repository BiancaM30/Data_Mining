import openai

from data_parser import read_input_file_for_chagpt, result_question
from performance import precision_at_1, mean_reciprocal_rank
import time

def rerank_wikipedia_pages(question, wiki_titles, retries=3, delay=5):
    """
        Communicates with OpenAI's GPT-3.5-turbo model to rerank or generate Wikipedia page titles.

        Parameters:
        - question (str): The question based on which Wikipedia page titles are to be reranked or generated.
        - wiki_titles (list of str or None): A list of existing Wikipedia titles for reranking.
                                              If None, the function will request generation of new titles.
        - retries (int, optional): Number of retry attempts for the API call in case of failure. Default is 3.
        - delay (int, optional): Delay in seconds before retrying the API call after failure. Default is 5.

        Returns:
        - list of str: A list of reranked or newly generated Wikipedia page titles.
    """
    # openai.api_key = "..." put your key here

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Question: {question}"}
    ]

    if wiki_titles:
        messages.append({"role": "user", "content": "Wikipedia Titles:"})
        for title in wiki_titles:
            messages.append({"role": "user", "content": title})
        messages.append({"role": "user", "content": "Rerank these titles in order of relevance to the question."})
    else:
        messages.append({"role": "user", "content": "What are the top 10 Wikipedia page titles that are relevant to this question?"})

    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            reranked_titles = process_chatgpt_response(response.choices[0].message['content'])
            return reranked_titles
        except openai.error.APIError as e:
            print(f"API request failed, attempt {attempt + 1} of {retries}. Retrying in {delay} seconds.")
            print(f"Error: {e}")
            time.sleep(delay)

def process_chatgpt_response(response):
    """
    Parses the response from ChatGPT to extract a list of reranked Wikipedia titles.

    Parameters:
    - response (str): The raw text response from ChatGPT, which includes the reranked titles.

    Returns:
    - list of str: A list of parsed and extracted Wikipedia titles.
    """
    lines = response.split('\n')
    reranked_titles = []
    for line in lines:
        if '. ' in line:
            _, title = line.split('. ', 1)
            reranked_titles.append(title)
        elif line.strip():
            reranked_titles.append(line.strip())
    return reranked_titles

def rerank_questions_file_answers(questions_file_path):
    """
        Processes a list of questions by reranking or generating Wikipedia titles using ChatGPT,
        and evaluates the performance of the reranked results.

        Parameters:
        - questions_file_path (str): Path to the input file containing questions and potential Wikipedia titles.
    """
    questions = read_input_file_for_chagpt('chatGpt_input.txt')
    results = []
    for question, wiki_titles in questions:
        print(question)
        if wiki_titles:
            reranked_titles = rerank_wikipedia_pages(question, wiki_titles)
        else:
            reranked_titles = rerank_wikipedia_pages(question, None)
        print(reranked_titles)
        results.append((question, reranked_titles))

    with open('chatGpt_output.txt', 'w', encoding='utf-8') as file:
        for question, reranked_titles in results:
            file.write(question + '\n')  # Write the question
            titles_str = str(reranked_titles)  # Convert the list of titles to a string
            file.write(titles_str + '\n\n')

    correct_answers = result_question(questions_file_path)

    p1_score = precision_at_1(correct_answers, [r[1] for r in results])
    mrr_score = mean_reciprocal_rank(correct_answers, [r[1] for r in results])
    print(f'Precision at 1: {p1_score}')
    print(f'Mean Reciprocal Rank: {mrr_score}')


