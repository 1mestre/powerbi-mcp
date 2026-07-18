---
name: powerbi-design-layout-themes
description: Design architecture, canvas layout grid, WCAG 2.1 AA contrast ratios, ThemeDataColor mapping, and 5 Premium Themes.
---

# Power BI Design, Layout Grid & Premium Themes Developer Skill

Use this skill when designing report page layouts, establishing visual positioning, configuring WCAG contrast ratios, binding theme color palettes (`ThemeDataColor`), and applying executive design principles.

---

## 1. Canvas Grid & Layout Framework (Anti-Cramping & Visual Safety)

To prevent visuals from looking cramped, overlapping, or having low-contrast double labels:

### Layout Metrics & Spacing Grid:
- **Standard Canvas Dimensions:** Use `1280` (width) x `920` (height) or `1280` x `1000` to support vertical scrolling and provide ample breathing room.
- **Minimum Margins:** Maintain a `20px` margin on the left, right, top, and bottom edges of the canvas.
- **Minimum Inter-Visual Spacing (Gaps):** Maintain at least `15px` of spacing vertically and horizontally between adjacent visual blocks.
- **Visual Heights:**
  - **KPI Cards:** Height must be **at least `90px`** (recommended: `95px` - `110px`). Anything below will cramp the text.
  - **Charts:** Height must be **at least `260px`** (recommended: `280px`) to prevent axis/legend overlaps.
  - **Tables:** Height must be **at least `220px`** (recommended: `240px`) to allow scroll-free visibility.
  - **Slicers:** Height must be **at least `100px`** (recommended: `110px`).

### KPI Card Styling Rules (Zero Crop Guarantee & Clean Typography):
- **Card Height Standard:** Height must be **at least `100px`** to ensure full vertical breathing room for callout values and titles.
- **Hide Category Label (Zero-Crop Fail-safe):** Always set `"categoryLabel"` properties:
  - `"show"`: `false`
  - `"fontSize"`: `1` (1pt font size so it occupies 0 vertical space)
  - `"transparency"`: `100` (100% transparent)
  - `"color"`: Set to the **exact same hex code as the card's background color**.
- **Text Sizing & Alignment:** Title size: `9pt` or `10pt` (`fontColor`: `#F8FAFC` or `#111827`). Callout value size: `22pt`.

### Layout Validation Script:
Before compiling report pages, run a validation script to programmatically assert coordinate boundaries and prevent overlaps:
```python
# Check overlaps between any two visuals A and B
x_overlap = not (A.x + A.width <= B.x or B.x + B.width <= A.x)
y_overlap = not (A.y + A.height <= B.y or B.y + B.height <= A.y)
if x_overlap and y_overlap:
    raise ValueError("Visual overlap detected!")
```

---

## 2. WCAG Contrast Ratios & Executive Design Architecture

To ensure reports look clean, high-contrast, professional, and visually unified across all Power BI themes:

### 1. WCAG 2.1 AA Contrast Ratio Standard:
- **Contrast Formula:** $CR = \frac{L_1 + 0.05}{L_2 + 0.05} \ge 4.5:1$ for body/title text and $\ge 3.0:1$ for large text/KPI callout numbers.
- **Power BI ThemeDataColor Mapping (CRITICAL):**
  - **`ColorId: 0`**: Maps to the active theme's **Background** color (White `#FFFFFF` in light themes, Slate `#0F172A` in dark themes).
  - **`ColorId: 1`**: Maps to the active theme's **Foreground** text color (Dark Slate `#111827` / Dark Vino `#92003A` in light themes, Ice White `#F8FAFC` in dark themes).
  - **`ColorId: 2, 3, etc.`**: Map to Theme Data Colors (Data Colors array).
- **Contrast Rules (GUARANTEED):**
  - Card/Container backgrounds must always use **`ColorId: 0`** (which automatically matches the canvas theme).
  - Card/Container titles must always use **`ColorId: 1`** (which dynamically switches to high-contrast dark text in light mode and white text in dark mode).
  - Callout numbers must use **`ColorId: 1`, `2`, or `3`** (never `0` on light themes, or any color that has a low contrast ratio against the background).
  - **NEVER** place white text (`ColorId: 0` on light themes) on light backgrounds.

### 2. Container Homogeneity Principle:
- **Unified Visual Containers:** All visual containers on a dashboard page (KPI Cards, Charts, Tables, Slicers) MUST share a single, homogeneous background container specification (e.g. Pure White `#FFFFFF` background with `0%` transparency and subtle `1px` border `#E5E7EB`).
- **Avoid "Patchwork" Designs:** Do not mix solid dark purple cards next to white donut charts and black KPI boxes. A patchwork of mismatched container backgrounds creates visual clutter and looks amateurish.

### 3. Data Accentuation vs Container Neutrality:
- Use colors purposefully for **data accentuation** (e.g. KPI callout value numbers, chart bars, line series, donut slices), while maintaining clean, neutral, high-contrast framing for containers and titles.

---

## 4. Premium Aesthetic Guidelines & Intentional Styling for Dashboards

To elevate standard dashboards into premium, modern executive interfaces, apply these styling patterns:

### 1. Intention-Based KPI Colors (Color semántico por intención)
Differentiate the primary values on KPI Cards based on what the metric signifies to the user:
* **Information (Neutral/Volume):** Use an elegant light blue (`#3B82F6` or similar) for counts, inventory, or products.
* **Success/Achievement:** Use emerald green (`#10B981`) or gold (`#FBBF24`) for key accomplishments, target completions, or average ratings.
* **Warning/Alert:** Use warm amber (`#F59E0B`) or light orange for discount percentages, low stocks, or rates that need attention.

### 2. Glowing Borders & Highlighted Cards (Glow / Resplandor)
To draw immediate executive focus to the most critical "North Star" metrics (e.g., Total Revenue, Avg Rating):
* Set a slightly thicker border (`2px` instead of `1px`).
* Use a bright, contrasting color for that border (e.g., `#FF9E2C` / Terracota suave) against the dark theme background.
* Maintain a darker neutral border (`#2E3F4C` or similar) on secondary cards to keep the visual hierarchy clean.

### 3. Visual Emojis/Symbols in Titles
Embed clean unicode symbols directly in visual container titles to make them instantly recognizable and visual (e.g., `"⭐ Avg Rating"`, `"💰 Total Revenue"`, `"📂 Filter by Category"`).

### 4. Distinct Series Colors in Chart Elements
Do not paint every bar or column chart in the same uniform accent color. Vary the series colors logically:
* **Revenue/Financial charts:** Use the primary theme highlight (`#D99B7F` / Terracota).
* **Volume/Quantity charts:** Use information blue (`#3B82F6`).
* **Performance/Rating charts:** Use success green (`#10B981`).

### 5. Font Family & Zero-Friction Typography (e.g. Montserrat)
To distribute reports without friction (so clients don't encounter missing font warnings or rendering fallbacks):
* **Custom Typography (e.g. `Montserrat`):** Specify `"fontFamily": "Montserrat"` in the theme JSON and visual titles.
* **Fallback Behavior:** If the client machine does not have the custom font installed, Power BI Desktop and Power BI Service automatically fallback to standard sans-serif system fonts (`Segoe UI` or `Arial`) without crashing or showing error dialogs.
* **Universal Native Fonts (Zero-Friction Guarantee):** When building for enterprise clients with locked-down PCs, use universal fonts built into all Windows/Web environments: `Segoe UI`, `Segoe UI Semibold`, `DIN`, `Calibri`, or `Arial`.

### 6. Python & R Custom Visuals (Cloud & Local Behavior)
* **Local Power BI Desktop Execution:** Visualizing via Python (`matplotlib`, `seaborn`, `plotly`) or R (`ggplot2`) inside Power BI Desktop requires local Python/R runtime installations on the developer/client machine.
* **Zero-Client-Friction Cloud Deployment (Power BI Service):** Once published to **Power BI Service (Cloud)**, Microsoft executes Python and R scripts on Azure cloud sandboxes automatically. The end-user client does NOT need Python or R installed on their machine to view interactive Python/R charts in their browser or mobile app.

---

## 3. Premium Theme Catalogue (Modos Claro y Oscuro)

These pre-configured themes are designed to enforce perfect readability and contrast standards while projecting distinct, premium vibes:

### 1. 🌸 **"Magenta Blossom" (Modo Claro)**
- **Palette**: `#92003A` (Vino oscuro), `#F62477` (Rosa brillante), `#FFADEE` (Rosa pastel), `#FFE185` (Arena suave).
- **Application**: Pure white canvas with soft sand card backgrounds. Vino/Magenta for high-contrast titles and text.

### 2. 🌌 **"Slate & Terracotta" (Modo Oscuro)**
- **Palette**: `#0F3040` (Slate Azul Oscuro), `#464858` (Gris Asfalto), `#A56F63` (Terracota), `#D99B7F` (Terracota claro).
- **Application**: Deep slate blue canvas with dark slate card surfaces. Light terracotta for text and callouts.

### 3. 🌿 **"Ecotone Spring" (Modo Claro)**
- **Palette**: `#769826` (Oliva), `#A1CB35` (Verde primavera), `#FFDE4E` (Amarillo), `#FF9D4D` (Naranja).
- **Application**: Clean light grey canvas, white containers, olive text, vibrant green/yellow/orange data series.

### 4. ☕ **"Roasted Espresso" (Modo Oscuro)**
- **Palette**: `#60241E` (Marrón Espresso), `#95271D` (Marrón rojizo), `#B34A44` (Marrón), `#E77B49` (Tono arcilla claro).
- **Application**: Dark espresso canvas, reddish-brown containers, light clay text for high contrast.

### 5. ❄️ **"Vintage Nordic" (Modo Claro)**
- **Palette**: `#0B1849` (Marino), `#124D1C` (Pino), `#E4B028` (Oro viejo), `#EBEDE3` (Gris pálido).
- **Application**: Pale nordic grey canvas, white containers, deep navy text, pine green and gold accents.

### Dark Navy Theme Color Reference:
For dark navy dashboards, use these colors consistently:
```python
BG_DARK = "#1E1E32"       # Page background
CARD_BG = "#252540"       # Card/visual container background
BORDER_BG = "#3A3A5C"     # Border color
TEXT_WHITE = "#FFFFFF"     # White text (KPI values)
TEXT_LIGHT = "#F0F0F0"    # Off-white text (titles, labels)
ACCENT_TEAL = "#00B4D8"   # Teal accent for data series
```

---

## 🔗 RELATED SKILLS & REPOSITORY FILES

- 🏠 **[powerbi-pbir-editor](file:///C:/Users/Sebas/desktop-ssas-mcp/.agents/skills/powerbi-pbir-editor/SKILL.md)** - Master Skill Hub
- 📊 **[powerbi-pbir-visuals-specs](file:///C:/Users/Sebas/desktop-ssas-mcp/.agents/skills/powerbi-pbir-visuals-specs/SKILL.md)** - Visual Types & JSON Formatting
- 📈 **[create_dashboard.py](file:///C:/Users/Sebas/desktop-ssas-mcp/create_dashboard.py)** - Dark theme Plotly dashboard implementation example
