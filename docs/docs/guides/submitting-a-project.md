# Submit a project

Authenticated users can publish Matrix bots, integrations, SDKs, and other
ecosystem projects directly from the directory.

## Before you start

Prepare the following information:

- A project name
- A short summary for directory cards and search results
- A longer description of what the project does and how to use it
- At least one repository or project website
- At least one category

You may also provide a Matrix room and indicate whether the project supports
end-to-end encrypted rooms.

!!! note "Listings are public"
    Do not include secrets, access tokens, private room links, or other
    information that should not appear in the public directory.

## Publish a listing

1. Sign in to Matrix Directory.
2. Open your dashboard.
3. Select **Add listing**.
4. Complete the required fields. The listing status panel shows which required
   information is still missing.
5. Review the directory-card preview.
6. Select **Publish listing**.

The listing is associated with your authenticated account and published
immediately. After a successful submission, the application redirects you to
the new public listing.

## Field requirements

| Field | Requirement |
| --- | --- |
| Name | Required; 2–100 characters |
| Short description | Required; 1–160 characters |
| About | Required; 1–10,000 characters; Markdown supported |
| Repository | Optional individually; required if no website is supplied |
| Website | Optional individually; required if no repository is supplied |
| Matrix room | Optional |
| Categories | At least one required; duplicate categories are not accepted |
| E2EE support | Select only when the project can operate in encrypted Matrix rooms |

Repository, website, and Matrix room values must be absolute `http://` or
`https://` URLs no longer than 255 characters. Blank optional URLs are treated
as omitted.

At least one repository or website must remain on the listing when it is
updated later.

## Markdown descriptions

The **About** editor supports CommonMark formatting, including:

- Headings
- Emphasis and strong emphasis
- Ordered and unordered lists
- Links
- Block quotes
- Inline and fenced code
- Horizontal rules

Raw HTML is displayed as text rather than interpreted as page markup.

Images embedded with Markdown are not rendered on saved listings. When the
Markdown is parsed, image nodes are reduced to their alternative text to
prevent a listing from making visitors contact an untrusted image host. Use a
normal link when readers need access to a screenshot or diagram.

## Manage your listings

Open the dashboard to see projects owned by your account. Ownership comes from
your authenticated session; it cannot be assigned to another user through the
submission form.

Only an owner can update or delete their listing. Deleting a listing is
permanent, so confirm that you selected the intended project before proceeding.

## Troubleshooting

If a listing cannot be published:

- Check the listing status panel for missing required fields.
- Confirm that every URL is absolute and begins with `http://` or `https://`.
- Confirm that at least one repository or website is present.
- Confirm that at least one category is selected.
- Shorten any field that exceeds its displayed character limit.
- Reload the page if categories could not be loaded.

For API-level validation and response details, see the
[HTTP API reference](../reference/api.md#create-a-project).
