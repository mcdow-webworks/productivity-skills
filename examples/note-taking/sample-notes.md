# Notes - November 2025

<!-- This is an example of what your monthly notes file looks like -->

# Idea - Generate llms.txt automatically from Reverb format
Could create a build step that extracts documentation structure from Reverb output and formats it as llms.txt. This would make our docs more AI-accessible without manual maintenance.

**Update (2025-11-16):** Discussed with German partner - they're interested in this approach. They mentioned it could help with their AI training pipeline.

**Update (2025-11-17):** Decision made to start with proof-of-concept. Will test with small subset of Reverb docs first.

# Meeting - Q4 Roadmap Planning
Attendees: Tony, Sarah, Mike
Date: 2025-11-10

Key decisions:
- Focus on three major features
- Launch timeline: End of Q1 2026
- Monthly check-ins to track progress

Action items:
- [ ] Tony: Draft technical specs for Feature A
- [ ] Sarah: User research on Feature B
- [ ] Mike: Resource allocation plan

# Work - Fixed cache busting issue for Reverb deployments
The problem was that browser caching was preventing updates from being visible. Solution: Added hash-based cache busting to the deployment script.

```bash
# Generate hash from file content
HASH=$(md5sum output.js | cut -d' ' -f1)
mv output.js "output-${HASH}.js"
```

This ensures every deployment gets a unique filename that browsers won't cache.

# Question - Should we migrate to microservices architecture?
Current monolith is getting complex. Considering breaking into:
- Auth service
- API service  
- Data processing service

Pros: Better scalability, independent deployments
Cons: Increased complexity, distributed system challenges

Need to research more and discuss with team.

# Decision - Using TypeScript for new projects
After team discussion, we've decided all new projects will use TypeScript instead of JavaScript.

Rationale:
- Better type safety reduces bugs
- Improved IDE support and autocomplete
- Easier refactoring
- Team consensus after 2-month trial

Exception: Quick scripts and prototypes can still use JS.

# Learning - Insights from "Building a Second Brain" article
Key takeaways from https://jkudish.com/newsletter/003:
- Plain markdown + AI = queryable knowledge system
- Claude as interface, not just storage
- Start simple, grow organically
- Don't over-engineer with plugins

Action: Implementing this approach with Claude Code skills.

# Idea - Automated customer feedback aggregation
Getting feedback from multiple channels (email, Slack, support tickets). Could build a system that:
1. Aggregates all feedback into central database
2. Uses AI to categorize and extract themes
3. Generates weekly summary reports

Would help prioritize feature requests based on actual customer needs.

# Update - Boat rental bookings up 20% this month
GetMyBoat platform showing strong growth. Comparing to last month:
- Bookings: +20%
- Revenue: +18%
- Average booking value: -2% (more short-term rentals)

Marketing campaign from last month seems to be working. Should continue current strategy.

# Work - Helped customer with ePUB table rendering issue
Customer reported tables not rendering correctly in ePUB output from ePublisher.

Root cause: CSS properties not supported by all ePUB readers.

Solution: Simplified table styling, used only basic CSS properties with broad reader support:
- border, border-collapse
- padding, margin  
- width (percentage-based)

Customer confirmed it works across their target readers now.

# Meeting - German partner technical integration call
Date: 2025-11-16
Duration: 1 hour

Topics covered:
- API authentication approach (decided on OAuth 2.0)
- Data format standards (JSON-LD for semantic data)
- Integration timeline (3-month phased rollout)
- Testing strategy (joint staging environment)

Next steps:
- Tony: Send API documentation by Nov 20
- Partner: Provide sample data by Nov 22
- Both: Joint testing session Dec 1

# Decision - WSL2 as primary Windows development environment
After testing various setups, decided to standardize on WSL2 for Windows development:
- Better performance than Git Bash
- Native Linux tools
- Docker integration
- Consistent with production environment

Will create setup guide for team.
