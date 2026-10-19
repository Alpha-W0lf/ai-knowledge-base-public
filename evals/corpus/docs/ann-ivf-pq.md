# IVF-PQ: inverted file indexes with product quantization

IVF-PQ combines two ideas to search very large vector collections with modest memory. The inverted file (IVF) part clusters the vectors with k-means into a set of partitions, each represented by a centroid. The product quantization (PQ) part compresses every vector so that millions fit in memory.

At query time, the index compares the query with all centroids, picks the nprobe closest partitions, and scans only the vectors in those partitions. With 1,000 partitions and nprobe = 10, roughly one percent of the collection is scanned per query.

## Product quantization

PQ splits each vector into m sub-vectors, for example 96 sub-vectors of 8 dimensions for a 768-dimensional embedding. For each sub-vector position, it learns a small codebook of 256 centroids, so each sub-vector is replaced by a one-byte code. A 3 KB float vector becomes 96 bytes. Distances are approximated with precomputed lookup tables, which makes scanning compressed vectors fast.

## Parameters

The number of partitions is usually set near the square root of the collection size. nprobe is the main runtime trade-off: more partitions scanned means higher recall and higher latency. The number of PQ sub-vectors controls compression versus accuracy. Because the centroids and codebooks are learned, the index needs a training sample that represents the data, and it should be retrained when the data distribution shifts or the embedding model changes.

## Typical problems

Vectors near a partition boundary can be missed when their partition is not probed, which is why recall plateaus below 100 percent at low nprobe. PQ distances are approximate, so the best results are commonly refined by re-ranking a candidate set with exact distances from full-precision vectors stored on disk. Very small collections give k-means too little data to learn meaningful partitions; below a few hundred thousand vectors, a graph index or a plain scan is often better.

## When to choose it

IVF-PQ is a strong choice for collections of tens of millions of vectors or more on a single machine, when memory is the binding constraint and a small recall loss is acceptable. Vector databases such as LanceDB use IVF-PQ as a default disk-friendly index type for this reason.
