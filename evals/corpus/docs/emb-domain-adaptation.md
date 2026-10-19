# Fine-tuning embedding models for a specific domain

General-purpose embedding models are trained on web text, question-answer pairs and public datasets. They can struggle with specialised vocabulary: internal product names, legal or medical terms, error codes, or jargon that means something different inside one company. Fine-tuning adapts the model to that vocabulary using pairs of queries and relevant passages from the target domain.

## Getting training pairs

Real user queries with clicked or confirmed results are the best source, but most teams do not have enough at the start. A common bootstrap is to generate synthetic queries: ask a language model to write questions that each passage answers, then use those (question, passage) pairs as positives. Filter the generated questions, because some will be answerable from many passages or from none, which teaches the wrong signal.

## Mining hard negatives

Contrastive training needs negatives as well as positives. Random passages are too easy; the model already knows a passage about billing is not about networking. Hard negatives are passages that the current model ranks highly but that do not answer the query. Mine them by running the base model over the training queries and taking top-ranked passages that are not labelled relevant. Check a sample by hand, because some "negatives" are actually relevant passages missing a label, and training against them hurts.

## Training and evaluation

Fine-tuning usually uses a multiple-negatives ranking loss with a modest learning rate for one to a few epochs on a few thousand pairs. Overfitting shows up quickly on small datasets, so keep a held-out set of real queries that no synthetic generation touched, and compare the fine-tuned model against the base model and against keyword search on it.

## Operational cost

A fine-tuned model is a new model. Every document must be re-embedded, the index version stamp must change, and the model artefact must be stored, versioned and served. Before committing to that, check whether cheaper fixes close the gap: adding keyword search for exact terms, expanding acronyms at query time, or adding a reranker. Fine-tuning tends to win when the domain vocabulary is large and stable and when a meaningful set of real labelled queries exists to prove it.
