---
name: create-pull-request
description: 'Create a GitHub pull request with a clear title, summary, and description; assign it to the current user and apply the green ready-for-review label. Use when asked to open, create, or prepare a PR.'
argument-hint: 'Optional PR title, base branch, or extra context'
user-invocable: true
---

# Create Pull Request

Create a ready-for-review GitHub pull request from the current branch, with a useful title and a factual summary and description. Assign it to the authenticated user and apply the `ready-for-review` label in green.

## Procedure

1. Identify the repository, current source branch, and target base branch. Use the repository's default branch unless the user specifies another target. Do not create a PR from the default branch into itself.
2. Inspect the commits and diff against the target base. Use them to write a concise, specific title and a body with these sections:
   - `## Summary`: the purpose and outcome of the change.
   - `## Changes`: the main implementation details.
   - `## Validation`: tests or checks actually run and their results. If none were run, say so; never imply checks passed when they were not run.
3. Use details provided by the user when supplied. Otherwise infer only facts supported by the diff and commit history. Ask a focused question if the target branch or intent cannot be determined safely.
4. Check whether a PR already exists for this source and target. If so, report it instead of creating a duplicate.
5. Ensure the source branch is available on the remote. If it is not, ask before pushing it. Never force-push as part of this workflow.
6. Create the PR as ready for review, not as a draft. Use the available GitHub PR creation integration when possible and set assignment to the authenticated user (`assign_to_me: true`). If that integration is unavailable, use `gh pr create` and then assign with `gh pr edit --add-assignee @me`.
7. Ensure the repository has a label named exactly `ready-for-review` with green color `0E8A16`. If it is absent, create it with `gh label create ready-for-review --color 0E8A16 --description "Ready for review"`. If it already exists with a different color, update it with `gh label edit ready-for-review --color 0E8A16`.
8. Apply the label to the new PR with `gh pr edit <number> --add-label ready-for-review`.
9. Verify the PR title, body, assignee, non-draft state, and label. Report the PR URL and any verification step that could not be completed.

## Failure Handling

- If GitHub authentication or repository permissions prevent creation, report the exact actionable failure. Do not switch accounts, change credentials, or expose tokens.
- If label management is unavailable or permission is denied, leave the PR intact and clearly report that the label was not applied.
- Do not claim the PR is ready for review until the PR exists, is not a draft, is assigned to the current user, and has the requested label.
