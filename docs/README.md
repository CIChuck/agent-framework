# Friday Documentation

Use this page to find the authoritative documentation surface for the task at
hand.

## Start Here

- [Guides](guides/) — end-user and operator documentation. This collection is
  intentionally independent from development-plan lifecycle.
- [Planning dashboard](planning/) — current initiatives, lifecycle state,
  controlling packets, and next gates.
- [Architecture](architecture/) — current system architecture only.
- [Reference](reference/) — durable policies, implemented contracts, testing
  references, and release evidence.
- [Archive](archive/) — completed, superseded, exploratory, or source material
  retained for provenance but not current authority by location alone.
- [Development skills](dev-skills/) — reusable document and review templates for
  contributors.

## Authority Rules

1. Explicit maintainer direction and the
   [repository engineering policy](reference/policies/repository-engineering-policy.md)
   govern implementation.
2. The [planning dashboard](planning/) identifies current work and its next gate.
3. Initiative packet indexes identify their controlling documents.
4. Release evidence establishes publication state.
5. Archive placement means a document is historical unless a current authority
   explicitly incorporates it.
6. Moving a document never changes its approval state.

When a plan becomes an implemented durable contract, promote the contract to
`reference/` or `architecture/` and archive the implementation packet with its
closeout evidence.
