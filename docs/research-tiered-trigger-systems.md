# Research: Best Practices for Tiered Trigger Systems in Conversational AI

**Date:** 2025-11-17
**Purpose:** Research best practices for implementing confidence-based trigger systems in AI skills that balance automatic execution with predictable, trustworthy behavior.

## Executive Summary

Tiered trigger systems use confidence levels to determine when AI assistants should act immediately, request confirmation, or reject ambiguous commands. Research across voice assistants (Alexa, Siri, Google Assistant), code editors (GitHub Copilot, VS Code), and conversational AI platforms reveals consistent patterns for creating predictable, trustworthy interfaces.

**Key Finding:** Predictability is the foundation of user trust in AI systems. Users need to understand when the system will act autonomously vs. when it will ask for confirmation.

---

## 1. Natural Language Command Parsing Best Practices

### 1.1 Three-Tier Confidence Model (Industry Standard)

Multiple authoritative sources recommend a three-tier confidence threshold system:

**High Confidence (>85%)** - Implicit Confirmation
- Execute action immediately
- Provide brief confirmation feedback ("Note added")
- No user intervention required
- **Use when:** Verbs are explicit, context is clear, action is reversible

**Medium Confidence (40-85%)** - Explicit Confirmation
- Ask user to confirm before acting
- Present what the system understood: "Did you mean to [action]?"
- Allow user to correct or approve
- **Use when:** Intent is probable but ambiguous, consequences matter

**Low Confidence (<40%)** - Rejection with Guidance
- Don't guess or act
- Ask user to rephrase: "I'm not sure what you meant. Try [suggestion]"
- Provide examples of valid commands
- **Use when:** Multiple interpretations possible, or no strong match

**Sources:**
- Genesys Blog: "Set bot confidence thresholds" (2024)
- Voice First AI: "5 Confirmations for Voice User Interfaces" (Medium)
- Machine Learning Confidence Scores (Voice Tech Global, Medium)

### 1.2 Adjusting Thresholds Based on Context

Thresholds should vary based on:

1. **Action Severity**
   - Destructive actions: Require higher confidence (>95%)
   - Irreversible actions: Always confirm explicitly
   - Routine actions: Can use lower thresholds

2. **User History**
   - Frequent users: Can lower thresholds slightly
   - New users: Use higher thresholds, provide more guidance
   - Error-prone contexts: Increase confirmation requirements

3. **Domain Risk**
   - Financial transactions: High thresholds
   - Note-taking/knowledge capture: Medium thresholds
   - Simple queries: Low thresholds acceptable

**Best Practice:** Start with conservative (higher) thresholds and adjust based on real user data. Monitor false positive and false negative rates continuously.

**Source:** Mindee Blog: "Understanding Confidence Scores in Machine Learning" (2024)

---

## 2. Confidence-Based Action Systems in AI Assistants

### 2.1 Explicit vs. Implicit Confirmation

**Implicit Confirmation:**
- System assumes it heard correctly and proceeds
- Confirms action through execution ("Turned on the lights")
- **Advantage:** Faster when correct
- **Disadvantage:** Users may not notice errors immediately
- **When to use:** High confidence (>85%), reversible actions

**Explicit Confirmation:**
- System asks user to verify before acting
- "Move it to Friday at 10:00 — correct?"
- **Advantage:** Prevents costly mistakes
- **Disadvantage:** Adds interaction step, slower
- **When to use:** Medium confidence (40-85%), important actions

**Research Finding:** 37% of users struggle to correct implicit confirmation errors when system is wrong (Weegels 2000, via ACIxD Wiki). This argues for explicit confirmation when confidence is not very high.

**Sources:**
- ACIxD Wiki: "Implicit vs. Explicit Confirmation"
- Google Developers: "Conversation Design - Confirmations"
- Voice First AI: "5 Confirmations for Voice User Interfaces"

### 2.2 When to Skip Confirmation Entirely

Some commands should ALWAYS execute without confirmation:

1. **Retrieval queries** - "What did I note about X?"
   - No state change
   - User expects immediate response
   - No risk of unintended consequences

2. **Explicitly commanded actions** - "Record this information..."
   - Strong action verbs signal intent
   - User clearly stating their goal
   - Confirmation would be redundant

3. **Cancelation commands** - "Never mind", "Stop"
   - User wants to abort current flow
   - Confirming cancellation is paradoxical

**Best Practice:** Document which command types always execute. This creates predictable behavior users can rely on.

---

## 3. User Experience Patterns for Command Disambiguation

### 3.1 Disambiguation Strategies

When confidence is medium or multiple intents match, use these patterns:

**1. Binary Choice (Most Common)**
```
"Did you mean A or B?"
```
- Best for 2 clear alternatives
- Quick to answer
- Works well in voice and text

**2. Multiple Choice (2-4 Options)**
```
"Did you want to:
1. Add a new note about X
2. Update the existing note about Y
3. Search for notes about Z"
```
- Best for 3-4 alternatives
- Numbered options aid clarity
- Show most likely option first

**3. Clarifying Question (Open-Ended)**
```
"I found several notes about 'project'. Which project did you mean?"
```
- Best when options are too numerous
- Allows user to provide more context
- More flexible but slower

**Sources:**
- Fastbots AI: "Chatbot Intents: Decoding User Messages" (2024)
- NN/g: "The User Experience of Chatbots"
- Netguru: "Top Chatbot UX Tips and Best Practices for 2025"

### 3.2 Smart Suggestions and Quick Replies

Reduce disambiguation needs by offering context-aware suggestions:

- Show buttons/chips for common follow-ups
- Display recent or related entities
- Use autocomplete for known values

**Research Finding:** Users appreciate predetermined options (buttons/chips) for common inputs, but also want text input flexibility for novel queries. Provide both.

**Source:** NN/g: "The User Experience of Chatbots"

### 3.3 Progressive Disclosure

Don't overwhelm users with all options at once:

1. **First attempt:** Show most likely option + "or something else?"
2. **If rejected:** Show 2-3 more alternatives
3. **If still rejected:** Ask open-ended question or suggest rephrasing

---

## 4. Documentation Strategies for Trigger Phrase Systems

### 4.1 Apple Siri Guidelines (Gold Standard)

Apple's Human Interface Guidelines provide the most comprehensive guidance for trigger phrase documentation:

**Make Phrases Specific and Accurate:**
- "Reorder coffee" or "Order my usual coffee" clearly describe action
- Avoid ambiguous phrases like "Do the thing"
- Users must speak phrase verbatim for recognition

**Keep Phrases Short and Memorable:**
- 2-3 word phrases work best
- Long or confusing phrases cause mistakes and frustration
- Example: "Check weather" vs "Tell me what the weather forecast is like today"

**Don't Imply Variation Support:**
- Avoid: "Order a large clam chowder" (suggests you can substitute sizes/items)
- This creates false expectations about system flexibility
- Be explicit about fixed vs. variable parts

**Exact Phrase Matching:**
- "When people speak the exact phrase, Siri recognizes it without additional processing"
- This creates predictable, deterministic behavior
- No fuzzy matching means no ambiguity

**Sources:**
- Apple Developer: "Siri - Shortcuts and Suggestions" (Human Interface Guidelines)
- Apple Developer: "Introduction - Siri"

### 4.2 Microsoft Copilot Studio Best Practices

**Start with Real Data:**
- Use actual user utterances from production rather than invented phrases
- The best trigger phrases match what users naturally say
- Collect 5-10 representative samples per intent

**Capture Natural Variations:**
- "Note that...", "Remember that...", "Write down that..."
- Users phrase the same intent many different ways
- Don't require exact wording (unlike Siri's exact-match approach)

**Train the NLU Model:**
- Trigger phrases train the natural language understanding
- More examples = better generalization
- Update based on unresolved utterances from logs

**Source:** Microsoft Learn: "Trigger phrases best practices - Microsoft Copilot Studio"

### 4.3 Documentation Content Guidelines

Effective trigger documentation includes:

1. **Categorized Examples:**
   - Group by intent (adding, searching, updating)
   - Show 3-5 examples per category
   - Include edge cases and variations

2. **Confidence Tier Explanation:**
   - Which phrases always execute
   - Which phrases may ask for confirmation
   - Why the system behaves differently

3. **Mental Model Building:**
   - Explain when system acts autonomously
   - Show example confirmations users might see
   - Clarify what happens on low confidence

4. **Negative Examples:**
   - Show what WON'T trigger the skill
   - Explain common ambiguities
   - Suggest better phrasings

**Example Documentation Structure:**
```markdown
## Always Executes Immediately
- "Record that..."
- "Save this information..."
- "Capture the following..."

## May Request Confirmation
- "Note that..."
- "Remember that..."
- "Keep in mind that..."

## Retrieval (Always Immediate)
- "What did I note about...?"
- "Show me notes on..."
- "Find my notes about..."
```

---

## 5. Testing Approaches for Natural Language Triggers

### 5.1 Test Coverage Strategies

**1. Intent Recognition Testing:**
- Test each trigger phrase variant
- Verify correct intent classification
- Measure confidence scores for each utterance

**2. Boundary Testing:**
- Test phrases at confidence thresholds (84%, 85%, 86%)
- Verify correct tier behavior (execute vs. confirm vs. reject)
- Test edge cases near boundaries

**3. Ambiguity Testing:**
- Test phrases with multiple possible intents
- Verify disambiguation flow activates
- Check that most likely intent ranks first

**4. False Positive Testing:**
- Test phrases that should NOT trigger
- Conversational phrases containing trigger words
- Measure false positive rate in natural dialogue

**5. Multi-Turn Conversation Testing:**
- Test follow-up clarifications
- Verify context maintenance
- Test conversation recovery from errors

**Sources:**
- QualiZeal: "The Ultimate Guide to Testing Conversational AI" (2024)
- Cyara: "Chatbot & Conversational AI Testing Platform"
- TestRigor: "Chatbot Testing Using AI"

### 5.2 Behavioral Testing (Non-Deterministic Systems)

**Challenge:** LLMs return different outputs each time, making traditional assertion-based testing insufficient.

**Solution:** Test behaviors rather than exact outputs:
- Define expected behavior patterns
- Use another LLM to score if behavior matches
- Set acceptable ranges rather than exact matches

**Example:**
```python
# Instead of: assert output == "Note added"
# Test: Did system acknowledge the action?
assessment = llm_judge.evaluate(
    output=actual_response,
    criteria="Did the system confirm it saved the note?",
    acceptable_variations=True
)
assert assessment.passed
```

**Sources:**
- Medium: "AI Chatbot Behavioral Testing" (Dan Jam Kuhn)
- Hatchworks: "Testing Your RAG-Powered AI Chatbot"

### 5.3 Real-World Testing Approaches

**A. Alexa Intent Confidence Dashboard:**
- Review intent history for unresolved utterances
- Identify low/medium confidence matches
- Map missing utterances to correct intents
- Use NLU evaluation tool for batch testing

**B. Production Monitoring:**
- Track confidence distribution over time
- Monitor false positive/negative rates
- Collect user correction patterns
- Adjust thresholds based on real usage

**C. User Feedback Integration:**
- "Was this what you meant?" after actions
- Collect explicit user ratings
- Track task success rates
- Measure user confidence post-task

**Sources:**
- Amazon Developer: "Use the Intent Confidence Dashboard to Improve Skill Accuracy"
- Amazon Developer: "5 Tips for Using Intent History to Enhance Your Alexa Skill"
- MeasuringU: "Measuring User Confidence in Usability Tests"

### 5.4 Test Automation Best Practices

1. **Intent Classification Unit Tests:**
   - Test each trigger phrase independently
   - Assert expected intent + confidence score
   - Run on every code change

2. **End-to-End Flow Tests:**
   - Test complete user conversations
   - Verify multi-turn context handling
   - Check confirmation flows

3. **Regression Testing:**
   - Maintain test corpus of real user utterances
   - Test against corpus after model changes
   - Track confidence score drift over time

4. **False Positive Monitoring:**
   - Run non-trigger conversations through system
   - Assert no unintended activations
   - Test with conversational text containing trigger words

---

## 6. Examples from Production Systems

### 6.1 Alexa Skills

**Intent Confidence Handling:**
- Dashboard shows high/medium/low confidence for each utterance
- Fallback intent handles low-confidence, out-of-domain requests
- Entity resolution disambiguates synonyms mapping to multiple values

**Best Practices:**
- Add 5-10 sample utterances per intent
- Use thesaurus to find synonyms for variation
- Include diverse carrier phrases around slots
- Review Intent History regularly for unresolved utterances

**Disambiguation Example (Pet Match Skill):**
```
User: "I want a small dog"
System: [Entity "small" maps to both "small" and "tiny"]
System: "Did you want a small or tiny dog?"
User: "Small"
System: [Resolves to "small" size]
```

**Source:** Amazon Developer Blog: "Alexa Skill Teardown: Understanding Entity Resolution"

### 6.2 Google Assistant

**Helper Intents for Confirmations:**
- `actions.intent.PERMISSION` - User information access
- `actions.intent.CONFIRMATION` - Yes/no questions
- Context-aware confirmations: "Turned on the lights" or "Brightness set"

**Design Pattern:**
- Use implicit confirmation for high-confidence, low-risk actions
- Use explicit confirmation for destructive/irreversible actions
- Provide clear recovery paths when errors occur

**Source:** Google Developers: "Helper intents (Dialogflow)"

### 6.3 Siri Shortcuts

**Exact Phrase Matching:**
- Users must speak phrase precisely as defined
- No additional processing or fuzzy matching
- If phrase doesn't match exactly, intent doesn't trigger

**Benefits:**
- Completely predictable behavior
- No false positives from similar phrases
- Users know exactly what to say

**Trade-offs:**
- Less flexible than NLU-based systems
- Requires user to memorize exact phrases
- Can't handle natural variations

**Source:** Apple Developer: "Siri - Shortcuts and Suggestions"

### 6.4 GitHub Copilot

**Automatic vs. Manual Triggering:**
- Default: Suggestions appear automatically as you type
- Manual mode: Disable auto-suggestions, trigger with Alt+\ (or Option+\)
- Context-aware: Analyzes comments, function signatures, surrounding code

**User Control:**
- Settings allow per-language enablement
- Keyboard shortcut provides manual trigger
- Ghost text preview before acceptance

**Pattern:** Provides both automatic (proactive) and manual (on-demand) modes to suit different user preferences and workflows.

**Sources:**
- VS Code Docs: "Inline suggestions from GitHub Copilot"
- Stack Overflow: "Can GitHub Copilot stop auto-suggesting"

### 6.5 VS Code Command Palette

**Predictable Triggers:**
- Consistent keyboard shortcut: Ctrl+Shift+P (Windows/Linux) or Cmd+Shift+P (Mac)
- Available from anywhere in the application
- Same query returns same result (deterministic)

**Design Principles:**
- Simple, memorable shortcut that doesn't conflict with typing
- Reliable inclusion in user workflows
- Doesn't clash with common editor operations

**Pattern:** Command palettes show the value of a SINGLE, universal, predictable trigger rather than multiple natural language variations.

**Sources:**
- Avery Vigolo: "Good design patterns: the command palette"
- Digital Seams: "Why do Sublime Text and VS Code use Ctrl-Shift-P"

---

## 7. Predictability and User Trust (Research Findings)

### 7.1 Core Principles

**Predictability Directly Impacts Trust:**
- "Agents with more predictable behaviors have a more positive impact on task performance, reliance and trust while reducing cognitive workload" (Frontiers in Robotics and AI, 2021)
- Users need to predict how the system will respond in various situations to feel in control
- Beginning of interaction and unpredictable moments are when trust is most at stake

**User Mental Models:**
- Users develop mental models of when AI will act autonomously
- Mismatches between expected and actual behavior erode trust
- Consistent behavior patterns strengthen mental models

**Sources:**
- Frontiers in Robotics and AI: "Inferring Trust From Users' Behaviours" (2021)
- AI & Society: "Artificial agents' explainability to support trust" (2022)

### 7.2 Designing for Predictability

**1. Set Clear Expectations:**
- Onboarding: Explain when system acts automatically
- Tooltips: Clarify trigger behavior in context
- Empty states: Show examples of valid commands

**2. Communicate Uncertainty:**
- Signal confidence: "I'm 85% confident in this answer"
- Highlight uncertain elements: "I'm still learning about [topic]"
- Encourage verification for low-confidence outputs

**3. Provide Consistent Feedback:**
- Always acknowledge actions: "Note added"
- Explain why confirmation was requested
- Show what the system understood

**4. Test Mental Models:**
- Ask users: "Before you clicked, what did you expect?"
- Measure surprise/confusion in user testing
- Track when users undo or correct actions

**Sources:**
- Smashing Magazine: "The Psychology Of Trust In AI" (2025)
- Google PAIR: "Explainability + Trust"

### 7.3 Trust-Eroding Patterns to Avoid

1. **Inconsistent Behavior:**
   - Same trigger phrase behaves differently in different contexts
   - Unpredictable confidence thresholds
   - Changing behavior without user notification

2. **False Confidence:**
   - Acting with high confidence on ambiguous input
   - Not signaling uncertainty
   - No way to verify before execution

3. **Poor Error Recovery:**
   - No clear path to correct mistakes
   - Losing context after errors
   - Requiring users to start over

4. **Overuse of Confirmation:**
   - Asking for confirmation on routine actions
   - Users stop paying attention (confirmation fatigue)
   - Dialogs lose power to prevent errors

**Source:** NN/g: "Confirmation Dialogs Can Prevent User Errors (If Not Overused)"

---

## 8. Implementation Recommendations for Note-Taking Skill

Based on comprehensive research, here are specific recommendations for implementing tiered triggers:

### 8.1 Recommended Confidence Tiers

**Tier 1: High Confidence - Execute Immediately (No Confirmation)**
- Strong action verbs: "Record", "Save", "Capture", "Log"
- Retrieval queries: "What did I note", "Show me notes", "Find notes"
- Explicit formats: "Note: [content]" or "Remember: [content]"
- Confidence threshold: >90%

**Tier 2: Medium Confidence - Request Confirmation**
- Ambiguous verbs: "Note that", "Remember that", "Keep in mind"
- Context-dependent: Conversational mentions of noting
- Confidence threshold: 60-90%
- Confirmation format: "Did you want me to save a note about [extracted topic]?"

**Tier 3: Low Confidence - Reject with Guidance**
- Unclear intent
- Multiple possible interpretations
- Confidence threshold: <60%
- Response: "I'm not sure if you want to save a note. Try 'Record that [content]' or 'What did I note about [topic]'?"

### 8.2 Documentation Structure

Create clear, tiered documentation:

```markdown
## Trigger Phrases That Always Execute

These phrases tell me you definitely want to save a note:
- "Record that..."
- "Save the information that..."
- "Capture this: ..."

## Trigger Phrases That May Ask for Confirmation

These phrases might be conversational, so I'll check with you first:
- "Note that..." (Could be "note" as in "observe")
- "Remember that..." (Could be a reminder vs. note)
- "Keep in mind that..." (Could be advice vs. persistent note)

## Searching Never Requires Confirmation

All search queries execute immediately:
- "What did I note about...?"
- "Show me notes on..."
- "Find notes about..."
```

### 8.3 Testing Strategy

**Phase 1: Intent Classification (Offline)**
```python
test_cases = [
    ("Record that meeting is at 3pm", "add", >0.90),
    ("Note that meeting is at 3pm", "add", 0.60-0.90),
    ("What did I note about meetings", "search", >0.95),
    ("I should note that he seemed tired", "add", 0.60-0.90),
    ("Take note of his reaction", "add", 0.60-0.90),
]
```

**Phase 2: End-to-End Flows**
- Test complete conversation including confirmations
- Verify correct tier behavior at boundaries
- Test multi-turn disambiguation

**Phase 3: False Positive Detection**
```python
false_positive_tests = [
    "That's a good note to end on",  # Should NOT trigger
    "Of note is the quarterly report",  # Should NOT trigger
    "The keynote speaker was excellent",  # Should NOT trigger
]
```

**Phase 4: Production Monitoring**
- Log all trigger attempts with confidence scores
- Track confirmation acceptance rate
- Monitor false positive reports from users
- Adjust thresholds monthly based on data

### 8.4 Feedback Mechanisms

**Immediate Feedback:**
- "Note added: [heading]"
- "Found 3 notes about [topic]"
- "I updated the note: [heading]"

**Confirmation Requests:**
- "Did you want me to save a note about [topic]? (Yes/No)"
- "I found multiple notes about [term]. Which did you mean? 1) [option A] 2) [option B]"

**Rejection Guidance:**
- "I'm not sure if you want to save a note. Try 'Record that [content]' if you'd like me to save it."
- "I couldn't find any notes matching '[query]'. Try rephrasing or use 'Search notes for [keywords]'."

---

## 9. Key Takeaways

### For Implementation:

1. **Use three confidence tiers** (high/medium/low) with clear thresholds
2. **Always execute retrieval queries** - no confirmation needed for reads
3. **Strong action verbs execute immediately** - "Record", "Save", "Capture"
4. **Ambiguous phrases request confirmation** - "Note", "Remember"
5. **Document the tiers clearly** - users need to understand when confirmation occurs
6. **Test at threshold boundaries** - verify correct tier behavior
7. **Monitor false positives continuously** - adjust thresholds based on real data
8. **Provide consistent feedback** - always acknowledge actions taken

### For User Experience:

1. **Predictability builds trust** - same trigger should behave the same way
2. **Don't overuse confirmations** - causes fatigue, reduces effectiveness
3. **Make confirmations specific** - restate what the system understood
4. **Provide clear recovery paths** - users must be able to correct errors easily
5. **Set expectations upfront** - explain behavior in documentation and onboarding
6. **Signal uncertainty** - when confidence is low, communicate that to users

### For Testing:

1. **Test intent classification independently** - unit test each trigger phrase
2. **Test end-to-end flows** - verify multi-turn conversations work
3. **Test false positives actively** - run non-trigger conversations through system
4. **Use behavioral testing** - test patterns, not exact outputs
5. **Monitor production data** - real usage reveals issues synthetic tests miss
6. **Measure user confidence** - track whether users feel system is reliable

---

## 10. References

### Academic Research
- Frontiers in Robotics and AI (2021): "Inferring Trust From Users' Behaviours"
- AI & Society (2022): "Artificial agents' explainability to support trust"
- CHI Conference (2019): "Implicit Communication of Actionable Information in Human-AI teams"

### Industry Documentation
- Apple Developer: Siri Human Interface Guidelines
- Google Developers: Conversation Design - Confirmations
- Amazon Developer: Alexa Intent Confidence Dashboard
- Microsoft Learn: Copilot Studio Trigger Phrases Best Practices

### UX Research
- Nielsen Norman Group: "The User Experience of Chatbots"
- Nielsen Norman Group: "Confirmation Dialogs Can Prevent User Errors"
- MeasuringU: "Measuring User Confidence in Usability Tests"
- Microsoft Research: "Define your threshold: Communicating confidence in UX"

### Technical Blogs
- Genesys Blog: "Set bot confidence thresholds" (2024)
- Voice Tech Global (Medium): "Machine Learning Confidence Scores"
- Voice First AI (Medium): "5 Confirmations for Voice User Interfaces"
- Smashing Magazine: "The Psychology Of Trust In AI" (2025)

### Testing Resources
- QualiZeal: "The Ultimate Guide to Testing Conversational AI" (2024)
- TestRigor: "Chatbot Testing Using AI"
- Cyara: "Botium - Chatbot & Conversational AI Testing Platform"

### Design Patterns
- Avery Vigolo: "Good design patterns: the command palette"
- Retool Blog: "Designing Retool's Command Palette"
- Netguru: "Top Chatbot UX Tips and Best Practices for 2025"

---

## Appendix A: Confidence Threshold Comparison Table

| System | High Confidence | Medium Confidence | Low Confidence | Notes |
|--------|----------------|-------------------|----------------|-------|
| Industry Standard | >85% | 40-85% | <40% | Most common pattern |
| Banking/Financial | >95% | 85-95% | <85% | Higher stakes = higher thresholds |
| Voice Assistants | >90% | 70-90% | <70% | Account for speech recognition errors |
| Note-Taking (Recommended) | >90% | 60-90% | <60% | Low-stakes, reversible actions |
| Search/Retrieval | >80% | N/A | <80% | Searches can be more permissive |

## Appendix B: Trigger Phrase Patterns to Avoid

**1. Phrases with Common Non-Intent Usage:**
- "Note" (musical note, notice, bank note)
- "Remember" (in context: "remember when we...")
- "Record" (as in "track record", "for the record")

**2. Phrases Requiring Extensive Context:**
- "Write that down" (what is "that"?)
- "Save it" (what is "it"?)
- "Don't forget" (forget what?)

**3. Phrases Implying Variation:**
- "Add a large note about..." (implies size variations)
- "Save this quickly to..." (implies location variations)

**4. Overly Generic Phrases:**
- "Do something about..."
- "Handle this..."
- "Take care of..."

## Appendix C: Sample Test Suite Structure

```python
# test_trigger_classification.py

import pytest
from notes_skill import classify_intent, get_confidence

class TestHighConfidenceTriggers:
    """Triggers that should always execute immediately."""

    @pytest.mark.parametrize("utterance,expected_intent", [
        ("Record that meeting is tomorrow", "add"),
        ("Save the information about the project", "add"),
        ("Capture this: quarterly goals", "add"),
        ("What did I note about meetings", "search"),
        ("Show me notes on project X", "search"),
    ])
    def test_high_confidence_classification(self, utterance, expected_intent):
        intent, confidence = classify_intent(utterance)
        assert intent == expected_intent
        assert confidence > 0.90, f"Expected >90% confidence, got {confidence}"

class TestMediumConfidenceTriggers:
    """Triggers that should request confirmation."""

    @pytest.mark.parametrize("utterance,expected_intent", [
        ("Note that meeting is tomorrow", "add"),
        ("Remember that he prefers email", "add"),
        ("Keep in mind that deadline is Friday", "add"),
    ])
    def test_medium_confidence_classification(self, utterance, expected_intent):
        intent, confidence = classify_intent(utterance)
        assert intent == expected_intent
        assert 0.60 <= confidence <= 0.90, f"Expected 60-90% confidence, got {confidence}"

class TestFalsePositives:
    """Phrases that should NOT trigger note-taking."""

    @pytest.mark.parametrize("utterance", [
        "That's a good note to end on",
        "Of note is the quarterly report",
        "The keynote speaker was excellent",
        "I should note that this is just my opinion",
        "Take note of his reaction" # Ambiguous - should be low confidence
    ])
    def test_false_positive_prevention(self, utterance):
        intent, confidence = classify_intent(utterance)
        if intent == "add":
            assert confidence < 0.60, f"False positive with {confidence} confidence"
        else:
            assert intent in ["none", "unclear", "out_of_scope"]
```

---

**End of Research Report**

This research synthesizes findings from 40+ authoritative sources including academic papers, industry documentation, UX research, and production system analysis to provide comprehensive guidance for implementing tiered trigger systems in conversational AI skills.
