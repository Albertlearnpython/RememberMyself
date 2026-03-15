# Request History

This file is the running log for future website requests.

Rule:

- Every new requirement for `RememberMyself` should be appended here.
- Each entry should record date, request summary, affected pages, and decision status.
- This file is the first source of truth for change history.

## 2026-03-15

### Request

Create a new GitHub repository named `RememberMyself`.

Before building the site, first sort out:

- the overall website idea
- the page/module breakdown
- the likely technical approach
- a persistent markdown record for future requirements

### Source Notes

The vision comes from `D:\09_Ai\Me_and_Ai.md`.

Key themes extracted:

- self-identity and self-remembering
- favorite books, food, music, and scenery
- body training and weight tracking
- income and expense balance
- time arrangement
- methods and insight-style reflections

### Decisions

- GitHub repository created: `Albertlearnpython/RememberMyself`
- Start with planning documents instead of immediate implementation
- Use page independence as a hard architectural principle
- Exclude secrets, passwords, and sensitive account data from website scope

### Affected Pages

- Global architecture
- Home
- Books
- Food
- Music
- Scenery
- Fitness
- Finance
- Schedule
- Methods

### Status

In planning.

## 2026-03-15 - Round 2

### Request

Continue discussing the design, not implementation yet.

Additional confirmed requirements:

- the site must be easy to extend with new pages later
- diagrams should be visible both in GitHub docs and in chat discussion
- page wireframes and data model design should be made explicit
- the site should be public-readable
- editing requires login
- uploaded books and music also require login
- account permissions should support layered roles
- each page should be allowed to have its own visual style

### Decisions

- Architecture must optimize for future page/module expansion
- Access policy is `public read + authenticated edit`
- File policy for books and music is `authenticated access only`
- Role model should support at least owner / editor / viewer separation
- Visual system is page-independent, not globally forced into one style

### Affected Pages

- Global architecture
- Auth and permission system
- Books
- Music
- All page styling strategy

### Status

Planning updated.

## 2026-03-15 - Round 3

### Request

Ignore all account/password content from the source article.

Focus only on two page designs first:

- Home
- Favorite Books

Design preference:

- minimal
- crafted
- refined material feeling

Still no implementation yet.

### Decisions

- Sensitive account/password content is fully excluded from the website scope
- Home and Books become the first pages to receive detailed design treatment
- Visual direction for this stage is `minimal + craftsmanship`

### Affected Pages

- Home
- Books
- Global visual system

### Status

Detailed page design in progress.
