"""This code was inspired from the playground code: https://github.com/ERIOS-project/Playground-GenAI-CLI"""

from functions import *
from random import randint

#Returns a list of (verbatim, tones), where:
#- verbatim is a string
#- tones is a list which, for the i-th category, contains a value between "Positif", "Négatif", "Pas mentionné", and "Neutre"
def get_verbatims_and_tones():
    res = []
    with open("generated-verbatims.txt", "r") as fd:
        for line in fd.readlines():
            verbatim = line[line.index("]")+1:]
            tones = eval(line[:line.index("]")+1]) #TODO : Change this to a JSON instead
            res.append((verbatim, tones))
    return res

#takes lists of categories and tones, and the real categories, and checks that the answer is valid
def verify_answer(generated_categories, generated_tones, categories):
    if generated_categories != categories:
        print("Error : LLM returned invalid category")
        exit(1)
    if any(tone not in ["Positif", "Négatif", "Neutre", "Pas mentionné"] for tone in tones):
        print("Error : LLM returned invalid tone")
        exit(1)

#Takes a prompt, a verbatim, the categories to classify, and returns a list of tones
def classify(prompt, categories, substutions = {}):
    """
    JSON_dict = LLM_query(prompt, substitutions, is_json=True)
    generated_categories, generated_tones = list(JSON_dict.keys()), list(JSON_dict.values())
    verify_answer(generated_categories, generated_tones, categories)
    return generated_tones
    """
    return ['Positif', 'Positif', 'Neutre', 'Positif', 'Positif', 'Positif', 'Négatif', 'Positif', 'Positif', 'Positif', 'Positif', 'Positif', 'Négatif', 'Positif', 'Positif', 'Positif', 'Pas mentionné', 'Négatif', 'Neutre', 'Positif', 'Négatif'][:len(categories)]

#Zero shot just gives a single prompt
def classify_zero_shot(verbatim, categories):
    prompt = get_prompt("zero-shot-prompt.txt", {"<verbatim>" : verbatim, "<categories>": list_to_JSON(categories)})
    #Debug: print(prompt) 
    return classify(prompt, categories)

#Suppose the minibatch size is 5
#Then prompt chaning starts by giving 5 categories to classify
#It then gives the five next, with a recap of what it did for the already classified categories.
#And so on until every category is classified
def classify_prompt_chaining(verbatim, categories, minibatch_size = 6):
    prompt = get_prompt("prompt-chaining-prompt.txt", {"<verbatim>" : verbatim})
    already_classified = []
    classified_tones = []
    while len(classified_tones)<len(categories):
        #We get the next categories to classify
        to_classify = categories[len(classified_tones):len(classified_tones) + minibatch_size]
        #We classify them in one prompt which also contains the already classified categories
        #Debug: print(substitute(prompt, {"<already-classified>": list_to_JSON(already_classified, classified_tones), "<to-classify>": list_to_JSON(to_classify)}))
        classified_tones += classify(prompt, to_classify, {"<already-classified>": list_to_JSON(already_classified, classified_tones), "<to-classify>": list_to_JSON(to_classify)})
        #We add them to the already classified categories
        already_classified += to_classify
    return classified_tones

#It is like prompt chaining, but it doesn't have memory of the previously classified categories
#TODO: Change the name as it is confusing
def classify_tree_of_thoughts(verbatim, categories, minibatch_size = 6):
    classified_tones = []
    while len(classified_tones)<len(categories):
        #We get the next categories to classify
        to_classify = categories[len(classified_tones):len(classified_tones) + minibatch_size]
        #We classify them in one prompt
        classified_tones += classify_zero_shot(verbatim, to_classify)
    return classified_tones



categories = list(json.loads(file_to_str("categories.json")).keys())

#for each classification technique
for classification_method, name_of_method in zip([classify_zero_shot, classify_prompt_chaining, classify_tree_of_thoughts], ["Zero-Shot", "Prompt Chaining", "Tree of Thoughts"]):
    sum_hallucination_rates = 0
    sum_precision_rates = 0
    sum_recall_rates = 0
    nb_verbatims = 0

    #For each verbatim and its gold standard (its real tones)
    for verbatim, tones in get_verbatims_and_tones():
        nb_verbatims += 1
        #We ask the LLM to classify according to the current classification method
        classified_tones = classification_method(verbatim, categories)

        #We count the number of "Positif", "Pas mentionné", "Négatif", "Neutre" that have been well classified
        well_classified = {key: 0 for key in ["Positif", "Pas mentionné", "Négatif", "Neutre"]}
        for i in range(len(well_classified)):
            if classified_tones[i]==tones[i]:
                well_classified[tones[i]]+=1

        #Hallucination rate :
        #We count the number of hallucinations (the number of tones that have wrongly been classified as "Pas mentionné"), and we divide it by the number of categories (21)
        hallucination_rate = (classified_tones.count("Pas mentionné") - well_classified["Pas mentionné"]) / 21
              
        #precision rate = (precision of "Positif" + ... + precision of "Pas mentionné")/4
        #precision of X = number of elements well classified as X / number of elements classified as X
        precision_rate = sum(well_classified[key] / max(1, classified_tones.count(key)) for key in well_classified)/4
        #The max() is to prevent division by zero

        #recall rate = (recall of "Positif" + ... + recall of "Pas mentionné")/4
        #recall of X = number of elements well classified as X / number of elements belonging to X
        recall_rate = sum(well_classified[key] / max(1, tones.count(key)) for key in well_classified)/4
        #The max() is to prevent division by zero

        sum_precision_rates += precision_rate
        sum_recall_rates += recall_rate
        sum_hallucination_rates += hallucination_rate

    print(f"Precision of {name_of_method}: {sum_precision_rates / nb_verbatims}")
    print(f"Recall of {name_of_method}: {sum_recall_rates / nb_verbatims}")
    print(f"Hallucination rate of {name_of_method}: {sum_hallucination_rates / nb_verbatims}")
    print()
