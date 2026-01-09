#!/bin/bash
# Bump version in plugin.json and marketplace.json
# Usage: ./scripts/bump-version.sh [patch|minor|major]

set -e

BUMP_TYPE="${1:-patch}"
PLUGIN_JSON="plugins/productivity-suite/.claude-plugin/plugin.json"
MARKETPLACE_JSON=".claude-plugin/marketplace.json"

# Validate bump type
if [[ ! "$BUMP_TYPE" =~ ^(patch|minor|major)$ ]]; then
    echo "Usage: $0 [patch|minor|major]"
    echo "  patch: 1.0.0 -> 1.0.1 (default)"
    echo "  minor: 1.0.0 -> 1.1.0"
    echo "  major: 1.0.0 -> 2.0.0"
    exit 1
fi

# Check if files exist
if [[ ! -f "$PLUGIN_JSON" ]]; then
    echo "Error: $PLUGIN_JSON not found"
    exit 1
fi

if [[ ! -f "$MARKETPLACE_JSON" ]]; then
    echo "Error: $MARKETPLACE_JSON not found"
    exit 1
fi

# Get current version
CURRENT=$(jq -r '.version' "$PLUGIN_JSON")
echo "Current version: $CURRENT"

# Parse version components
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

# Calculate new version
case $BUMP_TYPE in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    patch)
        PATCH=$((PATCH + 1))
        ;;
esac

NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
echo "New version: $NEW_VERSION ($BUMP_TYPE)"

# Update plugin.json
jq --arg v "$NEW_VERSION" '.version = $v' "$PLUGIN_JSON" > tmp.json && mv tmp.json "$PLUGIN_JSON"

# Update marketplace.json
jq --arg v "$NEW_VERSION" '.version = $v' "$MARKETPLACE_JSON" > tmp.json && mv tmp.json "$MARKETPLACE_JSON"

echo "Updated $PLUGIN_JSON"
echo "Updated $MARKETPLACE_JSON"
echo ""
echo "Next steps:"
echo "  git add $PLUGIN_JSON $MARKETPLACE_JSON"
echo "  git commit -m \"chore: bump version to $NEW_VERSION\""
