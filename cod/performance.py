def precision_at_1(correct_answers, search_results):
    """
        Calculates the precision at 1 (P@1) score for search results.

        Parameters:
        - correct_answers (list): A list of correct answers.
        - search_results (list): A list of lists, where each inner list contains the
                                  search results for a corresponding query.

        Returns:
        - float: The P@1 score, representing the accuracy of the first search results.
    """
    p1_scores = []
    for correct_answer, results in zip(correct_answers, search_results):
        score = 1 if results and correct_answer == results[0] else 0
        p1_scores.append(score)
    return sum(p1_scores) / len(p1_scores)


def mean_reciprocal_rank(correct_answers, search_results):
    """
        Calculates the mean reciprocal rank (MRR) for a set of search results.

        Parameters:
        - correct_answers (list): A list of correct answers.
        - search_results (list): A list of lists, each containing the search results
                                 for a corresponding query.

        Returns:
        - float: The MRR score for the provided search results.
    """
    mrr_score = 0
    max_rank = 10
    partial_results = [0] * max_rank
    for correct_answer, results in zip(correct_answers, search_results):
        if correct_answer in results:
            rank = results.index(correct_answer) + 1
            mrr_score += 1 / rank
            if rank <= max_rank:
                partial_results[rank - 1] += 1
            else:
                print(f"Warning: Rank {rank} is out of bounds for partial results tracking.")
    print("MRR partial results")
    for i, count in enumerate(partial_results):
        print(f"{i + 1}: {count}")
    return mrr_score / len(correct_answers)
