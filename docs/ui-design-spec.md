# UI Design Specification — list-mate

**Version**: 1.0
**Date**: 2026-05-18
**Based on**: docs/design.md, Iter 1 scope
**Target**: Vue 3 SPA, scoped CSS, responsive (<768px mobile, >=768px desktop)

---

## Table of Contents

1. [Design Foundations](#1-design-foundations)
   - 1.1 Color System
   - 1.2 Typography
   - 1.3 Spacing System
   - 1.4 Shadows and Elevation
   - 1.5 Border Radius
   - 1.6 Icons
2. [Navigation System](#2-navigation-system)
   - 2.1 Mobile Bottom Tab Bar
   - 2.2 Desktop Sidebar
3. [Component Library](#3-component-library)
   - 3.1 Work Card (List View)
   - 3.2 Work Card (Grid View)
   - 3.3 Category Badge
   - 3.4 Status Badge
   - 3.5 Progress Bar
   - 3.6 Progress Display Pattern
   - 3.7 Buttons
   - 3.8 Form Inputs
   - 3.9 Search Bar
   - 3.10 Filter Bar / Tab Bar
   - 3.11 Empty State
   - 3.12 Loading Skeleton
   - 3.13 Page Header
4. [Page Designs](#4-page-designs)
   - 4.1 Work List (`/`)
   - 4.2 Work Detail (`/works/:id`)
   - 4.3 Profile Detail (`/works/:id/profiles/:pid`)
   - 4.4 Search Add (`/search`)
   - 4.5 Manual Add (`/add`)
   - 4.6 Work Edit (`/works/:id/edit`)
   - 4.7 Profile Create/Edit (`/works/:id/profiles/new`, `/works/:id/profiles/:pid/edit`)

---

## 1. Design Foundations

### 1.1 Color System

#### Brand / Category Colors

Each ACGN category has a dedicated accent color used for category badges, active tab indicators, and highlighting.

| Category | Token | Hex | Usage |
|----------|-------|-----|-------|
| Anime | `--c-anime` | `#FF1A5E` (vibrant rose) | Tab active, card border, badge, progress |
| Novel | `--c-novel` | `#3366FF` (vibrant blue) | Same |
| Comic | `--c-comic` | `#00CC66` (vibrant emerald) | Same |
| Game | `--c-game` | `#FF7A00` (warm orange) | Same |

Each category has background and glow variants:
- `--c-anime-bg`: `rgba(255, 26, 94, 0.1)` — for hover/fill backgrounds
- `--c-anime-glow`: `rgba(255, 26, 94, 0.2)` — for card hover glow

#### Status Colors

| Status | Token | Hex | Usage |
|--------|-------|-----|-------|
| Wish | `--s-wish` | `#A39F98` (warm gray) | Stamp badge, icon |
| Watching | `--s-watching` | `#3366FF` (blue) | Same |
| Completed | `--s-completed` | `#00B85A` (green) | Same |
| Paused | `--s-paused` | `#FFB800` (amber) | Same |
| Dropped | `--s-dropped` | `#FF4444` (red) | Same |

#### Neutral / Background Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-primary` | `#F7F5F0` | Page background — warm album paper |
| `--bg-surface` | `#FFFFFF` | Card, modal, dropdown backgrounds |
| `--bg-surface-hover` | `#EFEDE8` | Hover state on list items / cards |
| `--bg-elevated` | `#FFFFFF` | Navigation bars, sticky headers |
| `--bg-input` | `#EFEDE8` | Input field backgrounds |
| `--color-border` | `rgba(0,0,0,0.05)` | Subtle card borders, dividers |

#### Text Hierarchy

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-text-primary` | `#111827` (gray-900) | Primary headings, titles |
| `--color-text-secondary` | `#4b5563` (gray-600) | Body text, descriptions |
| `--color-text-tertiary` | `#9ca3af` (gray-400) | Captions, meta text, placeholders |
| `--color-text-inverse` | `#ffffff` | Text on dark backgrounds |
| `--color-text-link` | `#3b82f6` (blue-500) | Interactive links |

#### Semantic Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-success` | `#22c55e` | Success feedback |
| `--color-warning` | `#f59e0b` | Warning feedback |
| `--color-error` | `#ef4444` | Error feedback |
| `--color-info` | `#3b82f6` | Info feedback |

### 1.2 Typography

#### Font Stack

```css
--font-sans: 'DM Sans', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', 
               Roboto, 'Helvetica Neue', Arial, sans-serif;
```

Primary font is DM Sans, falling back to Noto Sans SC for Chinese characters.

#### Font Scale

| Token | Size | Weight | Line Height | Usage |
|-------|------|--------|-------------|-------|
| `--fs-xs` | 0.75rem (12px) | 400 | 1.4 | Captions, meta text |
| `--fs-sm` | 0.8125rem (13px) | 400 | 1.5 | Secondary body text |
| `--fs-base` | 0.9375rem (15px) | 400 | 1.5 | Primary body text |
| `--fs-lg` | 1.0625rem (17px) | 500 | 1.4 | Card titles, subheadings |
| `--fs-xl` | 1.25rem (20px) | 600 | 1.3 | Section headings |
| `--fs-2xl` | 1.5rem (24px) | 600 | 1.3 | Page titles (desktop) |

Headings use `--color-text-primary`. Body uses `--color-text-secondary`. Captions use `--color-text-tertiary`.

### 1.3 Spacing System

Base unit: 4px. Scale follows a 4px grid.

| Token | Value | Common Usage |
|-------|-------|-------------|
| `--space-1` | 4px (0.25rem) | Micro spacing, icon gaps |
| `--space-2` | 8px (0.5rem) | Tight spacing, badge padding |
| `--space-3` | 12px (0.75rem) | Input padding, small gaps |
| `--space-4` | 16px (1rem) | Card padding, section gaps |
| `--space-5` | 20px (1.25rem) | Comfortable gaps |
| `--space-6` | 24px (1.5rem) | Section margins, card margins |
| `--space-8` | 32px (2rem) | Page padding (desktop) |
| `--space-10` | 40px (2.5rem) | Large section separation |
| `--space-12` | 48px (3rem) | Page top padding |

Responsive page padding:
- Mobile (<768px): 16px (`--space-4`) on each side
- Desktop (>=768px): 32px (`--space-8`) on each side

### 1.4 Shadows and Elevation

| Token | Value | Usage |
|-------|-------|-------|
| `--shadow-sm` | `0 1px 3px rgba(0,0,0,0.04)` | Card resting state |
| `--shadow-md` | `0 8px 24px rgba(0,0,0,0.06)` | Card hover, dropdowns |
| `--shadow-lg` | `0 16px 40px rgba(0,0,0,0.08)` | Modals, bottom sheet |

Cards have resting shadow `--shadow-sm`. On hover (desktop only), cards elevate to `--shadow-md` with `translateY(-2px)` at 200ms ease.

### 1.5 Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sm` | 6px | Small badges, tag chips |
| `--radius-md` | 10px | Cards, inputs, buttons |
| `--radius-lg` | 16px | Modals, large containers |
| `--radius-full` | 9999px | Pill-shaped badges, avatars |

### 1.6 Icons

Use SVG icons from iconfont.cn, stored in `src/assets/icons/`. Navigation icons use `fill="currentColor"` with 1024x1024 viewBox. Required icons for Iter 1:

- `nav-home` — home (收藏页)
- `nav-search` — magnifying glass (搜索)
- `nav-add` — plus (添加)
- `nav-stats` — bar chart (统计)
- `nav-tag` — tag (标签)
- Category icons for card fallback covers (simple SVG paths, not iconfont)

---

## 2. Navigation System

The app uses a responsive dual-navigation pattern: glassmorphism top bar on desktop, glassmorphism bottom tab bar on mobile.

### 2.1 Mobile Bottom Tab Bar (<768px)

```
┌─────────────────────────────────────────────┐
│                                             │
│               PAGE CONTENT                  │
│                                             │
├─────────────────────────────────────────────┤
│  ● 首页  ○ 搜索  ○ ＋  ○ 统计  ○ 标签    │
│  bottom-tab-bar height: 64px               │
│  bg: rgba(255,255,255,0.9), backdrop-filter │
└─────────────────────────────────────────────┘
```

**Structure**:
- Fixed to bottom, `position: fixed; bottom: 0; z-index: 100`
- Height: 64px (includes safe area padding)
- Background: `rgba(255,255,255,0.9)` with `backdrop-filter: blur(18px)`
- Top border: 1px solid `rgba(0,0,0,0.04)`
- Contains 5 tab items, evenly spaced

**Tab Items**:

| Icon | Label | Route |
|------|-------|-------|
| Home (house) | 首页 | `/` |
| Search | 搜索 | `/search` |
| + (FAB button, larger) | 添加 | `/add` |
| Stats (chart) | 统计 | `/stats` (future) |
| Tag | 标签 | `/tags` (future) |

**Active Tab**: Icon filled, label text in `--primary` (warm orange #FF6B35). Inactive: icon in `--text-tertiary`.

**FAB "+" Button**: Central tab item, larger than others. Circle button (52x52px) with warm orange gradient (`linear-gradient(135deg, #FF6B35, #FF8F5E)`), white plus icon, elevated with orange shadow.

**Page content bottom padding**: Must add 80px padding-bottom to account for the fixed tab bar.

### 2.2 Desktop Top Navigation Bar (>=768px)

```
┌─────────────────────────────────────────────────────────────┐
│  [list-mate]    收藏  搜索  添加  统计  标签   (glass bg)  │
│  bg: rgba(255,255,255,0.82), backdrop-filter: blur(20px)  │
└─────────────────────────────────────────────────────────────┘
```

**Structure**:
- Fixed top bar, full width, height 56px
- Background: `rgba(255,255,255,0.82)` with `backdrop-filter: blur(20px)`
- Bottom border: 1px solid `rgba(0,0,0,0.04)`
- Max width: 1400px, centered with padding 0 28px
- Brand "list-mate" on left, nav items to the right
- Hidden on mobile (<768px), only shown on desktop

**Nav Items**:

| Icon | Label | Route |
|------|-------|-------|
| Home | 收藏 | `/` |
| Search | 搜索 | `/search` |
| Plus | 添加 | `/add` |
| Stats | 统计 | `/stats` (future) |
| Tag | 标签 | `/tags` (future) |

**Active nav**: Warm orange text + background (`--primary`), font-weight 600.

```
┌──────────────┬────────────────────────────────┐
│              │                                │
│   SIDEBAR    │         MAIN CONTENT           │
│              │                                │
│  ┌────────┐  │                                │
│  │  LOGO  │  │                                │
│  └────────┘  │                                │
│              │                                │
│  ● 首页     │                                │
│  ○ 搜索     │                                │
│  ○ 添加     │                                │
│  ○ 统计     │                                │
│  ○ 标签     │                                │
│              │                                │
│  ────────   │                                │
│  分类筛选   │                                │
│  ○ 全部     │                                │
│  ○ 动漫     │                                │
│  ○ 小说     │                                │
│  ○ 漫画     │                                │
│  ○ 游戏     │                                │
│              │                                │
├──────────────┴────────────────────────────────┤
│              STATUS BAR (optional)            │
└───────────────────────────────────────────────┘
```

**Structure**:
- Fixed left sidebar, width: 240px (`--sidebar-width`)
- Background: white (`--color-bg-elevated`)
- Right border: 1px solid `--color-border`
- Height: 100vh, `overflow-y: auto`
- Main content area: `margin-left: 240px`

**Sidebar Sections**:

1. **Logo/Header** (top, 56px height): App name "list-mate" in `--fs-xl`, `--color-text-primary`, with a small colored dot or icon. Can be a clickable link to `/`.

2. **Primary Navigation** (menu items):
   - 首页 (`/`) — house icon + label
   - 搜索 (`/search`) — search icon + label
   - 添加 (`/add`) — plus icon + label
   - 统计 (`/stats`) — chart icon + label (grayed out if Iter 3 not done yet)
   - 标签 (`/tags`) — tag icon + label (grayed out if Iter 2 not done yet)

   Each item: height 44px, padding 12px 16px, border-radius 8px, `--fs-base` text. Hover: `--color-bg-hover`. Active: light primary bg (`rgba(59, 130, 246, 0.08)`) + primary text.

3. **Divider**: 1px solid `--color-border`, margin 8px 16px.

4. **Category Filter** (persistent sidebar filter):
   - 全部 — no icon
   - 动漫 — rose dot (8px circle, `--color-anime`)
   - 小说 — blue dot
   - 漫画 — green dot
   - 游戏 — violet dot

   Same styling as nav items. Active category uses the corresponding category color for text and dot.

5. **Footer** (bottom of sidebar):
   - Compact stats: "共 N 部作品" in `--fs-xs`, `--color-text-tertiary`
   - Version info (tiny)

**Active state communication**: When on the Work List page with a category filter, the sidebar category that matches the current filter is highlighted. When on other pages (Search, Add), the corresponding nav item is highlighted.

---

## 3. Component Library

### 3.1 Work Card — List View

Default view mode. Used on the Work List page.

```
┌──────────────────────────────────────────────────┐
│ ┌────────┐                                       │
│ │        │  Title (作品名)                    │
│ │ Cover  │  Category Badge  |  Status Badge    │
│ │ 80x112 │                                       │
│ │        │  Progress: EP 12/24  ██████░░░░     │
│ └────────┘  last updated: 2026-05-18            │
└──────────────────────────────────────────────────┘
```

**Specifications**:
- Card: white bg, `--shadow-sm`, `--radius-md`, padding 12px
- Cover thumbnail: 80px width, 112px height (2:2.8 ratio, roughly standard book/BD cover ratio)
- Border radius on cover: 4px. If no cover image, show a placeholder box with category-colored background and a generic icon.
- Title: `--fs-base`, weight 600, `--color-text-primary`, single-line truncation with ellipsis
- Meta row: Category badge + Status badge, spaced with 8px gap
- Progress row: Progress text (`--fs-sm`, `--color-text-secondary`) + progress bar
- Timestamp: `--fs-xs`, `--color-text-tertiary`
- Hover (desktop only): `--shadow-md` elevation, slight lift

**Click behavior**: Entire card is clickable, navigates to `/works/:id`.

### 3.2 Work Card — Grid View

Gacha collection / trading card visual language. Default on desktop.

```
┌────────────────────┐  ┌────────────────────┐
│ ┌──────────────┐  │  │ ┌──────────────┐  │
│ │              │  │  │ │              │  │
│ │   Cover      │  │  │ │   Cover      │  │
│ │  (gradient   │  │  │ │  (gradient   │  │
│ │   fallback)  │  │  │ │   fallback)  │  │
│ │              │  │  │ │              │  │
│ │ [想看] ────┐ │  │  │ │ [在看] ────┐ │  │
│ │ ██████░ 8% │ │  │  │ │ ████████ 50%│ │  │
│ └──────────────┘  │  │ └──────────────┘  │
│  作品名称         │  │  作品名称         │
└────────────────────┘  └────────────────────┘
```

**Specifications**:
- Card: white bg, `--radius-md`, `overflow: hidden`
- Card frame uses multi-layer box-shadow for card sleeper effect (removable per preference)
- Cover area: margin 5px from card edge, 3:4 aspect ratio, `--radius-sm` inset shadow
- Cover background: category gradient (e.g., `linear-gradient(135deg, #FF1A5E, #FF6B8A)` for anime)
- Category icon overlay centered on cover, translucent white
- Status stamp: top-right corner, rotated 3°, colored background, white text (e.g., 想看/在看/看完/暂停/弃了)
- EXP bar overlay at cover bottom: gradient fill with shimmer animation, shows progress text
- Holo shimmer on hover: diagonal white sweep across card with 0.6s transition
- Title: `--fs-sm`, weight 700, center-aligned, single-line truncation, padding 8px 10px 10px
- Hover: translateY(-8px) scale(1.02) + category color glow shadow
- Animations: `card-deal` entrance (staggered), `exp-shimmer` on progress bar, `stamp-in` on badge

**Grid column counts**:
- Mobile (<768px): 2 columns, gap 12px
- Desktop (768-1024px): 3 columns, gap 16px  
- Desktop (>1024px): 4 columns, gap 16px

### 3.3 Category Badge

Small pill badge indicating the work category.

```
 ┌──────────┐
 │  动漫    │  ← anime: rose bg + rose text
 └──────────┘
 ┌──────────┐
 │  小说    │  ← novel: blue bg + blue text
 └──────────┘
 ┌──────────┐
 │  漫画    │  ← comic: green bg + green text
 └──────────┘
 ┌──────────┐
 │  游戏    │  ← game: violet bg + violet text
 └──────────┘
```

**Specifications**:
- Height: 22px, horizontal padding: 8px
- Border-radius: `--radius-sm`
- Background: category color at 12% opacity
- Text color: category color at 100%
- Font: `--fs-xs`, weight 500
- Text: Chinese label: 动漫 / 小说 / 漫画 / 游戏

### 3.4 Status Badge

Rotating stamp-style badge indicating profile status.

```
 ┌──────────┐
 │  想看    │  ← wish: warm gray (#A39F98) stamp
 └──────────┘
 ┌──────────┐
 │  在看    │  ← watching: blue (#3366FF) stamp
 └──────────┘
 ┌──────────┐
 │  看完    │  ← completed: green (#00B85A) stamp
 └──────────┘
 ┌──────────┐
 │  暂停    │  ← paused: amber (#FFB800) stamp
 └──────────┘
 ┌──────────┐
 │  弃了    │  ← dropped: red (#FF4444) stamp
 └──────────┘
```

**Specifications**:
- Height: 20px, horizontal padding: 7px
- Border-radius: 2px (sharp corners for stamp feel)
- Background: status color at 100%
- Text color: white
- Font: 10px, weight 800, letter-spacing 0.8px
- Transform: `rotate(2deg)` for slight tilt
- Box-shadow: `0 1px 4px rgba(0,0,0,0.12)` for depth
- Animation: `stamp-in` entrance (pop in with slight overshoot)
- Labels: 想看 / 在看 / 看完 / 暂停 / 弃了

### 3.5 Progress Bar

EXP-style progress bar with gradient fill and shimmer animation.

```
EP 12/24     ████████░░░░░░░░  50%
[label]      [bar with shimmer]  [% text]
```

**Specifications**:
- Container height: 6px
- Bar background: `rgba(0,0,0,0.04)`, border `rgba(0,0,0,0.03)`, `border-radius: 3px`
- Filled portion: category gradient (e.g., `linear-gradient(90deg, #FF1A5E, #FF6B8A)`), with shine animation
- Shine: `@keyframes exp-shimmer` — diagonal sweep overlay, 2.5s infinite
- Transition: width change at 0.4s cubic-bezier(.2,0,0,1)
- Label: 11px, weight 700, `--text-tertiary`, tabular-nums for alignment
- Game category shows percentage only (e.g., "45%")
- Units: anime→full format, novel→full format, comic→full format, game→percentage

### 3.6 Progress Display Pattern

Various forms depending on context:

```
Pattern 1: "EP 12 / 24"     — standard, has total
Pattern 2: "EP 12"           — ongoing, no total
Pattern 3: "Chapter 5 / ?"   — ongoing, total unknown
Pattern 4: "已完成"           — completed state
Pattern 5: "12 / 24 (50%)"   — with percentage (desktop detail)
```

Unit labels by category:
- Anime: "EP"
- Novel: "Chapter"
- Comic: "Volume" (or "话" if preferred)
- Game: "%" (percent format, e.g., "45%")

### 3.7 Buttons

**Primary Button**:
- Height: 40px (default) / 48px (large) / 32px (small)
- Padding horizontal: 16px (default) / 20px (large) / 12px (small)
- Background: `#3b82f6` (blue-500)
- Text: white, `--fs-sm` weight 500 (default) / `--fs-base` weight 500 (large)
- Border-radius: `--radius-md`
- Hover: `#2563eb` (blue-600)
- Active: `#1d4ed8` (blue-700)
- Disabled: opacity 0.5, cursor not-allowed

**Secondary Button** (outline):
- Same dimensions
- Background: transparent
- Border: 1px solid `--color-border`
- Text: `--color-text-primary`
- Hover: `--color-bg-hover`
- Disabled: opacity 0.5

**Ghost Button** (text only):
- Same dimensions
- Background: transparent
- Text: `--color-text-secondary`
- Hover: `--color-bg-hover`
- No border, no shadow

**Icon Button** (circular, for increment/decrement, back, etc.):
- Size: 36px (default) / 44px (large for touch targets)
- Border-radius: 50%
- Background: transparent or `--color-bg-hover` on hover
- Icon: 20px, `--color-text-secondary`

**Increment Button** (for quick progress +1):
- Large touch target: 48x48px minimum
- Primary blue background, white "+" icon
- Rounded square or circle
- Used on Profile Detail page for "one more episode"

### 3.8 Form Inputs

**Text Input**:
- Height: 44px
- Padding: 12px 16px
- Background: `--color-bg-input`
- Border: 1px solid `--color-border`, `--radius-md`
- Text: `--fs-base`, `--color-text-primary`
- Placeholder: `--color-text-tertiary`
- Focus: border `--color-info`, inset glow box-shadow `0 0 0 3px rgba(59,130,246,0.1)`
- Error: border `--color-error`, glow `rgba(239,68,68,0.1)`

**Textarea**:
- Same as text input but height auto (min 100px)
- Used for review text
- Resize: vertical only

**Select / Dropdown** (native `<select>` styled):
- Same dimensions and styling as text input
- Custom chevron-down icon on the right

**Number Input** (for progress_value):
- Standard text input with `type="number"` or custom stepper
- Optional: +/- buttons flanking the input (for quick adjust)

**Label**:
- `--fs-sm`, weight 500, `--color-text-primary`
- 8px margin-bottom from input
- Optional: `<label>` element for accessibility

### 3.9 Search Bar

Used on Work List page (inline filter) and Search Add page.

```
┌──────────────────────────────────────────────┐
│ 🔍 搜索作品名称...                           │
└──────────────────────────────────────────────┘
```

**Specifications**:
- Height: 40px
- Background: `--color-bg-input`
- Border: none or 1px solid `--color-border`
- Border-radius: `--radius-md` or `--radius-full` for iOS-style
- Left icon: magnifying glass (16px), `--color-text-tertiary`
- Padding: 10px 16px
- Clear button (X) appears on the right when text is entered
- Focus: same as text input
- On mobile, can expand to full width or be inside a bar

### 3.10 Filter Bar / Tab Bar

Horizontal scrollable bar for category/status filtering.

Mobile:
```
← [全部] [动漫] [小说] [漫画] [游戏] →  (horizontal scroll)
```

Desktop:
```
[全部] [动漫] [小说] [漫画] [游戏]   (centered or left-aligned, no scroll needed)
```

**Specifications**:
- Container: full width, `overflow-x: auto` on mobile, `overflow: visible` on desktop
- Gap between items: 8px
- Each tab: pill-shaped (`--radius-full`), height 34px, `--fs-sm`, padding 12px 16px
- Inactive: white bg, 1px solid `--color-border`, `--color-text-secondary`
- Active: category color bg, white text
- Active when no category: use `#3b82f6` (blue) as default active indicator for "全部"
- Horizontal scroll with hidden scrollbar on mobile (use `-webkit-scrollbar: none`)

**Status Filter** (secondary filter row):
Same pattern but smaller tabs (height 30px, `--fs-xs`, padding 8px 12px). Only shows statuses that have results, or shows all 5 statuses. Placed below category tabs.

### 3.11 Empty State

Used when no works match the current filter or when the library is empty.

```
        ┌──────────────────┐
        │                  │
        │    📭 (icon)     │  ← large centered icon, 64px
        │                  │
        │ 还没有作品       │  ← heading, --fs-lg, --color-text-primary
        │ 点击下方添加你的
        │ 第一部作品吧     │  ← description, --fs-base, --color-text-secondary
        │                  │
        │ ┌────────────┐  │
        │ │  + 添加作品 │  │  ← primary button
        │ └────────────┘  │
        │                  │
        └──────────────────┘
```

**Text by context**:
- Empty library: "还没有作品" / "点击下方添加你的第一部作品"
- No search results: "没有找到相关作品" / "试试其他关键词"
- Filtered empty: "没有符合条件的作品" / "试试调整筛选条件"

### 3.12 Loading Skeleton

Used when data is being fetched.

```
┌──────────────────────────────────────────────┐
│ ┌────────┐                                   │
│ │ ████  │  █████████████████████████████    │
│ │ ████  │  █████████████████████████████    │
│ │ ██    │  ██████████████                   │
│ │ ██    │  █████████████████████            │
│ └────────┘  ████████████                    │
└──────────────────────────────────────────────┘
```

Use animated shimmer placeholders (linear gradient sweep from gray-100 to gray-200 and back). Match the dimensions of actual content: 80x112 cover placeholder, 2-3 line text placeholders, status badge placeholder (40x22 pill).

### 3.13 Page Header

Consistent top bar for each page.

```
Mobile:
┌──────────────────────────────────────────────┐
│ ← 返回         页面标题            ··· 更多 │
└──────────────────────────────────────────────┘

Desktop:
┌──────────────────────────────────────────────┐
│  页面标题                        [action btn] │
└──────────────────────────────────────────────┘
```

**Specifications**:
- Height: 56px (mobile) / 64px (desktop)
- Background: white with `position: sticky; top: 0; z-index: 10`
- Bottom border: 1px solid `--color-border-light`
- Padding: 16px horizontal
- Back button: 36px icon button on left (mobile only)
- Title: `--fs-xl`, weight 600, single-line truncation
- Action buttons: right-aligned (optional)

On mobile, the page header is sticky. On desktop, it can be sticky or static (sidebar already provides persistent navigation context).

---

## 4. Page Designs

### 4.1 Work List (`/`)

The landing page and primary interface. Shows all works with filters, search, and view mode toggle.

#### Mobile Layout (<768px)

```
┌──────────────────────────────────────────────┐
│  list-mate                          ○ ○ ☰  │  ← Page header (sticky)
├──────────────────────────────────────────────┤
│  🔍 搜索作品...                       ⊞⊟   │  ← Search bar + view toggle
├──────────────────────────────────────────────┤
│  [全部] [动漫] [小说] [漫画] [游戏]         │  ← Category tabs (scrollable)
│  [全部] [想看] [在看] [看完] [暂停] [弃了]  │  ← Status filter (scrollable)
├──────────────────────────────────────────────┤
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ ████████  Title                        │  │
│  │ ████████  动漫 | 在看                  │  │  ← Card item
│  │ ████████  EP 12/24  ██████░░░░░░      │  │
│  │           2026-05-18                   │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ Cover    Title 2                       │  │
│  │  80x112  Novel | 想看                  │  │
│  │          EP --                         │  │
│  └────────────────────────────────────────┘  │
│                                              │
│                    ...                        │
│                                              │
│  (infinite scroll or "load more" button)     │
│                                              │
│                                              │
├──────────────────────────────────────────────┤
│     ● Home  ○ 搜索 ○ ＋  ○ 统计 ○ 更多    │  ← Bottom tab bar (fixed)
└──────────────────────────────────────────────┘
```

**Behavior**:
- Default view: List view (first load). User preference can be remembered in localStorage.
- View toggle: Grid/List icon button in the header area. Active icon styled as filled.
- Search bar: As user types, debounce 300ms, then filter results by title match. Show a clear (X) button when search has text.
- Category tabs: Selecting a tab filters works by category. Tab underline/category color indicator follows selection.
- Status filter: Additional filter row. "全部" is default. Can combine with category filter.
- Empty state: Shown when no works match filters.
- Loading: Skeleton placeholders for first load. Subsequent fetches show a small spinner at the bottom.

#### Desktop Layout (>=768px)

```
┌──────────────┬───────────────────────────────────┐
│              │  list-mate               ⊞⊟     │  ← Page header (sticky)
│   SIDEBAR    ├───────────────────────────────────┤
│              │  🔍 搜索作品...                   │  ← Search bar
│   ● 首页    ├───────────────────────────────────┤
│   ○ 搜索    │  [全部] [动漫] [小说] [漫画] [游戏] │  ← Category tabs
│   ○ 添加    │  [全部] [想看] [在看] [看完] [暂停] [弃了]│
│   ○ 统计    ├───────────────────────────────────┤
│   ○ 标签    │  ┌────────┐  ┌────────┐           │
│              │  │ Cover  │  │ Cover  │           │  ← Grid view (default)
│   ───────   │  │ Title  │  │ Title  │           │     on desktop
│   分类筛选  │  │ Status │  │ Status │           │
│   ● 全部    │  │ EP 12  │  │ EP 12  │           │
│   ○ 动漫    │  └────────┘  └────────┘           │
│   ○ 小说    │                                     │
│   ○ 漫画    │  ┌────────┐  ┌────────┐           │
│   ○ 游戏    │  │        │  │        │           │
│              │  │ ...    │  │ ...    │           │
│              │  └────────┘  └────────┘           │
│              │                                     │
└──────────────┴───────────────────────────────────┘
```

**Desktop differences**:
- Default view: Grid (3-4 columns). Users can toggle to list view.
- Sidebar filters replace the mobile horizontal scroll for categories — clicking a category in the sidebar filters the list AND highlights that category.
- More whitespace, larger covers.
- Pagination: "Load more" button at the bottom, or infinite scroll.
- Tooltips on hover for long titles (optional).

#### Grid vs List View Toggle

```
Toggle button group:
┌──┬──┐
│⊞ │⊟ │  ← two buttons, active one filled
└──┴──┘
```

- Left button (grid): 4 small squares icon
- Right button (list): 3 horizontal lines icon
- Active state: primary blue bg, white icon. Inactive: gray bg or transparent.

#### View Toggle: on the work list page header row

On mobile, place the toggle inline with the search bar (right side). On desktop, place it in the page header area.

---

### 4.2 Work Detail (`/works/:id`)

Shows full work information and all associated profiles.

#### Mobile Layout

```
┌──────────────────────────────────────────────┐
│ ← 返回                          ✎ 编辑  ··· │  ← Page header (sticky)
├──────────────────────────────────────────────┤
│                                              │
│  ┌────────────────────────────────────┐      │
│  │                                    │      │
│  │          Cover Image               │      │  ← Full-width cover section
│  │          200x280                   │      │
│  │          centered                  │      │
│  │                                    │      │
│  └────────────────────────────────────┘      │
│                                              │
│  作品名称 (Title)                             │
│  动漫 | 在看                                 │  ← Category + Status badges
│                                              │
│  总进度: EP 24                               │
│                                              │
│  ┌─ 基本信息 ─────────────────────────────┐ │
│  │  分类: 动漫 · TV                       │ │  ← Info card
│  │  进度单位: EP                          │ │
│  │  来源: Bangumi                         │ │
│  │  添加于: 2026-05-18                   │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌─ 进度配置 ────────────────────────────┐ │
│  │                                         │ │
│  │  ┌────────────────────────────────┐    │ │
│  │  │ 默认                    ▶     │    │ │  ← Profile list items
│  │  │ EP 12/24  ██████░░░░          │    │ │
│  │  │ 在看      评分: 7            │    │ │
│  │  └────────────────────────────────┘    │ │
│  │                                         │ │
│  │  ┌────────────────────────────────┐    │ │
│  │  │ 二刷                    ▶     │    │ │
│  │  │ EP 5/24   ██░░░░░░░░░░        │    │ │
│  │  │ 在看                            │    │ │
│  │  └────────────────────────────────┘    │ │
│  │                                         │ │
│  │  [ + 新增配置 ]                        │ │  ← Add profile button
│  └─────────────────────────────────────────┘ │
│                                              │
│  ┌─ 备注 / 简介 ─────────────────────────┐ │
│  │                                         │ │
│  │  (简介内容来自 Bangumi 或用户填写)     │ │
│  │                                         │ │
│  └─────────────────────────────────────────┘ │
│                                              │
├──────────────────────────────────────────────┤
│              Bottom Tab Bar                  │
└──────────────────────────────────────────────┘
```

**Cover Section**:
- Full-width container, white background
- Cover image: max-width 200px, height auto, centered, aspect-ratio 5:7
- Placeholder: same dimensions, category-colored background with icon
- Bottom margin 16px

**Title**:
- `--fs-2xl`, weight 700, `--color-text-primary`
- Margin 0 0 8px 0

**Badge Row**:
- Category badge + Status badge, 8px gap, margin-bottom 16px

**Info Card**:
- White card, `--shadow-sm`, `--radius-md`, padding 16px, margin-bottom 16px
- Label-value pairs stacked vertically
- Label: `--fs-sm`, weight 500, `--color-text-tertiary`
- Value: `--fs-base`, `--color-text-primary`
- Gap between rows: 10px

**Profile List Section**:
- Header: "进度配置" in `--fs-lg`, weight 600, margin-bottom 12px
- Each profile card: white bg, `--shadow-sm`, `--radius-md`, padding 14px 16px, margin-bottom 8px
- Tap anywhere on a profile card -> navigate to Profile Detail
- Profile name: `--fs-base`, weight 600
- Progress display: `--fs-sm`, `--color-text-secondary`
- Progress bar: shown only when total > 0
- Status and rating display inline: "在看 · 评分 7"
- Right arrow (chevron) indicates tappable
- "+ 新增配置" button: ghost button at bottom of section

**Description / Summary Section**:
- Header: "简介" in `--fs-lg`, weight 600, margin-bottom 8px
- Body: `--fs-base`, `--color-text-secondary`, line-height 1.7
- If no description: "暂无简介" in `--color-text-tertiary`

#### Desktop Layout

```
┌──────────────┬───────────────────────────────────┐
│              │  ← 返回  作品详情    ✎ 编辑  ···│
│   SIDEBAR   ├───────────────────────────────────┤
│              │  ┌─────────┐                      │
│              │  │         │  ┌──────────────┐   │
│              │  │  Cover  │  │  Title        │   │  ← Two-column layout
│              │  │  220x310│  │  动漫 | 在看  │   │
│              │  │         │  │               │   │
│              │  └─────────┘  │  总进度: 24EP │   │
│              │               │               │   │
│              │               │  ┌─ 基本信息 ┐│   │
│              │               │  │ ...       ││   │
│              │               │  └───────────┘│   │
│              │               └──────────────┘   │
│              │                                   │
│              │  ┌─ 进度配置 ──────────────────┐  │
│              │  │  默认     EP 12/24  ██████  │  │
│              │  │  二刷     EP 5/24  ██░░░░  │  │
│              │  │  [ + 新增配置 ]            │  │
│              │  └────────────────────────────┘  │
│              │                                   │
│              │  ┌─ 简介 ──────────────────────┐  │
│              │  │  ...                        │  │
│              │  └────────────────────────────┘  │
└──────────────┴───────────────────────────────────┘
```

**Desktop differences**:
- Two-column layout: cover on left (fixed width 220px), info on right
- Cover: fixed width, sticky within its column on scroll
- Profile list: same but more spacious
- Edit button: prominently visible in header (primary button, not hidden behind menu)

---

### 4.3 Profile Detail (`/works/:id/profiles/:pid`)

Dedicated page for updating a single profile's progress, status, rating, and review.

#### Mobile Layout

```
┌──────────────────────────────────────────────┐
│ ← 返回          进度详情             ··· 更多 │  ← Page header
├──────────────────────────────────────────────┤
│                                              │
│  ┌─ 作品信息 ─────────────────────────────┐ │
│  │  ┌──────┐                               │ │
│  │  │ Cover│  作品名称                     │ │  ← Compact work info
│  │  │ 48x68│  动漫                         │ │     (tappable -> work detail)
│  │  └──────┘                               │ │
│  └─────────────────────────────────────────┘ │
│                                              │
│  配置名称: 默认                              │  ← Profile name heading
│                                              │
│  ┌─ 进度 ─────────────────────────────────┐ │
│  │                                         │ │
│  │     第 12 集 / 共 24 集                │ │  ← Large progress display
│  │     ████████████████████░░░░░░  50%    │ │
│  │                                         │ │
│  │         [- ]  [  12  ]  [ + ]          │ │  ← Stepper controls
│  │                                         │ │
│  │     ┌────────────────────────┐          │ │
│  │     │    更新进度            │          │ │  ← Save button (primary)
│  │     └────────────────────────┘          │ │
│  │                                         │ │
│  └─────────────────────────────────────────┘ │
│                                              │
│  ┌─ 状态 ─────────────────────────────────┐ │
│  │                                         │ │
│  │  [想看] [在看●] [看完] [暂停] [弃了]  │ │  ← Status selector
│  │                                         │ │  (horizontal pills, one active)
│  └─────────────────────────────────────────┘ │
│                                              │
│  ┌─ 评分 ─────────────────────────────────┐ │
│  │                                         │ │
│  │  ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆                  │ │  ← 10 stars in a row
│  │        当前: 7/10                       │ │
│  │                                         │ │
│  └─────────────────────────────────────────┘ │
│                                              │
│  ┌─ 评价 ─────────────────────────────────┐ │
│  │                                         │ │
│  │  ┌────────────────────────────────┐    │ │
│  │  │ 输入你的评价...                │    │ │  ← Textarea
│  │  │                                │    │ │
│  │  └────────────────────────────────┘    │ │
│  │                                         │ │
│  └─────────────────────────────────────────┘ │
│                                              │
│  [保存]                                      │  ← Bottom save button
│                                              │
├──────────────────────────────────────────────┤
│              Bottom Tab Bar                  │
└──────────────────────────────────────────────┘
```

**Work Info Strip**:
- Compact card linking back to work detail
- Small cover (48x68) + title + category badge
- Tapping navigates to `/works/:id`

**Profile Name**:
- `--fs-xl`, weight 600, `--color-text-primary`
- Below work info, above progress section

**Progress Section** (most prominent):
- Large progress text centered: `--fs-2xl`, weight 700
- Progress bar: full width of section
- Stepper: centered row with [-], number input, [+]
  - [-] and [+] buttons: 44x44px circular buttons, blue bg, white icon
  - Number input: 64px wide, centered text, `--fs-xl`, weight 600
  - Press-and-hold on +/- should auto-increment/decrement (optional, nice touch)
  - Min value: 0 (or current completed max). Max value: total (if set)
- "更新进度" button: records the current progress (if auto-save is not used)

**Auto-save consideration**: Consider auto-saving the progress step when user taps "+" or "-", eliminating the save button. This makes the "one tap per episode" workflow smooth. The save button would then only be needed for the larger form (status/rating/review).

**Status Selector**:
- Horizontal row of pill buttons
- Currently selected status: filled with that status color, white text
- Inactive: outline style, `--color-text-secondary`
- Tapping a status immediately selects it (auto-save or require save confirmation)

**Rating System**:
- 10 stars in a row (5 stars × 2 halves, or 10 full small stars)
- Each star: 24x24px, tappable
- Filled star: amber `#f59e0b`. Empty star: `#e5e7eb`
- Hover/focus effect: stars light up on hover (desktop)
- Below stars: text showing "当前: 7/10" or "未评分"
- Alternative: use a dropdown/select for 0-10 (easier for mobile precision)

**Review Textarea**:
- Full width, min-height 120px
- Placeholder: "写下你的评价..."
- Character count optional (not critical for personal tool)

**Save Button**:
- Full-width primary button at the bottom of the form
- On mobile: sticky at bottom, just above the tab bar (or inline at page end)
- On desktop: inline at the bottom of the section, not full-width

#### Desktop Layout

```
┌──────────────┬───────────────────────────────────┐
│              │  ← 返回  进度详情    ··· 更多    │
│   SIDEBAR   ├───────────────────────────────────┤
│              │  ┌──────┬──────────────────┐     │
│              │  │Cover │ 作品名称          │     │
│              │  │48x68 │ 动漫              │     │
│              │  └──────┴──────────────────┘     │
│              │                                   │
│              │  配置名称: 默认                    │
│              │                                   │
│              │  ┌─ 左栏 ──┐ ┌─ 右栏 ──┐       │
│              │  │ 进度    │ │ 状态    │       │
│              │  │ EP 12/24│ │ ○想看    │       │
│              │  │ ██████  │ │ ●在看   │       │
│              │  │ [-] []+ │ │ ○看完   │       │
│              │  │         │ │ ○暂停   │       │
│              │  │         │ │ ○弃了   │       │
│              │  │         │ │         │       │
│              │  │         │ │ 评分    │       │
│              │  │         │ │ ☆☆☆☆☆  │       │
│              │  │         │ │ ☆☆☆☆☆  │       │
│              │  │         │ │         │       │
│              │  │         │ │ 评价    │       │
│              │  │         │ │ [textarea]│     │
│              │  └─────────┘ └─────────┘       │
│              │                                   │
│              │  [保存]                           │
└──────────────┴───────────────────────────────────┘
```

**Desktop differences**:
- Two-column layout: progress controls on left, status/rating/review on right
- Wider, more comfortable form
- Profile name editable inline or via separate edit page

---

### 4.4 Search Add (`/search`)

Search Bangumi, preview results, then fill form and save.

#### Mobile Layout

```
┌──────────────────────────────────────────────┐
│ ← 返回         搜索添加                      │  ← Page header
├──────────────────────────────────────────────┤
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ 🔍 搜索作品名称或 Bangumi ID...        │  │  ← Search input (prominent)
│  └────────────────────────────────────────┘  │
│                                              │
│  ┌─ 搜索结果 ────────────────────────────┐  │
│  │                                         │  │
│  │  ┌────────────────────────────────┐    │  │
│  │  │ ┌────┐ Title (2024)           │    │  │  ← Search result item
│  │  │ │    │ 动漫 · TV · 24EP       │    │  │
│  │  │ │cover│ Rating: 7.8           │    │  │
│  │  │ │48x68│ [选择]                 │    │  │
│  │  │ └────┘                        │    │  │
│  │  └────────────────────────────────┘    │  │
│  │                                         │  │
│  │  ┌────────────────────────────────┐    │  │
│  │  │ ┌────┐ Title 2                │    │  │
│  │  │ │    │ 小说 · 轻小说 · 5卷    │    │  │
│  │  │ │    │ [选择]                 │    │  │
│  │  │ └────┘                        │    │  │
│  │  └────────────────────────────────┘    │  │
│  │                                         │  │
│  └─────────────────────────────────────────┘  │
│                                              │
│  ┌─ 手动添加 ─────────────────────────────┐  │
│  │  搜不到？点击这里手动填写               │  │  ← Link to /add
│  └─────────────────────────────────────────┘  │
│                                              │
│  (After selecting a result, form appears)     │
│                                              │
│  ┌─ 作品信息 ─────────────────────────────┐  │
│  │  标题: [________________________]      │  │  ← Pre-filled form
│  │  分类: [动漫 ▼]                        │  │
│  │  子分类: [TV ▼]                       │  │
│  │  总进度: [24]  单位: [EP ▼]           │  │
│  │  来源: ● Bangumi  ○ 手动              │  │
│  │                                         │  │
│  │  ┌──────────────────────────────┐      │  │
│  │  │     保存                     │      │  │  ← Primary save button
│  │  └──────────────────────────────┘      │  │
│  └─────────────────────────────────────────┘  │
│                                              │
├──────────────────────────────────────────────┤
│              Bottom Tab Bar                  │
└──────────────────────────────────────────────┘
```

**Search Input**:
- Large, prominent, auto-focused on page load
- Debounce 400ms before triggering API search
- Loading spinner inside input while searching
- Clear button (X) to reset

**Search Results List**:
- Appears after user types at least 2 characters
- Each result item: horizontal layout with small cover (48x68), title, meta info
- "选择" button or tap-on-row to select
- Selected item gets a highlight border or checkmark

**Result Item Details**:
- Cover thumbnail: 48x68, border-radius 4px
- Title: `--fs-base`, weight 600, single-line truncation
- Meta: category badge + sub_category + total (e.g., "动漫 · TV · 24EP")
- Rating: Bangumi rating shown as "7.8" in `--fs-sm`, `--color-text-secondary`
- Year: shown in parentheses after title if available

**After Selection**:
- Results list collapses (or reduces to just the selected item)
- Form appears below with fields pre-filled from Bangumi data
- Form is fully editable (user can override any field)
- "来源" shows as "Bangumi" with the bangumi_id
- "保存" creates the Work + a default Profile ("默认") with status "想看"

**Manual Add Fallback**:
- Link below search results: "搜不到? 点此手动填写" -> navigates to `/add`
- If user navigates to `/add` from here, they should have the category pre-set matching whatever they were searching for

#### Desktop Layout

```
┌──────────────┬───────────────────────────────────┐
│              │  ← 返回         搜索添加          │
│   SIDEBAR   ├───────────────────────────────────┤
│              │  ┌────────────────────────┐       │
│              │  │ 🔍 搜索作品名称...     │       │
│              │  └────────────────────────┘       │
│              │                                   │
│              │  ┌─ 搜索结果 ──┬─ 填表 ──┐      │
│              │  │ Result 1    │ Title   │      │  ← Side-by-side
│              │  │ Result 2    │ Category│      │
│              │  │ Result 3    │ Total   │      │
│              │  │ Result 4    │ ...     │      │
│              │  │ Result 5    │ [保存]  │      │
│              │  └─────────────┴─────────┘      │
│              │                                   │
│              │  ┌────────────────────────────┐   │
│              │  │ 搜不到？手动添加           │   │
│              │  └────────────────────────────┘   │
└──────────────┴───────────────────────────────────┘
```

**Desktop differences**:
- Two-panel layout: search results on left (scrollable, ~40% width), form on right (~60% width)
- Selecting a result fills the right panel form instantly
- This side-by-side approach makes it easy to compare results and quickly fill

---

### 4.5 Manual Add (`/add`)

Form to manually enter all work fields. No search step.

#### Mobile Layout

```
┌──────────────────────────────────────────────┐
│ ← 返回         手动添加                      │  ← Page header
├──────────────────────────────────────────────┤
│                                              │
│  ┌─ 作品信息 ─────────────────────────────┐ │
│  │  封面图片                               │ │
│  │  ┌────────────────────────────────┐    │ │
│  │  │     点击上传封面图片           │    │ │  ← Cover upload area
│  │  │     (or use Bangumi URL)      │    │ │
│  │  │     ┌────────┐               │    │ │
│  │  │     │  📷   │               │    │ │
│  │  │     │  添加  │               │    │ │
│  │  │     │  封面  │               │    │ │
│  │  │     └────────┘               │    │ │
│  │  └────────────────────────────────┘    │ │
│  │                                         │ │
│  │  标题 *                               │ │
│  │  ┌────────────────────────────────┐    │ │
│  │  │                                 │    │ │
│  │  └────────────────────────────────┘    │ │
│  │                                         │ │
│  │  分类 *                               │ │
│  │  ┌────────────────────────────────┐    │ │
│  │  │ 请选择  ▼                      │    │ │  ← Native select
│  │  └────────────────────────────────┘    │ │
│  │                                         │ │
│  │  子分类                                │ │
│  │  ┌────────────────────────────────┐    │ │
│  │  │ 请选择  ▼                      │    │ │
│  │  └────────────────────────────────┘    │ │
│  │                                         │ │
│  │  总进度（留空表示连载中/未知）          │ │
│  │  ┌────────────┐          ┌──────────┐ │ │
│  │  │ 24         │   集     │  EP ▼   │ │ │  ← Number + unit
│  │  └────────────┘          └──────────┘ │ │
│  │                                         │ │
│  │  封面 URL（可选，Bangumi 图片链接）    │ │
│  │  ┌────────────────────────────────┐    │ │
│  │  │ https://...                   │    │ │
│  │  └────────────────────────────────┘    │ │
│  │                                         │ │
│  │  简介 / 备注                           │ │
│  │  ┌────────────────────────────────┐    │ │
│  │  │                                 │    │ │
│  │  │                                 │    │ │
│  │  └────────────────────────────────┘    │ │
│  │                                         │ │
│  │  ┌──────────────────────────────┐      │ │
│  │  │     保存                     │      │ │  ← Primary button
│  │  └──────────────────────────────┘      │ │
│  │                                         │ │
│  └─────────────────────────────────────────┘ │
│                                              │
├──────────────────────────────────────────────┤
│              Bottom Tab Bar                  │
└──────────────────────────────────────────────┘
```

**Form Fields**:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| 标题 | Text input | Yes | Max 200 chars |
| 分类 | Native `<select>` | Yes | Options: 动漫/小说/漫画/游戏 |
| 子分类 | Native `<select>` | No | Depends on category (see below) |
| 总进度 | Number input | No | Nullable, placeholder "连载中留空" |
| 进度单位 | Native `<select>` | Auto | Default depends on category |
| 封面图片 | Upload area + URL text input | No | Iter 4 feature; Iter 1: URL only |
| 封面 URL | Text input | No | For Bangumi cover link |
| 简介 | Textarea | No | Max 1000 chars |

**Sub-category options by category**:
- 动漫: TV / 剧场版 / OVA / WEB / 其他
- 小说: 轻小说 / 网络小说 / 其他
- 漫画: 漫画 / 条漫 / 其他
- 游戏: 单机 / 手游 / 主机 / 网游 / 其他

**Progress unit auto-selection**:
- 动漫: EP
- 小说: Chapter
- 漫画: Volume (or 话)
- 游戏: Percent

Users can override the unit if needed, but the default is set when category is chosen.

**Cover Upload Area**:
- Dotted border, 120x168px, centered in its container
- Camera icon placeholder
- "点击添加封面" text
- For Iter 1: the area can accept a URL paste or be replaced by the "封面 URL" text field
- For Iter 4: file upload support

**Save Behavior**:
- Validates required fields (title, category)
- Creates Work + default Profile ("默认", status "想看")
- Navigates to the new work's detail page

#### Desktop Layout

```
┌──────────────┬───────────────────────────────────┐
│              │  ← 返回         手动添加          │
│   SIDEBAR   ├───────────────────────────────────┤
│              │  ┌─── Cover ───┐ ┌─── Form ──┐  │
│              │  │  ┌───────┐  │ │ Title     │  │
│              │  │  │  📷  │  │ │ Category  │  │
│              │  │  │ Upload│  │ │ Subcategory│  │
│              │  │  └───────┘  │ │ Total     │  │
│              │  │  Or URL:   │ │ Unit      │  │
│              │  │  [_______] │ │ URL       │  │
│              │  └────────────┘ │ Summary   │  │
│              │                 │ [保存]    │  │
│              │                 └───────────┘  │
└──────────────┴───────────────────────────────────┘
```

**Desktop differences**:
- Two-column layout: cover upload area on left (~240px), form fields on right
- Save button: not full-width, positioned at bottom-right of form or as primary button in header

---

### 4.6 Work Edit (`/works/:id/edit`)

Similar to Manual Add, but pre-filled with existing work data.

**Layout**: Same as Manual Add page.
**Differences**:
- Page title: "编辑作品" instead of "添加作品"
- All fields pre-filled with existing work data
- Save button text: "保存修改"
- Includes a "删除作品" danger button at the bottom (red text, with confirmation dialog)
- Cancel link back to work detail

**Delete Confirmation Dialog**:
```
┌──────────────────────────────────────┐
│                                       │
│        确认删除                       │
│                                       │
│  确定要删除「作品名称」吗？          │
│  此操作不可撤销，关联的进度          │
│  记录也将一并删除。                  │
│                                       │
│     [取消]        [确认删除]         │  ← Cancel + Danger button
│                                       │
└──────────────────────────────────────┘
```

- Dialog: white card, centered, max-width 320px, `--shadow-lg`, `--radius-lg`
- Overlay: black at 50% opacity
- "确认删除" button: red (`--color-error`) bg, white text

---

### 4.7 Profile Create/Edit

Used for adding new profiles (e.g., "二刷", "整合包") or editing existing ones.

#### Mobile Layout

```
┌──────────────────────────────────────────────┐
│ ← 返回         {新增/编辑} 进度配置          │  ← Page header
├──────────────────────────────────────────────┤
│                                              │
│  ┌─ 进度配置 ─────────────────────────────┐ │
│  │                                         │ │
│  │  配置名称 *                            │ │
│  │  ┌────────────────────────────────┐    │ │
│  │  │ 默认                            │    │ │  ← Text input
│  │  └────────────────────────────────┘    │ │
│  │                                         │ │
│  │  状态                                  │ │
│  │  [想看] [在看●] [看完] [暂停] [弃了]  │ │  ← Status pills
│  │                                         │ │
│  │  进度                                  │ │
│  │  ┌────────────────────────────────┐    │ │
│  │  │ 0                              │    │ │  ← Number input
│  │  └────────────────────────────────┘    │ │
│  │                                         │ │
│  │  评分（0-10，可选）                    │ │
│  │  ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆               │ │  ← Star rating
│  │                                         │ │
│  │  评价（可选）                          │ │
│  │  ┌────────────────────────────────┐    │ │
│  │  │                                 │    │ │
│  │  └────────────────────────────────┘    │ │
│  │                                         │ │
│  │  ┌──────────────────────────────┐      │ │
│  │  │     保存                     │      │ │
│  │  └──────────────────────────────┘      │ │
│  │                                         │ │
│  │  (if editing) ┌──────────────────┐     │ │
│  │  │ 删除此配置  │ — red danger link│     │ │
│  │  └──────────────────┘                  │ │
│  └─────────────────────────────────────────┘ │
│                                              │
├──────────────────────────────────────────────┤
│              Bottom Tab Bar                  │
└──────────────────────────────────────────────┘
```

**Fields**:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| 配置名称 | Text | Yes | default: "默认", max 50 chars |
| 状态 | Pill selector | No | Default: "想看" |
| 进度 | Number input | No | Default: 0 |
| 评分 | Star selector (or select) | No | 0-10, default null |
| 评价 | Textarea | No | Max 2000 chars |

**Save Behavior**:
- Create: creates new Profile with given data, navigates back to Work Detail
- Edit: updates Profile, navigates back to Profile Detail or Work Detail

---

## Responsive Behavior Summary

| Element | Mobile (<768px) | Desktop (>=768px) |
|---------|----------------|-------------------|
| Navigation | Bottom tab bar, 64px fixed, glassmorphism | Top bar, 56px fixed, glassmorphism |
| Page padding | 16px each side | 28px each side (max 1400px) |
| Work list view | Default: Grid view (2 cols) | Default: Grid view (3-4 cols) |
| Grid columns | 2 columns | 3-4 columns |
| Category filter | Horizontal scroll tabs | Inline segmented tabs |
| Status filter | Horizontal scroll pills | Inline scroll pills |

---

## Transitions and Micro-interactions

**Page Transitions**:
- Forward navigation (deeper into content): slide left
- Back navigation: slide right
- Duration: 250ms ease-in-out

**Card Interactions**:
- Tap/click: brief scale(0.97) before navigating (50ms feel)
- Hover (desktop): `translateY(-8px) scale(1.02)` + category glow + holo shimmer sweep at 0.35s cubic-bezier

**Button Interactions**:
- Hover: background darken
- Active (press): `scale(0.97)` at 100ms ease

**Progress Update** (Profile Detail):
- Tapping "+": number animates up (brief scale pulse on the number)
- Progress bar smoothly transitions to new width (0.4s cubic-bezier)
- Auto-complete: when progress_value >= total (>0), auto-set status to completed

**Star Rating**:
- On tap, stars fill from left up to the tapped position
- Brief scale animation (1.0 -> 1.2 -> 1.0) on the tapped star

**Bottom Sheet / Modal**:
- Slides up from bottom at 300ms ease
- Overlay fades in at 200ms ease

---

## Accessibility Notes

- All interactive elements must have `:focus-visible` outlines (2px solid blue, 2px offset)
- Touch targets: minimum 44x44px for all interactive elements on mobile
- Color contrast: all text meets WCAG AA (4.5:1 for normal text, 3:1 for large text)
- Semantic HTML: use `<nav>`, `<main>`, `<section>`, `<article>`, `<button>`, `<label>` properly
- ARIA labels on icon-only buttons (e.g., `aria-label="返回"`, `aria-label="编辑"`)
- Status changes should be announced to screen readers (use `aria-live="polite"` regions)
- Respect `prefers-reduced-motion`: disable all animations if user prefers reduced motion
- All form inputs must have associated `<label>` elements
- Progress bar should have `role="progressbar"` with `aria-valuenow`, `aria-valuemin`, `aria-valuemax`

---

## File / Component Organization (for developer reference)

Recommended Vue component structure for Iter 1:

```
src/
  components/
    layout/
      MobileNav.vue        — Bottom tab bar
      TopBar.vue           — Desktop top nav (glassmorphism)
      PageHeader.vue       — Sticky page header with back button
    work/
      WorkCardList.vue     — List view card
      WorkCardGrid.vue     — Grid view card
      CategoryBadge.vue    — Category pill badge
      StatusBadge.vue      — Status pill badge
      ProgressBar.vue      — Progress bar component
      CategoryTabs.vue     — Horizontal category filter tabs
      StatusFilter.vue     — Status filter pills
      ViewToggle.vue       — Grid/List toggle button
      WorkInfoCard.vue     — Info display card (work detail page)
    profile/
      ProfileListItem.vue  — Profile card in work detail
      ProgressStepper.vue  — Increment/decrement stepper
      StatusSelector.vue   — Status pill selector
      StarRating.vue       — 10-star rating component
    common/
      SearchBar.vue        — Search input with debounce
      EmptyState.vue       — Empty state placeholder
      LoadingSkeleton.vue  — Shimmer skeleton
      IconButton.vue       — Icon button wrapper
      ConfirmDialog.vue    — Confirmation modal
  views/
      WorkList.vue         — Home page
      WorkDetail.vue       — Work detail page
      ProfileDetail.vue    — Profile progress update page
      SearchAdd.vue        — Search + add page
      ManualAdd.vue        — Manual add page
      WorkEdit.vue         — Edit work page
      ProfileForm.vue      — Create/edit profile page
  router/
      index.js             — Route definitions
  api/
      works.js             — Work API calls
      profiles.js          — Profile API calls
      bangumi.js           — Bangumi search API calls
  App.vue                  — Root layout (responsive nav switching)
```

---

## Key Takeaway for Developer

1. **No UI framework** — all components built with scoped CSS using the design token CSS custom properties defined above
2. **Mobile-first** — default styles are for mobile (<768px), media queries add desktop behavior at `>=768px`
3. **Category colors** drive the visual identity — each category gets its accent color used across tabs, badges, and progress bars
4. **Two view modes** — List (compact, for mobile) and Grid (visual, for desktop), with user-toggle
5. **Progress update is the core interaction** — stepper with +/- buttons for quick update, auto-complete when reaching total
6. **All forms are editable** after Bangumi auto-fill — user can override any field
