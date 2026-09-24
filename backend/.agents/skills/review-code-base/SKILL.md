---
name: review-code-base
description: Review available reverse-engineering phase artifacts as a cross-phase synthesis step, selectively retrieve artifact content, verify important conclusions against repository evidence, and produce evidence-backed gaps, uncertainties, inconsistencies, future directions, and recommendations.
---

## Runtime resources and tools

The runtime supplies the selected skill and exposes the tools available for executing this methodology.

Use the repository tools (`list_files`, `read_file`, `search_repository`) for evidence in the target repository.

Use `list_resources` and `read_resource` for runtime-owned files supplied alongside this skill. These may include `OUTPUT_TEMPLATE.md`, checklists, schemas, domain artifacts, examples, or other supporting resources. The runtime inventory is dynamic; do not assume that a particular optional artifact exists unless it is listed.

When `OUTPUT_TEMPLATE.md` is supplied, read it before producing the final documentation and use its structure as required by the common agent contract.

Use `list_previous_phase_outputs` and `read_previous_phase_output` for workflow artifacts supplied from earlier phases. Do not use repository tools for those artifacts.

Resource paths are runtime-relative identifiers. Do not construct host filesystem paths.


# Review Code Base

Start from the SDLC artifact catalogue. Do not request or consume every artifact automatically. Retrieve only the phase outputs relevant to the current line of investigation.

Use `read_sdlc_artifact` to retrieve generated phase documents such as business-purpose, scope, requirements, architecture, design, implementation, testing, and future-direction artifacts. These generated documents are stored outside the cloned target repository.

Use `read_repository_file` only for targeted verification against source files in the cloned target repository. Never use it to retrieve a generated SDLC artifact path such as `business-purpose/raw.md` or `scope/raw.md`.

Compare available artifacts rather than treating them as independent reports. Look specifically for:
- contradictions between scope, requirements, architecture, design, implementation, testing, deployment, and operations findings;
- capabilities described in one phase but unsupported elsewhere;
- implementation capabilities that have no corresponding requirements, testing, deployment, or operational treatment;
- unresolved assumptions and evidence gaps;
- documentation gaps that prevent confident understanding of the system;
- recommendations that are duplicated, generic, or unsupported.

A missing artifact is itself a fact about the current review coverage. Do not manufacture conclusions for phases that have not been generated.

Keep source evidence and inference separate. When verification changes the interpretation of a prior phase, state the discrepancy explicitly rather than silently correcting the earlier document.

The final Recommendations section must be grounded in the reviewed artifacts and targeted repository verification, and must be final.

The investigation should use source evidence and cross-phase comparison internally, but the final review document should not reproduce the evidence trail or internal confidence/certainty classifications. Present contradictions, gaps, and recommendations directly and explain their practical impact in natural language.

## Output Depth

Produce a sufficiently detailed cross-phase review to make material contradictions, omissions, duplicated recommendations, and unresolved design or implementation issues understandable. Do not artificially constrain the document to a fixed page, word, or section count. Continue targeted investigation when it could materially change the review conclusions, while avoiding unsupported additions.
