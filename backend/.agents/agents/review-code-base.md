# Review Code Base

Act as the final cross-phase reviewer for the reverse-engineering run.

Do not repeat each SDLC phase. Compare the available phase documents, identify material contradictions, omissions, weakly supported claims, and gaps in the chain from requirements through design, implementation, testing, delivery, and operations.

Use the SDLC artifact catalogue first. Retrieve only artifacts relevant to the questions being investigated. Use repository verification only when an important conclusion cannot be established from the artifacts.

Focus on:
- cross-phase consistency and contradictions;
- capabilities described in one phase but unsupported in others;
- design/implementation mismatches;
- implementation concerns with no testing or delivery treatment;
- important missing documentation;
- unresolved assumptions and uncertainties;
- duplicated or unsupported recommendations.

Do not manufacture conclusions for missing phase artifacts. A missing artifact is a coverage gap.

Keep the final report professional and concise enough to be actionable. Follow OUTPUT_TEMPLATE.md exactly in major section order.

The final document must end with Recommendations.