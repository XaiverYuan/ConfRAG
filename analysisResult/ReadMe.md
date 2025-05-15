# RAG Contradiction Benchmark

This repository accompanies our submission to the **NeurIPS 2025 Datasets & Benchmarks Track**.

**Author**: Yizhen Yuan

## Repository Structure

- `grade.py`: Main script for grading the result

## Usage Instructions

1. Load the output from `generateResult/generate.py`:
```python
with open('xxx', 'r', encoding='utf-8') as f:
    result = json.load(f)
```
2. Load the output from the dataset:
```
if you are using the ConfRAG when you run `generateResult/generate.py`
```python
dataset=[]
with open("ConfRAG.jsonl",'r',encoding='utf-8') as f:
    for line in f:
        dataset.append(json.loads(l))
data=dataset[INDEX]#which data you are using when calling generate.py?
```
Or, you can load your own data generated from `reproduceDataset/pipeline.py` if you have chosen your own question to start with.

```python
with open('xxx', 'r', encoding='utf-8') as f:
    data = json.load(f)
```

3. grade the answer
```python
show(test(result,data))
```
