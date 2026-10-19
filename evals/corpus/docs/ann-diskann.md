# DiskANN: graph search on SSDs

DiskANN, published by Subramanya and colleagues at Microsoft Research in 2019, is a graph-based approximate nearest neighbour index designed to keep most of its data on a solid-state drive instead of in RAM. It targets collections of a billion vectors on a single machine with tens of gigabytes of memory, a scale where in-memory graph indexes need far too much RAM.

## The Vamana graph

DiskANN builds a single-layer graph with an algorithm called Vamana. Unlike a layered graph, it has no hierarchy; instead the construction adds some long-range edges deliberately, controlled by a parameter usually called alpha, so that greedy search can still cross the space in a few hops. Fewer hops matter because each hop on disk is a random read.

## What lives where

The full-precision vectors and the graph adjacency lists live on the SSD, laid out so that a node's vector and its neighbour list are read together in one block. Memory holds only compressed copies of every vector, typically product-quantized codes. During a search, the compressed vectors guide the traversal, the SSD is read for the neighbour lists of the nodes visited, and the full vectors fetched along the way are used to re-rank the final candidates exactly.

## Performance profile

Query latency depends on the number of random SSD reads, so DiskANN rewards fast NVMe drives and issues reads in parallel batches. Reported latencies are a few milliseconds at high recall, slower than a fully in-memory graph but at a fraction of the memory cost. Updates are harder than in memory; later work such as FreshDiskANN added support for streaming inserts and deletes with periodic consolidation.

## Choosing it

DiskANN-style indexes make sense when the collection is too large for an in-memory graph on your hardware and when SSD reads are fast and plentiful. For collections that fit in memory, an in-memory graph is simpler and faster; for small collections, an exact scan is simplest of all. Some managed vector databases now offer disk-based graph indexes under their own names, so check what the engine actually builds before comparing benchmarks.
