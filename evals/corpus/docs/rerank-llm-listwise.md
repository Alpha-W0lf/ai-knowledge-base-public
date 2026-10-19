# Listwise reranking with a large language model

A large language model can rerank search results directly. The retriever produces a shortlist, the passages are placed in a prompt with identifiers, and the model is asked to output the identifiers in order of relevance to the query. Because the model sees several candidates at once, this is called listwise reranking, in contrast to pointwise scoring of one passage at a time.

Listwise prompting lets the model compare candidates against each other, which helps when the question is subtle or several passages are partly relevant. Work such as RankGPT showed that general-purpose chat models can rival trained rerankers on public benchmarks with this approach.

## Sliding windows

Context limits and attention quality cap how many passages fit in one prompt. The standard workaround is a sliding window: rank the last 20 candidates, keep the best 10, slide the window up by 10, and repeat until the window reaches the top. Relevant passages bubble upward like a partial bubble sort. Window size and step size trade cost against quality.

## Costs and failure modes

LLM reranking is slow and expensive compared with a small cross-encoder: each query costs one or more long prompts, and latency is measured in seconds. Outputs can be malformed, with missing or duplicated identifiers, so the caller must validate and repair the ranking, falling back to the first-stage order when parsing fails. Position bias is real: models tend to favour passages placed first or last in the prompt, so shuffling and multiple passes are sometimes used to average it out. Results also drift when the provider updates the model behind a fixed name.

## Distillation

A common production pattern uses an LLM only offline. The LLM ranks shortlists for a large sample of real queries, and those rankings become training labels for a small cross-encoder or a bi-encoder. The small model serves traffic cheaply and deterministically, while the LLM's judgement is baked into its weights. Evaluate the distilled model against held-out human labels, because inheriting the LLM's biases is easy to miss when the LLM is also the judge.
