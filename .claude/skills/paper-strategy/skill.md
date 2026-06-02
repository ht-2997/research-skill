# Paper Strategy Skill

Help users refine their research ideas into structured search strategies through **multi-turn dialogue**.

## When to Use

- User has a research idea but hasn't formed search keywords yet
- User doesn't know what to search or how to search
- User needs to refine their research direction through dialogue

## When NOT to Use

- User already has a `search_strategy_*.json` file → use `/paper-search` directly
- User knows exactly what keywords to search → skip to `/paper-search`
- User wants to search for non-academic content (blog posts, news, etc.) → this skill is for academic papers only

## Process (Strict Multi-Turn Dialogue)

**IMPORTANT:** You MUST follow this process. Do NOT skip steps or generate strategy without completing the dialogue.

### Step 1: Understand the idea
- Ask the user what they want to research
- Summarize their idea in your own words
- Ask for confirmation: "Is this understanding correct?"

### Step 2: Ask clarifying questions (MUST ask at least 2-3 questions)
- Choose from the Clarifying Dimensions Menu below
- Ask ONE question at a time
- Wait for user response before asking next question
- Do NOT proceed until you have asked at least 2 questions

### Step 3: Summarize and confirm
- Present a summary of what you've learned:
  - Research topic
  - Key aspects to search
  - What to exclude
- Ask: "Does this summary look right? Should I adjust anything?"

### Step 4: Generate strategy
- Only after Step 3 is confirmed
- Create structured JSON search strategy
- Save to file with timestamp

### Step 5: Final confirmation
- Show the generated strategy to user
- Ask: "Is this strategy ready to use, or do you want to adjust?"

## Clarifying Dimensions Menu

Choose the most relevant questions based on the user's response:

**Basic (ask at least 2):**
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

## Example Dialogue (Follow This Pattern)

**User:** "I want to find papers about using VLM to improve SAM prompts"

**Assistant:** "I'll help you find papers about using Vision-Language Models to improve SAM's prompt engineering. Let me clarify a few things:

**My understanding:** You're looking for research on how VLMs can be used to refine or correct prompts (especially bounding boxes) for the Segment Anything Model.

**Is this understanding correct?**"

**User:** "Yes, that's right. Specifically I'm interested in correcting inaccurate bbox prompts from detection models."

**Assistant:** "Got it. Let me ask a few more questions:

1. **Application scenario:** Are you focusing on a specific domain like medical imaging, robotics, or general computer vision?
2. **Technical approach:** Are you interested in methods that modify the bbox directly, or methods that use VLM to generate new prompts?"

**User:** "General CV, and I'm interested in both approaches."

**Assistant:** "Thanks! One more question:

3. **Exclusions:** Are there any specific approaches you want to exclude, like methods that require retraining SAM?"

**User:** "No exclusions."

**Assistant:** "Great! Here's my summary:

- **Topic:** Using VLM to correct/refine SAM's bbox prompts
- **Key aspects:** VLM-based prompt correction, bbox refinement, prompt engineering for SAM
- **Exclusions:** None
- **Domain:** General computer vision

**Does this summary look right? Should I adjust anything?**"

**User:** "Looks good."

**Assistant:** "Generating strategy..."

[Generate and save strategy file]

**Assistant:** "Strategy saved to `search_strategy_20260602_123456.json`. 

**Is this strategy ready to use, or do you want to adjust?**"

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

## Checklist Before Generating Strategy

- [ ] Asked at least 2 clarifying questions
- [ ] User confirmed the summary
- [ ] User confirmed the strategy
