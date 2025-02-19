[ ] Establish baseline
  [ ] Run 100 q for all models, no news + different prompt
[ ] Small scale experiments
  [ ] OpenAI o3-mini-high on 100 q
  [ ] OpenAI o3-mini-low on 100 q
  [ ] Run 100 q on gpt-4o and Claude Sonnet 3.6, different news articles
[x] Clean q4 data
[ ] Models tested:
  [x] OpenAI GPT-4o (August version)
  [x] Anthropic Claude 3.5 Haiku
  [x] Anthropic Claude 3.5 Sonnet
  [x] Anthropic Claude 3.6 Sonnet
  [x] Deepseek V3-chat
  [ ] Gemini 2.0 Flash on q3 and remaining q4
  [ ] Gemini 1.5 Pro
  [ ] OpenAI o1
  [ ] Llama 3 405 B
  [ ] Llama 3.2 70B
  [ ] Qwen 2.5 Max
  [ ] OpenAI o3-mini-high/low (depends on results of 100q)
  [ ] RWKV7-2.9B-world / RWKV7-7B-world
  [ ] QRWKV-72B
[ ] Categorization and breakdowns
  [ ] Do I need more sports questions (ie. should categories be more equal--currently extremely skewed politics and econ/finance)
[ ] Optional: Set up Manifold bot
  [ ] Talk to Manifold API
  [ ] Limit to questions closing in a week
  [ ] Ping it everyday?
[ ] Use Claude 3.5 Haiku to generate more questions for AskNews to enrich news articles
[x] Are models systematically biased
  [x] If so, can I correct it mechanically?
[x] Get remaining aibq4 questions from Metaculus
[x] Randomly select 100 representative samples
  [x] Ask models to predict with the same prompt but no news articles
  [ ] Run Brier score analysis etc.
[x] Download data for aibq4 from server
[x] Refactor direct prediction and narrative prediction code

# Paper
[ ] Frame as the models are getting better every iteration --> correlates with other benchmarks?
[ ] Point out that log scores are better than Brier scores
[ ] Community prediction of pros were higher than community prediction of bots
