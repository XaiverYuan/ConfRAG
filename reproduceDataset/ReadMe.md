# RAG Contradiction Benchmark
This repository accompanies our submission to the **NeurIPS 2025 Datasets & Benchmarks Track**.

**Author**: Yizhen Yuan

## How we generate our dataset
### Input: 
- question: str

### Output: 
A dictionary with the following structure:
- id: int
- question: str
- contradicts: bool    
- answers: list of dict
    - answer: str
    - answer judge keyword: list of str
    - index: list of int
    - reason: list of dict
        - explain: str
        - reason judge keyword: list of str
- websites: list of dict
    - content: str
    - answer: str
    - reason: list of str
    - additional: str
    - trust score: int
    - index: int
    - website: str

### Process:
1. Get websites
    - First, use GPT-4o to generate a keyword for better search results
    - Use the generated keyword to search on SerpAPI
2. Process each website
    - Check if the website is allowed to be crawled
        - If not, continue to the next website
    - Crawl the information using jina.ai
    - Ask GPT-4o about the question with the web content
        - If GPT-4o determines the website is unrelated or useless, continue to the next website
3. Summarize information
    - Based on processed websites, summarize clusters, answers, and reasons

## Repository Layout

- pipeline.py
    - Main script for dataset generation pipeline
    - Handles the entire process of data collection, processing, and generation
    - Integrates with various APIs and models for data processing
- PromptForFullContext.txt
    - The prompt used to get the answer and reasons of a website in process 2
- PromptSummarizingNew.txt
    - The prompt used to summarize the information in process 3
- PromptGetKeyWord.txt
    - The prompt used to get the keyword in process 1

## How to reproduce the dataset
1. Prepare your questions
    - If you want to reproduce the dataset, you can load the questions from the dataset.
2. Get a SerpAPI key from https://serpapi.com/ and fill it in the config.py variable SERPAPI_API_KEY
3. Install prerequisites for this folder
4. Run pipeline.py:
```python
pipeline = Pipeline("Your question", "where you want to save the json file")
pipeline.process()
```
> Note: Due to network issues or invalid model responses, there might be a chance of creation failure. Please try multiple times if needed.