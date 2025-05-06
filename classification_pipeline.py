import sys
from functions import *

def verify_answer(generated_categories : list[str], generated_tones : list[str], categories : list[str]) -> bool:
    """Takes lists of categories and tones, and the real categories, and returns whether the answer is valid.

    When querying the LLM to get a json file, we must obtain a json whose keys are categories and whose
    values are tones. This function ensures that the json file indeed has valid keys and values.

    - generated_categories is a list of strings
    - generated_tones is a list of strings
    - categories is a list of strings
    """
    return (generated_categories == categories) and all(generated_tone in ["Positif", "Négatif", "Neutre", "Pas mentionné"] for generated_tone in generated_tones)


def classify(prompt : str, categories : list[str], substitutions : dict[str, str] = {}):
    """Queries the LLM to classify categories according to a prompt.

    It acts like LLM_query(), but it is made specifically for outputting
    json format. This function, after calling LLM_query(), verifies the
    values in the json before outputting it as a python list of strings.
    If the values in the json aren't valid, it repeats.

    - prompt is a string
    - categories is a list
    - substitutions is an optional dictionary (see substitute())
    """
    repeat = True
    if debug:
        print(prompt)
    while repeat:
        JSON_dict = LLM_query(prompt, substitutions, is_json=True)
        generated_categories, generated_tones = list(JSON_dict.keys()), list(JSON_dict.values())
        repeat = not(verify_answer(generated_categories, generated_tones, categories))
        print("retry" if repeat else "ok")

    return generated_tones

def classify_zero_shot(verbatim : str, categories : list[str]) -> list[str]:
    """Uses a single prompt to query the LLM.

    The prompt can be found in "prompts/zero_shot_prompt.txt"
    """
    prompt = file_to_str("prompts/zero_shot_prompt.txt", {"<verbatim>" : verbatim, "<categories>": list_to_JSON(categories)})
    return classify(prompt, categories)

def classify_prompt_chaining(verbatim : str, categories : list[str], minibatch_size : int = 9) -> list[str]:
    """Uses many prompts which each have a recap of the previous classifications.

    For instance, suppose the minibatch size is 5. Then prompt chaning starts by
    giving 5 categories to classify It then gives the five next, with a recap of
    what it did for the already classified categories. And so on until every
    category is classified.

    The prompt can be found in "prompts/prompt_chaining_prompt.txt"
    """
    prompt = file_to_str("prompts/prompt_chaining_prompt.txt", {"<verbatim>" : verbatim})
    already_classified = []
    classified_tones = []
    while len(classified_tones)<len(categories):
        #We get the next categories to classify
        to_classify = categories[len(classified_tones):len(classified_tones) + minibatch_size]
        #We classify them in one prompt which also contains the already classified categories
        classified_tones += classify(prompt, to_classify, {"<already_classified>": list_to_JSON(already_classified, classified_tones), "<to_classify>": list_to_JSON(to_classify)})
        #We add them to the already classified categories
        already_classified += to_classify
    return classified_tones

def classify_tree_of_thoughts(verbatim : str, categories : list[str], minibatch_size : int = 9) -> list[str]:
    """Works like prompt chaining, except that it doesn't have a recap of the previously classified categories."""
    classified_tones = []
    while len(classified_tones)<len(categories):
        #We get the next categories to classify
        to_classify = categories[len(classified_tones):len(classified_tones) + minibatch_size]
        #We classify them in one prompt
        classified_tones += classify_zero_shot(verbatim, to_classify)
    return classified_tones

def classify_reflexion(verbatim : str, categories : list[str], nb_loops : int = 2) -> list[str]:
    """Uses reflexion to classify the verbatim. The process is repeated nb_loops times.
    
    It starts with a zero-shot prompt, but then we use another prompt to evaluate the
    result with a score and a feedback comment. We then repeat the process by giving
    the feedback to the LLM. The result is repeated nb_loops times, and the result with
    the highest score is returned.

    Pseudo-code:
    ```
    Actor: classify like a zero-shot
    repeat nb_loops times:
        if it isn't the first iteration of the loop:
            in the same prompt:
                Reflexion: think about the feedback and the score, and how to improve the classification
                Action: re-classify according to the score and feedback
        Evaluation: evaluate the classification by giving a score and a feedback
        keep only the classification with the highest score
    ```
    
    In this way, the steps "Action", "Reflexion", and "Evaluation" loop like so:
        Action -> Evaluation -> Reflexion -> Action -> Evaluation -> Reflexion -> ... -> Action -> Evaluation

    Parameters:
      - verbatim: the text to classify.
      - categories: the list of categories to classify.
      - nb_loops: the number of iterations to make.

    Returns:
      - The best classification obtained.
    """
    #We start by doing a zero-shot prompt
    classified_tones = classify_zero_shot(verbatim, categories)
    #We get the prompts of "prompts/evaluation_prompt.txt" and "reflexion_prompt.txt"
    evaluation_prompt = file_to_str("prompts/evaluation_prompt.txt", {"<verbatim>" : verbatim})
    reflexion_and_action_prompt = file_to_str("prompts/reflexion_and_action_prompt.txt", {"<verbatim>" : verbatim})

    best_classification, best_score = None, -1
    for i in range(nb_loops):
        #From the second iteration of the loop:
        if i!=0:
            #We use the feedback and the score and reflect on them, and we then re-classify.
            classified_tones = classify(reflexion_and_action_prompt, categories, {"<categories>" : list_to_JSON(categories, classified_tones), "<feedback>" : feedback, "<score>" : score})
        #Evaluation: we use the prompt of "evaluator_prompt.txt" to evaluate the current classification
        evaluation_response = LLM_query(evaluation_prompt, {"<categories>" : list_to_JSON(categories, classified_tones)}, is_json=True)
        #We get the feedback comment ("Pas de feedback." by default) and score (0 by default)
        feedback, score = evaluation_response.get("feedback", "Pas de feedback."), evaluation_response.get("score", 0)
        #We keep only the best result
        if best_score < score:
            best_score = score
            best_classification = classified_tones
        
    return best_classification

def classification_pipeline():
    """The main function of the classification pipeline.

    The classification pipeline uses prompt chaining.

    The program takes as input two arguments:
    - The path of an input file, in which there is, for every line, a verbatim
    - The path of an output file, which will be overwritten with the corresponding classifications.

    An example of input file can be found in "prompts/verbatims_to_classify.txt"
    """
    if len(sys.argv)!=3:
        exit(f"Usage: {sys.argv[0]} input_file.txt output_file.txt")
        
    categories = list(json.loads(file_to_str("categories.json")).keys())

    #Read the input file
    verbatims = None
    with open(sys.argv[1], "r") as fd:
        verbatims = fd.readlines()

    #Write the classifications in the output file
    with open(sys.argv[2], "w") as fd:
        for verbatim in verbatims:
            fd.write(f"{classify_prompt_chaining(verbatim, categories)}\n")

#If we call the program directly (and not through an importation), this code is executed
if __name__ == '__main__':
    classification_pipeline()
    
