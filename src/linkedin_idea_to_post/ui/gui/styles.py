from __future__ import annotations

COLOR_PRIMARY = "#2563EB"
COLOR_SECONDARY = "#0F766E"
COLOR_ACCENT = "#0284C7"

GLOBAL_CSS = """
:root {
  --li2p-font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --li2p-font-mono: 'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace;
  --li2p-bg: #FAFAFA;
  --li2p-surface: #FFFFFF;
  --li2p-surface-subtle: #F4F4F5;
  --li2p-border: #E4E4E7;
  --li2p-border-hover: #D4D4D8;
  --li2p-text: #18181B;
  --li2p-text-secondary: #52525B;
  --li2p-text-muted: #71717A;
  --li2p-hover: #F4F4F5;
  --li2p-accent-manual-bg: #F0FDFA;
  --li2p-banner-bg: #ECFDF5;
  --li2p-banner-border: #A7F3D0;
  --li2p-banner-text: #065F46;
  --li2p-warn-bg: #FFFBEB;
  --li2p-warn-border: #FDE68A;
}

body.body--dark {
  --li2p-bg: #09090B;
  --li2p-surface: #111113;
  --li2p-surface-subtle: #18181B;
  --li2p-border: #27272A;
  --li2p-border-hover: #3F3F46;
  --li2p-text: #F4F4F5;
  --li2p-text-secondary: #D4D4D8;
  --li2p-text-muted: #A1A1AA;
  --li2p-hover: #1C1C20;
  --li2p-accent-manual-bg: #042F2E;
  --li2p-banner-bg: #052E16;
  --li2p-banner-border: #14532D;
  --li2p-banner-text: #A7F3D0;
  --li2p-warn-bg: #271E05;
  --li2p-warn-border: #78350F;
}

body {
  font-family: var(--li2p-font-sans);
  background-color: var(--li2p-bg) !important;
  color: var(--li2p-text) !important;
  font-size: 13px;
  line-height: 1.45;
  -webkit-font-smoothing: antialiased;
  overflow: hidden;
}

.nicegui-content {
  padding: 0 !important;
  margin: 0 !important;
  gap: 0 !important;
  height: 100vh !important;
  width: 100vw !important;
  overflow: hidden !important;
}

.li2p-tab-panels .q-panel,
.li2p-tab-panels .q-tab-panel {
  height: 100% !important;
  overflow: hidden !important;
}
.li2p-tab-panels .q-tab-panel {
  display: flex !important;
  flex-direction: column !important;
}
.q-separator {
  flex-shrink: 0 !important;
}

.li2p-header {
  background: var(--li2p-surface) !important;
  color: var(--li2p-text) !important;
  border-bottom: 1px solid var(--li2p-border);
}
.li2p-header .q-tab {
  min-height: 44px;
  padding: 0 10px;
}
.li2p-header .q-tab__label {
  font-size: 13px;
  font-weight: 500;
}
.li2p-header .q-tab__icon {
  font-size: 17px;
  margin-right: 5px;
}

.li2p-surface {
  background: var(--li2p-surface) !important;
  color: var(--li2p-text) !important;
  border: 1px solid var(--li2p-border);
  border-radius: 6px;
  box-shadow: none !important;
}

.li2p-card-fill {
  display: flex !important;
  flex-direction: column !important;
  min-height: 0 !important;
}

.li2p-row-item {
  background: var(--li2p-surface) !important;
  color: var(--li2p-text) !important;
  border: 1px solid var(--li2p-border);
  border-radius: 6px;
  box-shadow: none !important;
  transition: border-color 0.12s ease, background-color 0.12s ease;
}
.li2p-row-item:hover {
  border-color: var(--li2p-border-hover);
  background: var(--li2p-hover) !important;
}

.li2p-subtle-box {
  background: var(--li2p-surface-subtle) !important;
  border: 1px solid var(--li2p-border);
  border-radius: 6px;
}

.li2p-accent-manual {
  border-left: 2px solid #0D9488 !important;
  background: var(--li2p-accent-manual-bg) !important;
}
.li2p-accent-suggested {
  border-left: 2px solid var(--li2p-text-muted) !important;
}

.li2p-heading-1 {
  font-size: 14.5px;
  font-weight: 600;
  color: var(--li2p-text);
  letter-spacing: -0.01em;
}
.li2p-heading-2 {
  font-size: 13px;
  font-weight: 600;
  color: var(--li2p-text);
}
.li2p-text-body {
  font-size: 13px;
  color: var(--li2p-text);
}
.li2p-text-prose {
  font-size: 13.5px;
  line-height: 1.6;
  color: var(--li2p-text-secondary);
}
.li2p-text-preview {
  font-size: 13px;
  font-weight: 450;
  color: var(--li2p-text);
}
.li2p-text-muted {
  font-size: 12px;
  color: var(--li2p-text-muted);
}
.li2p-text-mono {
  font-family: var(--li2p-font-mono);
  font-size: 11.5px;
  color: var(--li2p-text-muted);
}
.li2p-pill {
  font-size: 11px;
  font-weight: 500;
  padding: 1px 6px;
  border-radius: 4px;
  border: 1px solid var(--li2p-border);
  background: var(--li2p-surface-subtle);
  color: var(--li2p-text-muted);
  white-space: nowrap;
}
.li2p-pill-published {
  color: #0F766E;
  border-color: rgba(15, 118, 110, 0.25);
  background: rgba(15, 118, 110, 0.08);
}
.li2p-pill-draft {
  color: #B45309;
  border-color: rgba(180, 83, 9, 0.25);
  background: rgba(180, 83, 9, 0.08);
}
.li2p-kv-row {
  border-bottom: 1px solid var(--li2p-border);
}
.li2p-banner-success {
  background: var(--li2p-banner-bg) !important;
  border: 1px solid var(--li2p-banner-border);
  color: var(--li2p-banner-text) !important;
  border-radius: 6px;
}
.li2p-warn-box {
  background: var(--li2p-warn-bg) !important;
  border: 1px solid var(--li2p-warn-border);
  border-radius: 6px;
}

.li2p-toml-editor .q-field__inner,
.li2p-toml-editor .q-field__control,
.li2p-toml-editor .q-field__control-container,
.li2p-toml-editor textarea {
  height: 100% !important;
}
.li2p-toml-editor textarea {
  overflow-y: auto !important;
  font-family: var(--li2p-font-mono);
  font-size: 12px;
  line-height: 1.5;
}
.li2p-fill-textarea,
.li2p-fill-textarea .q-field__inner,
.li2p-fill-textarea .q-field__control,
.li2p-fill-textarea .q-field__control-container,
.li2p-fill-textarea textarea {
  height: 100% !important;
}
.li2p-fill-textarea textarea {
  overflow-y: auto !important;
  font-size: 13.5px;
  line-height: 1.6;
}
"""


class Props:
    FLAT_DENSE = "flat dense"
    OUTLINED_DENSE = "outlined dense"
    OUTLINE_DENSE = "outline dense"
    TABS_HEADER = (
        "dense inline-label no-caps active-color=primary indicator-color=primary"
    )
    CSV_UPLOAD = "accept=.csv flat bordered"


class LayoutClass:
    APP_SHELL_COL = "w-full h-screen flex flex-col overflow-hidden gap-0"
    APP_HEADER = "li2p-header w-full shrink-0"
    APP_HEADER_INNER = (
        "w-full max-w-5xl mx-auto px-4 h-12 no-wrap items-center justify-between"
    )
    APP_TITLE = "text-[14px] font-semibold tracking-tight whitespace-nowrap"
    APP_TAB_BAR = "h-12"
    APP_TAB_PANELS = (
        "li2p-tab-panels w-full flex-1 min-h-0 bg-transparent q-pa-none overflow-hidden"
    )
    PANEL_FIXED = "w-full h-full px-4 py-2.5 flex flex-col min-h-0 overflow-hidden"

    PAGE_FLUID_FILL = "w-full max-w-5xl mx-auto h-full flex flex-col min-h-0 gap-2"
    SPLIT_EQUAL = "w-full grid grid-cols-1 lg:grid-cols-2 gap-3 flex-1 min-h-0"
    SPLIT_2_3 = "w-full grid grid-cols-1 lg:grid-cols-[5fr_7fr] gap-3 flex-1 min-h-0"

    CARD_MD = "li2p-surface w-full px-3.5 py-2.5 gap-2"
    CARD_SM = "li2p-surface w-full shrink-0 px-3 py-2 gap-1.5"
    CARD_INTERACTIVE = "li2p-row-item w-full shrink-0 px-3 py-1.5 cursor-pointer"
    CARD_FILL = "li2p-surface li2p-card-fill w-full h-full flex-1 min-h-0 px-3.5 py-2.5 overflow-hidden gap-2"
    CARD_COMPACT_ITEM = "li2p-surface w-full shrink-0 px-2.5 py-1.5 overflow-x-hidden"

    MODAL_WIDTHS: dict[str, str] = {
        "md": "li2p-surface w-full max-w-2xl p-4 gap-2.5 overflow-x-hidden",
        "lg": "li2p-surface w-full max-w-3xl p-4 gap-2.5 overflow-x-hidden",
        "xl": "li2p-surface w-full max-w-5xl p-4 gap-2.5 overflow-x-hidden",
    }

    BANNER_SUCCESS = (
        "li2p-banner-success w-full items-center justify-between px-3 py-1.5"
    )
    WARNING_EXPANSION = "li2p-warn-box w-full"
    SEARCH_PANEL = "li2p-subtle-box w-full p-2 gap-1"
    SEARCH_BOX = "w-full max-h-52 overflow-y-auto gap-1 pr-1"

    KV_TITLE = "text-[11px] font-semibold uppercase tracking-wider text-primary mb-0.5"
    KV_ROW = "li2p-kv-row w-full items-baseline justify-between gap-2 py-1"
    KV_KEY = "li2p-text-mono shrink-0"
    KV_VAL = "li2p-text-body font-medium text-right break-all"

    SCROLL_HEIGHTS: dict[str, str] = {
        "sm": "w-full h-64 min-h-40 li2p-subtle-box p-2.5 overflow-x-hidden",
        "md": "w-full h-72 min-h-48 li2p-subtle-box p-2.5 overflow-x-hidden",
        "lg": "w-full flex-1 min-h-0 li2p-subtle-box p-2.5 overflow-x-hidden",
        "xl": "w-full h-[64vh] min-h-72 li2p-subtle-box p-2.5 overflow-x-hidden",
        "fill": "w-full flex-1 min-h-0 overflow-x-hidden",
    }
    SCROLL_COLUMN = (
        "w-full flex-1 min-h-0 overflow-y-auto overflow-x-hidden gap-1.5 pr-1"
    )

    TEXT_HEADING_1 = "li2p-heading-1"
    TEXT_HEADING_2 = "li2p-heading-2"
    TEXT_BODY = "li2p-text-body"
    TEXT_MUTED = "li2p-text-muted"
    TEXT_MONO = "li2p-text-mono"
    TEXT_TAGS = "text-[12px] text-primary whitespace-normal break-words"
    TEXT_ERROR = "text-[12px] text-negative"
    TEXT_EMPTY = "li2p-text-muted text-center w-full py-8"
    TEXT_PROSE = "li2p-text-prose whitespace-pre-line break-words"
    TEXT_PREVIEW = "li2p-text-preview truncate"
    TEXT_PREVIEW_WRAP = "li2p-text-preview whitespace-normal overflow-visible"
    TOML_EDITOR = "w-full flex-1 min-h-0 li2p-toml-editor"
    FILL_TEXTAREA = "w-full flex-1 min-h-0 li2p-fill-textarea"
    CHECKBOX_COMPACT = "shrink-0 mt-0.5"
    EXPANSION_GROW = "col min-w-[200px]"

    GAP_CLASSES: dict[str, str] = {
        "xs": "gap-1",
        "sm": "gap-1.5",
        "md": "gap-2.5",
        "lg": "gap-3.5",
    }
    SELECT_WIDTHS: dict[str, str] = {
        "auto": "",
        "sm": "w-32 shrink-0",
        "md": "w-40 shrink-0",
        "col": "min-w-36 col",
    }
    NUMBER_WIDTHS: dict[str, str] = {
        "xs": "w-24 shrink-0",
        "sm": "w-28 shrink-0",
        "md": "w-32 shrink-0",
    }
