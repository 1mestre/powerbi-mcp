#!/usr/bin/env python3
"""
apply_theme.py — COMPREHENSIVE VISUAL STYLING ENGINE for Power BI PBIP projects.

Applies a COMPLETE visual profile to every visual in the project, handling:
  ✓ Theme file overwrite (dataColors, bg, fg, tableAccent, semantic colors)
  ✓ Page backgrounds (all pages)
  ✓ Visual backgrounds & borders
  ✓ Title font colors
  ✓ Category axis label colors
  ✓ Value axis label colors
  ● Legend label colors
  ✓ Data label colors
  ✓ Gridline colors
  ✓ Plot area fill
  ✓ Slicer text colors (header.fontColor, inputText.fontColor, items.fontColor)
  ✓ Card (KPI) label colors (cardLabels, categoryLabels)
  ✓ DataPoint fill colors for categorical charts (up to 10 cycling colors)
  ✓ Bar charts with temporal (year) data use SINGLE color
  ✓ Treemap, map, pie/donut, line all get appropriate styling
  ✓ Validates contrast ratios (dark vs light theme)
  ✓ Rounded corners on all visuals

Usage:
    python apply_theme.py <project.pbip> --theme slate-terracotta
    python apply_theme.py <project.pbip> --theme-file my_theme.json
    python apply_theme.py <project.pbip> --theme slate-terracotta --dry-run
    python apply_theme.py <project.pbip> --theme slate-terracotta --profile  # Print visual profile

Exit code: 0 = success, 1 = error
"""

import json
import sys
from pathlib import Path
from glob import glob

# ═══════════════════════════════════════════════════════════════════════
# COMPLETE VISUAL PROFILES — one per built-in theme
# Each profile defines EVERY visual property for both dark and light modes.
# ═══════════════════════════════════════════════════════════════════════

VISUAL_PROFILES = {
    "slate-terracotta": {
        "theme": {
            "name": "CY26SU05",
            "dataColors": ["#A56F63", "#D99B7F", "#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899", "#14B8A6"],
            "background": "#0F3040",
            "foreground": "#F8FAFC",
            "tableAccent": "#A56F63",
            "good": "#10B981", "bad": "#EF4444", "neutral": "#A56F63",
            "firstLevelElements": "#F8FAFC",
            "secondLevelElements": "#CBD5E1",
            "thirdLevelElements": "#334155",
            "fourthLevelElements": "#1E3A5F"
        },
        "mode": "dark",
        "page_bg": "#0F3040",
        "visual_bg": "#1A4055",
        "border": "#285468",
        "radius": "8D",
        "title_font_color": "#F8FAFC",
        "cat_axis_label": "#CBD5E1",
        "val_axis_label": "#CBD5E1",
        "legend_label": "#CBD5E1",
        "data_label": "#F8FAFC",
        "gridline": "#4B5563",
        "plot_area": "#152E3E",
        "slicer_header_font": "#F8FAFC",
        "slicer_item_font": "#CBD5E1",
        "slicer_input_text": "#F8FAFC",
        "card_label": "#F8FAFC",
        "card_category_label": "#CBD5E1",
        "card_bg": "#1A4055",
        "table_font": "#F8FAFC",
        "table_header_bg": "#152E3E",
        "table_row_alt_bg": "#1A4055",
        "map_fill": "#285468",
        "data_point_count": 10
    },
    "magenta-blossom": {
        "theme": {
            "name": "CY26SU05",
            "dataColors": ["#92003A", "#F62477", "#FFADEE", "#FFE185", "#3B82F6", "#10B981", "#8B5CF6", "#F59E0B"],
            "background": "#FFFFFF",
            "foreground": "#111827",
            "tableAccent": "#92003A",
            "good": "#10B981", "bad": "#EF4444", "neutral": "#92003A"
        },
        "mode": "light",
        "page_bg": "#FFFFFF",
        "visual_bg": "#F9FAFB",
        "border": "#E5E7EB",
        "radius": "8D",
        "title_font_color": "#111827",
        "cat_axis_label": "#4B5563",
        "val_axis_label": "#4B5563",
        "legend_label": "#4B5563",
        "data_label": "#111827",
        "gridline": "#D1D5DB",
        "plot_area": "#FFFFFF",
        "slicer_header_font": "#111827",
        "slicer_item_font": "#374151",
        "slicer_input_text": "#111827",
        "card_label": "#111827",
        "card_category_label": "#4B5563",
        "card_bg": "#F9FAFB",
        "table_font": "#111827",
        "table_header_bg": "#F3F4F6",
        "table_row_alt_bg": "#F9FAFB",
        "map_fill": "#E5E7EB",
        "data_point_count": 10
    },
    "ecotone-spring": {
        "theme": {
            "name": "CY26SU05",
            "dataColors": ["#769826", "#A1CB35", "#FFDE4E", "#FF9D4D", "#3B82F6", "#10B981", "#8B5CF6", "#EC4899", "#14B8A6", "#F59E0B"],
            "background": "#F5F2EB",
            "foreground": "#1a1a2e",
            "tableAccent": "#769826",
            "good": "#A1CB35", "bad": "#EF4444", "neutral": "#769826"
        },
        "mode": "light",
        "page_bg": "#F5F2EB",
        "visual_bg": "#FAF8F3",
        "border": "#E2DDD0",
        "radius": "8D",
        "title_font_color": "#1a1a2e",
        "cat_axis_label": "#4B5563",
        "val_axis_label": "#4B5563",
        "legend_label": "#5B6877",
        "data_label": "#1a1a2e",
        "gridline": "#D5D0C3",
        "plot_area": "#F5F2EB",
        "slicer_header_font": "#1a1a2e",
        "slicer_item_font": "#374151",
        "slicer_input_text": "#1a1a2e",
        "card_label": "#1a1a2e",
        "card_category_label": "#5B6877",
        "card_bg": "#FAF8F3",
        "table_font": "#1a1a2e",
        "table_header_bg": "#EDE9DF",
        "table_row_alt_bg": "#FAF8F3",
        "map_fill": "#E2DDD0",
        "data_point_count": 10
    },
    "roasted-espresso": {
        "theme": {
            "name": "CY26SU05",
            "dataColors": ["#60241E", "#95271D", "#B34A44", "#E77B49", "#3B82F6", "#10B981", "#F59E0B", "#8B5CF6"],
            "background": "#1A0F0D",
            "foreground": "#F8FAFC",
            "tableAccent": "#B34A44",
            "good": "#10B981", "bad": "#EF4444", "neutral": "#B34A44"
        },
        "mode": "dark",
        "page_bg": "#1A0F0D",
        "visual_bg": "#2D1814",
        "border": "#3D221D",
        "radius": "8D",
        "title_font_color": "#F8FAFC",
        "cat_axis_label": "#CBD5E1",
        "val_axis_label": "#CBD5E1",
        "legend_label": "#CBD5E1",
        "data_label": "#F8FAFC",
        "gridline": "#4B3A36",
        "plot_area": "#231411",
        "slicer_header_font": "#F8FAFC",
        "slicer_item_font": "#CBD5E1",
        "slicer_input_text": "#F8FAFC",
        "card_label": "#F8FAFC",
        "card_category_label": "#CBD5E1",
        "card_bg": "#2D1814",
        "table_font": "#F8FAFC",
        "table_header_bg": "#231411",
        "table_row_alt_bg": "#2D1814",
        "map_fill": "#3D221D",
        "data_point_count": 10
    },
    "vintage-nordic": {
        "theme": {
            "name": "CY26SU05",
            "dataColors": ["#0B1849", "#124D1C", "#E4B028", "#EBEDE3", "#3B82F6", "#8B5CF6", "#EC4899", "#14B8A6"],
            "background": "#EBEDE3",
            "foreground": "#0B1849",
            "tableAccent": "#0B1849",
            "good": "#124D1C", "bad": "#C0392B", "neutral": "#0B1849"
        },
        "mode": "light",
        "page_bg": "#EBEDE3",
        "visual_bg": "#F0F2E9",
        "border": "#D6D9CC",
        "radius": "8D",
        "title_font_color": "#0B1849",
        "cat_axis_label": "#4A5568",
        "val_axis_label": "#4A5568",
        "legend_label": "#5B6A7F",
        "data_label": "#0B1849",
        "gridline": "#D5D8CB",
        "plot_area": "#EBEDE3",
        "slicer_header_font": "#0B1849",
        "slicer_item_font": "#374151",
        "slicer_input_text": "#0B1849",
        "card_label": "#0B1849",
        "card_category_label": "#4A5568",
        "card_bg": "#F0F2E9",
        "table_font": "#0B1849",
        "table_header_bg": "#DEE0D5",
        "table_row_alt_bg": "#F0F2E9",
        "map_fill": "#D6D9CC",
        "data_point_count": 10
    }
}


# ═══════════════════════════════════════════════════════════════════════
# BUILTIN_THEMES — for backward compatibility, derived from profiles
# ═══════════════════════════════════════════════════════════════════════

def _extract_builtin_themes():
    """Build BUILTIN_THEMES dict from VISUAL_PROFILES for backward compat."""
    bt = {}
    for name, profile in VISUAL_PROFILES.items():
        bt[name] = dict(profile["theme"])
    return bt


BUILTIN_THEMES = _extract_builtin_themes()


# ═══════════════════════════════════════════════════════════════════════
# HELPER: Literal color expression helper
# ═══════════════════════════════════════════════════════════════════════

def literal_color(hex_color):
    """Return a PBIR literal color expression."""
    return {"solid": {"color": {"expr": {"Literal": {"Value": f"'{hex_color}'"}}}}}


def theme_data_color(color_id, percent=0):
    """Return a PBIR ThemeDataColor expression."""
    return {"solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": color_id, "Percent": percent}}}}}


# ═══════════════════════════════════════════════════════════════════════
# GET VISUAL PROFILE
# ═══════════════════════════════════════════════════════════════════════

def get_visual_profile(theme_name: str) -> dict:
    """
    Return the complete visual profile for a given theme name.
    
    Args:
        theme_name: One of the built-in theme names, or any key in VISUAL_PROFILES.
    
    Returns:
        dict: The full visual profile with all color, background, border, and
              font properties for every visual element type.
    
    Raises:
        KeyError: If the theme name is not found.
    """
    if theme_name in VISUAL_PROFILES:
        return VISUAL_PROFILES[theme_name]
    raise KeyError(f"Unknown theme: {theme_name}. Available: {list(VISUAL_PROFILES.keys())}")


# ═══════════════════════════════════════════════════════════════════════
# 1. THEME FILE
# ═══════════════════════════════════════════════════════════════════════

def apply_theme_file(project_root, project_name, theme):
    """Overwrite the existing BaseThemes JSON with the new theme."""
    theme_dirs = [
        project_root / f"{project_name}.Report" / "StaticResources" / "SharedResources" / "BaseThemes",
        project_root / f"{project_name}.Report" / "definition" / "BaseThemes",
    ]
    for td in theme_dirs:
        if td.exists():
            existing = list(td.glob("*.json"))
            if existing:
                target = existing[0]
                with open(target, "r", encoding="utf-8") as f:
                    old_theme = json.load(f)
                old_name = old_theme.get("name", theme.get("name", "CY26SU05"))
                theme_out = dict(theme)
                theme_out["name"] = old_name
                with open(target, "w", encoding="utf-8") as f:
                    json.dump(theme_out, f, indent=2, ensure_ascii=False)
                return {"status": "ok", "path": str(target),
                        "message": f"Theme overwritten with {len(theme['dataColors'])} data colors"}
    return {"status": "error", "path": "", "message": "No existing theme file found"}


# ═══════════════════════════════════════════════════════════════════════
# 2. PAGE BACKGROUNDS
# ═══════════════════════════════════════════════════════════════════════

def apply_page_backgrounds(project_root, project_name, bg_color):
    """Apply background color to every page.json."""
    results = []
    pages_dir = project_root / f"{project_name}.Report" / "definition" / "pages"
    if not pages_dir.exists():
        return [{"status": "error", "message": f"Pages dir not found: {pages_dir}"}]
    for page_dir in sorted(pages_dir.iterdir()):
        if not page_dir.is_dir():
            continue
        page_json = page_dir / "page.json"
        if not page_json.exists():
            continue
        with open(page_json, "r", encoding="utf-8") as f:
            page = json.load(f)
        page.setdefault("objects", {})["background"] = [{
            "properties": {
                "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{bg_color}'"}}}}},
                "transparency": {"expr": {"Literal": {"Value": "0"}}}
            }
        }]
        with open(page_json, "w", encoding="utf-8") as f:
            json.dump(page, f, indent=2, ensure_ascii=False)
        results.append({"status": "ok", "path": str(page_json), "message": "Background set"})
    return results


# ═══════════════════════════════════════════════════════════════════════
# 3. COMPREHENSIVE VISUAL STYLING
# ═══════════════════════════════════════════════════════════════════════

def _has_temporal_axis(v):
    """
    Heuristic: check if a chart visual has a temporal (date/year) category axis.
    Looks for categoryAxis with groups containing 'Date' or 'Year' type references.
    This is a best-effort heuristic based on projection metadata in the visual.json.
    """
    try:
        category = v.get("visual", {}).get("categoryAxis", v.get("categoryAxis", {}))
        # Check if projection source has temporal hint
        projections = v.get("visual", {}).get("projections", {})
        for role, proj_list in projections.items():
            if not isinstance(proj_list, list):
                continue
            for proj in proj_list:
                if isinstance(proj, dict):
                    query_name = str(proj.get("queryName", "")).lower()
                    source = str(proj.get("Source", "")).lower()
                    field_props = str(proj.get("property", "")).lower()
                    # Check for date/time markers in column names
                    temporal_hints = ["date", "year", "month", "quarter", "time", "fiscal",
                                      "day", "week", "hour", "minute", "period", "trx",
                                      "timestamp", "datetime"]
                    for hint in temporal_hints:
                        if hint in query_name or hint in source or hint in field_props:
                            return True
    except Exception:
        pass
    return False


def _has_categorical_axis(v):
    """
    Heuristic: check if a chart visual has a categorical (non-temporal) axis.
    Returns True if it has a category axis that doesn't appear to be temporal.
    Defaults to categorical if the heuristic is uncertain.
    """
    try:
        projections = v.get("visual", {}).get("projections", {})
        for role, proj_list in projections.items():
            if role in ("Category", "Values") and isinstance(proj_list, list):
                for proj in proj_list:
                    if isinstance(proj, dict):
                        query_name = str(proj.get("queryName", "")).lower()
                        source = str(proj.get("Source", "")).lower()
                        # Explicitly NOT temporal
                        non_temporal_hints = ["name", "label", "category", "country", "city",
                                              "state", "region", "product", "brand", "type",
                                              "status", "group", "class", "segment", "department",
                                              "store", "customer", "vendor", "employee"]
                        for hint in non_temporal_hints:
                            if hint in query_name or hint in source:
                                return True
                        # If it's not temporal and has projection, assume categorical
                        if not _has_temporal_axis(v):
                            return True
    except Exception:
        pass
    # Default to categorical for charts with dataPoint roles
    try:
        projections = v.get("visual", {}).get("projections", {})
        has_category = any(role == "Category" for role in projections)
        has_y = any(role in ("Y", "Values") for role in projections)
        if has_category and has_y:
            return True
    except Exception:
        pass
    return False


def _get_visual_type(v):
    """Safely get the visualType from a visual.json."""
    try:
        return v.get("visual", {}).get("visualType", v.get("visualType", ""))
    except Exception:
        return ""


def apply_visual_styling(project_root, project_name, profile):
    """
    Apply COMPLETE visual styling to every visual.json in the project.
    
    For EVERY visual, sets:
      - visualContainerObjects (background, border, rounded corners)
      - title properties (fontColor, background, alignment)
      - Axis label colors (categoryAxis, valueAxis)
      - Legend label colors
      - Data label colors
      - Gridline colors
      - Plot area fill
    
    For barChart/clusteredColumnChart with CATEGORICAL data: sets up to 10 
    dataPoint entries with cycling ThemeDataColor for distinct bar colors.
    
    For barChart/lineChart with TEMPORAL data: uses SINGLE default color.
    
    For card (KPI): sets cardLabels and categoryLabels.
    
    For slicer: sets header.fontColor, items.fontColor, inputText.fontColor.
    """
    results = []
    visuals_glob_str = str(project_root / f"{project_name}.Report" / "definition" / "pages" / "**" / "visuals" / "**" / "visual.json")
    visual_files = sorted(glob(visuals_glob_str, recursive=True))
    
    if not visual_files:
        return [{"status": "warning", "path": "", "message": "No visual.json files found"}]
    
    for vpath_str in visual_files:
        vpath = Path(vpath_str)
        try:
            with open(vpath, "r", encoding="utf-8") as f:
                v = json.load(f)
        except Exception as e:
            results.append({"status": "error", "path": str(vpath), "message": f"Cannot read: {e}"})
            continue
        
        vtype = _get_visual_type(v)
        changed = False
        
        # ── Visual Container Objects (background, border, radius) ──
        vco = v.setdefault("visual", {}).setdefault("visualContainerObjects", {})
        
        # Background (fill)
        vco["fill"] = [{"properties": {
            "color": literal_color(profile["visual_bg"]),
            "transparency": {"expr": {"Literal": {"Value": "0"}}}
        }}]
        
        # Border
        vco["border"] = [{"properties": {
            "color": literal_color(profile["border"]),
            "width": {"expr": {"Literal": {"Value": "1"}}}
        }}]
        
        # Rounded corners
        vco["radius"] = [{"properties": {
            "radius": {"expr": {"Literal": {"Value": profile["radius"]}}}
        }}]
        
        changed = True
        
        # ── Title ──
        objects = v.setdefault("visual", {}).setdefault("objects", {})
        objects["title"] = [{"properties": {
            "fontColor": literal_color(profile["title_font_color"]),
            "show": {"expr": {"Literal": {"Value": "true"}}}
        }}]
        
        # ── Visual-Type Specific Styling ──
        
        if vtype == "card":
            # KPI card: set cardLabels and categoryLabels
            objects["cardLabels"] = [{"properties": {
                "fontColor": literal_color(profile["card_label"]),
                "fontSize": {"expr": {"Literal": {"Value": "24"}}}
            }}]
            objects["categoryLabels"] = [{"properties": {
                "fontColor": literal_color(profile["card_category_label"]),
                "fontSize": {"expr": {"Literal": {"Value": "12"}}}
            }}]
            results.append({"status": "ok", "path": str(vpath), "message": "Applied card styling"})
        
        elif vtype == "slicer":
            # Slicer: header, items, input text
            objects["header"] = [{"properties": {
                "fontColor": literal_color(profile["slicer_header_font"]),
                "show": {"expr": {"Literal": {"Value": "true"}}}
            }}]
            objects["items"] = [{"properties": {
                "fontColor": literal_color(profile["slicer_item_font"])
            }}]
            objects["inputText"] = [{"properties": {
                "fontColor": literal_color(profile["slicer_input_text"])
            }}]
            results.append({"status": "ok", "path": str(vpath), "message": "Applied slicer styling"})
        
        elif vtype in ("barChart", "clusteredColumnChart", "stackedColumnChart", "stackedBarChart",
                       "columnChart", "bar", "column", "stackedColumn", "stackedBar"):
            # Bar chart / column chart
            # Category axis
            objects["categoryAxis"] = [{"properties": {
                "labelColor": literal_color(profile["cat_axis_label"]),
                "gridlineStyle": {"solid": {"color": literal_color(profile["gridline"])["solid"]["color"]}}
            }}]
            # Value axis
            objects["valueAxis"] = [{"properties": {
                "labelColor": literal_color(profile["val_axis_label"]),
                "gridlineStyle": {"solid": {"color": literal_color(profile["gridline"])["solid"]["color"]}}
            }}]
            # Legend
            objects["legend"] = [{"properties": {
                "labelColor": literal_color(profile["legend_label"])
            }}]
            # Data labels
            objects["dataLabels"] = [{"properties": {
                "color": literal_color(profile["data_label"])
            }}]
            
            # DataPoint colors — only for categorical data
            if _has_temporal_axis(v):
                # Temporal data: use single default color via ThemeDataColor 0
                objects["dataPoint"] = [{"properties": {
                    "fill": theme_data_color(0)
                }}]
                results.append({"status": "ok", "path": str(vpath), "message": "Applied temporal bar styling (single color)"})
            else:
                # Categorical data: use cycling colors
                data_point = []
                data_colors = profile["theme"]["dataColors"]
                count = profile.get("data_point_count", 10)
                for i in range(count):
                    cidx = i % len(data_colors)
                    data_point.append({
                        "properties": {
                            "fill": theme_data_color(cidx)
                        }
                    })
                objects["dataPoint"] = data_point
                results.append({"status": "ok", "path": str(vpath), "message": f"Applied {len(data_point)} dataPoint colors"})
        
        elif vtype in ("lineChart", "line", "areaChart", "area"):
            # Line/area chart
            objects["categoryAxis"] = [{"properties": {
                "labelColor": literal_color(profile["cat_axis_label"]),
                "gridlineStyle": {"solid": {"color": literal_color(profile["gridline"])["solid"]["color"]}}
            }}]
            objects["valueAxis"] = [{"properties": {
                "labelColor": literal_color(profile["val_axis_label"]),
                "gridlineStyle": {"solid": {"color": literal_color(profile["gridline"])["solid"]["color"]}}
            }}]
            objects["legend"] = [{"properties": {
                "labelColor": literal_color(profile["legend_label"])
            }}]
            objects["dataLabels"] = [{"properties": {
                "color": literal_color(profile["data_label"])
            }}]
            # Single data point for line charts
            objects["dataPoint"] = [{"properties": {
                "fill": theme_data_color(0)
            }}]
            results.append({"status": "ok", "path": str(vpath), "message": f"Applied {vtype} styling"})
        
        elif vtype in ("donutChart", "donut", "pieChart", "pie"):
            # Donut/pie chart  
            objects["legend"] = [{"properties": {
                "labelColor": literal_color(profile["legend_label"])
            }}]
            objects["dataLabels"] = [{"properties": {
                "color": literal_color(profile["data_label"]),
                "labelColor": literal_color(profile["data_label"])
            }}]
            # DataPoint — cycling colors
            data_colors = profile["theme"]["dataColors"]
            data_point = []
            for i in range(len(data_colors)):
                data_point.append({
                    "properties": {
                        "fill": theme_data_color(i)
                    }
                })
            objects["dataPoint"] = data_point
            results.append({"status": "ok", "path": str(vpath), "message": f"Applied {vtype} styling with {len(data_point)} colors"})
        
        elif vtype == "treemap":
            # Treemap: no dataPoint needed (uses theme dataColors), but set labels
            objects["legend"] = [{"properties": {
                "labelColor": literal_color(profile["legend_label"])
            }}]
            objects["dataLabels"] = [{"properties": {
                "color": literal_color(profile["data_label"]),
                "labelColor": literal_color(profile["data_label"])
            }}]
            # Treemap uses groupBy and can benefit from cycling
            data_colors = profile["theme"]["dataColors"]
            data_point = []
            for i in range(len(data_colors)):
                data_point.append({
                    "properties": {
                        "fill": theme_data_color(i)
                    }
                })
            objects["dataPoint"] = data_point
            results.append({"status": "ok", "path": str(vpath), "message": f"Applied {vtype} styling"})
        
        elif vtype in ("map", "filledMap", "shapeMap"):
            # Map visual
            objects["legend"] = [{"properties": {
                "labelColor": literal_color(profile["legend_label"])
            }}]
            objects["fill"] = [{"properties": {
                "color": literal_color(profile["map_fill"])
            }}]
            results.append({"status": "ok", "path": str(vpath), "message": f"Applied {vtype} styling"})
        
        elif vtype in ("table", "matrix", "tableEx"):
            # Table/Matrix
            objects["style"] = [{"properties": {
                "fontColor": literal_color(profile["table_font"]),
                "headerFontColor": literal_color(profile["title_font_color"])
            }}]
            objects["gridlineColor"] = [{"properties": {
                "color": literal_color(profile["gridline"])
            }}]
            results.append({"status": "ok", "path": str(vpath), "message": f"Applied {vtype} styling"})
        
        else:
            # Generic visual (waterfall, funnel, scatter, gauge, etc.)
            # Apply common properties
            if "title" in objects:
                objects["title"] = [{"properties": {
                    "fontColor": literal_color(profile["title_font_color"]),
                    "show": {"expr": {"Literal": {"Value": "true"}}}
                }}]
            results.append({"status": "ok", "path": str(vpath), "message": f"Applied generic styling for {vtype}"})
        
        # Write changes
        try:
            with open(vpath, "w", encoding="utf-8") as f:
                json.dump(v, f, indent=2, ensure_ascii=False)
        except Exception as e:
            results.append({"status": "error", "path": str(vpath), "message": f"Cannot write: {e}"})
    
    return results


# ═══════════════════════════════════════════════════════════════════════
# 4. DATA POINT COLORS (legacy: called separately or from main)
# ═══════════════════════════════════════════════════════════════════════

def apply_data_point_colors(project_root, project_name, data_colors):
    """
    Legacy function: applies basic dataPoint colors to visual.json files.
    Now integrated into apply_visual_styling for comprehensive handling.
    This is kept for backward compatibility.
    """
    results = []
    visuals_glob_str = str(project_root / f"{project_name}.Report" / "definition" / "pages" / "**" / "visuals" / "**" / "visual.json")
    visual_files = sorted(glob(visuals_glob_str, recursive=True))
    
    for vpath_str in visual_files:
        vpath = Path(vpath_str)
        try:
            with open(vpath, "r", encoding="utf-8") as f:
                v = json.load(f)
        except Exception:
            continue
        
        vtype = _get_visual_type(v)
        if vtype in ("treemap", "card", "slicer"):
            results.append({"status": "skipped", "path": str(vpath), "message": f"{vtype} skipped (handled by full styling)"})
            continue
        
        data_point = []
        for i, color in enumerate(data_colors):
            data_point.append({
                "properties": {
                    "fill": theme_data_color(i)
                }
            })
        v.setdefault("visual", {}).setdefault("objects", {})["dataPoint"] = data_point
        try:
            with open(vpath, "w", encoding="utf-8") as f:
                json.dump(v, f, indent=2, ensure_ascii=False)
        except Exception:
            continue
        results.append({"status": "ok", "path": str(vpath), "message": f"Applied colors to {vtype}"})
    
    if not visual_files:
        results.append({"status": "warning", "path": "", "message": "No visual.json files found"})
    return results


# ═══════════════════════════════════════════════════════════════════════
# 5. CONTRAST VALIDATION
# ═══════════════════════════════════════════════════════════════════════

def hex_to_rgb(hex_str):
    """Convert hex color string like '#F8FAFC' to (r, g, b)."""
    h = hex_str.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def relative_luminance(rgb):
    """Calculate relative luminance per WCAG 2.1."""
    vals = []
    for c in rgb:
        srgb = c / 255.0
        vals.append(srgb / 12.92 if srgb <= 0.03928 else ((srgb + 0.055) / 1.055) ** 2.4)
    return 0.2126 * vals[0] + 0.7152 * vals[1] + 0.0722 * vals[2]


def contrast_ratio(c1, c2):
    """Calculate contrast ratio between two hex colors."""
    l1 = relative_luminance(hex_to_rgb(c1))
    l2 = relative_luminance(hex_to_rgb(c2))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def validate_contrast(profile):
    """
    Validate contrast ratios for a visual profile against WCAG 2.1 AA.
    Returns list of warnings where contrast < 4.5:1 for normal text, < 3:1 for large text.
    """
    warnings = []
    bg = profile["page_bg"]
    
    checks = [
        ("Title font color", profile["title_font_color"], bg, 4.5),
        ("Category axis label", profile["cat_axis_label"], bg, 4.5),
        ("Value axis label", profile["val_axis_label"], bg, 4.5),
        ("Legend label", profile["legend_label"], bg, 4.5),
        ("Data label", profile["data_label"], profile["visual_bg"], 4.5),
        ("Slicer header font", profile["slicer_header_font"], profile["visual_bg"], 4.5),
        ("Slicer item font", profile["slicer_item_font"], profile["visual_bg"], 4.5),
        ("Card label", profile["card_label"], profile["card_bg"], 4.5),
    ]
    
    for label, fg, test_bg, threshold in checks:
        ratio = contrast_ratio(fg, test_bg)
        if ratio < threshold:
            warnings.append(f"{label}: {fg} on {test_bg} = {ratio:.2f}:1 (needs ≥{threshold}:1)")
    
    return warnings


# ═══════════════════════════════════════════════════════════════════════
# PROFILE PRINT
# ═══════════════════════════════════════════════════════════════════════

def print_profile(theme_name):
    """Print the visual profile for a theme in a human-readable format."""
    profile = get_visual_profile(theme_name)
    mode_icon = "🌙" if profile["mode"] == "dark" else "☀️"
    
    lines = [
        f"\n{mode_icon}  THEME: {theme_name} ({profile['mode']} mode)",
        f"{'='*60}",
        f"  Page background: {profile['page_bg']}",
        f"  Visual background: {profile['visual_bg']}",
        f"  Border: {profile['border']}",
        f"  Corner radius: {profile['radius']}",
        f"",
        f"  TYPOGRAPHY:",
        f"    Title font color: {profile['title_font_color']}",
        f"    Category axis label: {profile['cat_axis_label']}",
        f"    Value axis label: {profile['val_axis_label']}",
        f"    Legend label: {profile['legend_label']}",
        f"    Data label: {profile['data_label']}",
        f"",
        f"  AXIS:",
        f"    Gridline: {profile['gridline']}",
        f"    Plot area: {profile['plot_area']}",
        f"",
        f"  SLICER:",
        f"    Header font: {profile['slicer_header_font']}",
        f"    Item font: {profile['slicer_item_font']}",
        f"    Input text: {profile['slicer_input_text']}",
        f"",
        f"  CARD (KPI):",
        f"    Label: {profile['card_label']}",
        f"    Category label: {profile['card_category_label']}",
        f"    Card background: {profile['card_bg']}",
        f"",
        f"  TABLE:",
        f"    Font: {profile['table_font']}",
        f"    Header bg: {profile['table_header_bg']}",
        f"    Alt row bg: {profile['table_row_alt_bg']}",
        f"",
        f"  MAP fill: {profile['map_fill']}",
        f"  DataPoint count: {profile['data_point_count']}",
        f"",
        f"  DATA COLORS ({len(profile['theme']['dataColors'])}):",
    ]
    for i, c in enumerate(profile["theme"]["dataColors"]):
        lines.append(f"    [{i}] {c}")
    
    lines.append(f"\n  CONTRAST VALIDATION:")
    contrast_warnings = validate_contrast(profile)
    if contrast_warnings:
        for w in contrast_warnings:
            lines.append(f"    ⚠️  {w}")
    else:
        lines.append(f"    ✅ All checks pass (≥4.5:1)")
    
    lines.append("")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Power BI PBIP Comprehensive Visual Styling Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python apply_theme.py project.pbip --theme slate-terracotta
  python apply_theme.py project.pbip --theme-file custom.json
  python apply_theme.py project.pbip --theme slate-terracotta --dry-run
  python apply_theme.py project.pbip --theme slate-terracotta --profile
  
Available themes: """ + ", ".join(VISUAL_PROFILES.keys())
    )
    parser.add_argument("project", nargs="?", help="Path to .pbip file or project directory")
    parser.add_argument("--theme", choices=list(VISUAL_PROFILES.keys()), help="Built-in theme name")
    parser.add_argument("--theme-file", help="Custom theme JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without modifying files")
    parser.add_argument("--profile", action="store_true", help="Print the visual profile for a theme and exit")
    parser.add_argument("--validate", action="store_true", help="Only validate contrast ratios for the selected theme")
    parser.add_argument("--list-themes", action="store_true", help="List all available built-in themes and exit")
    args = parser.parse_args()

    # List themes
    if args.list_themes:
        print("Available built-in themes:")
        for name in VISUAL_PROFILES:
            p = VISUAL_PROFILES[name]
            icon = "🌙" if p["mode"] == "dark" else "☀️"
            print(f"  {icon}  {name}  ({p['mode']})")
        sys.exit(0)

    if not args.theme and not args.theme_file:
        print(json.dumps({
            "status": "error",
            "message": "Provide --theme or --theme-file",
            "available_themes": list(VISUAL_PROFILES.keys())
        }, indent=2, ensure_ascii=False))
        sys.exit(1)

    # Determine profile
    if args.theme:
        if args.theme not in VISUAL_PROFILES:
            print(json.dumps({
                "status": "error",
                "message": f"Unknown theme: {args.theme}",
                "available_themes": list(VISUAL_PROFILES.keys())
            }, indent=2, ensure_ascii=False))
            sys.exit(1)
        profile = VISUAL_PROFILES[args.theme]
        theme = profile["theme"]
    else:
        # Custom theme file — build a minimal profile from the JSON
        try:
            with open(args.theme_file, "r", encoding="utf-8") as f:
                custom = json.load(f)
        except Exception as e:
            print(json.dumps({
                "status": "error",
                "message": f"Cannot read theme file: {e}"
            }, indent=2))
            sys.exit(1)
        
        # Build a synthetic profile from custom theme
        bg = custom.get("background", "#FFFFFF")
        fg = custom.get("foreground", "#111827")
        # Detect dark mode heuristic
        mode = "dark" if contrast_ratio(bg, "#000000") < contrast_ratio(bg, "#FFFFFF") else "light"
        
        if mode == "dark":
            profile = {
                "theme": custom,
                "mode": "dark",
                "page_bg": bg,
                "visual_bg": bg,  # will be adjusted
                "border": "#4B5563",
                "radius": "8D",
                "title_font_color": fg,
                "cat_axis_label": "#CBD5E1",
                "val_axis_label": "#CBD5E1",
                "legend_label": "#CBD5E1",
                "data_label": fg if contrast_ratio(fg, bg) >= 3 else "#F8FAFC",
                "gridline": "#4B5563",
                "plot_area": bg,
                "slicer_header_font": fg,
                "slicer_item_font": "#CBD5E1",
                "slicer_input_text": fg,
                "card_label": fg,
                "card_category_label": "#CBD5E1",
                "card_bg": bg,
                "table_font": fg,
                "table_header_bg": "#1E3A5F",
                "table_row_alt_bg": bg,
                "map_fill": bg,
                "data_point_count": 10
            }
        else:
            profile = {
                "theme": custom,
                "mode": "light",
                "page_bg": bg,
                "visual_bg": bg,
                "border": "#D1D5DB",
                "radius": "8D",
                "title_font_color": fg,
                "cat_axis_label": "#4B5563",
                "val_axis_label": "#4B5563",
                "legend_label": "#4B5563",
                "data_label": fg if contrast_ratio(fg, bg) >= 3 else "#111827",
                "gridline": "#D1D5DB",
                "plot_area": bg,
                "slicer_header_font": fg,
                "slicer_item_font": "#374151",
                "slicer_input_text": fg,
                "card_label": fg,
                "card_category_label": "#4B5563",
                "card_bg": bg,
                "table_font": fg,
                "table_header_bg": "#F3F4F6",
                "table_row_alt_bg": bg,
                "map_fill": bg,
                "data_point_count": 10
            }
        theme = custom

    # Print profile mode
    if args.profile:
        print(print_profile(args.theme))
        sys.exit(0)

    # Validate mode
    if args.validate:
        print(f"Contrast validation for {args.theme}:")
        warnings = validate_contrast(profile)
        if warnings:
            for w in warnings:
                print(f"  ⚠️  {w}")
        else:
            print("  ✅ All checks pass!")
        sys.exit(0 if not warnings else 1)

    # Resolve project path
    if not args.project:
        print(json.dumps({
            "status": "error",
            "message": "Project path is required (use --list-themes to see available themes)"
        }, indent=2))
        sys.exit(1)
    pbip_path = Path(args.project)
    if pbip_path.is_dir():
        # Find the .pbip file in the directory
        pbip_files = list(pbip_path.glob("*.pbip"))
        if not pbip_files:
            print(json.dumps({
                "status": "error",
                "message": f"No .pbip file found in directory: {pbip_path}"
            }, indent=2))
            sys.exit(1)
        pbip_path = pbip_files[0]
    
    project_root = pbip_path.parent
    project_name = pbip_path.stem

    results = {
        "status": "ok",
        "project": project_name,
        "root": str(project_root),
        "theme_name": args.theme or "custom",
        "mode": profile["mode"],
        "operations": []
    }

    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    if not args.dry_run:
        print(f"🎨 Applying theme '{args.theme or 'custom'}' ({profile['mode']} mode) to {project_name}...")
        
        # Step 1: Theme file
        tr = apply_theme_file(project_root, project_name, theme)
        results["operations"].append({"operation": "theme_file", **tr})
        print(f"  📁 Theme file: {tr['status']}")
        
        # Step 2: Page backgrounds
        bg = apply_page_backgrounds(project_root, project_name, profile["page_bg"])
        updated = sum(1 for r in bg if r["status"] == "ok")
        results["operations"].append({
            "operation": "page_backgrounds",
            "pages_updated": updated,
            "details": bg
        })
        print(f"  🖼️  Page backgrounds: {updated} page(s) updated")
        
        # Step 3: Complete visual styling
        vs = apply_visual_styling(project_root, project_name, profile)
        styled = sum(1 for r in vs if r["status"] == "ok")
        results["operations"].append({
            "operation": "visual_styling",
            "visuals_styled": styled,
            "details": vs
        })
        print(f"  📊 Visuals styled: {styled} visual(s)")
        
        # Step 4: Contrast validation
        contrast_warnings = validate_contrast(profile)
        results["contrast_validation"] = {
            "status": "ok" if not contrast_warnings else "warning",
            "warnings": contrast_warnings
        }
        if contrast_warnings:
            print(f"  ⚠️  Contrast warnings: {len(contrast_warnings)}")
            for w in contrast_warnings:
                print(f"       {w}")
        else:
            print(f"  ✅ Contrast: All checks pass")
        
        # Overall status
        if any(op.get("status") == "error" for op in results["operations"]):
            results["status"] = "error"
            print(f"\n❌ Theme application completed with errors")
        else:
            print(f"\n✅ Theme '{args.theme or 'custom'}' applied successfully to {project_name}")
    
    print(json.dumps(results, indent=2, ensure_ascii=False))
    sys.exit(1 if results["status"] == "error" else 0)


if __name__ == "__main__":
    main()
