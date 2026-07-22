# [PR Template] Code Changes

> Replace the title with a more descriptive alternative. Delete
> content below that doesn't apply to your PR. Also delete this paragraph!

## Description of Changes
Please provide a brief description of the changes made in this pull request:

* What is the purpose of this PR?
* What new function or feature is being added?
* How does it improve the existing repository?

## Related Issues
List any related issues or PRs that this submission addresses:

* Issue numbers (e.g., #123, #456)
* PR numbers (e.g., #789)

## Testing Performed
Describe the testing performed to validate the changes:

* Unit tests added or updated
* Integration tests performed
* Any other relevant testing or validation
* The command `make before-pr` completes successfully

## Code Changes
Provide an overview of the code changes made:

* New files or directories added
* Modified files or functions
* Deleted files or functions

## Example Usage
Include an example of how to use the new function or feature:

* Code snippet demonstrating usage
* Expected output or results

## Checklist
Confirm that the following have been completed.

- [ ] I have read and understood the [CONTRIBUTING](https://github.com/The-AI-Alliance/community/blob/main/CONTRIBUTING.md) guide.

Ignore (or delete) any of the following check list sections or items that aren't applicable, like the code-related check list items when this is a documentation-only PR:

For code changes:

- [ ] I have tested the code changes in my local development environment.
- [ ] I have added or modified tests for all code changes.
- [ ] I have followed the existing code styles and conventions.
- [ ] I have removed all API keys and other sensitive information.
- [ ] I have updated any related documentation.
- [ ] I have confirmed that the command `make before-pr` completes successfully.

For changes to the _microsite_:

- [ ] I have verified the microsite `make view-local` runs without errors and the changes render as expected.
- [ ] I have checked that external links (i.e., those going to different domains) have `target="..."` specifications by running `./check-external-links.sh` and fixing any flagged URLs. (This tool doesn't fix missing `target="..."` links itself nor does it verify that the links found are not 404s!)

For other documentation changes, such as `README`s:

- [ ] I have followed the existing documentation styles and conventions.
- [ ] I have included helpful diagrams, screenshots, tables, etc.

## Additional Context
Any additional context or information that might be helpful for reviewers:

* Relevant discussions or meetings
* Open questions or areas for further discussion
