[] Gemini Flash 2.0 on original dataset
[] Run 100 q for all models, no news
[] Run 100 q for all models, different prompt
[] Run 100 q for all models, different news articles
[] Llama 405 B on both datasets
[] Clean q4 data
[] OpenAI o1
[] OpenAI o3-mini-high on 100 q
[] OpenAI o3-mini-low on 100 q4
[] OpenAI o3-mini-[blank], whatever performs better
[] Llama 3.2 70-B on both datasets
[] Categorization and breakdowns
[] Set up Manifold bot
  [] Talk to Manifold API
  [] Limit to questions closing in a week
  [] Ping it everyday?
[] Use Claude 3.5 Haiku to generate more questions for AskNews to enrich news articles
[x] Are models systematically biased
  [x] If so, can I correct it mechanically?
[x] Get remaining aibq4 questions from Metaculus
[x] Randomly select 100 questions
  [] Ask models to predict with the same prompt but no news articles
  [] Run Brier score analysis etc.
[x] Download data for aibq4 from server
[x] Refactor direct prediction and narrative prediction code

# Paper
[] Frame as the models are getting better every iteration --> correlates with other benchmarks?
[] Point out that log scores are better than Brier scores
[] Community prediction of pros were higher than community prediction of bots
