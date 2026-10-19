# Vector quantization: int8 and binary embeddings

A 768-dimensional embedding stored as 32-bit floats takes about 3 KB. Ten million of them take about 30 GB before any index overhead. Quantization stores each vector in fewer bits so that more of the index fits in memory and distance computations run faster.

## Scalar int8 quantization

Scalar quantization maps each float dimension to an 8-bit integer. The range for each dimension is estimated from a sample of vectors, often using percentiles to ignore outliers, and values are scaled into the range -128 to 127. Storage drops by four times. Quality loss is usually small, often within a percent or two on retrieval benchmarks, because embedding values are concentrated in a narrow range.

## Binary quantization

Binary quantization keeps only the sign of each dimension: one bit per dimension, a 32 times reduction. Distances become Hamming distances, which CPUs compute extremely fast with population-count instructions. The quality loss is larger and varies by model; some embedding models are trained to tolerate binarisation and lose little, others degrade badly.

## Rescoring

The standard way to recover quality is to rescore. Search the compressed index for a generous candidate set, for example the top 100 by Hamming distance, then recompute exact similarities for those candidates using the full-precision vectors, which can stay on disk because only a few are read per query. Retrieval quality then approaches the full-precision result at a fraction of the memory cost.

## Product quantization is different

Product quantization, used in IVF-PQ indexes, splits each vector into sub-vectors and replaces each with the id of its nearest centroid from a learned codebook. It is a learned compression tied to the index structure, while scalar and binary quantization are fixed transforms applied per dimension. They can be combined, but they solve slightly different problems.

## Measure before shipping

Quantization effects depend on the model and the data. Build the quantized index, run the same labelled queries against full and reduced precision, and compare recall at the cut-off your reranker or reader uses. A drop that does not change the top 10 is usually acceptable; a drop that removes correct documents from the shortlist is not.
