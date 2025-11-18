# Search Relevance Algorithm

This document describes the search relevance scoring algorithm used by `notes_manager.py` to rank note entries when searching.

## Overview

The relevance algorithm prioritizes heading matches over content matches and weights results by recency. This ensures that users find notes by their titles first, with content acting as a secondary signal.

## Scoring Formula

Each note entry receives a relevance score based on multiple factors:

```
Total Score = Heading Score + Content Score + Recency Bonus
```

### Heading Score

Headings are prioritized because they represent the note's primary topic.

**Exact Phrase Match in Heading:**
- **+500 points** - Overwhelming bonus for exact query phrase in heading
- Ensures exact matches rank first, regardless of content matches
- Case-insensitive matching

**Example:**
```
Query: "Claude Code"
Heading: "Learning - Claude Code basics"
Score: +500 (exact phrase match)
```

**All Query Terms in Heading:**
- **+100 points** - All individual query terms appear in heading
- Ensures headings containing all terms rank highly
- Case-insensitive matching

**Example:**
```
Query: "Claude Code basics"
Heading: "Learning - Code basics for Claude"
Score: +100 (all terms: "Claude", "Code", "basics")
```

**Individual Query Terms in Heading:**
- **+20 points per term** - For each individual query term in heading
- Provides partial matches when not all terms present
- Case-insensitive matching

**Example:**
```
Query: "Claude Code basics"
Heading: "Learning - Claude fundamentals"
Score: +20 (term: "Claude")
```

### Content Score

Content scoring is intentionally capped to prevent content matches from overwhelming heading matches.

**Query Terms in Content:**
- **+5 points per term occurrence** (capped at +50 total)
- Case-insensitive matching
- Prevents long notes from dominating results
- Ensures headings remain primary signal

**Example:**
```
Query: "Claude Code"
Content: "I learned Claude Code today. Claude Code is amazing. I use Claude Code daily."
Score: +15 (3 occurrences × +5 = +15, within cap)
```

**Maximum Content Score:**
```
Max Content Score = min(term_count × 5, 50)
```

### Recency Bonus

Recent notes receive a small boost to surface current work.

**Recency Tiers:**
- **< 30 days**: +10 points
- **< 90 days**: +5 points
- **< 180 days**: +2 points
- **≥ 180 days**: 0 points

**Example:**
```
Note from 15 days ago: +10 recency bonus
Note from 60 days ago: +5 recency bonus
Note from 120 days ago: +2 recency bonus
Note from 200 days ago: 0 recency bonus
```

## Special Handling

### File Headers Excluded

File headers (e.g., "Notes - November 2025") are automatically filtered out during entry extraction and never appear in search results.

**Filter Pattern:**
```regex
^Notes - \w+ \d{4}$
```

This prevents accidental updates to file headers and keeps search results focused on actual note entries.

### Update Threshold

For the `append` command, notes must meet a minimum relevance threshold to prevent incorrect updates:

**Minimum Threshold: ≥50 points**

This prevents weak matches from being updated with incorrect content.

**Example Scenarios:**

**Strong Match (Updates Allowed):**
```
Query: "testing"
Heading: "Work - Testing the skill"
Score: 520 (exact phrase: 500 + recency: 10 + content: 10)
Result: ✅ Update allowed
```

**Weak Match (Updates Blocked):**
```
Query: "testing"
Heading: "Meeting - Team discussion"
Content: "We briefly mentioned testing"
Score: 15 (content: 15)
Result: ❌ Update blocked, alternatives suggested
```

## Complete Examples

### Example 1: Exact Heading Match

```
Query: "Claude Code skills"

Note 1:
Heading: "Learning - Claude Code skills implementation"
Content: "Today I worked on skills"
Date: 10 days ago

Score Breakdown:
- Exact phrase in heading: +500
- Recency (< 30 days): +10
- Content terms: +5
Total: 515
```

### Example 2: Partial Heading Match

```
Query: "Claude Code skills"

Note 2:
Heading: "Work - Claude implementation"
Content: "I built Code skills today. Code skills are great."
Date: 20 days ago

Score Breakdown:
- Individual terms in heading: +40 ("Claude" +20, "Code" implicit in content)
- Content terms (capped): +15 (3 terms × 5)
- Recency (< 30 days): +10
Total: 65
```

### Example 3: Content-Only Match

```
Query: "Claude Code skills"

Note 3:
Heading: "Meeting - Team discussion"
Content: "We talked about using Claude Code skills extensively"
Date: 5 days ago

Score Breakdown:
- Heading terms: 0
- Content terms (capped): +15 (3 terms × 5)
- Recency (< 30 days): +10
Total: 25 (Below update threshold of 50)
```

### Example 4: All Terms in Heading

```
Query: "Claude Code skills"

Note 4:
Heading: "Idea - New skills for Claude Code"
Content: "Brainstorming ideas"
Date: 100 days ago

Score Breakdown:
- All terms in heading: +100
- Individual terms: +60 (3 terms × 20)
- Content terms: +5
- Recency (< 180 days): +2
Total: 167
```

## Ranking Order

Notes are returned sorted by relevance score (highest first):

```
1. Exact phrase matches in heading (500+)
2. All query terms in heading (100+)
3. Partial heading matches with content support (50-100)
4. Content-only matches (< 50) - not eligible for updates
```

## Implementation Notes

### Case Insensitivity

All matching is case-insensitive:
```python
query_lower = query.lower()
heading_lower = heading.lower()
content_lower = content.lower()
```

### Term Extraction

Query is split on whitespace into individual terms:
```python
terms = query.lower().split()
```

### Exact Phrase Matching

Exact phrase matching checks for the full query as a substring:
```python
if query.lower() in heading.lower():
    score += 500
```

### Content Capping

Content scoring is capped at 50 points total:
```python
content_score = 0
for term in terms:
    content_score += content.lower().count(term) * 5
content_score = min(content_score, 50)
```

## Design Rationale

### Why Cap Content Scoring?

Without capping, long notes with many term occurrences could overwhelm heading matches:

**Problem:**
```
Note A: Heading: "Work - Testing" (score: 520)
Note B: Heading: "Meeting - Discussion" with 20 occurrences of "testing" in content (score: 100)

Without cap: Note B could score higher than Note A
With cap: Note A (520) always beats Note B (max 50 from content)
```

### Why Prioritize Headings?

Headings represent the note's primary topic and what users remember:
- Users search for "that note about X" where X is in the heading
- Content matches are often coincidental or tangential
- Heading-first ensures intuitive results

### Why Minimum Threshold for Updates?

Prevents "fouled up" entries where updates go to wrong notes:

**Without Threshold:**
```
User: "Update my testing note with success status"
Claude finds: "Meeting - Discussion" (score: 15, word "testing" in content)
Result: Wrong note updated
```

**With Threshold (≥50):**
```
User: "Update my testing note with success status"
Claude finds: "Meeting - Discussion" (score: 15)
Result: Update blocked, alternatives suggested
```

## Future Enhancements

Potential algorithm improvements:

1. **TF-IDF Weighting**: Weight rare terms higher than common terms
2. **Bigram Matching**: Reward consecutive term matches
3. **Category Filtering**: Allow filtering by note category
4. **Date Range Filtering**: Search within specific date ranges
5. **Fuzzy Matching**: Handle typos and variations
6. **Semantic Search**: Vector embeddings for conceptual matches

## Version History

**1.0.0** - Initial algorithm
- Basic heading/content scoring
- Recency boost
- Content capping at 50 points
- Minimum threshold of 50 for updates

## References

- [CLAUDE.md](../../../CLAUDE.md) - Project documentation with key learnings
- [API.md](../docs/API.md) - Search command reference
- [WORKFLOW.md](./WORKFLOW.md) - When to search vs. add vs. update
