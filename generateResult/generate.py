import json

from Tools import chatWithGPT, jsonClean
from generateIndex import generateIndex
from config import TEST_PROMPT_PATH


def generate(data:dict, human_prompt:bool=False, manual_index:list[list[int]]=None)->tuple[list[dict],list[list[int]]]:
    """
    Generate a prompt and website grouping information based on input data.

    This function processes website data to create a structured prompt and grouping
    information, ensuring the number of websites does not exceed MAX_WEBSITES (5).
    It handles various edge cases to maintain valid partitioning of websites.

    Parameters
    ----------
    data : dict
        For more information, please refer to the reproduceDataset/ReadMe.md file.
    human_prompt : bool, optional
        If True, uses website URLs instead of content in the prompt.
        Default is False.
    manual_index : list[list[int]], optional
        The manual index of the websites.
        If not None, the function will use manual index to as the correct answer to generate the prompt.
        Default is None.
    Returns
    -------
    tuple
        A tuple containing:
        - list[dict]
            List of prompt messages in chat format
        - list[list[int]]
            The gold answer for the web partitioning

    Raises
    ------
    InvalidDataException
        If the input data cannot generate a valid partition (e.g., only one group
        or all groups have single websites)
    Exception
        If an impossible state is reached during processing

    Notes
    -----
    The function ensures:
    1. Number of groups > 1
    2. At least one group has multiple websites
    3. Total websites <= MAX_WEBSITES (5)
    """
    with open(TEST_PROMPT_PATH, 'r', encoding='utf-8') as f:
        prompt = [{"role":"system", "content":f.read()}]
    content=f"## Question\n{data['question']}\n\n## Website Information\n"
    filteredWebs=[]
    for i in range(len(data['websites'])):
        if 'index' in data['websites'][i]:
            filteredWebs.append(data['websites'][i])
    data['websites']=filteredWebs

    print(len(data['websites']))
    print([i.keys() for i in data['websites']])
    websites={e['index']:e for e in data['websites']}
    remaining,info=generateIndex(data,manual_index)
    forPrompt=[]
    print(len(data['websites']))
    websites={e['index']:e for e in data['websites']}
    for i in remaining:
        if human_prompt:
            if i in data['websites']:
                forPrompt.append({"index":i,"website":websites[i]['website']})
            else:
                for web in websites:
                    if str(websites[web]['index']) == str(i):
                        forPrompt.append({"index":i,"website":websites[web]['website']})
                        break
        else:
            if i in data['websites']:
                forPrompt.append({"index":i,"website":websites[i]['content']})
            else:
                for web in websites:
                    if str(websites[web]['index']) == str(i):
                        forPrompt.append({"index":i,"website":websites[web]['content']})
                        break
    content+=json.dumps(forPrompt,indent=4,ensure_ascii=False)
    prompt[0]['content']=prompt[0]['content'].replace('[CLUSTERING NUMBER]',str(len(info)))
    prompt.append({"role":"user","content":content})
    return prompt,info

class GenerateResult:
    def __init__(self,data:dict,saveTo:str=None):
        self.data=data
        self.info=None
        self.prompt=None
        self.saveTo=saveTo
    def get_prompt(self,human_prompt:bool=False):
        self.prompt,self.info=generate(self.data,human_prompt)
        return self.prompt
    def get_answer(self):
        if self.prompt is None:
            self.get_prompt()
        answer,success=chatWithGPT(self.prompt)
        if not success:
            raise Exception('Failed to get answer from GPT')
        answer,success=jsonClean(answer,['answers'])
        if not success:
            raise Exception('Failed to parse answer from GPT')
        return answer
    def get_info(self):
        return self.info
    def process(self):
        answer=self.get_answer()
        toSave={'answer':answer,'info':self.info,'prompt':self.prompt}
        if self.saveTo is not None:
            with open(self.saveTo,'w',encoding='utf-8') as f:
                json.dump(toSave,f,indent=4,ensure_ascii=False)
        else:
            print(json.dumps(toSave,indent=4,ensure_ascii=False))
if __name__=='__main__':
    from datasets import load_dataset
    data=load_dataset("OracleY/ConfRAG")['train'][8]
    print(GenerateResult(data,saveTo='result.json').process())
