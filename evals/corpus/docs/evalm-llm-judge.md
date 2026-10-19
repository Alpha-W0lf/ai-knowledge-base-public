# Using a language model as a relevance judge

Labelling relevance by hand is slow and expensive. A language model can act as a judge instead: give it the query, a passage and a grading rubric, and ask for a relevance grade with a short justification. This makes it practical to label thousands of query and passage pairs, or to evaluate generated answers for faithfulness to their sources.

## Make the judge trustworthy

An LLM judge is a model, and models need evaluation. Before trusting it, have people label a sample of a few hundred pairs, run the judge on the same pairs, and measure agreement, for example with Cohen's kappa or simple accuracy per grade. Look at the disagreements; they usually reveal a vague rubric rather than a bad model.

Write the rubric concretely. "Grade 2: the passage contains the information needed to answer the question. Grade 1: the passage is on the same topic but does not answer it. Grade 0: unrelated." Include the reasoning before the grade in the output format, and keep the temperature at zero for repeatability.

## Known biases

LLM judges tend to favour longer passages, passages that share wording with the query, and outputs written in their own style. When comparing two answers side by side, they show position bias, often preferring whichever answer comes first, so evaluate both orders and average. A judge from the same model family as the system under test can be lenient toward its own outputs.

## Keep the judge fixed

Pin the judge model version and prompt, and record both with every result. Hosted models change behind stable names, and a silently updated judge turns into a drift in your metrics that looks like a change in the system. Re-validate against the human sample whenever the judge changes.

## Where it fits

LLM judging is excellent for scaling labels, for regression monitoring, and for qualities that are hard to capture with string metrics, such as whether an answer is supported by its citations. It is a weak foundation for headline claims unless its agreement with people is measured and reported alongside the results.
