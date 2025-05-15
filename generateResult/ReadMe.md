# RAG Contradiction Benchmark

This repository accompanies our submission to the **NeurIPS 2025 Datasets & Benchmarks Track**.

**Author**: Yizhen Yuan

## Experiment Design

The experiment follows a structured input-output format as described below:

### Input:
- question: str
- how many clusters: int
- websites: list of dict
    - key: index:int
    - value:dict
        - content: str
        - index: int

### Output: 
- answers: list of dict
    - answer: str
    - index: list of int
    - reason: list of str

## Repository Structure

- `generate.py`: Main script for generating results
- `TestPrompt.txt`: Template prompt used for model interaction

## Usage Instructions

1. Get data:
- Load the output from pipeline.py:
```python
import json
with open('test.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
```
- Or, use the data from datasets
```python
from datasets import load_dataset
ds = load_dataset("OracleY/ConfRAG")
data=ds['train'][8]
```
Please remember which source you are using. If you used our dataset, please remember the index, it will be used in grading

2. Select the model you want to test on:
- By default GPT-4o
- You can change the model you want to test on by change the DEFAULT_MODEL in config.py
    - If you try to use a model that run in your own machine, you will need to write your own `chatWithGPT` and replace the one we listed in `Tools.py`
3. Process the data:
```python
GenerateResult(data, saveTo='result.json').process()
```

> **Note**: Due to potential network issues or invalid model responses, the generation process might occasionally fail. In such cases, please retry the operation.