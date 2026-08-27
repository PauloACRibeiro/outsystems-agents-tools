# Timeline / Activity Feed Screen


> **Harvested from:** a curated OutSystems UI screen-guide reference set (`timeline.md`) (read-only source, harvested 2026-07-13).
> **Upstream origin:** OutSystems UI pattern reference, curated upstream reference (no further upstream repo cited in source).
> **Merge note:** the Conversation / chat variant was locally corrected 2026-08-27 — local corrections preserved where noted in `maintenance/refresh-checklist.md`.
> See `maintenance/refresh-checklist.md` for the refresh procedure.

## Anatomy

A chronological stream of events, actions, or updates. Used for activity logs, audit trails, notification feeds, and social-style feeds.

1. **Feed header**: Title (heading3) + optional filter controls (date range, actor, action type) + optional "Mark all read" action
2. **Timeline stream**: Vertical list of entries, ordered by timestamp (newest first or oldest first depending on context):
   - **Date separator**: When entries span multiple days, insert a date heading between day groups ("Today", "Yesterday", "April 28, 2026")
   - **Entry anatomy**:
     - Avatar or icon (left side): actor photo (Avatar pattern, small) or action-type icon
     - Content (right side): Actor name (font-semi-bold) + action description + target entity link + timestamp (text-neutral-7, font-size-xs)
     - Optional: preview snippet, attachment thumbnail, or comment text below the action line
   - **Connector line**: Vertical line connecting entry icons/avatars (left-aligned)
3. **Load more / pagination**: "Load older" button at bottom, or infinite scroll for casual feeds
4. **Empty state**: "No activity yet" with illustration + description

## Variants

- **Audit trail**: Formal log — actor + action + entity + timestamp. No avatars, icon-based. Compact density
- **Notification feed**: Read/unread state. Unread entries bold/highlighted. Dismiss or mark-read actions per entry
- **Social-style feed**: Rich content — images, comments, reactions. Cards per entry with more padding
- **Conversation / chat**: a message stream with a composer. It inverts most of the anatomy, layout and data defaults above — see `## Variant: Conversation / chat` below, and design from that section, not from this one

## Variant: Conversation / chat

A chat surface claims this archetype's slot, but almost none of the feed anatomy above
applies to it. Design it from this section.

**Anatomy**

1. **Conversation header**: participant or agent name + optional status ("Online", "Thinking…") + optional actions (clear, export)
2. **Message stream**: a `List` of `ChatMessage` blocks, one per message. `ChatMessage.MessageText` holds the body; `ChatMessage.Actions` holds per-message inline actions (copy, retry, react). `ChatMessage.IsRight` = `True` for the current user's own messages, which is what produces the alternating sides — set the input, do not style the alignment by hand. `ChatMessage.MessageStatus` (`Sent` · `Delivered` · `Read`) carries delivery state where the app tracks it
3. **Date / session separators**: same as the feed — a centered heading between day groups
4. **Composer**, docked at the bottom: a multi-line `TextArea` + a send button, plus any attach or voice affordances. **OutSystems UI ships no composer block** — `blocks-index.md` has `ChatMessage` and nothing else for this surface, so the composer is a **custom block** the design must declare, not a pattern to reference
5. **Empty state**: a first-use prompt or suggested openers, not "No activity yet"

**Layout and styling**

- Stream: single column, max-width ~700px, **no connector line** and no avatar gutter — the bubble's side carries the actor, so the 2px vertical line and the fixed-width icon column above do not apply
- Bubbles: own-messages right-aligned, others left; padding inside the bubble replaces the between-entry padding
- Composer: docked to the bottom of the content area (sticky), full stream width, growing with its content up to a max height
- Timestamps: per message or per group, `text-neutral-7`, `font-size-xs`

**Data and behaviour**

- **Default sort: oldest first** — messages append at the bottom, and the view scrolls to the newest on arrival. The feed's "newest first (descending timestamp)" default is inverted here
- **Paging: "Load older" at the top**, or load-on-scroll-up. The bottom belongs to the composer and the newest message, so the feed's bottom-anchored "Load more" is wrong for this surface
- **While an answer is in flight**: disable the composer as well as the send button, and show the pending message in the stream — see `states-and-feedback.md`, "Composer / async answer in flight"

## Layout

- Stream: single-column, centered with max-width (~700px) for readability. Or full-width in a sidebar panel
- Entries: avatar/icon fixed-width left column (~40px), content fills remaining width
- Connector line: 2px vertical line through the avatar/icon column center
- Date separators: centered text with horizontal rules on each side

## Styling

- Entries: padding-s vertically between entries. No card wrapper needed (connector line provides structure)
- Avatars: 32-36px circle (Avatar pattern, small)
- Action text: "**John Smith** updated the status of **Order #1234** to Shipped" — actor and entity names in font-semi-bold or as clickable links
- Timestamps: text-neutral-7, font-size-xs, positioned right of action text or below
- Unread items (notification variant): background-neutral-1 or left border in primary color
- Connector line: border-left on the avatar column, color neutral-3

## Data Patterns

- Data source: activity/event records with actor, action type, target entity, timestamp, and optional detail text
- Default sort: newest first (descending timestamp)
- Pagination: load 20-50 at a time, "Load more" at bottom
- Real-time updates: new entries prepended to top with subtle animation (slide-in)

## Responsive Behavior

- Desktop/Tablet: single-column stream with avatars and connector line
- Phone: simplified — smaller avatars or icons only, shortened action text, timestamps abbreviated ("2h ago")
