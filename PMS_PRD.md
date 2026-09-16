# Proxy Management System (PMS) --- Product Requirements Document

**Version:** MVP v1.0\
**Primary user:** Mrs. Vaishali Patil, School Supervisor\
**Platform:** Mobile-first responsive web application\
**School timetable source:** D.G. Tatkare Secondary & Higher Secondary
School, Kolad

## 1. Product Vision

### Product overview

PMS is a mobile-first supervisor tool for handling teacher absences and
assigning substitute/proxy teachers during the school day. It converts
the school's weekly teacher timetable into a real-time availability
engine.

The supplied timetable contains 19 named teachers, six teaching days
(Monday--Saturday), nine periods, and a daily recess from 2:30--3:00 PM.
A `-` represents an unassigned/free period. Teachers are associated with
classes where specified, while several teachers have no class specified.

**Core loop:** Attendance → Absent teacher → Affected periods →
Available teachers → Recommended proxy → Confirm assignment → Live
record.

### Problem statement

The supervisor currently has to mentally cross-check multiple teacher
timetables whenever a teacher is absent. This creates delay, accidental
double-booking, and unnecessary administrative work. PMS should make a
safe proxy decision in seconds.

### Target audience

-   **Primary:** Mrs. Vaishali Patil, supervisor teacher.
-   **Secondary/future:** Vice-principal, headmaster, academic
    administrator.

### Goals

1.  Mark daily teacher attendance in seconds.
2.  Detect every period affected by an absence automatically.
3.  Calculate available teachers for each affected slot in real time.
4.  Recommend the safest substitute without double-booking.
5.  Make assignment status visible at a glance.
6.  Work comfortably on a phone with one-handed interaction.
7.  Preserve an auditable history of attendance and proxy decisions.

### Success metrics

-   0% double-booked proxy assignments.
-   Candidate availability calculation \<150 ms for a 150-faculty
    timetable.
-   SUS ≥88 in usability testing.
-   ≥95% of normal absence-to-assignment journeys completed without
    assistance.
-   Median time from selecting an absent teacher to confirming a proxy
    \<30 seconds.
-   ≥99.9% successful save rate for attendance/proxy actions under
    normal connectivity.

## 2. User Persona

### Mrs. Vaishali Patil --- Supervisor

**Goals:** Quickly know who is absent, identify affected classes, find a
free teacher, assign the proxy, and continue supervising the school.

**Pain points:** Paper/spreadsheet cross-checking, remembering who is
free in each period, risk of assigning a teacher who is already
teaching, repeated searching, and lack of a single live status view.

**Usage context:** Mobile phone, often standing/walking, limited
attention, school-day time pressure. The interface must therefore favor
large touch targets, short flows, strong visual hierarchy, and immediate
confirmation.

## 3. Functional Requirements

### FR-01 --- Authentication and supervisor access

-   Provide secure supervisor login.
-   MVP has one operational role: Supervisor.
-   Persist authenticated session securely.
-   Unauthorized users cannot access attendance, timetable, or
    assignment data.

**Validation/error:** Invalid credentials show a concise error; expired
sessions redirect to login; failed writes must not appear successful.

### FR-02 --- Today dashboard

The home screen must show: - Current date/day. - Attendance summary:
Present / Absent / Not marked. - Number of affected proxy periods. -
Number of assigned proxies. - Number of unresolved periods. -
Current/next period indicator where time data is available. - Prominent
CTA: **Mark Attendance**. - Prominent alert when proxy assignments are
pending.

**Empty state:** "Attendance not marked yet" with one primary action.

### FR-03 --- Live teacher attendance

**User story:** As the supervisor, I want to search all teachers and
mark them present/absent so the system can calculate required proxies.

Requirements: - Display all teachers. - Search by teacher name with
typo-tolerant prefix/substring matching. - Show teacher name, class
(when available), and current attendance state. - States: Not Marked,
Present, Absent. - One-tap state change with confirmation only for
destructive/ambiguous actions. - Attendance is date-specific. - Prevent
duplicate attendance records.

**Flow:** Dashboard → Mark Attendance → Search/select teacher →
Absent/Present → Save → affected slots appear.

**Edge cases:** - Changing Absent → Present removes only *unassigned*
proxy requirements created by that absence; already confirmed
assignments require explicit resolution. - Marking a teacher absent
after proxies have already been assigned recalculates the affected
queue. - Teacher with no scheduled classes today creates no proxy
work. - A teacher may be absent for the full day in MVP; partial-period
absence can be a later extension.

### FR-04 --- Affected period detection

For every absent teacher: - Read the teacher's timetable for the current
weekday. - Ignore `-`/empty periods and recess. - Create one proxy
requirement per scheduled class period. - Store subject and class for
the affected slot. - Sort requirements chronologically. - Recalculate
immediately after attendance changes.

### FR-05 --- Candidate availability engine

For a selected affected slot, a teacher is **available** only when: 1.
They are marked Present (or attendance policy treats unmarked as
eligible; MVP should default to **Present only** for safety). 2. They
have no timetable class in the same day + period. 3. They have not
already been assigned another proxy in that same slot. 4. They are not
the absent teacher. 5. They are not otherwise blocked by a future
exclusion rule.

Candidate calculation should target \<150 ms for a 150-faculty
timetable.

### FR-06 --- Proxy recommendation

Rank eligible candidates using deterministic scoring: 1. **No
collision** --- mandatory. 2. Present status --- mandatory. 3. Free
scheduled period --- mandatory. 4. Fewer proxy assignments already
received today. 5. Subject compatibility, when known. 6. Same/nearby
class level familiarity. 7. Avoid repeated consecutive proxy assignments
when alternatives exist.

Display: - Recommended candidate first. - Why recommended: e.g. "Free
period · 0 proxies today · Mathematics experience". - Other eligible
teachers below. - Clear "Assign Proxy" action.

The algorithm must never trade a hard constraint for a better score.

### FR-07 --- Proxy assignment

**User story:** As the supervisor, I want to confirm a recommended
teacher so the class is covered without creating a collision.

On confirmation: - Revalidate availability server-side. - Create
assignment atomically. - Mark the affected period as Assigned. - Update
the candidate's daily proxy count. - Prevent the same candidate from
being assigned twice for the same slot. - Show success feedback and
advance to the next unresolved period.

If the candidate became unavailable between recommendation and
confirmation, reject the write and refresh candidates.

### FR-08 --- Proxy queue

Display affected periods as cards: - Period number. - Time label if
configured. - Class. - Subject. - Absent teacher. - Status: Pending /
Assigned / Conflict / Unresolved. - Assigned proxy, if any.

Provide "Next pending" behavior to minimize navigation.

### FR-09 --- Recent searches and favorites

Replace the irrelevant template term "Favourite Trains" with **Favorite
Teachers**. - Recent teacher searches are stored locally. - Supervisor
can favorite frequently used teachers. - Favorites appear near the top
of candidate lists/search. - Provide clear/remove controls. - Do not let
favorites override collision or attendance rules.

### FR-10 --- Journey statistics dashboard

Provide lightweight operational analytics: - Teachers absent today. -
Proxy periods required. - Proxies assigned. - Unresolved periods. -
Average assignment time. - Collision attempts prevented. - Most
frequently absent teachers. - Most frequently assigned proxy teachers. -
Proxy load distribution.

Analytics are for supervision and planning, not punitive performance
scoring.

### FR-11 --- Audit/history

Record: - Attendance changes. - Proxy requirements created. - Candidate
recommendations. - Confirmed assignments. -
Reassignments/cancellations. - Timestamp and acting user.

History should be searchable by date and teacher.

### FR-12 --- Loading, empty, and error states

-   Use skeletons for teacher lists, dashboard cards, and candidate
    cards.
-   Show inline progress during saves.
-   Disable duplicate submissions while saving.
-   Offline/network failure: preserve unsent intent locally where safe
    and clearly label data as unsynced.
-   Never silently discard attendance or proxy actions.
-   Provide retry.
-   For server conflicts, refresh the slot and explain that availability
    changed.

## 4. Information Architecture

**Bottom navigation** 1. **Today** --- dashboard and live proxy queue.
2. **Attendance** --- teacher attendance. 3. **Timetable** --- browse
teacher/day/period schedule. 4. **History** --- previous
attendance/proxy activity. 5. **More** --- profile, favorites, settings.

Primary navigation should remain available on mobile; proxy assignment
itself is a focused workflow rather than a permanent tab.

### Screen hierarchy

-   Login
-   Today Dashboard
    -   Attendance summary
    -   Proxy queue
    -   Assignment workflow
-   Attendance
    -   Search
    -   Teacher details
-   Timetable
    -   Day selector
    -   Teacher schedule
-   History
-   Analytics
-   Settings

## 5. UI/UX Specification

### Visual direction

Premium, calm, white-first interface inspired by Apple, Linear, Stripe,
Arc, and Notion. Use generous spacing, restrained borders, soft
surfaces, strong typography, and minimal decoration.

### Mobile layout

-   Designed first for 360--430 px wide phones.
-   Bottom navigation fixed to safe-area inset.
-   Primary actions reachable with the thumb.
-   Minimum touch target: 44×44 px.
-   Avoid dense tables on phones; use cards and horizontal day chips.
-   Desktop/tablet can expand cards into split-pane/table layouts.

### Today Dashboard

Top: - Greeting: "Good morning, Mrs. Patil" - Date and weekday. -
Compact status indicator.

Main: - 2×2 metric cards: Absent, Proxy Needed, Assigned, Unresolved. -
"Needs Attention" queue. - Next period card. - Quick attendance CTA.

### Attendance screen

-   Sticky search field.
-   Filter chips: All / Not Marked / Present / Absent.
-   Teacher rows with avatar initials, name, class, status pill.
-   Swipe is optional; explicit buttons are preferred for reliability.
-   Bulk "Mark remaining as Present" may be offered after review, but
    must require confirmation.

### Candidate screen

-   Header: `Period 4 · IX-1 · Marathi`
-   "Absent: Mrs. Mahable A.A."
-   Recommended teacher card with strong primary action.
-   Other available teachers.
-   Unavailable teachers should not clutter the default list; optionally
    show "Why unavailable" on demand.

### Timetable screen

-   Day chips Monday--Saturday.
-   Teacher selector/search.
-   9 period cards with subject/class.
-   Recess shown distinctly between periods 5 and 6.
-   Empty slots visibly labeled Free.

### History/analytics

Keep analytics secondary. Prioritize today's operational data over
charts.

### Animation

-   150--250 ms transitions.
-   Skeleton shimmer while loading.
-   Number counters animate once on dashboard load.
-   Success checkmark on assignment.
-   Smooth page transitions and scrolling.
-   Respect `prefers-reduced-motion`.
-   Avoid animation that delays task completion.

### Dark mode

The product is **white-first**, but the design system should support a
dark theme through semantic tokens. Dark mode can be hidden behind
Settings in MVP if implementation time is constrained.

## 6. Technical Architecture

### Recommended stack

-   **Frontend:** React + TypeScript + Vite/PWA.
-   **UI:** Tailwind CSS or equivalent token-based CSS system.
-   **State:** TanStack Query for server state; lightweight local state
    for UI/workflows.
-   **Backend:** FastAPI or Node.js/NestJS REST API.
-   **Database:** PostgreSQL.
-   **Authentication:** Secure cookie/session or short-lived access
    token + refresh mechanism.
-   **Deployment:** Managed HTTPS hosting with separate frontend/API
    services or a unified deployment.

### Architecture

Mobile browser/PWA → API → service layer → PostgreSQL.

The availability engine should be a pure, testable domain service
independent of UI.

### Folder structure

``` text
src/
  app/
  components/
    ui/
    dashboard/
    attendance/
    proxy/
    timetable/
    analytics/
  features/
    attendance/
    proxy/
    timetable/
    history/
  hooks/
  lib/
  services/
  types/
  styles/
  routes/
```

Backend:

``` text
app/
  api/
  models/
  schemas/
  services/
    attendance.py
    availability.py
    proxy_assignment.py
    analytics.py
  repositories/
  auth/
  tests/
```

### API surface

-   `POST /auth/login`
-   `GET /teachers`
-   `GET /timetable?day=...`
-   `GET /attendance?date=...`
-   `PUT /attendance/{teacherId}`
-   `GET /proxy-requirements?date=...`
-   `GET /proxy-requirements/{id}/candidates`
-   `POST /proxy-assignments`
-   `DELETE /proxy-assignments/{id}` with permission checks
-   `GET /analytics?date=...`
-   `GET /history`

### Concurrency

Assignment must use a transaction plus a server-side collision check.
Two simultaneous requests must not be able to assign the same teacher to
the same slot.

## 7. Data Models

``` text
Teacher
- id
- name
- class_name nullable
- active
- created_at

TimetableEntry
- id
- teacher_id
- weekday
- period_number
- subject nullable
- class_name nullable
- is_recess
- is_free

Attendance
- id
- teacher_id
- date
- status: PRESENT | ABSENT | NOT_MARKED
- marked_at
- marked_by

ProxyRequirement
- id
- date
- weekday
- period_number
- absent_teacher_id
- class_name
- subject
- status: PENDING | ASSIGNED | UNRESOLVED

ProxyAssignment
- id
- requirement_id
- proxy_teacher_id
- assigned_at
- assigned_by
- cancelled_at nullable

AuditEvent
- id
- actor_id
- event_type
- entity_type
- entity_id
- metadata JSON
- created_at

FavoriteTeacher
- user_id
- teacher_id
- created_at
```

### Key database constraints

-   Unique `(teacher_id, date)` for attendance.
-   Unique `(date, period_number, proxy_teacher_id)` for proxy
    assignment.
-   Unique `(requirement_id)` for active assignment.
-   Foreign keys on all relationships.
-   Index timetable by `(weekday, period_number, teacher_id)`.

## 8. Component Inventory

**Core:** AppShell, BottomNav, TopBar, Button, IconButton, Badge,
StatusPill, Card, Modal, Toast, Skeleton, EmptyState, ErrorState,
SearchInput, FilterChips.

**Attendance:** TeacherList, TeacherRow, AttendanceToggle,
AttendanceSummary, AttendanceSearch.

**Proxy:** ProxyQueue, ProxyRequirementCard, CandidateList,
CandidateCard, RecommendationBadge, AssignProxyButton,
AssignmentConfirmation, ConflictBanner.

**Timetable:** DaySelector, PeriodCard, TimetableGrid, TeacherSelector.

**Analytics:** MetricCard, AnimatedCounter, MiniBarChart,
JourneyStatCard.

## 9. Security

-   Enforce authenticated access to all operational APIs.
-   MVP role: `SUPERVISOR`.
-   Authorization checks on every write.
-   Validate teacher IDs, dates, period numbers, statuses, and
    assignment IDs server-side.
-   Never trust candidate availability calculated only in the browser.
-   Use parameterized queries/ORM.
-   HTTPS everywhere.
-   Secure cookies where cookie auth is used.
-   Rate-limit login and sensitive endpoints.
-   Keep secrets in environment variables; never commit `.env`.
-   Avoid exposing unnecessary personal data in analytics.
-   Audit all attendance and assignment mutations.

## 10. Accessibility

Target WCAG 2.2 AA: - 44×44 px minimum touch targets. - Keyboard
navigation for larger screens. - Visible focus states. - Semantic
headings and buttons. - Labels for all form controls. - Do not
communicate status by color alone. - Sufficient contrast. -
Screen-reader-friendly status updates after saves. - Reduced-motion
support. - Error messages associated with their controls. - Large,
readable type and adequate spacing.

## 11. Non-functional Requirements

-   Candidate calculation p95 \<150 ms at 150 teachers.
-   Dashboard initial API response target \<500 ms under normal
    conditions.
-   PWA should remain usable on typical school mobile networks.
-   Idempotent attendance updates.
-   Atomic proxy assignment.
-   Automated unit tests for availability and collision logic.
-   Integration tests for attendance → requirement → assignment.
-   Responsive from 360 px upward.

## 12. MVP Acceptance Criteria

The MVP is complete when Mrs. Vaishali Patil can: 1. Log in from a
phone. 2. See today's teachers and attendance state. 3. Search and mark
a teacher absent. 4. Automatically see every affected class period. 5.
Open any affected period and receive only valid available candidates. 6.
See a ranked recommendation. 7. Assign the proxy with one confirmation.
8. Never create a double-booking, including under concurrent requests.
9. See assignment status update immediately. 10. Review today's
completed/unresolved proxy work. 11. Review historical activity. 12. Use
the application comfortably on a 360--430 px mobile screen.

## 13. Development Roadmap

### Milestone 1 --- Foundation

-   Project setup, design tokens, authentication.
-   Teacher/timetable seed data.
-   PostgreSQL schema.
-   Mobile app shell.

### Milestone 2 --- Attendance

-   Teacher list/search.
-   Present/Absent state.
-   Date-based persistence.
-   Dashboard summary.

### Milestone 3 --- Proxy engine

-   Affected-period generation.
-   Availability calculation.
-   Ranking algorithm.
-   Collision-safe assignment.
-   Proxy queue.

### Milestone 4 --- UX polish

-   Skeletons, animations, counters, transitions.
-   Favorites and recent searches.
-   Timetable browser.
-   Responsive QA and accessibility.

### Milestone 5 --- History & analytics

-   Audit trail.
-   Journey statistics.
-   Operational analytics.
-   Export/reporting can follow after MVP.

### Milestone 6 --- Production hardening

-   Security review.
-   Load/performance tests.
-   Offline/retry behavior.
-   Monitoring/logging.
-   Backup and recovery.
-   SUS usability test and iteration.

## Product Decisions / Assumptions

-   Mrs. Vaishali Patil is the only intended operator for the MVP.
-   "Favourite Trains" from the supplied feature list is treated as a
    template error and replaced with "Favorite Teachers".
-   The supplied timetable is the authoritative starting dataset. It
    contains six weekdays and nine periods, with recess after period 5.
-   A free timetable slot is represented by `-`.
-   MVP requires a teacher to be marked Present before they can be
    recommended as a proxy; this is the safer default.
-   Subject/class compatibility is a ranking signal, never a reason to
    violate availability.
-   Partial-day teacher absence is not required for MVP.
