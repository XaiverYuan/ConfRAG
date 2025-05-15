import random
from config import MAX_WEBSITES


class InvalidDataException(Exception):
    pass


def generateIndex(data:dict, manual_index:list[list[int]]=None)->tuple[list[dict],list[list[int]]]:
    """Generate a valid partition of indexes.

    A valid partition must satisfy the following conditions:
    1. Number of groups > 1
    2. At least one group has multiple websites
    3. Total number of websites <= MAX_WEBSITES (5)

    Parameters
    ----------
    data : dict
        Input data dictionary containing website information and answers.
        See reproduceDataset/ReadMe.md Output part for more details.
    manual_index : list[list[int]], optional
        Manual index of websites to use as the correct answer for prompt generation.
        If provided, the function will use this index instead of generating one.
        Default is None.

    Returns
    -------
    tuple
        A tuple containing:
        - list[dict]
            List of prompt messages in chat format
        - list[list[int]]
            The gold answer for website partitioning

    Raises
    ------
    InvalidDataException
        If the input data cannot generate a valid partition, specifically when:
        - Only one group exists in the answer
        - All groups contain single websites
        - No group has more than 1 and less than 5 websites
    Exception
        If an impossible state is reached during processing

    Notes
    -----
    The function implements a sophisticated website selection algorithm that:
    1. Handles both manual and automatic indexing
    2. Ensures balanced website distribution across groups
    3. Maintains group integrity while respecting MAX_WEBSITES limit
    4. Implements fallback strategies for edge cases
    """
    if manual_index is not None:
        info=manual_index
        remaining=[i for e in manual_index for i in e]
    else:
        if len(data['answers'])==1:
            # there is only one group of answer
            # this data can not generate a valid partition
            # so we raise an exception
            raise InvalidDataException('Question with only one group of answer is not usable!')
        if len([i['index'] for i in data['answers']])==len([e for i in data['answers'] for e in i['index']]):
            # all group only have one website
            # this data can not generate a valid partition
            # so we raise an exception
            raise InvalidDataException('Question with all group only have one website is not usable!')
    
        groupInfo=[i['index'] for i in data['answers']]
        groupDict={}
        for i,group in enumerate(groupInfo):
            for e in group:
                groupDict[e]=i
        groupCount={i:len(a) for i,a in enumerate(groupInfo)}

        flattenGroupInfo={e for group in groupInfo for e in group}
        if len(flattenGroupInfo)<MAX_WEBSITES:
            # if the group number is less than MAX_WEBSITES, then we can just use all the websites
            remaining=list(flattenGroupInfo)
            info=groupInfo
        else:
            drop=set(random.sample(list(flattenGroupInfo),len(flattenGroupInfo)-MAX_WEBSITES))
            remaining=list(flattenGroupInfo-drop)
            # check if all the remaining elements are from one group
            remainGroups={groupDict[e] for e in remaining}
            # if all the remaining elements are from one group, then we randomly delete one element, and add one element from other groups
            # this is not fully "random", but it is not a big problem
            if len(remainGroups)==1:
                currGroup=remainGroups.pop()
                remaining.pop(random.randint(0,len(remaining)-1))
                couldAdd=[i for i in drop if groupDict[i]!=currGroup]
                remaining.append(random.choice(couldAdd))
            # if the number of remaining elements is equal to the number of groups, then it is not a valid partition
            if len(remainGroups)==len(remaining):
                # find a group, the number of elements in the group is larger than 1, and less than 5
                availableGroups=[i for i in groupCount if groupCount[i]>1 and groupCount[i]<5]
                if len(availableGroups)==0:
                    theGroup=[i for i in groupCount if groupCount[i]==5]
                    if len(theGroup)==0:
                        raise InvalidDataException('No group with more than 1 and less than 5')
                    selectedGroup=theGroup[0]
                else:
                    selectedGroup=random.choice(availableGroups)
                newRemaining={i for i in groupDict if groupDict[i]==selectedGroup}
                if len(newRemaining)==MAX_WEBSITES:
                    newRemaining.pop()
                remaining={i for i in remaining if groupDict[i]!=selectedGroup}
                newRemainingAddon=set(random.sample(list(remaining),MAX_WEBSITES-len(newRemaining)))
                remaining=newRemaining|newRemainingAddon
                if len(remaining)!=MAX_WEBSITES:
                    remaining.pop()
            info=[]
            existedGroup={}
            for e in remaining:
                if groupDict[e] not in existedGroup:
                    existedGroup[groupDict[e]]=len(info)
                    info.append([e])
                else:
                    info[existedGroup[groupDict[e]]].append(e)
        # check again, if there is only one group, or the number of groups is equal to the number of elements, then it is not a valid partition
        remainGroups={groupDict[e] for e in remaining}
        if len(remainGroups)==1 or len(remainGroups)==len(remaining):
            raise Exception('Impossible!')
    return remaining,info
