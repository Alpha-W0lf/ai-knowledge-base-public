# Semantic chunking with embedding breakpoints

Semantic chunking places chunk boundaries where the topic changes, instead of at fixed sizes or at headings. The usual method embeds each sentence, computes the similarity between neighbouring sentences, and starts a new chunk wherever the similarity drops sharply. The idea is that a dip in similarity marks a shift from one subject to another.

## The breakpoint rule

Raw similarity values vary between documents, so a fixed cut-off such as 0.7 does not travel well. Implementations usually compute all the neighbour distances in a document and cut at a percentile, for example every gap larger than the 95th percentile of distances. Others smooth the similarity curve over a window of three to five sentences first, so that one odd sentence does not create a boundary. A maximum chunk size is still needed as a backstop, because a long passage on one topic would otherwise become a single huge chunk.

## Costs

Semantic chunking embeds every sentence once just to decide where to split, and then embeds the resulting chunks again for retrieval. For a large corpus this roughly doubles the embedding bill at ingest. Boundaries also depend on the embedding model, so changing the model changes the chunks, their ids and every citation that pointed at them.

## Evidence

Results in the literature and in practitioner reports are mixed. Some studies find small gains over fixed-size chunking on question answering datasets; others find no reliable difference once chunk size is tuned for both methods. The gain seems largest on documents that mix many short topics without headings, such as meeting notes or interview transcripts, and smallest on structured documentation, where headings already mark the topic shifts.

A sound way to decide is to hold everything else fixed, build two indexes that differ only in chunking, and compare retrieval metrics on the same labelled queries. Watch the chunk size distribution while doing so: semantic chunkers often produce many tiny chunks, and tiny chunks can win on precision metrics while hurting the answers built from them.
