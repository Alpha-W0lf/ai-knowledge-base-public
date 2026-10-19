# CombSUM and CombMNZ score fusion

CombSUM and CombMNZ are score-based fusion methods from early metasearch research by Fox and Shaw in the 1990s. Instead of using positions, they add up the scores each retriever gave a document. CombSUM is the plain sum. CombMNZ multiplies that sum by the number of retrievers that returned the document at all, which boosts items that several systems agree on.

Both methods require the scores to be comparable first, and that is where most of the engineering effort goes. A cosine similarity of 0.82 and a BM25 score of 14.3 cannot be added directly. The standard fix is per-query normalisation.

## Normalising scores before adding them

Min-max normalisation rescales each list so its best score becomes 1 and its worst becomes 0: (s - min) / (max - min). It is simple, but it is sensitive to outliers and to how deep the list is. If one leg returns 10 results and the other returns 100, the minimum of the longer list is much lower, which compresses its scores differently.

Z-score normalisation subtracts the mean and divides by the standard deviation of the list. It handles outliers better but can produce negative values, and a query with a single strong match gets a very different distribution from a query with many weak ones. Some teams normalise against a fixed reference distribution measured offline instead of per query.

Whatever normalisation you pick, documents missing from a list need a value. Treating them as 0 after min-max scaling is common, but it quietly assumes that "not retrieved" means "worst possible".

## CombSUM in practice

Score fusion can beat rank fusion when the scores carry real information, for example when the vector leg's similarity drops sharply after the first two results. That drop is visible to CombSUM and invisible to rank-based methods. The price is calibration work: score distributions shift when you change the embedding model, the tokenizer or the corpus, and the normalisation has to be re-checked each time.

A practical sequence is to start with a rank-based method, measure, and only move to CombSUM or CombMNZ if a labelled dev set shows a gain that survives a held-out check. Keep the normalisation code in one place and log the raw scores next to the fused ones so regressions can be traced.
