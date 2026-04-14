# Skill Search Command

Search for available skills in the claude-skills marketplace.

## Usage

```
/skill:search [query]
```

## Description

Searches the marketplace for skills matching the provided query string.
Returns a list of matching skills with their descriptions, versions, and install commands.

## Arguments

- `query` (optional): Search term to filter skills by name or description.
  If omitted, lists all available skills.

## Examples

```
/skill:search git
/skill:search code review
/skill:search
```

## Steps

1. Read `.claude-plugin/marketplace.json`
2. Filter skills matching `$ARGUMENTS` against name and description fields
3. Display results in a formatted table with: name, version, description, author
4. Show total count of matching skills
5. Suggest `/skill:install <name>` to install any listed skill
