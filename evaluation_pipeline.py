import sys
from functions import *
from classification_pipeline import *
from time import time
import numpy as np
import krippendorff
import pandas

def get_verbatims_and_tones(filename : str) -> list[tuple[str, list[str]]]:
    """Returns a list of (verbatim, tones) which have previously been generated via verbatim-generator.py

    This function takes a filename as an input. TAn example of such filename is "generated_verbatims.txt"

    More precisions for the output:
    - verbatim is a string
    - tones is a list which, for the i-th category, contains a value between POSITIVE, NEGATIVE, NEUTRAL, NOT_MENTIONED
    """
    res = []
    with open(filename, "r") as fd:
        for line in fd.readlines():
            #The verbatim is the right part of the line, just after the table of tones
            verbatim = line[line.index("]")+1:]
            #We transform the table of tones into a python table
            tones = eval(line[:line.index("]")+1])
            res.append((verbatim, tones))
    return res

def to_number(s : str) -> int:
    """This function converts a tone into a number
    
    POSITIVE      -> 0
    NEGATIVE      -> 1
    NEUTRAL       -> 2
    NOT_MENTIONED -> 3
    """
    return [POSITIVE, NEGATIVE, NEUTRAL, NOT_MENTIONED].index(s)

def mean(x: list[int]) -> float:
    """Computes the mean of a list or generator"""
    x = list(x)
    return sum(x)/len(x) if len(x)!=0 else 0.5

def update_resume_table(M : list[list[int]], classified_tones : list[str], actual_tones : list[str]):
    """Updates the so-called "resume table" M.

    The resume table M is a matrix with five rows and four columns such that:
    - The five rows are named POSITIVE, NEGATIVE, NEUTRAL, NOT_MENTIONED, and POSITIVE_OR_NEGATIVE.
    - The four columns are named TRUE_POSITIVES, FALSE_POSITIVES, TRUE_NEGATIVES, FALSE_NEGATIVES
    - The intersection between (for instance) the column NEUTRAL and FALSE_POSITIVES is the number
    of false positives in the class Neutral, that is, the number of elements which have been classified
    as neutral when they shouldn't.

    This function takes the resume table, a list of classified tones, and the actual tones,
    and updates the resume table accordingly. That is, for every class POSITIVE, NEGATIVE,
    NEUTRAL, NOT_MENTIONED, and POSITIVE_OR_NEGATIVE, it counts the number of true positives,
    false positives, true negatives, and false negatives, and updates the row accordingly.    
    """
    possible_tones = [[POSITIVE], [NEGATIVE], [NEUTRAL], [NOT_MENTIONED], [POSITIVE, NEGATIVE]]
    #For every row
    for i in range(len(possible_tones)):
        #We count the number of True Positives, False Positives, True Negatives, and False Negatives
        for actual_tone, classified_tone in zip(actual_tones, classified_tones):
            if classified_tone in possible_tones[i] and actual_tone in possible_tones[i]:
                M[i][TP] += 1
            elif classified_tone in possible_tones[i] and actual_tone not in possible_tones[i]:
                M[i][FP] += 1
            elif classified_tone not in possible_tones[i] and actual_tone not in possible_tones[i]:
                M[i][TN] += 1
            elif classified_tone not in possible_tones[i] and actual_tone in possible_tones[i]:
                M[i][FN] += 1

def print_table(M):
    """Prints the so-called "resume table" M, whose values are percentages.

    For more info about the resume table, see the documentation of update_resume_table().
    """
    M = pandas.DataFrame(np.round(M/sum(M[0])*100, 1), index=[POSITIVE, NEGATIVE, NEUTRAL, NOT_MENTIONED, POSITIVE_OR_NEGATIVE], columns=[TRUE_POSITIVES, FALSE_POSITIVES, TRUE_NEGATIVES, FALSE_NEGATIVES])
    print(M)

def precision(M, bis=False):
    """Returns the precision.
    
    The precision is equal to mean(precision of POSITIVE, ..., precision of NOT_MENTIONED).
    The precision of the class i is the number of true positives of class i,
    divided by the number of true positives and false positives of class i.

    If bis=true, then the precision is the number of true positives of class POSITIVE_OR_NEGATIVE,
    divided by the number of true positives and false positives of class POSITIVE_OR_NEGATIVE

    If the division is impossible in any of these cases, we return -1.

    The second implementation is the method used in Zeno's article. In Zeno's article, they set
    POSITIVE = NEGATIVE = 1 and NEUTRAL = NOT_MENTIONED = 0, and compute the precision of the class 1.

    We include both methods since the first one has an advantage: as it considers POSITIVE as different from
    NEGATIVE, it penalizes a misclassification between these two classes, and the same can be said for the
    classes NEUTRAL and NOT_MENTIONED.
    """
    if bis:
        #precision_bis = precision of class POSITIVE_OR_NEGATIVE
        return -1 if (M[BIS][TP]+M[BIS][FP])==0 else M[BIS][TP]/(M[BIS][TP]+M[BIS][FP])
    else:
        #precision = mean(precision of POSITIVE, ..., precision of NOT_MENTIONED)
        #precision of class X = True Positives of class X / (True Positives of class X + False positives of class X)
        return -1 if any(M[i][TP]+M[i][FP]==0 for i in range(4)) else mean(M[i][TP]/(M[i][TP]+M[i][FP]) for i in range(4))

def recall(M, bis=False):
    """Returns the recall.
    
    The recall is equal to mean(recall of POSITIVE, ..., recall of NOT_MENTIONED).
    The recall of class i is the number of true positives of class i,
    divided by the number of true positives and false negatives of class i.

    If bis=true, then the recall is the number of true positives of class POSITIVE_OR_NEGATIVE,
    divided by the number of true positives and false negatives of class POSITIVE_OR_NEGATIVE

    If the division is impossible in any of these cases, we return -1.

    For more info about the bis option, see the documentation of precision().
    """
    if bis:
        #recall_bis = recall of class POSITIVE_OR_NEGATIVE
        return -1 if (M[BIS][TP]+M[BIS][FN])==0 else M[BIS][TP]/(M[BIS][TP]+M[BIS][FN])
    else:
        #recall = mean(recall of POSITIVE, ..., recall of NOT_MENTIONED)
        #recall of class X = True Positives of class X / (True Positives of class X + False Negatives of class X)
        return -1 if any((M[i][TP]+M[i][FN])==0 for i in range(4)) else mean(M[i][TP]/(M[i][TP]+M[i][FN]) for i in range(4))

def hallucination_rate(M):
    """Returns the hallucination rate.
    
    The hallucination rate is equal to the number of false negatives of NOT_MENTIONED,
    divided by the true positives, false positives, true negatives, and false negatives of NOT_MENTIONED.

    Equivalently, it is the proportion of time where elements are wrongly not classified as NOT_MENTIONED,
    which represents the rate at which the LLM sees features where there aren't.
    """
    #hallucination_rate = ratio of tones which haven't been classified as NOT_MENTIONED when they should
    #hallucination_rate = False Negatives of NOT_MENTIONED / (True Positives of NOT_MENTIONED + ... + False Negatives of NOT_MENTIONED)
    return M[to_number(NOT_MENTIONED)][FN]/sum(M[to_number(NOT_MENTIONED)][i] for i in range(4))

def evaluation_pipeline():
    """The main function of the evaluation pipeline.

    This program takes as an input a single argument:
    - The path of an input file, which contains for each line a list of tones and a verbatim

    An example of input file can be found in "generated_verbatims.txt"

    The output will be given on the stdout. It will show metrics of all the prompt methods.
    """
    if len(sys.argv)!=2:
        exit(f"Usage: {sys.argv[0]} input_file.txt")

    categories = list(json.loads(file_to_str(CATEGORIES_PATH)).keys())

    #for each classification method
    for classification_method, name_of_method in zip([classify_zero_shot, classify_prompt_chaining, classify_tree_of_thoughts, classify_reflexion], ["Zero-Shot", "Prompt Chaining", "Tree-of-Thoughts", "Reflexion"]):
        time_taken = 0
        list_classified_tones = [[], []]
        nb_verbatims = 0
        
        #M is the "resume table"
        M = np.zeros((5, 4))

        #We classify and evaluate twice every verbatim to compute Krippendorff's alpha
        #We also use this opportunity to calculate twice all metrics
        for i in range(2):
            #For each verbatim and its gold standard (its real tones)
            for verbatim, tones in get_verbatims_and_tones(sys.argv[1]):
                print("classifying verbatim...")
                nb_verbatims += 1
                #We ask the LLM to classify according to the current classification method (while measuring the time)
                t0 = time(); classified_tones = classification_method(verbatim, categories); t1 = time()
                time_taken += t1 - t0
                #We store it (it will be useful to compute Krippendorff's alpha)
                list_classified_tones[i] += map(to_number, classified_tones)
                #We update the resume table (we count the number of true positives, false positives, true negatives, and false negatives)
                update_resume_table(M, classified_tones, tones)

        print("\n======")
        print_table(M)
        print(f"Precision of {name_of_method}: {precision(M):.2f}")
        print(f"Precision (bis) of {name_of_method}: {precision(M, bis=True):.2f}")
        print(f"Recall of {name_of_method}: {recall(M):.2f}")
        print(f"Recall (bis) of {name_of_method}: {recall(M, bis=True):.2f}")
        print(f"Hallucination rate of {name_of_method}: {hallucination_rate(M):.2f}")
        print(f"Krippendorff's alpha of {name_of_method}: {krippendorff.alpha(reliability_data=list_classified_tones, level_of_measurement="nominal"):.2f}")
        print(f"Time taken for {name_of_method}: {time_taken/(2*nb_verbatims):.2f}") #We divide by 2 since we classified everything twice

if __name__ == '__main__':
    evaluation_pipeline()