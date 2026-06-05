# Skill: get-page-title

## Description
Takes a URL as input, fetches the HTML content of the page, and extracts and returns the page title.

## Input
- `url`: The full URL of the webpage to be analyzed.

## Implementation Logic
1. **Fetch Content**: Use the `WebFetch` tool to retrieve the content of the provided `url`.
2. **Extract Title**:
   - If the tool returns the page title in its metadata, use that.
   - Otherwise, parse the returned markdown/HTML content for the `<title>` element or the first `<h1>` tag.
3. **Return Result**: Output the extracted title as a plain string.

## Example
**Input:** `https://www.anthropic.com`
**Output:** `Anthropic`
