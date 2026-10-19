# HyDE: searching with a hypothetical answer

Hypothetical Document Embeddings (HyDE), proposed by Gao and colleagues in 2022, change what gets embedded at query time. Instead of embedding the user's short question, the system first asks a language model to write a plausible answer passage, then embeds that generated passage and uses it as the search vector.

The idea is that a question and its answer look different. Questions are short and phrased as requests; documents are longer and declarative. A generated answer, even if some of its facts are wrong, uses the vocabulary and structure of real documents, so its embedding lands closer to the relevant passages than the question's embedding does.

## When it helps

HyDE helps most when queries are short or vague and when the embedding model was not trained on question-to-passage pairs. It was introduced as a zero-shot method: it improved retrieval without any relevance labels, using an off-the-shelf instruction-following model and an unsupervised dense retriever.

## Costs and risks

Every query now needs a language model call before retrieval can start, which adds hundreds of milliseconds to seconds of latency and a per-query cost. The generated passage can hallucinate specifics, such as a wrong version number or function name, and steer retrieval toward documents that match the hallucination. Generating several hypothetical passages and averaging their embeddings reduces the variance but multiplies the cost.

For queries that contain exact identifiers, error codes or names, HyDE can hurt: the model may paraphrase or drop the identifier, while keyword search would have matched it directly. Keeping a keyword leg on the original query text in a hybrid setup guards against this.

## Evaluating it

Compare HyDE against plain query embedding on the same labelled queries, broken down by query type. Expect gains on vague natural-language questions and losses on lookups. If the average gain is small, the latency and cost are rarely worth it; a better embedding model or hybrid search may close the same gap more cheaply.
