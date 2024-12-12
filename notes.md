# Notes: 

Scraping folder contains scraping information
- `metaculus.py` scrapes all binary, resolved questions.
- `metaculus_aibqi.py` scrapes all resolved questions from aibq{i} tournament
- `metaculus_aibq3_wd.py` scrapes all resolved questions and background information
- `metaculus_data_binary_resolved_all.json` contains ALL binary, resolved questions from Metaculus
- `metaculus_data_binary_resolved_May24.json` contains ALL binary, resolved questions from Metaculus after May 1, 2024
- `metaculus_data_aibq3_wd.json` contains all binary, resolved questions from Metaculus in Q3 LLM Benchmarking tournament
- `metaculus_data_aibq4_wd.json` contains all binary, resolved questions from Metaculus in Q4 LLM Benchmarking tournament
- `classification.py` gets Gemini to categorize the questions
- `metaculus_data_aibq3_categories.csv` has all the categories
- `metaculus_data_path.json` exists because claude sonnet 3.5 old errorred out in the first resolution

Graphs folder contains visualizations

`newspipeline.py` takes each question query and open_date and gets the relevant articles from *before* that date from AskNews

`models.py` contains all the code to call models. Prompts located in `prompts.py`
`directprediction.py` asks the LLM makes the prediction after reading articles from aibq3_news.json

`extract_probabilities.py` gets probabilities from aibq3_predictions_{model name}.json and writes it to a .csv
`extract_probabilities_conf.py` gets probabilities from aibq3_predictions_conf_{model name}.json and writes it to a .csv

`Narrativeprediction.py` asks the LLM to write a script between Tetlock and Silver the day *after* the question's scheduled close date, and say the probability the models had calculated before the event.

`Brier_score.py` calculates the Brier score for the .csv that has BOTH gpt-4o and sonnet 3.5 old
`Brier_score_singlemodel.py` calculates the Brier score for a .csv that only has one model (currently 4o) 

# Results:
## Direct Prediction
### Brier Scores for 4o and old Sonnet 3.5
Individual Model Brier Scores(score, standard error):
gpt0: 0.2104, 0.0132
gpt1: 0.1989, 0.0130
gpt2: 0.1985, 0.0127
gpt3: 0.1951, 0.0118
gpt4: 0.2010, 0.0125
claude0: 0.1923, 0.0127
claude1: 0.2015, 0.0130
claude2: 0.2100, 0.0135
claude3: 0.1985, 0.0129
claude4: 0.1992, 0.0129

Ensemble Brier Scores (score, standard error):
GPT median: 0.1968, 0.0122
Claude median: 0.1947, 0.0125
GPT mean: 0.1924, 0.0115
Claude mean: 0.1910, 0.0119
Combined mean: 0.1912

Statistical Test Results:
Paired t-test (GPT vs Claude):
t-statistic: 0.1078
p-value: 0.9141
The difference between GPT and Claude scores is not statistically significant (p >= 0.05).

Effect size (Cohen's d): 0.0021
The effect size is small.

### Brier scores for new Sonnet model: 
Individual Model Brier Scores (score, standard error):
claude0: 0.1860, 0.0127
claude1: 0.1798, 0.0127
claude2: 0.1919, 0.0131
claude3: 0.1826, 0.0127
claude4: 0.1851, 0.0128
Median: 0.1810, 0.0126
Mean: 0.1785, 0.0120

Cross-Model Ensemble Brier Scores (4o and Sonnet-new):
Median of all predictions: 0.1791
Mean of all predictions: 0.1792

### Brier score for 3.5 Haiku
Individual Model Brier Scores (score, standard error):
claude0: 0.2531, 0.0145
claude1: 0.2491, 0.0136
claude2: 0.2601, 0.0142
claude3: 0.2507, 0.0134
claude4: 0.2448, 0.0138
Median: 0.2476, 0.0135
Mean: 0.2415, 0.0128

### Brier scores for 4o with confidence levels:
Individual Model Brier Scores (score, standard error):
gpt0: 0.2186, 0.0133
gpt1: 0.2141, 0.0134
gpt2: 0.2166, 0.0130
gpt3: 0.2095, 0.0129
gpt4: 0.2122, 0.0133
Median: 0.2100, 0.0126
Mean: 0.2046, 0.0120

### Brier scores for Gemini 2.0 Flash (q4 dataset):
Individual Model Brier Scores (score, standard error):
geminiflash20: 0.2351, 0.0192
geminiflash21: 0.2249, 0.0179
geminiflash22: 0.2338, 0.0206
geminiflash23: 0.2216, 0.0203
geminiflash24: 0.2439, 0.0208

Ensemble Brier Scores (score, standard error):
Median Ensemble: 0.2227, 0.0189
Mean Ensemble: 0.2194, 0.0173

### future prompt:
Average Brier Scores (score, standard error):
gpt0: 0.2099, 0.0143
gpt1: 0.2005, 0.0138
gpt2: 0.2117, 0.0143
gpt3: 0.1887, 0.0136
gpt4: 0.2097, 0.0147
claude0: 0.1987, 0.0132
claude1: 0.2074, 0.0137
claude2: 0.2038, 0.0135
claude3: 0.2119, 0.0133
claude4: 0.2013, 0.0135

Ensemble Brier Scores (score, standard error):
GPT median: 0.1950, 0.0132
Claude median: 0.1897, 0.0123
GPT mean: 0.1901, 0.0124
Claude mean: 0.1891, 0.0117

Statistical Test Results:
Paired t-test (GPT vs Claude):
t-statistic: -0.0984
p-value: 0.9216
The difference between GPT and Claude scores is not statistically significant (p >= 0.05).

Effect size (Cohen's d): -0.0022
The effect size is small.

## Narrative Prompt

### Brier scores for 4o
Average Brier Scores:
gpt0: 0.2694
gpt1: 0.2819
gpt2: 0.2439
gpt3: 0.2644
gpt4: 0.2805

GPT median: 0.2430

### Brier scores for 4o after I fixed flipped scenarios
Individual Model Brier Scores (score, standard error):
gpt0: 0.2651, 0.0187
gpt1: 0.2718, 0.0191
gpt2: 0.2252, 0.0179
gpt3: 0.2552, 0.0184
gpt4: 0.2766, 0.0188
Median: 0.2313, 0.0173
Mean: 0.2080, 0.0133

### 4o Brier scores prompted to be Tetlock and Silver
Individual Model Brier Scores (score, standard error):
gpt0: 0.2302, 0.0104
gpt1: 0.2255, 0.0097
gpt2: 0.2161, 0.0096
gpt3: 0.2177, 0.0100
gpt4: 0.2212, 0.0101
Median: 0.2053, 0.0088
Mean: 0.2087, 0.0079

### new Sonnet 3.5 Brier scores prompted to be Tetlock and Silver
Average Brier Scores (sonnet-new):
Individual Model Brier Scores (score, standard error):
claude0: 0.2245, 0.0135
claude1: 0.2219, 0.0135
claude2: 0.2463, 0.0175
claude3: 0.2329, 0.0136
claude4: 0.2264, 0.0133
Median: 0.2197, 0.0130
Mean: 0.2180, 0.0120

Average Brier Scores (sonnet-new): <-- only ran 3 times by mistake
claude0: 0.2177
claude1: 0.2278
claude2: 0.2348
Median: 0.2156
Mean: 0.2090


##  Brier Scores by Category (average of 5 runs)
category,Claude Sonnet (new),Claude Haiku,Claude Sonnet (old),GPT-4o,Narrative Claude,Narrative 4o,Conf 4o
Arts & Recreation,0.1657,0.1686,0.1584,0.1683,0.1686,0.2076,0.1633
Economics & Business,0.2223,0.2767,0.2258,0.2149,0.2819,0.2429,0.2289
Environment & Energy,0.2073,0.338,0.2334,0.2845,0.2695,0.2568,0.3087
Healthcare & Biology,0.1697,0.2087,0.1769,0.1658,0.1989,0.1868,0.181
Politics & Governance,0.1624,0.2324,0.1807,0.1699,0.2283,0.1919,0.19
Science & Tech,0.2047,0.3134,0.2425,0.2623,0.1994,0.2503,0.2744
Sports,0.1554,0.2086,0.1714,0.1925,0.2075,0.2677,0.1844

## Misc
### Comparing Sonnet new and o1-preview on test set
Individual Model Brier Scores:
gpt0: 0.1213
gpt1: 0.3114
gpt2: 0.2421
gpt3: 0.2142
gpt4: 0.2813

Ensemble Brier Scores:
Median Ensemble: 0.2625
Mean Ensemble: 0.2097

claude0: 0.2179
claude1: 0.0845
claude2: 0.2255
claude3: 0.1563
claude4: 0.2629

Ensemble Brier Scores:
Median Ensemble: 0.1566
Mean Ensemble: 0.1748
