# Matryoshka embeddings and dimension truncation

Matryoshka representation learning, introduced by Kusupati and colleagues in 2022, trains an embedding model so that the first few dimensions of each vector are already a useful embedding on their own. The loss is applied not only to the full vector but also to prefixes of it, for example the first 64, 128, 256 and 512 dimensions. Like nested dolls, each shorter vector sits inside the longer one.

The practical result is that you can truncate a 768-dimensional vector to 256 dimensions, renormalise it, and still get most of the retrieval quality, while storing a third of the data and computing distances three times faster.

## Using truncation safely

Truncation only works for models trained this way. Cutting the dimensions of an ordinary embedding model throws away information arbitrarily and usually hurts badly. Check the model card for a stated list of supported dimensions.

After truncating, normalise the shorter vector to unit length again before computing cosine similarity or dot products. Forgetting this step is a common bug, and it skews scores toward documents whose leading dimensions happen to have large values.

The chosen dimension is part of the model configuration. An index built from 256-dimensional prefixes cannot be queried with 768-dimensional query vectors, so the dimension belongs in the index version stamp alongside the model name.

## Coarse-to-fine search

Matryoshka vectors enable a two-pass search. The first pass uses short prefixes, such as 64 dimensions, to scan a large candidate set cheaply. The second pass rescores the best candidates using the full vectors. This resembles quantization with rescoring, and the two techniques combine well: short prefixes plus binary quantization give a very small first-pass index.

## Choosing a size

The quality curve is usually flat at first and then drops: going from 768 to 512 dimensions may cost almost nothing, while going from 128 to 64 costs a lot. Measure recall at your shortlist size on labelled queries for a few candidate sizes, and pick the smallest one whose loss you can accept. Record the choice and the measurement in the same place, so the trade-off can be revisited when the model changes.
