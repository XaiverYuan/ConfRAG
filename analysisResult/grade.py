import json
import math

from functools import lru_cache
from collections import defaultdict
from config import CACHE_SIZE

def bad_partition(grouping_pred:list[list[int]],grouping_true:list[list[int]]):
    """
    Check if grouping_pred is a bad partition.

    Parameters
    ----------
    grouping_pred : list[list[int]]
        Predicted grouping of elements
    grouping_true : list[list[int]]
        True grouping of elements

    Returns
    -------
    str
        "Missing Elements" if elements are missing
        "Extra Elements" if there are extra elements
        "Duplicate Elements" if there are duplicate elements
        "Normal" if the partition is valid
    """
    # Check if both groups contain the same elements
    elements_true = {e for group in grouping_true for e in group}
    elements_pred = {e for group in grouping_pred for e in group}
    if len(elements_true-elements_pred)>0:
        return "Missing Elements"
    if len(elements_pred-elements_true)>0:
        return "Extra Elements"
    # Check if each index appears only once in grouping_pred
    existed_idx=set()
    for group in grouping_pred:
        for element in group:
            if element in existed_idx:
                return "Duplicate Elements"
            existed_idx.add(element)
    return "Normal"
  

def clustering_to_soft_matrix(clustering):
    """
    Construct soft contingency matrix.

    Parameters
    ----------
    clustering : list[list]
        List of groups where each group contains elements

    Returns
    -------
    tuple
        - membership: Dict[element] -> List of group_idx it belongs to
        - group_sizes: Dict[group_idx] -> number of members
    """
    membership = defaultdict(list)
    group_sizes = defaultdict(int)
    for group_idx, group in enumerate(clustering):
        for element in group:
            membership[element].append(group_idx)
            group_sizes[group_idx] += 1
    return membership, group_sizes

def compute_soft_nmi(grouping_true, grouping_pred):
    """
    Calculate Soft NMI (Normalized Mutual Information) that allows element overlap.
    
    When elements are repeated, each group contributes a weight of 1/number of occurrences.
    For non-overlapping cases, the result is consistent with original NMI.
    For predictions with increased duplicates, the score will decrease.

    Parameters
    ----------
    grouping_true : list[list]
        True grouping of elements
    grouping_pred : list[list]
        Predicted grouping of elements

    Returns
    -------
    float
        Soft NMI score between 0 and 1
    """
    # Get all unique elements
    elements = sorted(set(e for group in grouping_true for e in group) | set(e for group in grouping_pred for e in group))
    N = len(elements)

    # Construct soft matrix
    true_membership, true_group_sizes = clustering_to_soft_matrix(grouping_true)
    pred_membership, pred_group_sizes = clustering_to_soft_matrix(grouping_pred)

    # List of all groups
    true_groups = list(true_group_sizes.keys())
    pred_groups = list(pred_group_sizes.keys())

    # Calculate mutual information I(U, V)
    I_uv = 0.0
    for i in true_groups:
        for j in pred_groups:
            pij = 0.0
            for x in elements:
                if i in true_membership[x] and j in pred_membership[x]:
                    wx = 1 / len(true_membership[x])
                    wy = 1 / len(pred_membership[x])
                    pij += wx * wy
            pij /= N
            if pij > 0:
                pi = sum(1 / len(true_membership[x]) for x in elements if i in true_membership[x]) / N
                pj = sum(1 / len(pred_membership[x]) for x in elements if j in pred_membership[x]) / N
                I_uv += pij * math.log(pij / (pi * pj))

    # Entropy H(U), H(V)
    H_u = 0.0
    H_v = 0.0
    for i in true_groups:
        pi = sum(1 / len(true_membership[x]) for x in elements if i in true_membership[x]) / N
        if pi > 0:
            H_u -= pi * math.log(pi)
    for j in pred_groups:
        pj = sum(1 / len(pred_membership[x]) for x in elements if j in pred_membership[x]) / N
        if pj > 0:
            H_v -= pj * math.log(pj)

    return 2 * I_uv / (H_u + H_v) if (H_u + H_v) > 0 else 0.0

def compare_answer(answers: list[str], info: list[list[str]]) -> tuple[int, list[tuple[int, int]]]:
    """
    Compare answers with information and find the best matching path.

    Parameters
    ----------
    answers : list[str]
        List of answer strings
    info : list[list[str]]
        List of information groups containing keywords

    Returns
    -------
    tuple
        - score: Number of successful matches
        - match_path: List of tuples containing matched indices
    """
    n, m = len(answers), len(info)
    @lru_cache(maxsize=CACHE_SIZE)
    def dfs(used_mask: int, idx: int) -> tuple[int, tuple[tuple[int, int], ...]]:
        if idx == n:
            return 0, ()

        # Skip current answer[idx]
        best_score, best_path = dfs(used_mask, idx + 1)

        # Try matching with each info[j]
        for j in range(m):
            if not (used_mask & (1 << j)):
                if any(keyword in answers[idx] for keyword in info[j]):
                    new_score, new_path = dfs(used_mask | (1 << j), idx + 1)
                    new_score += 1
                    new_path = ((idx, j),) + new_path
                    if new_score > best_score:
                        best_score = new_score
                        best_path = new_path

        return best_score, best_path

    score, match_path = dfs(0, 0)
    return score, list(match_path)

def test(received,data):
    """
    Test and evaluate the received answers against the ground truth data.

    Parameters
    ----------
    received : dict
        Dictionary containing received answers and information
    data : dict
        Dictionary containing ground truth data

    Returns
    -------
    dict
        Dictionary containing evaluation results including NMI score, answer scores,
        and matching information
    """
    if 'answer' in received and 'info' in received:
        answer=received['answer']['answers']
        info=received['info']
    elif 'answers' in received:
        answer=received['answers']
        allIndex=[e for i in answer for e in i['index']]
        info=[]
        for group in data['final_answer']['answers']:
            currGroup=[]
            for i in group['index']:
                if i in allIndex:
                    currGroup.append(i)
            if len(currGroup)>0:
                info.append(currGroup)
    else:
        raise Exception("Please check the format of the received data")
    result={'id':data['id'],'correctAnswer':data['answers'],'gotAnswer':answer}
    received_group=[i['index'] for i in answer]
    newGroupInfo=info
    result['badPartition']=bad_partition(received_group,newGroupInfo)
    if result['badPartition']!='Normal':
        result['NMI']=0
    else:
        nmiscore=compute_soft_nmi(newGroupInfo,received_group)
        result['NMI']=nmiscore
    result['NMIcorrect']=newGroupInfo
    result['NMIgot']=received_group
    selfinfo=data['answers']
    answers=[i['answer'] for i in answer]
    info=[i['answer judge keyword'] for i in selfinfo]
    answerMatchScore,matchPath= compare_answer(answers,info)
    result['answerMatchCount']=answerMatchScore
    result['match']=[]
    result['answerScore']=0
    result['reasonScore']=0
    Lans=len(answer)
    Linfo=len(info)
    for match in matchPath:
        answerReason=answer[match[0]]['reason']
        infoReason=[i['reason judge keyword'] for i in selfinfo[match[1]]['reason']]
        reasonMatches,_=compare_answer(answerReason,infoReason)
        if len(answerReason)!=0:
            result['reasonScore']+=reasonMatches/((len(answerReason)*len(infoReason))**0.5)
        result['answerScore']+=1
        result['match'].append({"currMatch":match,"currReasonMatch":reasonMatches})
    if Lans!=0:
        result['answerScore']/=((Lans*Linfo)**0.5)
        result['reasonScore']/=((Lans*Linfo)**0.5)
    else:   
        result['answerScore']=0
        result['reasonScore']=0
    return result

def show(result):
    """
    Display the evaluation results.

    Parameters
    ----------
    result : dict
        Dictionary containing evaluation results
    """
    print("NMI: ",result['NMI'])
    print("answerScore: ",result['answerScore'])
    print("reasonScore: ",result['reasonScore'])
    print("badPartition: ",result['badPartition'])
    
if __name__ == "__main__":
    with open("generateResult/example.json", "r") as f:
        result = json.load(f)
    from datasets import load_dataset
    data=load_dataset("OracleY/ConfRAG")['train'][8]
    # the question should be "Are children more susceptible to radiation from electronic devices?"
    show(test(result,data))
