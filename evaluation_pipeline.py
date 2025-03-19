import sys
from functions import *
from classification_pipeline import *

def get_verbatims_and_tones(filename):
    """Returns a list of (verbatim, tones) which have previously been generated via verbatim-generator.py

    This function takes a filename as an input. TAn example of such filename is "generated_verbatims.txt"

    More precisions for the output:
    - verbatim is a string
    - tones is a list which, for the i-th category, contains a value between "Positif", "Négatif", "Pas mentionné", and "Neutre"
    """
    res = []
    with open(filename, "r") as fd:
        for line in fd.readlines():
            verbatim = line[line.index("]")+1:]
            tones = eval(line[:line.index("]")+1]) #TODO : Change this to a JSON instead
            res.append((verbatim, tones))
    return res

def evaluation_pipeline():
    """The main function of the evaluation pipeline.

    This program takes as an input a single argument:
    - The path of an input file, which contains for each line a list of tones and a verbatim

    An example of input file can be found in "generated_verbatims.txt"

    The output will be given on the stdout. It will show metrics of all the prompt methods.
    """
    if len(sys.argv)!=2:
        exit(f"Usage: {sys.argv[0]} input_file.txt")

    categories = list(json.loads(file_to_str("categories.json")).keys())

    #for each classification technique
    for classification_method, name_of_method in zip([classify_zero_shot, classify_prompt_chaining, classify_tree_of_thoughts], ["Zero-Shot", "Prompt Chaining", "Tree of Thoughts"]):
        sum_hallucination_rates = 0
        sum_precision_rates = 0
        sum_recall_rates = 0
        nb_verbatims = 0

        #For each verbatim and its gold standard (its real tones)
        for verbatim, tones in get_verbatims_and_tones(sys.argv[1]):
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

if __name__ == '__main__':
    evaluation_pipeline()
