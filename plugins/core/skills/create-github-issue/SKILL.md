---
name: create-github-issue
description: Create a GitHub issue with the correct existing labels and, when a Projects v2 board applies, the relevant custom field values (Status, Priority, Size, dates). Discovers real labels and field IDs first and never invents them. Triggers: 'create a github issue', 'open an issue', 'file an issue', 'log this as an issue', 'raise a ticket'.
---

# Create GitHub Issue

Create an issue with labels and project fields that actually exist. Discover real values first; never invent a label, field, or option.

## 1. Discover before creating

Labels (use only what exists; `gh issue create --label` fails on an unknown label):
```bash
gh label list -R <OWNER>/<REPO> --limit 100 --json name | jq -r '.[].name'
```

If the issue belongs on a Projects v2 board, read its number, node id, and fields:
```bash
gh project list --owner <OWNER> --format json | jq '.projects[] | {number, title}'
gh project view <PROJECT_NUMBER> --owner <OWNER> --format json | jq -r '.id'        # PVT_... project node id
gh project field-list <PROJECT_NUMBER> --owner <OWNER> --format json                # field ids + single-select option ids
```
Project operations need the `project` token scope: `gh auth refresh -h github.com -s project`.

## 2. Create the issue

```bash
gh issue create -R <OWNER>/<REPO> \
  --title "<TITLE>" \
  --body "<BODY>" \
  --label "<LABEL>" --label "<LABEL>" \
  --assignee <LOGIN> \
  --milestone "<MILESTONE>"
```
Pick labels that match the issue's content (type, area, priority). Apply the few that fit, not every label. `--project "<TITLE>"` links the issue to a board but does not set field values; do that in step 3. `gh issue create` prints the new issue URL; capture it for the next step.

## 3. Set project custom fields

Add the issue to the board and capture the item id and project node id:
```bash
ITEM_ID=$(gh project item-add <PROJECT_NUMBER> --owner <OWNER> --url <ISSUE_URL> --format json | jq -r '.id')   # PVTI_...
PROJECT_ID=$(gh project view <PROJECT_NUMBER> --owner <OWNER> --format json | jq -r '.id')                     # PVT_...
```
Set one field per call, using the field id (and option id for single-select) from step 1:
```bash
# single-select (Status, Priority, Size)
gh project item-edit --id "$ITEM_ID" --project-id "$PROJECT_ID" --field-id <FIELD_ID> --single-select-option-id <OPTION_ID>
# text
gh project item-edit --id "$ITEM_ID" --project-id "$PROJECT_ID" --field-id <FIELD_ID> --text "<VALUE>"
# number
gh project item-edit --id "$ITEM_ID" --project-id "$PROJECT_ID" --field-id <FIELD_ID> --number <N>
# date (YYYY-MM-DD)
gh project item-edit --id "$ITEM_ID" --project-id "$PROJECT_ID" --field-id <FIELD_ID> --date "<YYYY-MM-DD>"
# iteration
gh project item-edit --id "$ITEM_ID" --project-id "$PROJECT_ID" --field-id <FIELD_ID> --iteration-id <ITERATION_ID>
```
Set only fields that genuinely apply. Don't invent a Priority or Size the user hasn't implied.

## Rules

- Never invent a label, field, or option. If nothing fits, create the issue without it and say so.
- `--project-id` is the project node id (`PVT_...`), not the number. The number is the positional argument.
- `--owner <ORG>` for org boards; `@me` for a personal board.
- One field per `item-edit` call; loop for several.
- If labels or field values are ambiguous, ask which apply rather than guessing.
- Iteration field ids may not surface in `field-list`; fall back to `gh api graphql` to read `ProjectV2IterationField` ids.
