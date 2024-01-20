import re


def extract_categories(page):
    """
       Extracts the categories from a given wikipedia page.

       Parameters:
       - page (str): The text content of a page from which categories need to be extracted.

       Returns:
       - str: A string containing the extracted categories, or an empty string if
              the "CATEGORIES:" line is not found.
    """
    categories_line = next((line for line in page.split('\n') if line.startswith("CATEGORIES:")), None)
    if categories_line:
        return categories_line[len("CATEGORIES:"):].strip()
    return ""


def parse_file(file_content):
    """
        Parses the content of a file into individual wikipedia  pages, extracting the title, content, and categories of each page.

        Parameters:
        - file_content (str): The entire text content of a file to be parsed.

        Yields:
        - tuple: A tuple (title, content, categories) for each page in the file.
    """
    pages = re.split(r'\n(?=\[\[)', file_content)
    for page in pages:
        if page.startswith("[["):
            title_end = page.find("]]")
            title = page[2:title_end]
            content = page[title_end + 2:].strip()
            categories = extract_categories(page)
            yield title, content, categories


def result_question(file_path):
    """
        Extracts and returns the correct answers from the question file.

        Parameters:
        - file_path (str): The path to the file containing the questions and answers.

        Returns:
        - list: A list containing the answers for each question block in the file.
    """
    results = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.read().split('\n\n')
        for block in lines:
            parts = block.strip().split('\n')
            if len(parts) >= 3:
                category, clue, answer = parts[0], parts[1], parts[2]
                results.append(answer)
    return results


def read_input_file_for_chagpt(file_path):
    """
        Reads and parses a file containing questions and their associated Wikipedia title lists.

        Parameters:
        - file_path (str): Path to the file which contains the questions and Wikipedia titles.

        Returns:
        - list of tuples: A list where each tuple contains a question and its corresponding list of titles.
                          The list of titles may be empty if no titles are associated with a question.
    """
    with open(file_path, 'r') as file:
        content = file.read()

    questions_with_answers = content.strip().split('\n\n')
    parsed_data = []

    for qa in questions_with_answers:
        lines = qa.split('\n')
        question = lines[0]
        if len(lines) > 1 and lines[1]:
            answers = eval(lines[1])
        else:
            answers = []
        parsed_data.append((question, answers))

    return parsed_data
