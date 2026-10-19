# Mean reciprocal rank (MRR)

Mean reciprocal rank measures how high the first relevant result appears. For each query, find the rank of the first relevant document and take its reciprocal: 1 if it is first, 1/2 if it is second, 1/3 if third, and 0 if no relevant document appears within the cut-off. MRR is the average of these values over all queries.

MRR fits tasks where the user needs one good answer and stops looking once they find it: navigational search, question answering with a single correct passage, and retrieval that feeds a reader which mostly uses the top result.

## Reading the number

MRR is dominated by the top positions. Moving the right document from rank 2 to rank 1 adds 0.5 for that query; moving it from rank 9 to rank 8 adds about 0.014. An MRR of 0.8 roughly means the correct document is usually first and occasionally second. Report the cut-off, such as MRR@10, because results beyond the cut-off count as zero and different cut-offs give different numbers.

## Limitations

MRR only looks at the first relevant document. If a query has three relevant documents and the system returns all three at ranks 1, 2 and 3, it gets the same score as a system that returns one relevant document at rank 1 followed by junk. For queries with many relevant results, or with graded relevance, use nDCG or mean average precision as well.

MRR is also coarse on small query sets. With 50 queries, one query changing from rank 1 to rank 2 moves MRR by 0.01, so differences of a few hundredths between two systems can be noise. Report a confidence interval, for example from a paired bootstrap over queries, before claiming that one system beats another.

## Hit rate at one

A related and even simpler metric is hit@1, the share of queries whose top result is relevant. It is easy to explain to non-specialists, and paired with MRR it shows whether a system that is often second could be improved by a reranker.
