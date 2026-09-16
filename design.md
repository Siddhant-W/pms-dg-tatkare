# PMS Design System --- `design.md`

## 1. Design Principle

PMS should feel like a calm control panel rather than a school ERP. The
supervisor should understand what needs attention within two seconds and
complete the common proxy workflow with minimal navigation.

**References:** Apple --- clarity; Linear --- information density;
Stripe --- hierarchy and trust; Arc --- fluidity; Notion --- clean
utility.

## 2. Brand Direction

-   White-first.
-   Minimal borders.
-   Soft neutral surfaces.
-   One restrained accent color for primary actions.
-   Status colors are semantic and must never be the only indicator.
-   Rounded cards, but avoid excessive "floating app" styling.
-   No gradients in core operational screens.

## 3. Design Tokens

``` css
:root {
  --bg: #ffffff;
  --surface: #f8f9fb;
  --surface-raised: #ffffff;
  --text: #17181c;
  --text-muted: #6b7280;
  --border: #e6e8ec;
  --accent: #2563eb;
  --success: #16a34a;
  --warning: #d97706;
  --danger: #dc2626;

  --radius-sm: 10px;
  --radius-md: 14px;
  --radius-lg: 20px;

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

Dark-theme semantic tokens should map the same roles to dark surfaces
without changing component structure.

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

1.  Greeting/date.
2.  Four compact metrics.
3.  "Needs Attention" proxy queue.
4.  Next period.
5.  Quick attendance button.

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
