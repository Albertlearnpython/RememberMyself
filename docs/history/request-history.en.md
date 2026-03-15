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

## 2026-03-16 - Round 4

### Request

Refine the documentation system and continue the page design:

- reorganize docs into clearer categories
- provide Chinese versions and make Chinese the primary reading path
- shape the home page tone into "cool poetic restraint"
- use a drawer pattern for book-page editing
- keep the current books data structure direction
- continue with richer explanations and design diagrams

### Decisions

- Docs are reorganized into `planning / design / history`
- Chinese-first docs are added as the primary entry point
- The home page tone is refined to `calm, crafted, quietly poetic`
- Favorite Books uses drawer-based create/edit interactions
- The current books-page structure remains the baseline
- High-fidelity design explanation docs are added for Home and Favorite Books

### Affected Pages

- Documentation system
- Home
- Books

### Status

Design deepening in progress.

## 2026-03-16 - Round 5

### Request

Move into the next design round:

- push the Home page closer to a formal UI specification
- define the Favorite Books field structure
- define the drawer-based create/edit form
- define the mobile interaction flow and prototype
- keep everything saved in GitHub

### Decisions

- A deeper Home layout composition spec is added
- A Favorite Books field schema doc is added
- A Favorite Books interaction and mobile-flow doc is added
- The planning docs are now moving toward implementation-ready specifications

### Affected Pages

- Home
- Books
- Documentation index

### Status

Completed for this round.

## 2026-03-16 - Round 6

### Request

Stay in the design phase and do not build yet.

This round requires:

- final visual specifications for Home and Favorite Books
- enough detail on colors, weights, and card styles for direct frontend implementation
- an explicit definition of how the Home page navigates to the other modules
- save everything to GitHub

### Decisions

- A final visual specification doc is added for Home
- A final visual specification doc is added for Favorite Books
- Home now has explicit route, anchor, and click-navigation rules
- Entry to other modules from Home is fixed as four layers: top bar, Hero, module index cards, and recent update cards

### Affected Pages

- Home
- Books
- Documentation index

### Status

Completed for this round.

## 2026-03-16 - Round 7

### Request

Expand the design work across the remaining modules:

- add Food and Music
- add initial design specs for the other modules
- keep everything synced to GitHub

### Decisions

- A final visual spec is added for Favorite Food
- A final visual spec is added for Favorite Music
- Initial design specs are added for Scenery, Fitness, Finance, Schedule, and Methods
- A summary doc is added to show the current maturity level of all modules

### Affected Pages

- Food
- Music
- Scenery
- Fitness
- Finance
- Schedule
- Methods
- Documentation index

### Status

Completed for this round.

## 2026-03-16 - Round 8

### Request

Continue refining the design work, with priority on:

- Fitness
- Finance

The goal remains design-only, without implementation.

### Decisions

- A final visual spec is added for Fitness
- A final visual spec is added for Finance
- The module maturity overview is updated
- The next suggested priorities are now Scenery, Methods, and Schedule

### Affected Pages

- Fitness
- Finance
- Documentation index
- Module maturity overview

### Status

Completed for this round.

## 2026-03-16 - Round 9

### Request

Finish the remaining modules as well.

### Decisions

- A final visual spec is added for Scenery
- A final visual spec is added for Schedule
- A final visual spec is added for Methods
- All nine primary modules are now at the final-visual-spec level
- The site-wide maturity overview and documentation index are updated

### Affected Pages

- Scenery
- Schedule
- Methods
- Documentation index
- Site-wide maturity overview

### Status

Completed for this round.
