# Technical Plan

## Recommended Technical Direction

Recommendation for phase 1:

- Backend: Django
- Frontend: Django templates + modular JS
- Charts: Chart.js or ECharts
- Database: SQLite for local start, PostgreSQL for deployment growth
- File storage: local media storage first, later object storage if needed
- Auth: public read + authenticated edit
- Permission layer: owner / editor / viewer-capable design

This direction fits the current need because:

- CRUD-heavy pages are the main workload
- there are many independent modules
- file upload/download is important
- charts are needed but not complex enough to require SPA-first architecture
- fast iteration matters more than frontend complexity

## Suggested Project Structure

```text
RememberMyself/
  docs/
  apps/
    core/
    accounts/
    home/
    books/
    food/
    music/
    scenery/
    fitness/
    finance/
    schedule/
    methods/
  media/
  static/
```

## Data Strategy

Use separate model groups by page:

- `Book`, `BookFile`, `BookNote`
- `FoodEntry`, `FoodPhoto`
- `MusicTrack`
- `SceneryEntry`, `SceneryPhoto`
- `WeightLog`, `MealLog`, `CalorieLog`
- `FinanceEntry`
- `ScheduleEntry`
- `MethodNote`

This keeps later changes isolated.

## File Handling

Books:

- support pdf, epub, txt, md upload first
- browser reading priority: pdf, txt, md
- download requires authenticated permission
- epub can be added in phase 2

Music:

- support mp3, wav, m4a upload first
- browser streaming playback
- playback and download require authenticated permission

Images:

- store originals
- generate thumbnails later if needed

## Admin and Editing

Phase 1 should support owner-side editing in normal pages, not only Django admin.

Recommended editing mode:

- list page
- create drawer or modal
- edit drawer or modal
- delete confirm

## Auth and Permissions

Recommended access model:

- anonymous user: can view public page content
- viewer: can access protected personal media such as books/music after login
- editor: can create/update/delete normal content records
- owner: full access including account/role management

Recommended enforcement split:

- page visibility policy
- action policy
- file access policy

This is better than only a simple logged-in / not-logged-in split.

## Charts

Needed charts:

- weight trend
- calorie trend
- expense trend
- category distribution

## Versioning Approach

Because the user wants each page independently adjustable:

- routes should be page-based
- templates should be page-based
- services should be page-based
- optional future versioning can use `v1`, `v2` page templates or feature flags per module
- new modules should be addable as separate apps without rewriting existing ones

## Visual Strategy

The user wants independent visual style by page.

Recommended rule:

- keep shared shell small: navigation, auth, layout primitives
- let each page own its own accent palette, spacing rhythm, media layout, and typography treatment
- avoid over-centralizing UI rules that would block later redesign of one page

## Delivery Phases

### Phase 0

- planning
- repository
- docs

### Phase 1

- home
- books
- fitness
- finance

These four are the strongest core identity modules.

### Phase 2

- food
- music
- scenery

### Phase 3

- schedule
- methods
- polish

## Confirmed Decisions

- public-readable
- authenticated editing
- protected access for books and music
- role layering needed
- independent page style preferred
