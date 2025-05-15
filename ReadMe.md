# RAG Contradiction Benchmark
This repository accompanies our submission to the **NeurIPS 2025 Datasets & Benchmarks Track**.

**Author**: Yizhen Yuan

## Repository Layout

- reproduce_dataset/
    - Scripts and configuration files for rebuilding the dataset from scratch or for creating a new dataset on your own questions / webpages / corpora.
    - Note: A regenerated dataset may differ slightly from the released version because of
        - changes in Google-Search / SerpAPI results
        - websites that appear, disappear, or are modified over time
        - the intrinsic stochasticity of large-language-model (LLM) generations.
- generate_result/
    - End-to-end evaluation pipeline. Run these scripts to obtain model predictions ready for scoring and later analysis.
    - Note: Model outputs can vary slightly across runs for the same reasons mentioned above.
- analysis_result/
    - Code for scoring and visualizing results. These reproduce the metrics, tables, and figures reported in the paper.
    - The scoring code itself is deterministic, but any upstream variation in the predictions will naturally propagate to the final numbers.
- Tools.py
    - Code for chat with models and json parse.
## Prerequisite
### Secret Keys
- OpenAI Secret Keys
- SerpAPI Secret Keys
- The secret key of the model you want to test on
- Fill in the keys in config.py
### packages
We are using python version 3.12.9. However we think as far as it supports ```list```, ```tuple``` as type annotation (after 3.9), it is fine. On the other hand, if it is not fine, use 3.12.9.

- beautifulsoup4==4.13.4

- datasets==3.6.0

- google-search-results==2.4.2

- openai==1.78.1

- readability_lxml==0.8.1

- requests==2.32.3

- lxml_html_clean==0.4.2
## Quick Start
- Fill out the Constants in Tools.py
- Test if it works properly
- Go to each sub-directory based on your purpose. Each sub-directory has its own ReadMe.
    - When I try to read other repo's Readme, I always struggle with those loooooooooooooooooooong ReadMe. In most case, I only want to redo 10% experiment.
- If you want to reproduce our dataset, please go to folder ```reproduceDataset```
- If you want to evaluate some model on our dataset, please go to folder ```generateResult```
- If you want to grade a existed json, please go to folder ```analysisResult```
    - For this folder, you need to generate a json from ```generateResult```
> Due to the difference in environment, if you see errors like: ModuleNotFoundError, No Module named 'Tools'. You could set your PYTHONPATH to the directory by 
```bash
export PYTHONPATH=$(pwd)
```
## FAQ
- **Q: I encountered errors when running XXXX. What should I do?**  
  **A:** Please try re-running the command multiple times and ensure that your secret keys are valid. Common causes for failure include:
  - Your secret key has exceeded its usage limit — you can test this by running a simple query.
  - The LLM returned an invalid or improperly formatted response.
  - The question is not clusterable, meaning:
    - The model assigns all documents to a single cluster, or
    - The model assigns one document to each cluster.

---

- **Q: In `analysisResult`, can we only evaluate results generated using your dataset?**  
  **A:** No. As mentioned in our paper, we are not just releasing a static dataset — we are providing a complete pipeline for dataset generation and evaluation.

  You can use arbitrary questions in the pipeline to generate reference clusters (via `pipeline.py`), then run arbitrary models or human annotators to generate answers (via `generate.py`). Finally, use `grade.py` to evaluate the results.

  ⚠️ Just make sure you load the JSON files correctly:  
  - Files from `pipeline.py` serve as ground truth references (equivalent to those in the dataset).  
  - Files from `generate.py` contain model- or human-generated answers to be evaluated.


## License
Code is released under the CC-by-4.0 License.
The dataset is distributed for research use only; please respect the original licences of all crawled webpages.

## Contact
For questions or issues, email <yuanyz21@mails.tsinghua.edu.cn>.