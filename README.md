# Data_Mining

## Compiling and Running - Instructions

### Setting Up the Environment
1. **Install PyCharm**: If you haven’t already, download and install PyCharm from the JetBrains website.
2. **Clone the Project**: Open PyCharm, go to `VCS -> Checkout from Version Control -> Git`. Enter the specified Git link to clone the project. This provides a dedicated space for your code and associated files.

### Install Required Libraries
1. **Open the Terminal in PyCharm**: You can find it at the bottom of the PyCharm window.
2. **Install Libraries**: The code uses several libraries (`nltk`, `whoosh`, `openapi`). To install them, use the `pip` command in the terminal:

### Download or Build the Index
- **Download the Index**: You can obtain the index by downloading it from [here](https://drive.google.com/drive/folders/1dapWGLerbHQdf1fvQVcSS_OVfJjqsYW8). Once downloaded, simply place it within your project directory.
- **Build the Index**: If the index is not already present within your project, it will be generated during the first run of the program. However, please note that this indexing process may take several hours to complete. Therefore, we highly recommend opting for the first option.

### Paths Verification
Ensure that the paths to the dataset directory, index directory, and questions file are correctly set in the main file.

### Choose an Option
The program will prompt: `Choose an option:`
- Enter `1`, `2`, `3` or `4` corresponding to your choice and press `Enter`.

#### Option 1 - Run Tests from Questions File
- Selecting `1` will automatically process a set of questions from `questions.txt` file.
- The script will display each query and the search results.
- After processing all questions, it will display the number of correct answers, performance metrics, list of questions with correct answers, and the list with all answers.

#### Option 2 - Enter a Custom Query
- If you choose `2`, you’ll be prompted to enter a category and a clue for your query.
- After entering each, the script constructs and runs your query against the index.
- Results, if any, will be displayed in the console.

#### Option 3: Rerank Titles from Questions File with ChatGPT
- Selecting `3` will automatically process a set of questions and answers from `chatGpt_input.txt` file.
- The system makes calls to ChatGPT 3.5 to either perform reranking on titles returned by the Standard IR system or generate new results.
- Performance metrics will be displayed in the console, and the new answers will be stored in `chatGpt_output.txt`.

### Exiting the Program
- To exit, enter `4`. The script will display "Exiting program." and terminate.

### Invalid Choice
- If you enter a choice other than `1`, `2`, or `3`, the script will display "Invalid choice, please try again." You will then be prompted to make another choice.
