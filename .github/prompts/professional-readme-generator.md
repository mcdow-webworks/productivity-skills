# Professional README Generator Prompt

Use this prompt in a new Claude session to generate a professional, visually appealing README.md for any repository.

---

## Prompt

```
I need you to create a professional README.md for my project. Please follow this structure and style guide exactly:

## Project Information

**Project Name:** [Your project name]
**One-line Description:** [Brief description of what it does]
**License:** [MIT/Apache/GPL/etc.]
**Primary Language/Framework:** [e.g., Python, Node.js, React, etc.]
**Target Audience:** [Who will use this?]
**GitHub URL:** [Your repo URL]
**Author/Organization:** [Name and optional social links]

## Key Features (3-5 bullet points)
1. [Feature 1]
2. [Feature 2]
3. [Feature 3]

## Installation Command(s)
[How users install/setup your project]

## Basic Usage Example
[A simple example showing core functionality]

---

## Style Guide to Follow

### 1. Header Section
- Title as H1 with project name
- shields.io badges immediately after title (License, Platform, Version, etc.)
- One compelling sentence describing the value proposition

### 2. Emoji Section Headers
Use emoji icons for ALL major sections:
- 🎯 What is This? / Overview
- ✨ Quick Start
- 🚀 Features / Available Features
- 💡 Why This? / Benefits
- 📖 Philosophy / Principles
- 🎮 Examples / Workflows
- 📚 Documentation
- 🔧 Requirements
- 📂 Repository Structure
- 🤝 Contributing
- 🐛 Troubleshooting
- 📄 License
- 🌟 Star History
- 💬 Community
- 🙏 Acknowledgments
- 📬 Support

### 3. Visual Elements
- Use emoji bullets (📝 🔍 🔗 📊 💡 ✅ ❌) in feature lists
- Bold text for emphasis on key terms
- Code blocks with language hints for all code
- Blockquotes (>) for important notes/warnings
- Screenshots/images with italic captions below
- Arrow links for documentation: `[Guide Name →](link)`

### 4. Content Patterns
- "Before/After" or "Traditional/With This" comparison sections
- Real conversational examples showing actual usage
- Multiple persona workflows (Developer, Designer, PM, etc.)
- Numbered philosophy/principles list
- Tree-style directory structure for repo layout

### 5. Call-to-Action Elements
- Clear Quick Start with time estimate: "## ✨ Quick Start (X Minutes)"
- Prominent "That's it!" after simple instructions
- Star request: "If you find this useful, please ⭐ star the repo!"
- Closing tagline in bold italics

### 6. Footer Section
- Horizontal rule (---) before closing
- Memorable closing tagline
- Made with / Powered by attribution with emoji

### 7. Badge Examples (shields.io)
```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org)
[![Claude Code](https://img.shields.io/badge/Claude-Code-purple)](https://claude.ai/code)
[![npm](https://img.shields.io/npm/v/PACKAGE.svg)](https://npmjs.com/package/PACKAGE)
[![Build](https://img.shields.io/github/actions/workflow/status/USER/REPO/ci.yml)](https://github.com/USER/REPO/actions)
```

---

Now generate a complete README.md following this structure. Make it feel polished, approachable, and professional. The tone should be confident but friendly, technical but accessible.
```

---

## Example Section Templates

### Feature List with Emoji Bullets
```markdown
- 📝 **Feature name** - brief description
- 🔍 **Feature name** - brief description
- 🔗 **Feature name** - brief description
```

### Before/After Comparison
```markdown
## 💡 Why [Project]?

### Traditional Approach
```
[Show the painful way]
```

### With [Project]
```
[Show the elegant solution]
```

**[Project] provides:**
- ✅ Benefit one
- ✅ Benefit two
- ✅ Benefit three
```

### Workflow Example
```markdown
## 🎮 Example Workflows

### [Persona Name]

```bash
# Step 1
command here

# Step 2
You: "Natural language input"
Tool: Response showing value

# Step 3
You: "Follow-up"
Tool: Shows benefit
```
```

### Documentation Links
```markdown
## 📚 Documentation

- **[Guide Name](docs/guide.md)** - Description
- **[Another Guide](docs/other.md)** - Description
```

### Requirements Section
```markdown
## 🔧 Requirements

**Required:**
- **Tool** version+ (purpose)
- **Dependency** version+ (purpose)

**Optional:**
- **Optional tool** (for what)

> **Note:** Important caveat or limitation here.
```

### Repository Structure
```markdown
## 📂 Repository Structure

```
project-name/
├── src/
│   ├── main.py          # Description
│   └── utils/           # Description
├── docs/                # Documentation
├── tests/               # Test suite
├── README.md            # This file
└── LICENSE              # License file
```
```

### Support Section
```markdown
## 📬 Support

Need help?

1. Check the [FAQ](docs/faq.md)
2. Search [existing issues](https://github.com/USER/REPO/issues)
3. Open a [new issue](https://github.com/USER/REPO/issues/new)
4. Join the [discussion](https://github.com/USER/REPO/discussions)
```

### Closing
```markdown
---

**Your memorable tagline here.**

🛠️ Made with [Tool] | 🚀 Powered by [Platform]
```

---

## Usage Tips

1. **Fill in all project information** before running the prompt
2. **Provide real examples** - the more specific, the better the output
3. **Iterate** - run once, then ask for specific section improvements
4. **Add screenshots** manually after generation
5. **Customize badges** for your specific tech stack

## Common Badge Colors

- `blue` - Primary/default
- `green` - Success/active/Node.js
- `yellow` - Warning/MIT license
- `red` - Critical/breaking
- `purple` - Claude/AI/special
- `orange` - Documentation
- `brightgreen` - Passing/success
