# Paper Strategy Skill

Help users refine their research ideas into structured search strategies through dialogue.

## When to Use

- User has a research idea but hasn't formed search keywords yet
- User doesn't know what to search or how to search
- User needs to refine their research direction through dialogue

## When NOT to Use

- User already has a `search_strategy_*.json` file → use `/paper-search` directly
- User knows exactly what keywords to search → skip to `/paper-search`
- User wants to search for non-academic content (blog posts, news, etc.) → this skill is for academic papers only

## Process

1. **Understand the idea:** Ask the user what they want to research
2. **Summarize and suggest keywords:** Provide initial direction
3. **Ask clarifying questions:** Choose 2-4 most relevant dimensions from the menu below
4. **Generate strategy:** Create structured JSON search strategy
5. **Save and confirm:** Save to file and get user approval

## Clarifying Dimensions Menu

Choose the most relevant questions based on the user's response:

**Basic:**
- Research domain/subdomain
- Core problem to solve
- Known methods/techniques/papers

**Deep (choose as needed):**
- Application scenario (academic/industry/specific domain)
- Technical approach preference (theory/experiment/engineering)
- Data/environment constraints
- Differences from existing methods
- Evaluation criteria
- Time range (classic/recent/SOTA)
- Exclusions
- Interdisciplinary possibilities

## Output Format

Save as `search_strategy_YYYYMMDD_HHMMSS.json`:

```json
{
  "topic": "...",
  "keywords": ["...", "..."],
  "exclude": ["...", "..."],
  "dimensions": ["relevance", "novelty", "reproducibility"],
  "date_range": "2023-2026",
  "max_results": 50,
  "reasoning": "Why these keywords were chosen..."
}
```

## Example Dialogue

User: "I want to find papers about making AI models smaller"

Assistant: "I'll help you find papers about model compression/efficiency. Let me clarify a few things:

**Initial direction:** Model compression, efficiency, deployment optimization

**Possible keywords:** model compression, knowledge distillation, pruning, quantization, efficient inference

**Questions:**
1. What's your specific use case? (mobile deployment, edge devices, cloud cost reduction?)
2. Are you interested in specific techniques? (distillation, pruning, quantization, architecture search?)
3. What model types? (LLMs, vision models, general?)

Please share more details so I can create a targeted search strategy."
