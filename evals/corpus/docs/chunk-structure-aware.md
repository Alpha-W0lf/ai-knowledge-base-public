# Structure-aware and recursive chunking

Documents usually carry structure: headings, sections, lists, code blocks and tables. Structure-aware chunking uses that structure to decide where to split, so that each chunk is a coherent unit such as one section under one heading.

A recursive splitter is the common implementation. It tries the coarsest separator first, for example top-level markdown headings. Any piece that is still too long is split again with the next separator, such as second-level headings, then blank lines between paragraphs, then sentence ends, and finally spaces. The result respects the document's own boundaries wherever the size limit allows.

## Keeping the heading path

A chunk taken from the middle of a long manual often makes no sense alone. "Set the value to 30 seconds" is useless without knowing which setting. Prepending the heading path, such as "Configuration > Timeouts > Upstream", to each chunk before embedding gives the vector the missing context, and it doubles as a readable citation. Store the path as metadata as well, so the user interface can show it.

## Special content

Code blocks and tables should not be cut in the middle. A table split across two chunks loses its header row in the second half, and half a function rarely answers a question. Treat them as atomic units where possible, and if a table is too large, repeat the header row in each piece.

HTML and PDF sources need their structure recovered first. PDF text extraction often scrambles reading order in multi-column layouts and repeats page headers and footers on every page; strip those before chunking, or every chunk will contain the same footer text and match queries about it.

## When it helps

Structure-aware chunking pays off on well-organised content: documentation, manuals, policies and wiki pages. It does little for transcripts, chat logs or scraped text with no reliable headings, where a fixed window is just as good and simpler. As with any chunking choice, compare it against a fixed-window baseline on the same labelled queries before switching, because the effect varies a lot between corpora.
