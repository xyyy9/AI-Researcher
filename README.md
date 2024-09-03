<h1 align="center">
  <b>Research Ideation Agent & Human Study</b><br>
  <b>by Stanford NLP</b><br>
</h1>

![teaser](figures/title.png)

This repo implements the research ideation agent used in our paper "Are LLMs Better than Experts on Generating Novel Research Ideas? A Large-Scale Human Study with 100+ NLP Researchers". Based on evaluation results by 79 expert reviewers, the ideas produced by our agent were rated as more novel than those generated by human experts. 

The input to our agent is a research topic described as a natural language sentence; and the output is a list of project proposals ranked by their estimated quality. The project proposals are designed to be very detailed such that a student can directly follow each step in the proposal to execute the entire project.

Our agent pipeline consists of the following modules:
(1) Related Paper Search;
(2) Grounded Idea Generation;
(3) Idea Deduplication;
(4) Project Proposal Generation;
(5) Project Proposal Ranking;
(6) Project Proposal Filtering.

These modules are designed to be run sequentially as an end-to-end idea generation pipeline. Each module can also be run separately as standalone research assistance tools. We describe how to run each module as well as the entire pipeline below.

## Table of Contents

1. [Setup](#setup)
2. [Related Paper Search](#related-paper-search)
3. [Grounded Idea Generation](#grounded-idea-generation)
4. [Idea Deduplication](#idea-deduplication)
5. [Project Proposal Generation](#project-proposal-generation)
6. [Project Proposal Ranking](#project-proposal-ranking)
7. [Project Proposal Filtering](#project-proposal-filtering)
8. [End-to-End Pipeline](#end-to-end-pipeline)
9. [Review Scores](#review-scores)


## Setup

You can set up the environment by running the following commands:

```bash
git clone https://github.com/NoviScl/AI-Researcher.git
cd AI-Researcher
conda create -n ai-researcher python=3.10
conda activate ai-researcher
pip install -r requirements.txt
```

Create `keys.json` and store it in the project directory. The file should look like this:

```
{
    "api_key": "Your OpenAI API Key",
    "organization_id": "Your OpenAI Organization ID (Optional)",
    "s2_key": "Your Semantic Scholar API Key (Optional)",
    "anthropic_key": "Your Anthropic API Key"
}
```

## Related Paper Search

The related work search module will iteratively propose search queries and search through the Semantic Scholar API. We then use an LLM to score the relevance of retrieved papers for reranking. The module takes a topic description or an idea as input and returns a list of the most relevant papers as output.

Example usage (finding related papers for a given topic):
```
cd ai_researcher 
bash scripts/lit_review.sh 
```

The `max_paper_bank_size` is a hyperparameter to control when to stop the paper search process (until the specified number of papers has been retrieved). The generated search queries as well as the ranked papers will be stored in the specified cache file. The cache file can be used as part of the input to the idea generation module. We used `max_paper_bank_size=120` for the experiments in our paper and used `max_paper_bank_size=50` in this demo example. Running this demo example costs $0.51. 


## Grounded Idea Generation

The idea generation module takes a topic description and optionally a list of relevant papers as input, and returns a list of generated ideas as the output. 

Example usage: 
```
cd ai_researcher 
bash scripts/grounded_idea_gen.sh
```

Due to the max output length constraint, we recommend generating ideas in batches of 5 (`ideas_n=5`) and running the script multiple times with different seeds to collect a larger set of ideas. You can set `RAG` to either `True` or `False` to turn on or off retrieval augmentation where we ground the idea generation on retrieved papers. We generated 4K ideas for each topic in our paper. In the demo example, we only generate 20 seed ideas, which costs $0.85.

## Idea Deduplication

We do a round of deduplication to remove similar ideas generated by the grounded idea generation module. We set a threshold of `similarity_threshold=0.8` cosine similarity based on the sentence embeddings to determine if two ideas are similar. The embedding is from the `sentence-transformers` library so this step doesn't cost any API credits to run.

Example usage:
```
cd ai_researcher
bash scripts/idea_dedup.sh
```

## Project Proposal Generation

Next, we expand each seed idea into a detailed project proposal. 

Example usage:
```
cd ai_researcher
bash scripts/project_proposal_gen.sh
```

Since the project proposals are long, each generation takes an average of $0.3 and running the whole demo example here takes $2.9.

## Project Proposal Ranking

We rank all the generated project proposals by using an LLM ranker. 

Example usage:
```
cd ai_researcher
bash scripts/project_proposal_ranking.sh
```

The output will be a json file storing the score of each project proposal, which you can use to rank the proposals. The demo example costs $0.74 to rank 10 project proposals for 5 rounds of scoring.

## Project Proposal Filtering (Optional)

If you wish, you can also apply the last filtering step where we check whether each project proposal is novel and feasible. For novelty check, we will retrieve the most similar papers to the generated project proposal and compare them one by one. The project proposal will be filtered as long as it's judged as the same as any of the retrieved papers by the LLM.

Example usage:
```
cd ai_researcher
bash scripts/project_proposal_filter.sh
```

All the project proposals that passed the filters will be stored in the specified output cache directory, along with the retrieved papers used for the novelty check. Note that this filtering step is rather expensive (it costs $1.9 to check through each project proposal in this demo example). You can lower the costs by reducing the number of retrieved papers for novelty check.

## End-to-End Pipeline

We also provide a script that runs the entire pipeline to generate the project proposals based on the given research topic.

Example usage:
```
cd ai_researcher
bash scripts/end_to_end.sh
```
We are not releasing the full set of AI-generated project proposals since we are using them in the next phase of our study and we want to avoid any potential bias. However, you should be able to reproduce ideas with similar quality by following the steps above with an increased inference budget. 

## Review Scores

We release the full set of review scores collected in the `results` directory, along with all the scripts that we used to do the stistical tests in the paper. 
All reviewer names have been anonymized to protect their information.
We will release the free-text rationales later after phase II of our study is completed.

## Citation

Please cite the paper and star this repo if you find our work useful, thanks! Feel free to contact clsi@stanford.edu or open an issue if you have any questions.

```bibtex
@article{si2024llmideas,
      title={Can LLMs Generate Better Research Ideas than Experts? A Large-Scale Human Study with 100+ NLP Researchers}, 
      author={Chenglei Si and Diyi Yang and Tatsunori Hashimoto},
      year={2024},
      journal={arXiv}
}
```