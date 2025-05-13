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
### packages
## Quick Start
- Fill out the Constants in Tools.py
- test if it works properly
- go to each sub-directory based on your purpose. Each sub-directory has its own ReadMe.
> Due to the difference in environment, if you see errors like: ModuleNotFoundError, No Module named 'Tools'. You could set your PYTHONPATH to the directory by 
```bash
export PYTHONPATH=$(pwd)
```


## License
Code is released under the CC-by-4.0 License.
The dataset is distributed for research use only; please respect the original licences of all crawled webpages.

## Contact
For questions or issues, email <yuanyz21@mails.tsinghua.edu.cn>.