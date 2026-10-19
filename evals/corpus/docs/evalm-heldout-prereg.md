# Held-out query sets and pre-registration

Every retrieval system is tuned, whether deliberately or not. Choosing a chunk size, a fusion constant, a prompt or a model after looking at metrics on a query set fits the system to those queries. The metric on that set then overstates how the system performs on queries it has never seen. The fix is to keep a separate held-out set that is used only for reporting.

## Splitting the queries

Write or collect the full query set first, then split it before running anything. A common split is half for development and half held out, stratified so both halves cover the same topics and query types. Use a fixed random seed and record it, so the split is reproducible and nobody can quietly move hard queries into the dev half.

Tune freely on the dev set: try ideas, read failures, adjust. Run the held-out set only when the system is frozen, and report what it shows. If held-out results are disappointing, the honest move is to report them, go back to the dev set, and build a new held-out set for the next round, because a held-out set that has influenced decisions is no longer held out.

## Pre-registration

Pre-registration means writing down, before the first held-out run, exactly what will be measured and what result counts as success. The document names the dataset files and their checksums, the metrics and cut-offs, the systems being compared, the statistical test, and the decision rule, such as "the reranker becomes the default only if held-out nDCG@10 improves by at least 0.03 and the 95 percent confidence interval of the difference excludes zero."

Committing that document to version control before the results exist creates a timestamp that anyone can check. It prevents the most common self-deception in evaluation: picking the metric, cut-off or subset that happens to look good after seeing the numbers.

## Practical rules

Never add held-out queries to training data or few-shot prompts. Add new held-out cases only in a new, versioned file. Keep the dev and held-out files byte-for-byte unchanged once registered, and verify their checksums in the evaluation code. Report failures with the same prominence as successes.
