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

## 2026-03-16 - Round 11

### Request

Continue refining the Favorite Books module:

- change the score system from 5-point to 100-point
- support multi-select tags
- make tags reusable shared entities instead of per-book comma strings
- allow creating a new tag directly during editing when existing tags do not fit
- update the GitHub documentation at the same time

### Decisions

- Existing ratings are migrated proportionally from the old 5-point scale into the new 100-point scale
- A shared tag model is introduced and books now relate to tags through a many-to-many structure
- The editor uses a two-part tag input: select existing tags and create new tags
- Newly entered tags are created automatically and immediately reusable by later books
- Books design and implementation docs are updated to reflect the new rating and tag rules

### Affected Pages

- Books
- Book editor drawer
- Tag filtering and shared-tag system
- Request history

### Status

Implemented and documented.

## 2026-03-16 - Round 11

### Request

Reposition the Favorite Books module:

- remove in-browser reading
- keep upload, download, and editing
- use the book cover as the main visual representation
- keep account-based permission isolation
- update the GitHub documentation at the same time

### Decisions

- The books module is narrowed from a mixed reader/library concept into a book archive
- The in-browser reader page, scripts, and reader endpoints are removed
- Uploaded files are kept only for archival storage and download
- The detail panel still keeps cover, notes, reading timeline, and protected file actions
- The documentation now describes archive/download behavior instead of a reader experience

### Affected Pages

- Books
- File permissions
- Books module implementation spec
- Request history

### Status

Implemented and documented.

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

## 2026-03-16 - Round 12

### Request

Continue discussing the external metadata enrichment feature for books, without implementing code yet, and define:

- the drawer entry placement
- the preview modal structure
- the `preview / apply` API draft
- the field overwrite rules
- a provider dropdown instead of a single source

### Decisions

- the main entry lives inside the book editor drawer, not on the list page
- the entry is composed of a provider dropdown plus a preview button
- phase one supports `WeRead / Douban / Open Library`
- actual writes must be split into `metadata-preview` and `metadata-apply`
- not-found cases use a lightweight 3-second toast instead of a large modal
- field overwrite follows a cautious flow: preview first, checkbox selection second, apply last
- a dedicated Chinese design doc is added for this feature

### Affected Pages

- Favorite Books editor drawer
- Books interaction spec
- Books implementation spec
- Books request history

### Status

Completed for this round.

## 2026-03-16 - Round 13

### Request

Continue refining the books module:

- stop rendering all existing tags as a large always-open block in the editor
- try to fill missing covers from WeRead first
- auto-generate short reviews where they are still empty
- prefill any other stable metadata that can be found reliably

### Decisions

- the editor drawer now uses a collapsed, searchable multi-select for existing tags
- public WeRead search results are used to fill authors, translators, publishers, and covers where available
- missing short reviews are batch-generated for the imported books
- uncertain matches are handled conservatively to avoid overwriting books with obviously wrong metadata

### Affected Pages

- Favorite Books editor drawer
- Online book data
- Books visual spec
- Books implementation spec

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

## 2026-03-16 - Round 10

### Request

Continue with component-level implementation planning, including:

- frontend component specifications
- API drafts
- state-machine descriptions
- finer module-level implementation docs for each page

### Decisions

- A new `implementation` documentation layer is added
- Shared implementation docs are added for frontend components, APIs, and state machines
- Module implementation specs are added for all nine primary pages
- The docs index is now structured as planning / design / implementation / history

### Affected Pages

- All nine primary pages
- Documentation structure
- Implementation planning layer

### Status

Completed for this round.

## 2026-03-16 - Round 11

### Request

Continue refining the books module:

- add a `word count (in ten-thousands)` field with decimal support
- remove the `paused` status
- make tags render in different colors
- sync the related design and implementation docs

### Decisions

- a new `word_count` field is added to the book model with decimal support
- the list cards, detail panel, and editor drawer now expose the word-count field
- the `paused` status is removed, and old data is migrated back to `planned`
- tag colors are now derived from the tag name so the same tag keeps the same tone site-wide
- the Chinese design docs, English overview, and implementation spec are updated together

### Affected Pages

- Favorite Books
- Book editor drawer
- Books design docs
- Books implementation docs

### Status

Completed for this round.
