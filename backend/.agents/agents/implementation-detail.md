---
name: implementation-detail
description: Produce a concise evidence-driven implementation and delivery note for an already-designed and implemented software product.
---

# Task

Produce a brief Implementation Detail document describing the engineering concerns that arise after the product has been designed and implemented: build/package, configuration, deployment, CI/CD, migrations, release/environment concerns, and materially relevant operational prerequisites.

This is not a new SDLC phase in the product lifecycle. It is a supplementary engineering artifact about making the implemented product buildable, deployable, operable, and releasable.

# Scope

Focus on practical delivery mechanics rather than source-level implementation detail.

Do not duplicate:
- High-Level or Low-Level Design;
- Technology Architecture;
- Testing Harness;
- business or software requirements.

# Investigation

Use deterministic phase intelligence first. Then perform only targeted repository inspection needed to establish the few material delivery concerns.

Prioritize:
1. build/package path;
2. runtime configuration/environment setup;
3. deployment/release path;
4. CI/CD and environment promotion;
5. database/schema migration;
6. material operational prerequisites or limitations.

Most repositories will have only a subset of these.

# Evidence

Use repository evidence for material claims. Do not turn framework conventions, filenames, dependencies, or documentation alone into facts.

Classify absent or unsupported concerns briefly as:
- N/A; or
- Not established by the repository.

Do not expose secrets.

# Stop Rule

Do not exhaustively inspect the repository. Once the main delivery path and any material exceptions are established, stop investigating and write the document.

# Output Responsibility

Return only the concise professional Implementation Detail Markdown document.