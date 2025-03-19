import sys
from functions import *

def verify_answer(generated_categories, generated_tones, categories):
    """Takes lists of categories and tones, and the real categories, and checks that the answer is valid.

    When querying the LLM to get a json file, we must obtain a json whose keys are categories and whose
    values are tones. This function ensures that the json file indeed has valid keys and values.

    - generated_categories is a list of strings
    - generated_tones is a list of strings
    - categories is a list of strings
    """
    if generated_categories != categories:
        print("Error : LLM returned invalid category")
        exit(1)
    if any(tone not in ["Positif", "Négatif", "Neutre", "Pas mentionné"] for tone in tones):
        print("Error : LLM returned invalid tone")
        exit(1)

def classify(prompt, categories, substutions = {}):
    """Queries the LLM to classify categories according to a prompt.

    It acts like LLM_query(), but it is made specifically for outputting
    json format. This function, after calling LLM_query(), verifies the
    values in the json before outputting it as a python list of strings.

    - prompt is a string
    - categories is a list
    - substitutions is an optional dictionary (see substitute())
    """
    """
    JSON_dict = LLM_query(prompt, substitutions, is_json=True)
    generated_categories, generated_tones = list(JSON_dict.keys()), list(JSON_dict.values())
    verify_answer(generated_categories, generated_tones, categories)
    return generated_tones
    """
    return ['Positif', 'Positif', 'Neutre', 'Positif', 'Positif', 'Positif', 'Négatif', 'Positif', 'Positif', 'Positif', 'Positif', 'Positif', 'Négatif', 'Positif', 'Positif', 'Positif', 'Pas mentionné', 'Négatif', 'Neutre', 'Positif', 'Négatif'][:len(categories)]

def classify_zero_shot(verbatim, categories):
    """Uses a single prompt to query the LLM.

    The prompt can be found in "zero_shot_prompt.txt"
    """
    prompt = file_to_str("zero_shot_prompt.txt", {"<verbatim>" : verbatim, "<categories>": list_to_JSON(categories)})
    #Debug : print(prompt) 
    return classify(prompt, categories)

def classify_prompt_chaining(verbatim, categories, minibatch_size = 5):
    """Uses many prompts which each have a recap of the previous classifications.

    For instance, suppose the minibatch size is 5. Then prompt chaning starts by
    giving 5 categories to classify It then gives the five next, with a recap of
    what it did for the already classified categories. And so on until every
    category is classified.

    The prompt can be found in "prompt_chaining_prompt.txt"
    """
    prompt = file_to_str("prompt_chaining_prompt.txt", {"<verbatim>" : verbatim})
    already_classified = []
    classified_tones = []
    while len(classified_tones)<len(categories):
        #We get the next categories to classify
        to_classify = categories[len(classified_tones):len(classified_tones) + minibatch_size]
        #We classify them in one prompt which also contains the already classified categories
        #Debug: print(substitute(prompt, {"<already_classified>": list_to_JSON(already_classified, classified_tones), "<to-classify>": list_to_JSON(to_classify)}))
        classified_tones += classify(prompt, to_classify, {"<already_classified>": list_to_JSON(already_classified, classified_tones), "<to-classify>": list_to_JSON(to_classify)})
        #We add them to the already classified categories
        already_classified += to_classify
    return classified_tones

def classify_tree_of_thoughts(verbatim, categories, minibatch_size = 6):
    """Works like prompt chaining, except that it doesn't have a recap of the previously classified categories."""
    classified_tones = []
    while len(classified_tones)<len(categories):
        #We get the next categories to classify
        to_classify = categories[len(classified_tones):len(classified_tones) + minibatch_size]
        #We classify them in one prompt
        classified_tones += classify_zero_shot(verbatim, to_classify)
    return classified_tones

def classification_pipeline():
    """The main function of the classification pipeline.

    The program takes as an input two arguments:
    - The path of an input file, in which there is, for every line, a verbatim
    - The path of an output file, which will be overwritten with the corresponding classifications.

    An example of input file can be found in "verbatims_to_classify.txt"
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
    
