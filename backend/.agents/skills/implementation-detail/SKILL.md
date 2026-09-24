---
name: implementation-detail
description: Summarize the few engineering and delivery concerns that remain once a software product has been designed and implemented.
compatibility: opencode
---

# Implementation Detail Reverse-Engineering Skill

## Objective

Produce a brief supplementary engineering artifact about making the implemented product buildable, deployable, operable, and releasable.

Implementation Detail is not a separate product-development SDLC lifecycle phase. It captures practical post-design/post-implementation concerns such as build and packaging, environment configuration, deployment, CI/CD, migrations, release mechanics, and material operational prerequisites.

The central question is:

> Once the product has been implemented, what additional engineering decisions or mechanisms are needed to turn it into a buildable, deployable, releasable, and operable system?

Many repositories will have very little to report. That is expected.

## Scope

Cover only material concerns in these areas, where evidenced:

- build/package and release artifacts;
- runtime/environment configuration;
- deployment and hosting mechanics;
- CI/CD and environment promotion;
- database/schema/data migration;
- release/versioning or rollback considerations;
- operational prerequisites, health/observability hooks, or delivery constraints.

Do not repeat:

- business purpose or requirements;
- Technology Architecture;
- High-Level Design;
- Low-Level Design;
- Testing Harness;
- detailed source-level implementation.

## Investigation Strategy

Start with deterministic repository intelligence and supplied phase research.

Inspect only the small number of repository files needed to answer the material delivery questions. Prefer targeted evidence from:

1. package/build configuration;
2. deployment/runtime configuration;
3. CI/CD or release workflows;
4. migration/configuration mechanisms;
5. materially relevant operational scripts or manifests.

Do not perform an exhaustive repository audit.

## Evidence Rules

Material claims must be supported by current repository evidence.

Do not infer active deployment, CI/CD, migrations, environment behavior, or operational mechanisms from filenames, dependencies, framework conventions, or documentation alone.

Where a concern is not applicable or not established, say:

- N/A; or
- Not established by the repository.

Never expose secret values.

## Required Questions

Answer only those that materially apply:

- How is the implemented product built or packaged?
- What runtime/environment configuration is required?
- How is deployment or release performed?
- What CI/CD exists, if any?
- Are database/schema/data migrations part of delivery?
- Are there environment-specific or rollback concerns?
- What important operational prerequisites or delivery limitations remain?

## Output Style

Keep the document short and practical.

Prefer a compact table or short sections. Omit empty sections. Do not expand a topic merely because the template contains it.

The output is an engineering delivery note, not an implementation manual.

## Verification Gate

Before finishing:

- material claims are repository-supported;
- implementation concerns are not duplicated from design or testing phases;
- absent mechanisms are not invented;
- the document remains brief;
- secrets are not exposed.
