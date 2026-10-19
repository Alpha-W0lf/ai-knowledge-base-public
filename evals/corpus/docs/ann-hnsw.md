# HNSW graph indexes for approximate nearest neighbour search

Hierarchical Navigable Small World graphs, described by Malkov and Yashunin in 2016, are the most widely used index for approximate nearest neighbour search over embeddings. Each vector is a node in a graph and is linked to a small number of nearby vectors. The graph has several layers: the top layer is sparse and contains few nodes, and each lower layer contains more nodes, down to the bottom layer, which contains every vector.

A search starts at an entry point on the top layer and greedily moves to whichever neighbour is closest to the query, descending a layer whenever it can no longer improve. The sparse upper layers make long jumps across the space; the dense bottom layer refines the result locally. Search cost grows roughly logarithmically with the number of vectors.

## The three knobs

M sets how many links each node keeps. Larger M improves recall and robustness but increases memory and build time; values between 16 and 64 are typical. efConstruction sets how many candidates are considered while inserting each node; higher values build a better graph more slowly. efSearch sets how many candidates are kept during a query; it is the main runtime trade-off between recall and latency, and it can be changed per query without rebuilding.

## Strengths and costs

HNSW offers excellent recall at low latency and supports inserting new vectors at any time without retraining. Its main cost is memory: the full vectors plus the link lists usually must sit in RAM for good performance. Deletes are awkward; most implementations mark nodes as deleted and clean up during periodic rebuilds, and heavy churn degrades the graph.

## Tuning in practice

Measure recall against exact brute-force search on a sample of real queries, at the cut-off your application uses, such as recall@10. Raise efSearch until recall stops improving or latency exceeds your budget. If memory is the constraint, combine HNSW with scalar quantization, or move to a disk-oriented index. For collections of a few thousand vectors, skip the index entirely: an exact scan is fast enough and has perfect recall.
