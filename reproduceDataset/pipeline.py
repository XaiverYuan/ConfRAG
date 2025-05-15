import os
import sys
import json
import requests
import urllib.robotparser

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from urllib.parse import urlparse

from serpapi import GoogleSearch

from Tools import chatWithGPT, jsonClean
from config import SERPAPI_API_KEY, DEFAULT_USER_AGENT, KEYWORD_PROMPT_PATH, FULL_CONTEXT_PROMPT_PATH, SUMMARIZING_PROMPT_PATH


"""
Following key is used for Google Search API.
You can get a free key from https://serpapi.com/
It is only used in getWebsites function.
If you want to alter the way to get websites, you can change the function.
"""


def is_allowed_by_robots(url:str, user_agent:str=DEFAULT_USER_AGENT)->bool:
    """Check if a URL is allowed to be crawled according to robots.txt.
    
    We automatically respected robots.txt policies for all websites by using Python's robotparser before any retrieval.
    Only publicly accessible pages were processed. No login-restricted, private, or sensitive content was accessed or stored.
    All collected content is used solely for academic research and will not be redistributed in full text.
    Parameters
    ----------
    url : str
        The URL to check against robots.txt
    user_agent : str, optional
        The user agent to check for, by default from config
        
    Returns
    -------
    bool
        True if the URL is allowed to be crawled, False otherwise
    """
    
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        return rp.can_fetch(user_agent, url)
    except:
        return True


def getWebsites(q:str)->tuple[list[str],bool]:
    """Get list of websites from Google search results.
    
    This is the function to get websites from Google search results.
    If you want to alter the way to get websites, you can change the function.

    Parameters
    ----------
    q : str
        Search query string
        
    Returns
    -------
    tuple
        A tuple containing (websites, success_status)
        - websites: List of website URLs from search results
        - success_status: Boolean indicating if the search was successful
    """
    try:
        params = {
            "engine": "google",
            "q": q,
            "num":40,
            "api_key": SERPAPI_API_KEY
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        organic_results = results["organic_results"]
        answer=[]
        for result in organic_results:
            if "link" in result.keys() and (type(result['link']) is str):
                answer.append(result['link'])
        return answer,True
    except Exception as e:
        return [],False

# Read prompt file
with open(KEYWORD_PROMPT_PATH, "r", encoding='utf-8') as f:
    keywordPrompt = f.read()
with open(FULL_CONTEXT_PROMPT_PATH, 'r') as f:
    FCprompt = f.read()
with open(SUMMARIZING_PROMPT_PATH, 'r') as f:
    Summarizingprompt = f.read()


class Pipeline:
    def __init__(self,question:str,saveTo:str):
        self.question = question
        self.saveTo = saveTo
        self.errorCode = None
        self.data={'question':question}
    def _process(self)->None:
        # search for websites
        print("search for websites...")
        response,success=chatWithGPT([
            {"role": "system", "content": keywordPrompt},
            {"role": "user", "content": self.question}
        ])
        if not success:
            self.errorCode="Failed to chat with GPT when getting keywords\n" + response
            return
        keywords,success=jsonClean(response,['question_keyword','answer_keywords'])
        # the answer_keywords is deprecated.
        if not success:
            self.errorCode="Failed to parse keywords to json\n" + keywordPrompt
            return
        self.data["question_keyword"]=keywords['question_keyword']
        print("get websites...")
        websites,success=getWebsites(self.data["question_keyword"])
        if not success:
            self.errorCode="Failed to get websites\n"
            return
        # process websites
        print("get contents of websites...")
        self.data["websites"]={website:{} for website in websites}
        goodWebsites=[]
        for i,url in enumerate(websites,1):
            try:
                if not is_allowed_by_robots(url):
                    continue
                headers = {"Content-Type": "application/json"}
                payload = {"url": url}
                response = requests.post("https://r.jina.ai/", headers=headers, json=payload)
                if response.status_code == 200:
                    self.data["websites"][url]["content"] = response.text
                else:
                    continue
                FCresult,success = chatWithGPT([{"role":"system","content":FCprompt},
                                                {"role":"user","content":f"Question: {self.data['question']}\nWebpage Content: {self.data['websites'][url]['content']}"}])
                if not success:
                    continue
                FCresult,success = jsonClean(FCresult,['answer','reason','additional','trust_score'])
                # trust_score is deprecated.
                if not success:
                    continue
                if FCresult['additional']!='':
                    # we ask model to provide abnormal cases in additional
                    # if additional is not empty, it means the website is not a good website
                    continue
                self.data['websites'][url]|=FCresult
                self.data['websites'][url]['index']=i
                goodWebsites.append(i)
                print(f"process website successfully: {i}")
                if len(goodWebsites)>=10:
                    break
            except Exception as e:
                continue
        if len(self.data['websites'])<3:
            # this could be changed to a warning
            # in practice, we use 3 here
            self.errorCode="too few websites processed"
            return
        # summarize the answer
        print("summarize the answer...")
        content=f"Question: {self.data['question']}\n"
        # filter out websites without index
        content_websites = [i for i in self.data['websites'].keys() if 'index' in self.data['websites'][i].keys()]
        for k in sorted(content_websites,key=lambda x:self.data['websites'][x]['index']):
            answer=self.data['websites'][k]['answer']
            reason=str(self.data['websites'][k]['reason'])
            content+=f"Webpage {self.data['websites'][k]['index']}:\nAnswer: {answer}\nReason: {reason}\n\n"
        
        result,success = chatWithGPT([{"role":"system","content":Summarizingprompt},{"role":"user","content":content}])
        if not success:
            self.errorCode=f"Error in summarize GPTCall: {result}"
            return
        result,success = jsonClean(result,['answers','additional','contradicts'])
        if not success:
            self.errorCode=f"Error in summarize jsonClean: {result}"
            return
        self.data['final_answer']=result
        self.data['websites']=list(self.data['websites'].values())
        self.data['contradicts']=self.data['final_answer']['contradicts']
        self.data['from']='created by user'
        self.data['answers']=self.data['final_answer']['answers']
        self.data.pop('final_answer')
        for ans in self.data['answers']:
            ans['answer_judge_keyword']=ans['answer judge keyword']
            ans.pop('answer judge keyword')
            for r in ans['reason']:
                r['reason_judge_keyword']=r['reason judge keyword']
                r.pop('reason judge keyword')
    def _save(self)->None:
        with open(self.saveTo,'w') as f:
            json.dump(self.data,f,ensure_ascii=False)
    def process(self)->None:
        self._process()
        if self.errorCode is not None:
            print("Program Failed due to the following error:")
            print(self.errorCode)
            self._save()
            print("Intermediate result is saved to",self.saveTo)
        else:
            self._save()
            print("Program Finished Successfully and saved to",self.saveTo)
if __name__=="__main__":
    pipeline=Pipeline("Which one is better? Genshin Impact or Honkai Impact 3rd?","test.json")
    pipeline.process()
    