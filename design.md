# PMS Design System --- `design.md`

## 1. Design Principle

PMS should feel like a calm control panel rather than a school ERP. The
supervisor should understand what needs attention within two seconds and
complete the common proxy workflow with minimal navigation.

**References:** Apple --- clarity; Linear --- information density;
Stripe --- hierarchy and trust; Arc --- fluidity; Notion --- clean
utility.

## 2. Brand Direction

_Updated to the "Administrative Calm" system (v2, sourced from the Stitch
mobile redesign package). Same principles, new palette: deep teal replaces
blue as the single accent, and the canvas is a soft slate instead of pure
white._

-   Slate canvas, white cards --- surfaces tier clearly without needing
    heavy shadows.
-   Minimal borders (1px hairlines), calm and administrative rather than
    decorative.
-   Soft neutral surfaces.
-   One restrained accent color for primary actions: deep teal, denoting
    trust and stewardship rather than a generic product blue.
-   Status colors are semantic (emerald / amber / rose) and must never be
    the only indicator --- always pair with an icon.
-   Rounded cards (8px base), but avoid excessive "floating app" styling.
-   No gradients in core operational screens.

## 3. Design Tokens

``` css
:root {
  --bg: #f8fafc;
  --surface: #f1f5f9;
  --surface-raised: #ffffff;
  --text: #0f172a;
  --text-muted: #475569;
  --border: #e2e8f0;
  --accent: #0d6e6e;
  --accent-hover: #0b5b5b;
  --success: #059669;
  --warning: #d97706;
  --danger: #e11d48;

  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;

  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
}
```

Dark-theme semantic tokens map the same roles to dark surfaces without
changing component structure; the accent brightens to `#14b8a6` in dark
mode for adequate contrast on near-black surfaces.

This is the spec of record for the app's palette --- `frontend/src/styles/tokens.css`
implements it as CSS custom properties consumed through Tailwind's
semantic color names (`bg-primary`, `text-success`, `bg-pending-bg`,
etc.), so components should never hardcode a hex value directly.

## 4. Typography

Recommended system stack:

``` css
font-family:
  Inter,
  ui-sans-serif,
  system-ui,
  -apple-system,
  BlinkMacSystemFont,
  "Segoe UI",
  sans-serif;
```

-   Display: 28--32 px / semibold.
-   Screen title: 22--24 px / semibold.
-   Card title: 16--18 px / semibold.
-   Body: 14--16 px.
-   Metadata: 12--13 px.
-   Use tabular numerals for animated metrics.

## 5. Layout

### Mobile

-   16 px horizontal page padding.
-   8--12 px card gaps.
-   Bottom navigation height \~64--72 px plus safe area.
-   Sticky search when lists are long.
-   Primary action near the bottom of the thumb zone.

### Tablet/Desktop

-   Max content width \~1200 px.
-   Two-column dashboard when width permits.
-   Candidate list and requirement details can become a split pane.

## 6. Core Components

### Button

Variants: - Primary - Secondary - Ghost - Destructive

States: - Default - Pressed - Focused - Disabled - Loading - Success

### Status pill

Use icon + label: - Present ✓ - Absent × - Pending ○ - Assigned ✓ -
Unresolved !

### Teacher row

``` text
[Initials]  Mrs. Jadhav S.S.
            Class VIII-2
                         [Present]
```

### Metric card

``` text
ABSENT TODAY
3
↑ 1 from yesterday
```

### Proxy card

``` text
PERIOD 4                         PENDING
IX-1 · Marathi

Absent teacher
Mrs. Mahable A.A.

Recommended
Mrs. Patil S.D.
Free period · 0 proxies today

[ Assign Proxy ]
```

## 7. Screen Specifications

### Login

Centered logo/wordmark, supervisor identifier, password/PIN field,
primary Sign In button. Keep it intentionally sparse.

### Today

_v2 layout (Administrative Calm), real data only --- no widget is shown
unless it is backed by an actual query:_

1.  Greeting + date, using the signed-in supervisor's real name.
2.  Primary "Mark Attendance" CTA --- always the strongest visual
    element on the page, never downgraded to a ghost button once
    attendance has started (this was a v1 bug: the CTA lost its fill
    style after the first mark).
3.  Compact faculty summary strip: total active faculty, absent today,
    proxies assigned, proxies still pending. Four numbers, one row,
    no separate cards sprawling down the page.
4.  "Needs Attention" proxy queue, in a bounded internally-scrollable
    panel (not an ever-growing page) --- a heavy-absence morning can
    produce a dozen-plus pending slots, and the panel keeps the page
    from ballooning while still surfacing every item on scroll.
5.  "Today's Confirmed Coverage" --- a short log of proxies already
    assigned today, so the supervisor can see progress without
    opening History.

Explicitly deferred (no backing data yet, so not built): notifications
bell/broadcast, AI-suggested candidate match %, live staffroom camera
feed, "free right now" faculty count. See the project backlog for
what each would need.

### Attendance

Search at top → filters → teacher list. Status change should update
optimistically only after the request is safely accepted; rollback on
failure.

### Proxy assignment

Use a focused full-screen/mobile sheet: - affected class and subject, -
absent teacher, - recommended candidate, - alternative candidates, -
confirmation.

After assignment, show a short success animation and move to the next
pending requirement.

### Timetable

Day selector + teacher selector + period list. Recess appears as a
dedicated separator between periods 5 and 6.

### History

Date filter → event list. Keep details collapsed by default.

### Analytics

Use compact cards and simple charts. Avoid dashboard clutter. The main
dashboard is for action; analytics is for reflection.

## 8. Interaction Rules

-   Tap targets ≥44 px.
-   Search results appear as the user types.
-   Debounce remote search around 150--250 ms.
-   Candidate list should update immediately after attendance changes.
-   Assignment confirmation is a single clear action.
-   After success, use a toast plus inline status update.
-   Destructive actions require confirmation.
-   Never hide a collision error behind a generic toast.

## 9. Motion

-   Page transition: 180--220 ms.
-   Card entrance: 160--200 ms.
-   Button press: 100--140 ms.
-   Counter animation: 500--700 ms.
-   Success check: \~400 ms.
-   Skeleton shimmer: 1.2--1.6 s loop.
-   Respect `prefers-reduced-motion: reduce`.

## 10. Empty / Error States

### No absences

**All clear**\
"No teacher absences have been marked today."

### No proxy needed

**No proxy required**\
"Everyone's scheduled classes are covered."

### No candidate

**No available teacher**\
"No present teacher is free for this period. Review the timetable or
resolve manually."

### Network error

**Couldn't save changes**\
"Your last action was not confirmed by the server."\
`Retry`

### Collision

**Availability changed**\
"This teacher was assigned elsewhere. We refreshed the available
teachers."

## 11. Accessibility

-   Contrast must meet WCAG AA.
-   Status uses icon + text.
-   Visible keyboard focus.
-   Screen-reader labels for icon buttons.
-   Announce assignment success and errors.
-   Reduced-motion support.
-   Do not use red/green as the sole distinction.

## 12. PWA Behavior

-   Installable on Android/iOS-compatible browsers where supported.
-   App shell can load quickly.
-   Cache static assets.
-   Do not cache sensitive operational data indefinitely.
-   Show an explicit "Offline" state.
-   Queueing writes is optional for MVP; if implemented, clearly show
    "Pending sync".

## 13. UX Quality Bar

A supervisor should be able to perform:

**Open app → Mark absent → Select affected period → Tap recommended
teacher → Confirm**

in approximately 20--30 seconds for a normal case, without opening a
desktop timetable or manually comparing multiple schedules.
