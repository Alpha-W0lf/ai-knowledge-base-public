# Borda count and Condorcet fusion for ranked lists

Borda count comes from voting theory. Each retriever is a voter that ranks the candidates. A candidate earns points from each voter based on its position: with n candidates, first place gets n points, second place n - 1, and so on down to 1. The fused order is the order of total points.

Borda is position-based, like reciprocal rank fusion, but it is linear: the difference between first and second place is worth exactly as much as the difference between fiftieth and fifty-first. That makes it more sensitive to the long tail of each list. In retrieval, where only the top few positions matter to a user, this linear weighting is usually a weakness, and it explains why Borda tends to trail RRF in published comparisons.

## Handling partial lists

Retrievers return truncated lists, so most candidates are missing from at least one of them. A common convention gives missing candidates the points of the last position, or splits the remaining points evenly among all unranked candidates. The choice changes results noticeably on short lists, so write it down and keep it fixed between experiments.

## Condorcet fusion

Condorcet fusion asks a pairwise question: for each pair of documents, does a majority of retrievers rank A above B? The winner is a document that beats every other document head to head. Montague and Aslam showed that a Condorcet ordering can be built efficiently by sorting with a majority-vote comparator. With only two retrievers, ties are frequent, because the legs disagree on many pairs, so Condorcet methods make more sense with three or more systems.

## Where voting methods fit

Voting methods are attractive when you combine many retrievers whose scores you cannot or do not want to interpret, such as several different embedding models plus a keyword engine. With two legs in a hybrid search system, the simpler reciprocal formula usually wins on both quality and explainability. Borda is still a useful sanity baseline: if a new fusion method cannot beat Borda on your dev set, it is probably not exploiting anything real.
