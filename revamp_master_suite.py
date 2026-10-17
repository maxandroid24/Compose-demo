import os
import re
import html
import json

import build_full_suite
from detailed_activity_explanations import ACTIVITY_LINE_EXPLANATIONS
from line_analyzer import get_rule_based_explanation
from build_symbol_index import generate_symbol_database

ROOT_DIR = build_full_suite.ROOT_DIR
ALL_FILES = build_full_suite.ALL_FILES
TOKEN_REGEX = build_full_suite.TOKEN_REGEX

print("Rebuilding Web Application with Revamped Editorial-Developer Design System...")

SYMBOL_DATABASE = generate_symbol_database()
KNOWN_SYMBOLS = set(SYMBOL_DATABASE.keys())

def highlight_line_with_symbols(line, state, known_symbols):
    in_comment = state['in_comment']
    in_string = state['in_string']
    
    if in_comment:
        if '*/' in line:
            idx = line.find('*/') + 2
            cmt_part = html.escape(line[:idx])
            rest = line[idx:]
            state['in_comment'] = False
            return f'<span class="tok-cmt">{cmt_part}</span>' + highlight_line_with_symbols(rest, state, known_symbols)
        else:
            return f'<span class="tok-cmt">{html.escape(line)}</span>'
            
    if in_string:
        if '"""' in line:
            idx = line.find('"""') + 3
            str_part = html.escape(line[:idx])
            rest = line[idx:]
            state['in_string'] = False
            return f'<span class="tok-str">{str_part}</span>' + highlight_line_with_symbols(rest, state, known_symbols)
        else:
            return f'<span class="tok-str">{html.escape(line)}</span>'

    out = []
    last_idx = 0
    for m in TOKEN_REGEX.finditer(line):
        start, end = m.span()
        if start > last_idx:
            out.append(html.escape(line[last_idx:start]))
            
        group = m.lastgroup
        text = m.group(0)
        escaped = html.escape(text)
        
        if group == 'COMMENT':
            out.append(f'<span class="tok-cmt">{escaped}</span>')
        elif group == 'STRING':
            out.append(f'<span class="tok-str">{escaped}</span>')
        elif group == 'ANNOTATION':
            out.append(f'<span class="tok-ann">{escaped}</span>')
        elif group == 'KEYWORD':
            out.append(f'<span class="tok-kw">{escaped}</span>')
        elif group == 'NUMBER':
            out.append(f'<span class="tok-num">{escaped}</span>')
        elif group == 'TYPE':
            if text in known_symbols:
                out.append(f'<span class="tok-type sym-link" data-sym="{escaped}" onclick="handleSymbolClick(event, \'{escaped}\')">{escaped}</span>')
            else:
                out.append(f'<span class="tok-type">{escaped}</span>')
        elif group == 'FUNCTION':
            clean_name = text.split('(')[0].split('<')[0].strip()
            if clean_name in known_symbols:
                out.append(f'<span class="tok-fn sym-link" data-sym="{clean_name}" onclick="handleSymbolClick(event, \'{clean_name}\')">{escaped}</span>')
            else:
                out.append(f'<span class="tok-fn">{escaped}</span>')
            
        last_idx = end
        
    if last_idx < len(line):
        rest = line[last_idx:]
        if '/*' in rest and '*/' not in rest:
            idx = rest.find('/*')
            out.append(html.escape(rest[:idx]))
            out.append(f'<span class="tok-cmt">{html.escape(rest[idx:])}</span>')
            state['in_comment'] = True
        elif '"""' in rest and rest.count('"""') % 2 == 1:
            idx = rest.find('"""')
            out.append(html.escape(rest[:idx]))
            out.append(f'<span class="tok-str">{html.escape(rest[idx:])}</span>')
            state['in_string'] = True
        else:
            out.append(html.escape(rest))
            
    return ''.join(out)

# Architectural tier categorization helper
def get_architecture_layer(cat, file_id, name):
    name_lower = name.lower()
    if 'activity' in name_lower or 'screen' in name_lower or 'dialog' in name_lower:
        return {'layer': 'Presentation', 'badge': 'UI Layer', 'tier': 1, 'color': 'var(--accent-primary)'}
    elif 'viewmodel' in name_lower or 'state' in name_lower:
        return {'layer': 'ViewModel & State', 'badge': 'State Layer', 'tier': 2, 'color': '#8B5CF6'}
    elif 'usecase' in name_lower:
        return {'layer': 'Domain Use Cases', 'badge': 'Domain Layer', 'tier': 3, 'color': '#06B6D4'}
    elif 'repository' in name_lower or 'api' in name_lower:
        return {'layer': 'Data Repository', 'badge': 'Repo Layer', 'tier': 4, 'color': '#10B981'}
    elif 'dao' in name_lower or 'entity' in name_lower or 'database' in name_lower:
        return {'layer': 'Local Persistence', 'badge': 'Room DB', 'tier': 5, 'color': '#F59E0B'}
    elif 'worker' in name_lower or 'service' in name_lower or 'receiver' in name_lower:
        return {'layer': 'Background Services', 'badge': 'Async System', 'tier': 4, 'color': '#EC4899'}
    elif 'di' in name_lower or 'module' in name_lower:
        return {'layer': 'Dependency Injection', 'badge': 'Hilt DI', 'tier': 0, 'color': '#6366F1'}
    return {'layer': 'Core Utilities', 'badge': 'Utility', 'tier': 3, 'color': 'var(--text-muted)'}

# Compose vs XML Activity mapping
COMPOSE_XML_PAIRS = {
    'act_task_list_compose': {
        'counterpart': 'act_task_list_xml',
        'counterpart_name': 'TaskListXmlActivity.kt',
        'title': 'Task List: Jetpack Compose vs Imperative XML ViewBinding',
        'compose_highlights': 'Declarative UI with LazyColumn and collectAsStateWithLifecycle(). Eliminates RecyclerView adapters, ViewHolder boilerplate, and imperative View mutations.',
        'xml_highlights': 'Imperative ViewBinding, RecyclerView with custom ListAdapter, DiffUtil callback, and manual View state synchronization.'
    },
    'act_task_list_xml': {
        'counterpart': 'act_task_list_compose',
        'counterpart_name': 'TaskListComposeActivity.kt',
        'title': 'Task List: Imperative XML ViewBinding vs Jetpack Compose',
        'compose_highlights': 'Declarative UI with LazyColumn and collectAsStateWithLifecycle(). Eliminates RecyclerView adapters, ViewHolder boilerplate, and imperative View mutations.',
        'xml_highlights': 'Imperative ViewBinding, RecyclerView with custom ListAdapter, DiffUtil callback, and manual View state synchronization.'
    },
    'act_task_detail_compose': {
        'counterpart': 'act_task_detail_xml',
        'counterpart_name': 'TaskDetailXmlActivity.kt',
        'title': 'Task Detail: Jetpack Compose vs Imperative XML',
        'compose_highlights': 'Reactive Form with TextField, DropdownMenu, and auto-validating state. No XML findViewById or ButterKnife/ViewBinding overhead.',
        'xml_highlights': 'ActivityTaskDetailBinding inflating activity_task_detail.xml, manual text watcher listeners, and imperative error setters.'
    },
    'act_task_detail_xml': {
        'counterpart': 'act_task_detail_compose',
        'counterpart_name': 'TaskDetailComposeActivity.kt',
        'title': 'Task Detail: Imperative XML vs Jetpack Compose',
        'compose_highlights': 'Reactive Form with TextField, DropdownMenu, and auto-validating state. No XML findViewById or ButterKnife/ViewBinding overhead.',
        'xml_highlights': 'ActivityTaskDetailBinding inflating activity_task_detail.xml, manual text watcher listeners, and imperative error setters.'
    },
    'act_analytics_compose': {
        'counterpart': 'act_analytics_xml',
        'counterpart_name': 'TaskAnalyticsXmlActivity.kt',
        'title': 'Analytics Dashboard: Compose Canvas vs Custom XML Views',
        'compose_highlights': 'Declarative Canvas drawArc() and AnimatedContent for smooth productivity charts directly in Kotlin code.',
        'xml_highlights': 'Custom View XML definitions with styled-attributes, onDraw() overrides, and manual ValueAnimator synchronization.'
    },
    'act_analytics_xml': {
        'counterpart': 'act_analytics_compose',
        'counterpart_name': 'TaskAnalyticsComposeActivity.kt',
        'title': 'Analytics Dashboard: Custom XML Views vs Compose Canvas',
        'compose_highlights': 'Declarative Canvas drawArc() and AnimatedContent for smooth productivity charts directly in Kotlin code.',
        'xml_highlights': 'Custom View XML definitions with styled-attributes, onDraw() overrides, and manual ValueAnimator synchronization.'
    },
    'act_settings_compose': {
        'counterpart': 'act_settings_xml',
        'counterpart_name': 'SettingsXmlActivity.kt',
        'title': 'Preferences & Settings: Compose Switch vs PreferenceFragmentCompat',
        'compose_highlights': 'Stateless Switch composables linked to DataStore Preferences Flow with zero lifecycle leaks.',
        'xml_highlights': 'Legacy PreferenceScreen XML definitions with SharedPreferences listeners requiring manual unregister onStop().'
    },
    'act_settings_xml': {
        'counterpart': 'act_settings_compose',
        'counterpart_name': 'SettingsComposeActivity.kt',
        'title': 'Preferences & Settings: PreferenceFragmentCompat vs Compose Switch',
        'compose_highlights': 'Stateless Switch composables linked to DataStore Preferences Flow with zero lifecycle leaks.',
        'xml_highlights': 'Legacy PreferenceScreen XML definitions with SharedPreferences listeners requiring manual unregister onStop().'
    },
    'act_contact_compose': {
        'counterpart': 'act_contact_xml',
        'counterpart_name': 'ContactPickerXmlActivity.kt',
        'title': 'Contact Picker: Modern ActivityResultContracts vs startActivityForResult',
        'compose_highlights': 'rememberLauncherForActivityResult() integrated directly inside Composable lifecycle.',
        'xml_highlights': 'Deprecated onActivityResult() requestCode inspection or ActivityResultLauncher managed in Activity onCreate.'
    },
    'act_contact_xml': {
        'counterpart': 'act_contact_compose',
        'counterpart_name': 'ContactPickerComposeActivity.kt',
        'title': 'Contact Picker: Legacy Activity Lifecycle vs Compose Result Contract',
        'compose_highlights': 'rememberLauncherForActivityResult() integrated directly inside Composable lifecycle.',
        'xml_highlights': 'Deprecated onActivityResult() requestCode inspection or ActivityResultLauncher managed in Activity onCreate.'
    }
}

# Architectural review notes (nested discussion threads)
FILE_REVIEW_NOTES = {
    'act_task_list_compose': [
        {
            'author': 'Staff Mobile Architect',
            'role': 'Architecture Lead',
            'avatar': '🏛️',
            'time': 'Production Review',
            'comment': 'Notice how <code>collectAsStateWithLifecycle()</code> handles Android configuration changes and backgrounding. Unlike legacy <code>collectAsState()</code>, it automatically pauses upstream Flow emissions when the Activity drops below <code>Lifecycle.State.STARTED</code>, preventing background CPU and battery drain.',
            'replies': [
                {
                    'author': 'Senior Android Engineer',
                    'role': 'Compose Core Team',
                    'avatar': '⚡',
                    'time': 'Follow-up',
                    'comment': 'Crucially, the ViewModel uses <code>SharingStarted.WhileSubscribed(5000)</code>. The 5-second buffer prevents Room queries from restarting during rapid screen rotations while still tearing down connections when the app goes into the background.'
                }
            ]
        }
    ],
    'vm_task': [
        {
            'author': 'Principal Engineer',
            'role': 'State Management Lead',
            'avatar': '📐',
            'time': 'State Review',
            'comment': 'The combination of <code>searchQuery.debounce(200)</code> with <code>combine()</code> ensures search queries never flood SQLite with transient keystrokes while maintaining instant responsive UI state.',
            'replies': [
                {
                    'author': 'Database Engineer',
                    'role': 'Room & SQLite Specialist',
                    'avatar': '💾',
                    'time': 'Follow-up',
                    'comment': 'The Room DAO query uses an indexed composite index on <code>(isCompleted, priority, createdAt)</code>, allowing queries across 100,000+ tasks to execute in under 2ms.'
                }
            ]
        }
    ]
}

# Build file data dictionary
files_data_dict = {}

for cfg in ALL_FILES:
    file_id = cfg["id"]
    file_name = cfg["name"]
    file_cat = cfg["category"]
    raw_code = cfg["raw_code"]
    lines = raw_code.splitlines()
    
    # Handcrafted explanations
    handcrafted = ACTIVITY_LINE_EXPLANATIONS.get(file_id, [])
    hc_map = {}
    for item in handcrafted:
        if "line" in item:
            hc_map[item["line"]] = item
        elif "lines" in item:
            start, end = item["lines"]
            for l in range(start, end + 1):
                hc_map[l] = item
                
    explanations = []
    for idx, raw_l in enumerate(lines, 1):
        if idx in hc_map:
            hc_item = hc_map[idx]
            explanations.append({
                "line": idx,
                "code": raw_l.strip(),
                "why": hc_item["why"],
                "what": hc_item["what"],
                "concept": hc_item.get("concept", "Architecture Rationale")
            })
        else:
            rule_item = get_rule_based_explanation(idx, raw_l, file_name, file_cat)
            if rule_item:
                explanations.append(rule_item)
            else:
                explanations.append({
                    "line": idx,
                    "code": raw_l.strip(),
                    "why": f"Part of the architectural implementation of {file_name}.",
                    "what": "Evaluated during lifecycle execution of this component.",
                    "concept": "General Implementation"
                })

    state = {'in_comment': False, 'in_string': False}
    html_lines = []
    parallel_rows = []
    
    for idx, line in enumerate(lines, 1):
        highlighted = highlight_line_with_symbols(line, state, KNOWN_SYMBOLS)
        exp_item = explanations[idx - 1] if idx - 1 < len(explanations) else None
        
        html_lines.append(
            f'<div class="code-line" id="line-{file_id}-{idx}" data-file="{file_id}" data-line="{idx}" '
            f'onclick="selectCodeLine(\'{file_id}\', {idx})" title="Click to inspect Line {idx}">'
            f'<span class="line-num">{idx}</span><span class="line-code">{highlighted}</span></div>'
        )
        
        why_text = html.escape(exp_item["why"]) if exp_item else ""
        what_text = html.escape(exp_item["what"]) if exp_item else ""
        concept_text = html.escape(exp_item.get("concept", "")) if exp_item else ""
        
        parallel_rows.append(
            f'<tr class="parallel-row" id="prow-{file_id}-{idx}" onclick="selectCodeLine(\'{file_id}\', {idx})">'
            f'<td class="parallel-col-code"><span class="line-num-inline">{idx}</span><span style="white-space:pre;">{highlighted}</span></td>'
            f'<td class="parallel-col-why"><div class="p-why-label">🎯 Why Added</div><div class="editorial-reading-sm">{why_text}</div></td>'
            f'<td class="parallel-col-what"><div class="p-what-label">⚙️ What It Does</div><div class="editorial-reading-sm">{what_text}</div>{f"<div class=\'p-concept\'>💡 {concept_text}</div>" if concept_text else ""}</td>'
            f'</tr>'
        )

    arch_info = get_architecture_layer(file_cat, file_id, file_name)
    compare_pair = COMPOSE_XML_PAIRS.get(file_id, None)
    review_notes = FILE_REVIEW_NOTES.get(file_id, [
        {
            'author': 'Android Code Review',
            'role': 'Clean Architecture Guard',
            'avatar': '📐',
            'time': 'Production Quality',
            'comment': f'This {file_name} adheres to strict Clean Architecture separation of concerns, providing high testability and isolation within the {arch_info["layer"]}.',
            'replies': []
        }
    ])

    files_data_dict[file_id] = {
        "id": file_id,
        "name": file_name,
        "relPath": cfg["rel_path"],
        "category": file_cat,
        "badge": cfg["badge"],
        "summary": cfg["summary"],
        "lineCount": len(lines),
        "annotations": cfg["annotations"],
        "breakdown": cfg["breakdown"],
        "rawCode": raw_code,
        "formattedCode": "\n".join(html_lines),
        "parallelRowsHtml": "\n".join(parallel_rows),
        "explanations": explanations,
        "arch": arch_info,
        "comparePair": compare_pair,
        "reviewNotes": review_notes
    }

# Group by category for sidebar
categories = {}
for cfg in ALL_FILES:
    cat = cfg["category"]
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(cfg)

# Serialize JSON data
json_files_data = json.dumps(files_data_dict)
json_symbols = json.dumps(SYMBOL_DATABASE)

# Assemble Master HTML with the Editorial-Developer Design System
html_out = f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
  <title>Android Task Manager — Architecture & Code Studio</title>
  
  <!-- Premium Editorial and Developer Typography -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&display=swap" rel="stylesheet">
  
  <style>
    /* ========================================================
       REVAMPED DESIGN SYSTEM: EDITORIAL-MEETS-DEVELOPER
       Default: Light Mode with Dim/Dark Mode Toggle
       ======================================================== */
    :root, [data-theme="light"] {{
      --theme-name: "light";
      --bg-base: #F9F9F8;
      --bg-surface: #FFFFFF;
      --bg-surface-elevated: #F2F2EF;
      --bg-card: #FFFFFF;
      --bg-well: #F5F5F3;
      
      --border-subtle: #E8E7E3;
      --border-strong: #D5D3CC;
      --border-focus: #2563EB;

      --text-main: #1C1B18;
      --text-muted: #57554F;
      --text-dim: #88867E;
      --text-serif: #282724;

      --accent-primary: #1E40AF;
      --accent-primary-hover: #1D4ED8;
      --accent-glow: rgba(30, 64, 175, 0.08);
      --accent-secondary: #6D28D9;
      --accent-teal: #0F766E;

      /* Minimalist Warm Gold Accent */
      --accent-gold: #B45309;
      --accent-gold-light: #F59E0B;
      --accent-gold-bg: rgba(245, 158, 11, 0.08);
      --accent-gold-border: rgba(245, 158, 11, 0.3);

      --accent-success: #15803D;
      --accent-warning: #B45309;
      --accent-danger: #B91C1C;

      /* Editor Canvas */
      --ide-bg: #F8F9FA;
      --ide-border: #E8E7E3;
      --ide-line-num: #9CA3AF;
      --ide-line-hover: #EFF2F5;
      --ide-text: #1F2937;
      --ide-active-line: rgba(37, 99, 235, 0.08);

      /* Shadows & Elevations */
      --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.04);
      --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.03);
      --shadow-card: 0 3px 12px -2px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.03);
      --shadow-modal: 0 20px 48px -8px rgba(0, 0, 0, 0.15), 0 8px 16px -4px rgba(0, 0, 0, 0.06);

      --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      --font-serif: 'Newsreader', 'Charter', 'Source Serif 4', 'Georgia', serif;
      --font-mono: 'JetBrains Mono', 'Fira Code', Menlo, Consolas, monospace;
      
      --sidebar-width: 310px;
    }}

    [data-theme="dark"], [data-theme="dim"] {{
      --theme-name: "dark";
      --bg-base: #111216;
      --bg-surface: #181A20;
      --bg-surface-elevated: #21242D;
      --bg-card: #181A20;
      --bg-well: #1C1E26;

      --border-subtle: #292D38;
      --border-strong: #383E4C;
      --border-focus: #60A5FA;

      --text-main: #EDEDEC;
      --text-muted: #A2A6B0;
      --text-dim: #717582;
      --text-serif: #E1E3E8;

      --accent-primary: #3B82F6;
      --accent-primary-hover: #60A5FA;
      --accent-glow: rgba(59, 130, 246, 0.18);
      --accent-secondary: #8B5CF6;
      --accent-teal: #14B8A6;

      /* Minimalist Warm Gold Accent */
      --accent-gold: #F59E0B;
      --accent-gold-light: #FBBF24;
      --accent-gold-bg: rgba(245, 158, 11, 0.12);
      --accent-gold-border: rgba(245, 158, 11, 0.32);

      --accent-success: #10B981;
      --accent-warning: #F59E0B;
      --accent-danger: #EF4444;

      /* Editor Canvas */
      --ide-bg: #1A1C24;
      --ide-border: #292D38;
      --ide-line-num: #5A6072;
      --ide-line-hover: #232632;
      --ide-text: #D5D9E2;
      --ide-active-line: rgba(59, 130, 246, 0.16);

      --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.25);
      --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.35);
      --shadow-card: 0 4px 20px -2px rgba(0, 0, 0, 0.45);
      --shadow-modal: 0 24px 60px rgba(0, 0, 0, 0.7);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      background-color: var(--bg-base); color: var(--text-main); font-family: var(--font-sans);
      line-height: 1.6; display: flex; height: 100vh; overflow: hidden;
      transition: background-color 0.22s ease, color 0.22s ease;
    }}

    /* Reduced Motion Preference */
    @media (prefers-reduced-motion: reduce) {{
      *, ::before, ::after {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
      }}
    }}

    /* Accessible focus outlines */
    :focus-visible {{
      outline: 2px solid var(--border-focus);
      outline-offset: 2px;
    }}

    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: var(--border-strong); border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--accent-gold); }}

    /* ========================================================
       SIDEBAR NAVIGATION & DRAWER
       ======================================================== */
    .sidebar {{
      width: var(--sidebar-width); background-color: var(--bg-surface); border-right: 1px solid var(--border-subtle);
      height: 100vh; display: flex; flex-direction: column; flex-shrink: 0; z-index: 100;
      transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    .sidebar-backdrop {{
      position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.45);
      backdrop-filter: blur(4px); display: none; z-index: 95;
    }}

    .sidebar-header {{
      padding: 16px 18px 14px; border-bottom: 1px solid var(--border-subtle); display: flex; align-items: center; justify-content: space-between;
    }}
    .sidebar-brand-group {{ display: flex; align-items: center; gap: 10px; }}
    .brand-icon {{
      width: 32px; height: 32px; border-radius: 8px; background: var(--accent-gold-bg);
      border: 1px solid var(--accent-gold-border); color: var(--accent-gold);
      display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 700;
    }}
    .brand-title {{ font-size: 14px; font-weight: 700; letter-spacing: -0.2px; color: var(--text-main); }}
    .brand-sub {{ font-size: 10px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.6px; font-weight: 600; }}

    .sidebar-close-btn {{
      display: none; background: transparent; border: none; color: var(--text-dim); font-size: 18px;
      cursor: pointer; padding: 6px; border-radius: 6px;
    }}
    .sidebar-close-btn:hover {{ background: var(--bg-surface-elevated); color: var(--text-main); }}

    /* Architecture Mastery Progress Widget */
    .mastery-progress-box {{
      padding: 12px 18px; background: var(--bg-well); border-bottom: 1px solid var(--border-subtle);
    }}
    .mastery-header {{
      display: flex; align-items: center; justify-content: space-between; font-size: 11px; margin-bottom: 6px;
    }}
    .mastery-title {{ font-weight: 600; color: var(--text-muted); display: flex; align-items: center; gap: 5px; }}
    .mastery-pct {{ font-family: var(--font-mono); font-size: 11px; font-weight: 700; color: var(--accent-gold); }}
    .mastery-bar-bg {{
      width: 100%; height: 5px; background: var(--border-subtle); border-radius: 4px; overflow: hidden;
    }}
    .mastery-bar-fill {{
      height: 100%; width: 12%; background: linear-gradient(90deg, var(--accent-gold), var(--accent-primary));
      border-radius: 4px; transition: width 0.4s ease;
    }}

    .sidebar-search {{ padding: 10px 14px; border-bottom: 1px solid var(--border-subtle); }}
    .search-input-box {{ position: relative; width: 100%; }}
    .search-input-box input {{
      width: 100%; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle);
      padding: 7px 12px 7px 32px; border-radius: 8px; color: var(--text-main); font-size: 12px; outline: none;
      transition: border-color 0.15s ease;
    }}
    .search-input-box input:focus {{ border-color: var(--border-focus); }}
    .search-input-box svg {{ position: absolute; left: 10px; top: 50%; transform: translateY(-50%); width: 13px; height: 13px; color: var(--text-dim); }}

    .sidebar-nav {{ flex: 1; overflow-y: auto; padding: 12px 0; -webkit-overflow-scrolling: touch; }}
    
    .sidebar-special-btn {{
      margin: 0 12px 12px; padding: 9px 12px; background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle); border-radius: 8px; color: var(--text-main);
      font-size: 12px; font-weight: 600; display: flex; align-items: center; gap: 8px; cursor: pointer; transition: all 0.15s ease;
    }}
    .sidebar-special-btn:hover, .sidebar-special-btn.active {{
      background: var(--accent-gold-bg); border-color: var(--accent-gold-border); color: var(--accent-gold);
    }}

    .category-group {{ margin-bottom: 14px; }}
    .category-label {{
      padding: 6px 16px; font-size: 10px; font-weight: 700; text-transform: uppercase;
      letter-spacing: 0.8px; color: var(--text-dim); display: flex; align-items: center; justify-content: space-between;
    }}
    .category-badge {{ background: var(--bg-surface-elevated); padding: 1px 6px; border-radius: 10px; font-size: 9px; font-family: var(--font-mono); }}

    .file-tree-item {{
      display: flex; align-items: center; gap: 8px; padding: 7px 16px; font-size: 12px;
      color: var(--text-muted); cursor: pointer; transition: all 0.15s ease; border-left: 2px solid transparent; user-select: none;
    }}
    .file-tree-item:hover {{ background-color: var(--bg-surface-elevated); color: var(--text-main); }}
    .file-tree-item.active {{
      background-color: var(--accent-glow); color: var(--accent-primary);
      border-left-color: var(--accent-primary); font-weight: 600;
    }}
    .file-tree-item.reviewed .item-badge {{
      background: var(--accent-gold-bg); color: var(--accent-gold); border: 1px solid var(--accent-gold-border);
    }}
    .item-badge {{ margin-left: auto; font-size: 9px; padding: 1px 5px; border-radius: 4px; background: var(--bg-surface-elevated); color: var(--text-dim); font-family: var(--font-mono); }}

    /* ========================================================
       MAIN WORKSPACE AREA
       ======================================================== */
    .main-wrapper {{
      flex: 1; display: flex; flex-direction: column; height: 100vh; overflow: hidden; min-width: 0;
    }}

    .top-header {{
      height: 52px; background-color: var(--bg-surface); border-bottom: 1px solid var(--border-subtle);
      display: flex; align-items: center; justify-content: space-between; padding: 0 18px; flex-shrink: 0; gap: 10px;
    }}
    .header-left {{ display: flex; align-items: center; gap: 12px; min-width: 0; }}
    
    .mobile-nav-toggle {{
      display: none; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle);
      color: var(--text-main); padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 600;
      align-items: center; gap: 6px; cursor: pointer; flex-shrink: 0;
    }}
    .mobile-nav-toggle:hover {{ border-color: var(--border-strong); }}

    /* Editorial Breadcrumb trail */
    .breadcrumb-trail {{
      display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}
    .breadcrumb-node {{ color: var(--text-dim); }}
    .breadcrumb-current {{ color: var(--text-main); font-weight: 600; font-family: var(--font-mono); font-size: 11.5px; }}

    .mobile-active-file-pill {{
      display: none;
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 600;
      color: var(--text-main);
      background: var(--bg-surface-elevated);
      padding: 3px 8px;
      border-radius: 6px;
      border: 1px solid var(--border-subtle);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 140px;
    }}

    .header-actions {{ display: flex; align-items: center; gap: 8px; flex-shrink: 0; }}

    .btn-pill {{
      background: var(--bg-surface); border: 1px solid var(--border-subtle); color: var(--text-muted);
      padding: 5px 11px; border-radius: 6px; font-size: 11.5px; font-weight: 500; text-decoration: none;
      display: flex; align-items: center; gap: 6px; cursor: pointer; transition: all 0.15s ease; white-space: nowrap;
    }}
    .btn-pill:hover {{ border-color: var(--border-strong); color: var(--text-main); background: var(--bg-surface-elevated); }}
    .btn-pill.primary {{ background: var(--accent-primary); border-color: var(--accent-primary); color: white; }}
    .btn-pill.primary:hover {{ background: var(--accent-primary-hover); }}
    .btn-pill.gold {{ background: var(--accent-gold-bg); border-color: var(--accent-gold-border); color: var(--accent-gold); font-weight: 600; }}

    /* Editor Tabs Bar */
    .editor-tabs-bar {{
      height: 38px; background: var(--bg-surface-elevated); border-bottom: 1px solid var(--border-subtle);
      display: flex; align-items: center; overflow-x: auto; padding: 0 10px; gap: 4px; flex-shrink: 0;
      scrollbar-width: none; -webkit-overflow-scrolling: touch;
    }}
    .editor-tabs-bar::-webkit-scrollbar {{ display: none; }}
    .editor-tab {{
      display: flex; align-items: center; gap: 8px; padding: 6px 12px; background: var(--bg-surface);
      border: 1px solid var(--border-subtle); border-bottom: none; border-radius: 6px 6px 0 0;
      font-size: 11.5px; color: var(--text-muted); cursor: pointer; white-space: nowrap; transition: all 0.15s; flex-shrink: 0;
    }}
    .editor-tab:hover {{ color: var(--text-main); }}
    .editor-tab.active {{
      background: var(--ide-bg); color: var(--accent-primary); font-weight: 600;
      border-color: var(--border-strong); border-top: 2px solid var(--accent-gold);
    }}
    .editor-tab-close {{
      font-size: 11px; color: var(--text-dim); border-radius: 3px; padding: 0 3px; cursor: pointer;
    }}
    .editor-tab-close:hover {{ background: var(--bg-surface-elevated); color: var(--text-main); }}

    /* Workspace Content Area */
    .workspace-content {{
      flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 20px;
      -webkit-overflow-scrolling: touch;
    }}

    /* Card Modular Layout */
    .card-modular {{
      background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 10px;
      box-shadow: var(--shadow-card); overflow: hidden; display: flex; flex-direction: column;
    }}

    /* Component Header with Editorial Subtext */
    .component-header {{
      padding: 16px 20px; background: var(--bg-surface); border-bottom: 1px solid var(--border-subtle);
      display: flex; align-items: center; justify-content: space-between; gap: 14px; flex-wrap: wrap;
    }}
    .file-meta {{ display: flex; align-items: center; gap: 12px; min-width: 0; }}
    .file-icon {{
      width: 32px; height: 32px; border-radius: 8px; background: var(--bg-well); border: 1px solid var(--border-subtle);
      color: var(--accent-primary); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 11.5px; flex-shrink: 0;
    }}
    .file-path {{ font-family: var(--font-mono); font-size: 13px; font-weight: 600; color: var(--text-main); word-break: break-all; }}
    .file-summary-editorial {{
      font-family: var(--font-serif); font-size: 13.5px; color: var(--text-muted); line-height: 1.5; font-style: italic; margin-top: 2px;
    }}

    /* Interactive Clean Architecture Node Pipeline Graph */
    .architecture-pipeline-strip {{
      padding: 12px 20px; background: var(--bg-well); border-bottom: 1px solid var(--border-subtle);
      display: flex; align-items: center; gap: 8px; overflow-x: auto; scrollbar-width: none;
    }}
    .pipeline-node {{
      display: flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 6px;
      background: var(--bg-surface); border: 1px solid var(--border-subtle); font-size: 11px;
      color: var(--text-muted); cursor: pointer; white-space: nowrap; transition: all 0.15s ease;
    }}
    .pipeline-node:hover {{ border-color: var(--border-strong); color: var(--text-main); }}
    .pipeline-node.active-tier {{
      background: var(--accent-glow); border-color: var(--accent-primary); color: var(--accent-primary); font-weight: 600;
    }}
    .pipeline-arrow {{ color: var(--text-dim); font-size: 10px; user-select: none; }}

    /* Compose vs XML Counterpart Banner */
    .compare-banner {{
      padding: 10px 20px; background: var(--accent-gold-bg); border-bottom: 1px solid var(--accent-gold-border);
      display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap;
    }}
    .compare-desc {{ font-size: 12px; color: var(--accent-gold); font-weight: 500; display: flex; align-items: center; gap: 6px; }}
    .compare-btn {{
      background: var(--bg-surface); border: 1px solid var(--accent-gold-border); color: var(--accent-gold);
      padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer; transition: all 0.15s;
    }}
    .compare-btn:hover {{ background: var(--accent-gold); color: white; }}

    /* View Mode Toggles */
    .view-mode-toggles {{
      display: flex; align-items: center; gap: 2px; background: var(--bg-surface-elevated); padding: 3px; border-radius: 6px; border: 1px solid var(--border-subtle);
    }}
    .v-btn {{
      background: transparent; border: none; color: var(--text-muted); font-size: 11px; font-weight: 500;
      padding: 4px 9px; border-radius: 5px; cursor: pointer; transition: all 0.15s; white-space: nowrap;
    }}
    .v-btn:hover {{ color: var(--text-main); }}
    .v-btn.active {{
      background: var(--bg-surface); color: var(--text-main); font-weight: 600; box-shadow: var(--shadow-xs);
    }}

    /* ========================================================
       SIDE-BY-SIDE SPLIT VIEW LAYOUT
       ======================================================== */
    .split-view-container {{
      display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(360px, 0.75fr);
      background: var(--bg-surface);
    }}

    .split-code-pane {{
      border-right: 1px solid var(--border-subtle); min-width: 0; overflow: hidden;
    }}

    .split-view-container.pane-expanded {{
      grid-template-columns: minmax(0, 0.85fr) minmax(420px, 1.15fr);
    }}

    .split-explainer-pane {{
      background: var(--bg-surface); padding: 20px; position: relative;
    }}

    .sticky-explainer-box {{
      display: flex; flex-direction: column; gap: 16px;
    }}
    
    .se-header {{
      background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 12px 14px;
      transition: border-color 0.15s, box-shadow 0.15s;
    }}
    .se-drag-handle {{
      display: none; width: 100%; justify-content: center; padding: 2px 0 10px; cursor: pointer;
    }}
    .se-drag-bar {{
      width: 40px; height: 4px; border-radius: 2px; background: var(--border-strong);
    }}

    .se-title-row {{
      display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; gap: 6px;
    }}
    .se-tag {{
      font-family: var(--font-mono); font-size: 11px; font-weight: 700; color: var(--accent-primary);
      background: var(--accent-glow); padding: 2px 8px; border-radius: 4px; white-space: nowrap;
    }}
    .se-nav-group {{ display: flex; gap: 4px; align-items: center; }}
    .se-nav-btn {{
      background: var(--bg-surface); border: 1px solid var(--border-subtle); color: var(--text-muted);
      font-size: 11px; padding: 2px 8px; border-radius: 4px; cursor: pointer; transition: all 0.15s; font-weight: 500;
    }}
    .se-nav-btn:hover {{ border-color: var(--border-strong); color: var(--text-main); }}

    .se-expand-btn {{
      background: var(--bg-surface); border: 1px solid var(--accent-gold-border); color: var(--accent-gold);
      font-size: 11px; padding: 2px 8px; border-radius: 4px; cursor: pointer; transition: all 0.15s; font-weight: 600;
      display: inline-flex; align-items: center; gap: 4px; white-space: nowrap;
    }}
    .se-expand-btn:hover {{ background: var(--accent-gold); color: white; }}

    .se-peek-prompt {{
      display: none; font-size: 10.5px; font-weight: 600; color: var(--accent-primary);
      text-align: center; margin-top: 8px; cursor: pointer; padding: 5px 8px;
      border-radius: 6px; background: var(--accent-glow); border: 1px dashed var(--accent-primary);
    }}

    .se-code-chip {{
      font-family: var(--font-mono); font-size: 11px; color: var(--text-main); background: var(--ide-bg);
      padding: 8px 10px; border-radius: 6px; border: 1px solid var(--border-subtle); overflow-x: auto;
      white-space: pre-wrap; word-break: break-word; overflow-wrap: anywhere; max-height: 120px; line-height: 1.5;
    }}

    /* Editorial Book-like Explanations */
    .se-card {{
      background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 14px 16px;
    }}
    .se-card.why-card {{ border-left: 3px solid var(--accent-primary); }}
    .se-card.what-card {{ border-left: 3px solid var(--accent-teal); }}
    
    .se-label {{
      font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 8px;
      display: flex; align-items: center; justify-content: space-between;
    }}
    .why-label {{ color: var(--accent-primary); }}
    .what-label {{ color: var(--accent-teal); }}

    /* Serif Primary Reading Content */
    .editorial-reading {{
      font-family: var(--font-serif); font-size: 14.5px; line-height: 1.72; color: var(--text-serif);
      letter-spacing: -0.01em;
    }}
    .editorial-reading-sm {{
      font-family: var(--font-serif); font-size: 13.5px; line-height: 1.62; color: var(--text-serif);
    }}

    .se-concept-badge {{
      font-size: 11.5px; color: var(--text-muted); background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle); padding: 8px 12px; border-radius: 6px;
    }}

    /* Review & Completion Action */
    .file-review-action-row {{
      display: flex; align-items: center; justify-content: space-between; padding-top: 6px; border-top: 1px dashed var(--border-subtle);
    }}
    .review-status-label {{ font-size: 11px; color: var(--text-dim); display: flex; align-items: center; gap: 5px; }}

    /* ========================================================
       PARALLEL TABLE LAYOUT
       ======================================================== */
    .parallel-table-container {{
      display: none; overflow-x: auto; max-height: 720px; -webkit-overflow-scrolling: touch;
    }}
    .parallel-table {{
      width: 100%; border-collapse: collapse; font-size: 12px;
    }}
    .parallel-table th {{
      position: sticky; top: 0; background: var(--bg-surface-elevated); padding: 10px 14px; text-align: left;
      font-size: 10px; font-weight: 700; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.6px;
      border-bottom: 1px solid var(--border-strong); z-index: 10;
    }}
    .parallel-row {{
      border-bottom: 1px solid var(--border-subtle); transition: background 0.12s; cursor: pointer;
    }}
    .parallel-row:hover {{ background: var(--ide-line-hover); }}
    .parallel-row.active-row {{ background: var(--accent-glow) !important; }}
    .parallel-col-code {{
      width: 44%; padding: 10px 14px; font-family: var(--font-mono); font-size: 11.5px;
      vertical-align: top; border-right: 1px solid var(--border-subtle); line-height: 1.55;
    }}
    .line-num-inline {{
      display: inline-block; width: 34px; color: var(--ide-line-num); user-select: none;
    }}
    .parallel-col-why {{
      width: 28%; padding: 10px 14px; vertical-align: top; border-right: 1px solid var(--border-subtle);
    }}
    .parallel-col-what {{
      width: 28%; padding: 10px 14px; vertical-align: top;
    }}
    .p-why-label {{ font-size: 9.5px; font-weight: 700; color: var(--accent-primary); margin-bottom: 4px; text-transform: uppercase; }}
    .p-what-label {{ font-size: 9.5px; font-weight: 700; color: var(--accent-teal); margin-bottom: 4px; text-transform: uppercase; }}
    .p-concept {{ font-size: 10px; color: var(--text-dim); margin-top: 6px; }}

    /* ========================================================
       IDE CODE EDITOR VIEWPORT
       ======================================================== */
    .code-viewport {{
      background: var(--ide-bg); padding: 14px 0; font-family: var(--font-mono); font-size: 12px;
      line-height: 1.65; overflow-x: auto; max-height: 720px; color: var(--ide-text);
      position: relative; -webkit-overflow-scrolling: touch;
    }}
    .code-line {{ display: flex; min-height: 23px; padding: 0 16px 0 0; cursor: pointer; transition: background 0.12s ease; }}
    .code-line:hover {{ background-color: var(--ide-line-hover); }}
    .code-line.active-line {{ background-color: var(--ide-active-line) !important; border-left: 3px solid var(--accent-gold); }}
    .line-num {{
      display: inline-block; width: 44px; padding-right: 14px; text-align: right;
      color: var(--ide-line-num); user-select: none; font-size: 11px; flex-shrink: 0;
    }}
    .line-code {{ flex: 1; white-space: pre; }}

    /* Syntax Tokens: Light Mode Defaults */
    .tok-kw {{ color: #0033B3; font-weight: 600; }}
    .tok-ann {{ color: #871094; }}
    .tok-type {{ color: #267F99; }}
    .tok-str {{ color: #067D17; }}
    .tok-num {{ color: #1750EB; }}
    .tok-cmt {{ color: #8C8C8C; font-style: italic; }}
    .tok-fn {{ color: #00627A; }}

    /* Syntax Tokens: Dark Mode Override */
    [data-theme="dark"] .tok-kw {{ color: #CF8E6D; font-weight: 600; }}
    [data-theme="dark"] .tok-ann {{ color: #E0AC16; }}
    [data-theme="dark"] .tok-type {{ color: #56A8F5; }}
    [data-theme="dark"] .tok-str {{ color: #6AAB73; }}
    [data-theme="dark"] .tok-num {{ color: #2AACB8; }}
    [data-theme="dark"] .tok-cmt {{ color: #7A7E85; font-style: italic; }}
    [data-theme="dark"] .tok-fn {{ color: #FFC66D; }}

    /* Ctrl+Click and Touch Navigation */
    .sym-link {{
      position: relative; transition: all 0.15s ease; border-radius: 2px;
    }}
    body.ctrl-pressed .sym-link {{
      text-decoration: underline !important;
      cursor: pointer !important;
      color: var(--accent-primary) !important;
      background-color: var(--accent-glow);
      outline: 1px dashed var(--accent-primary);
    }}
    @media (pointer: coarse), (hover: none) {{
      .sym-link {{
        cursor: pointer !important;
        border-bottom: 1px dashed var(--accent-primary);
        padding-bottom: 1px;
      }}
    }}

    @keyframes flashGlow {{
      0% {{ background-color: var(--accent-gold-bg); }}
      50% {{ background-color: var(--accent-glow); }}
      100% {{ background-color: transparent; }}
    }}
    .flash-highlight {{ animation: flashGlow 1.8s ease-out; }}

    /* ========================================================
       NESTED ARCHITECTURAL DISCUSSION THREADS
       ======================================================== */
    .discussion-section {{
      padding: 20px; background: var(--bg-surface); border-top: 1px solid var(--border-subtle);
    }}
    .discussion-header {{
      font-size: 13px; font-weight: 700; color: var(--text-main); margin-bottom: 14px; display: flex; align-items: center; gap: 8px;
    }}
    .discussion-thread {{
      background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 14px; margin-bottom: 12px;
    }}
    .thread-author-bar {{
      display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;
    }}
    .author-meta {{ display: flex; align-items: center; gap: 8px; }}
    .author-avatar {{ font-size: 16px; }}
    .author-name {{ font-size: 12px; font-weight: 700; color: var(--text-main); }}
    .author-role {{ font-size: 10px; color: var(--accent-primary); background: var(--accent-glow); padding: 1px 6px; border-radius: 10px; }}
    .thread-time {{ font-size: 10px; color: var(--text-dim); }}
    .thread-body {{ font-family: var(--font-serif); font-size: 13.5px; line-height: 1.6; color: var(--text-serif); }}
    .thread-replies {{
      margin-top: 12px; padding-left: 14px; border-left: 2px solid var(--border-subtle); display: flex; flex-direction: column; gap: 10px;
    }}
    .reply-card {{
      background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 6px; padding: 10px 12px;
    }}

    /* ========================================================
       FIND USAGES MODAL
       ======================================================== */
    .fu-modal-overlay {{
      position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.55);
      backdrop-filter: blur(5px); display: none; align-items: center; justify-content: center;
      padding: 16px; z-index: 1000;
    }}
    .fu-modal-overlay.open {{ display: flex; }}
    .fu-modal {{
      background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 12px;
      width: 100%; max-width: 760px; max-height: 85vh; display: flex; flex-direction: column;
      box-shadow: var(--shadow-modal); overflow: hidden;
    }}
    .fu-header {{
      padding: 14px 18px; background: var(--bg-surface-elevated); border-bottom: 1px solid var(--border-subtle);
      display: flex; align-items: center; justify-content: space-between; gap: 10px;
    }}
    .fu-title-row {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
    .fu-title {{ font-size: 14px; font-weight: 700; color: var(--text-main); font-family: var(--font-mono); }}
    .fu-kind-badge {{
      font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 4px;
      background: var(--accent-glow); color: var(--accent-primary);
    }}
    .fu-count-badge {{
      font-size: 10.5px; color: var(--accent-gold); background: var(--accent-gold-bg);
      padding: 2px 8px; border-radius: 10px; border: 1px solid var(--accent-gold-border); font-weight: 600;
    }}
    .fu-close-btn {{
      background: transparent; border: none; color: var(--text-dim); font-size: 18px;
      cursor: pointer; padding: 4px 8px; border-radius: 6px;
    }}
    .fu-close-btn:hover {{ background: var(--bg-surface); color: var(--text-main); }}

    .fu-filter-box {{ padding: 8px 18px; border-bottom: 1px solid var(--border-subtle); background: var(--bg-surface); }}
    .fu-filter-box input {{
      width: 100%; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle);
      padding: 6px 12px; border-radius: 6px; color: var(--text-main); font-size: 12px; outline: none;
    }}

    .fu-body {{ flex: 1; overflow-y: auto; padding: 14px 18px; display: flex; flex-direction: column; gap: 12px; -webkit-overflow-scrolling: touch; }}

    .fu-decl-card {{
      background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle);
      border-radius: 8px; padding: 12px 14px; display: flex; align-items: center; justify-content: space-between; gap: 10px;
    }}
    .fu-decl-meta {{ font-size: 11px; font-weight: 700; color: var(--accent-primary); margin-bottom: 3px; }}
    .fu-decl-code {{ font-family: var(--font-mono); font-size: 11.5px; color: var(--text-main); word-break: break-all; }}
    .fu-jump-btn {{
      background: var(--accent-primary); color: white; border: none; padding: 6px 12px; border-radius: 6px;
      font-size: 11px; font-weight: 600; cursor: pointer; white-space: nowrap;
    }}
    .fu-jump-btn:hover {{ background: var(--accent-primary-hover); }}

    .fu-file-group {{
      background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 8px; overflow: hidden;
    }}
    .fu-file-header {{
      padding: 8px 12px; background: var(--bg-surface-elevated); border-bottom: 1px solid var(--border-subtle);
      font-size: 11.5px; font-weight: 600; color: var(--text-main); display: flex; align-items: center; justify-content: space-between;
    }}
    .fu-usage-row {{
      padding: 8px 12px; display: flex; align-items: center; gap: 10px; cursor: pointer;
      border-bottom: 1px dashed var(--border-subtle); font-size: 11.5px;
    }}
    .fu-usage-row:last-child {{ border-bottom: none; }}
    .fu-usage-row:hover {{ background: var(--accent-glow); }}
    .fu-line-badge {{
      font-family: var(--font-mono); font-size: 10px; color: var(--text-dim); width: 48px; flex-shrink: 0;
    }}
    .fu-usage-code {{
      font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); flex: 1;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}
    .fu-sym-highlight {{
      color: var(--accent-gold); font-weight: 700; background: var(--accent-gold-bg); padding: 1px 3px; border-radius: 2px;
    }}

    /* ========================================================
       LIVE APP SIMULATOR & PIPELINE
       ======================================================== */
    .simulator-workspace {{
      display: grid; grid-template-columns: 360px 1fr; gap: 24px; align-items: start;
    }}
    .phone-mockup {{
      width: 100%; background: #000000; border: 10px solid #1E293B; border-radius: 36px;
      box-shadow: var(--shadow-modal); overflow: hidden; display: flex; flex-direction: column;
      height: 680px;
    }}
    .phone-notch-bar {{
      height: 26px; background: #000000; display: flex; align-items: center; justify-content: space-between;
      padding: 0 18px; font-size: 10px; font-weight: 600; color: #FFFFFF; flex-shrink: 0;
    }}
    .phone-screen {{ flex: 1; background: var(--bg-surface); display: flex; flex-direction: column; overflow: hidden; position: relative; }}
    
    .sim-topbar {{
      background: var(--bg-surface-elevated); padding: 12px 14px; border-bottom: 1px solid var(--border-subtle);
      display: flex; align-items: center; justify-content: space-between;
    }}
    .sim-topbar h4 {{ font-size: 13.5px; font-weight: 700; display: flex; align-items: center; gap: 6px; }}
    .sim-controls-row {{ display: flex; gap: 4px; }}
    .sim-btn-icon {{
      background: var(--bg-surface); border: 1px solid var(--border-subtle); color: var(--text-muted);
      width: 28px; height: 28px; border-radius: 6px; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 11px;
    }}
    .sim-search-bar {{ padding: 8px 12px; background: var(--bg-surface); border-bottom: 1px solid var(--border-subtle); }}
    .sim-search-bar input {{
      width: 100%; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle);
      padding: 6px 10px; border-radius: 6px; font-size: 11px; color: var(--text-main); outline: none;
    }}
    .sim-chips-scroll {{
      display: flex; gap: 4px; overflow-x: auto; padding: 6px 12px; border-bottom: 1px solid var(--border-subtle); scrollbar-width: none;
    }}
    .sim-chips-scroll::-webkit-scrollbar {{ display: none; }}
    .sim-chip {{
      padding: 3px 8px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle);
      border-radius: 10px; font-size: 9.5px; font-weight: 600; color: var(--text-muted); cursor: pointer; white-space: nowrap;
    }}
    .sim-chip.active {{ background: var(--accent-primary); border-color: var(--accent-primary); color: white; }}
    
    .sim-task-list {{ flex: 1; overflow-y: auto; padding: 10px 12px; display: flex; flex-direction: column; gap: 8px; -webkit-overflow-scrolling: touch; }}
    .sim-task-card {{
      background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); border-radius: 8px;
      padding: 10px 12px; display: flex; align-items: flex-start; gap: 10px; transition: all 0.2s; position: relative; overflow: hidden;
    }}
    .sim-task-card.completed {{ opacity: 0.65; }}
    .sim-priority-stripe {{ position: absolute; left: 0; top: 0; bottom: 0; width: 4px; }}
    .priority-urgent {{ background: var(--accent-danger); }}
    .priority-high {{ background: var(--accent-warning); }}
    .priority-medium {{ background: var(--accent-primary); }}
    .priority-low {{ background: var(--accent-teal); }}

    .sim-checkbox {{
      width: 18px; height: 18px; border-radius: 4px; border: 2px solid var(--border-strong);
      display: flex; align-items: center; justify-content: center; cursor: pointer; margin-top: 1px; flex-shrink: 0; transition: all 0.15s;
    }}
    .sim-checkbox.checked {{ background: var(--accent-gold); border-color: var(--accent-gold); }}
    .sim-task-content {{ flex: 1; cursor: pointer; min-width: 0; }}
    .sim-task-title {{ font-size: 12px; font-weight: 600; color: var(--text-main); margin-bottom: 2px; }}
    .sim-task-card.completed .sim-task-title {{ text-decoration: line-through; color: var(--text-dim); }}
    .sim-task-desc {{ font-size: 10px; color: var(--text-muted); margin-bottom: 6px; line-height: 1.4; }}
    .sim-task-footer {{ display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }}
    .sim-tag {{ font-size: 9px; padding: 1px 5px; border-radius: 3px; background: var(--bg-surface); border: 1px solid var(--border-subtle); font-weight: 600; }}

    .sim-fab {{
      position: absolute; right: 14px; bottom: 14px; width: 40px; height: 40px; border-radius: 20px;
      background: var(--accent-gold); color: white; display: flex; align-items: center; justify-content: center;
      font-size: 20px; box-shadow: var(--shadow-card); cursor: pointer;
    }}

    .sim-modal-overlay {{
      position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.5); backdrop-filter: blur(4px);
      display: none; align-items: center; justify-content: center; padding: 14px; z-index: 50;
    }}
    .sim-modal-overlay.open {{ display: flex; }}
    .sim-modal {{
      background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 10px;
      padding: 14px; width: 100%; max-width: 290px; display: flex; flex-direction: column; gap: 8px;
    }}
    .sim-form-group {{ display: flex; flex-direction: column; gap: 3px; }}
    .sim-form-group label {{ font-size: 9px; text-transform: uppercase; font-weight: 700; color: var(--text-dim); }}
    .sim-form-group input, .sim-form-group select {{
      background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle);
      padding: 6px 8px; border-radius: 6px; font-size: 11px; color: var(--text-main); outline: none;
    }}
    .sim-modal-actions {{ display: flex; justify-content: flex-end; gap: 6px; margin-top: 6px; }}

    /* Execution Inspector */
    .live-inspector-panel {{
      background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 10px;
      padding: 18px; display: flex; flex-direction: column; gap: 14px; box-shadow: var(--shadow-card);
    }}
    .inspector-header {{ display: flex; align-items: center; justify-content: space-between; }}
    .live-pulse {{
      display: flex; align-items: center; gap: 5px; font-size: 10px; font-weight: 700; color: var(--accent-gold);
      background: var(--accent-gold-bg); padding: 3px 8px; border-radius: 10px; border: 1px solid var(--accent-gold-border);
    }}
    .pulse-dot {{ width: 6px; height: 6px; border-radius: 50%; background: var(--accent-gold); box-shadow: 0 0 6px var(--accent-gold); }}
    
    .execution-pipeline-box {{
      background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 14px;
    }}
    .pipeline-step {{
      display: flex; align-items: flex-start; gap: 10px; padding: 8px 0; border-bottom: 1px dashed var(--border-subtle);
    }}
    .pipeline-step:last-child {{ border-bottom: none; }}
    .step-badge {{
      font-size: 9.5px; font-weight: 700; padding: 2px 6px; border-radius: 4px; white-space: nowrap; flex-shrink: 0;
    }}
    .badge-ui {{ background: var(--accent-glow); color: var(--accent-primary); }}
    .badge-vm {{ background: rgba(109, 40, 217, 0.12); color: var(--accent-secondary); }}
    .badge-domain {{ background: rgba(15, 118, 110, 0.12); color: var(--accent-teal); }}
    .badge-data {{ background: var(--accent-gold-bg); color: var(--accent-gold); }}
    .step-desc {{ font-size: 11.5px; color: var(--text-muted); word-break: break-all; }}
    .step-desc code {{ font-family: var(--font-mono); color: var(--text-main); font-size: 11px; }}

    /* ========================================================
       TASTEFUL CELEBRATION PARTICLES & TOAST FEEDBACK
       ======================================================== */
    .toast-pill {{
      position: fixed; bottom: 24px; right: 24px; background: var(--bg-surface);
      border: 1px solid var(--accent-gold-border); box-shadow: var(--shadow-modal);
      padding: 10px 16px; border-radius: 20px; font-size: 12px; font-weight: 600;
      color: var(--text-main); display: flex; align-items: center; gap: 8px;
      transform: translateY(100px); opacity: 0; pointer-events: none;
      transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1); z-index: 2000;
    }}
    .toast-pill.show {{ transform: translateY(0); opacity: 1; }}

    /* Particle burst container */
    #celebrationCanvas {{
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      pointer-events: none; z-index: 3000;
    }}

    /* ========================================================
       MOBILE & RESPONSIVE BREAKPOINTS
       ======================================================== */
    @media (max-width: 900px) {{
      .sidebar {{
        position: fixed; top: 0; left: 0; bottom: 0; width: 85vw; max-width: 320px;
        transform: translateX(-100%); z-index: 200;
      }}
      .sidebar.open {{ transform: translateX(0); box-shadow: var(--shadow-modal); }}
      .sidebar-backdrop.open {{ display: block; }}
      .sidebar-close-btn {{ display: block; }}

      .mobile-nav-toggle {{ display: flex; }}
      .breadcrumb-trail {{ display: none; }}
      .mobile-active-file-pill {{ display: inline-block; }}

      /* Remove Component Header in mobile UI as requested */
      .component-header {{
        display: none !important;
      }}

      .split-view-container {{ grid-template-columns: 1fr; }}
      .split-code-pane {{ border-right: none; border-bottom: 1px solid var(--border-subtle); }}
      .code-viewport {{ max-height: 48vh; }}

      .workspace-content {{ padding: 12px; gap: 12px; }}
      .parallel-table {{ min-width: 580px; }}
      .simulator-workspace {{ grid-template-columns: 1fr; }}
      .phone-mockup {{ height: 580px; }}

      .se-drag-handle {{
        display: flex;
      }}
      .se-peek-prompt {{
        display: block;
      }}

      /* Smooth transition for explainer pane */
      .split-explainer-pane {{
        transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1), height 0.28s ease;
      }}

      /* Full expandable bottom sheet on mobile */
      .split-explainer-pane.sheet-expanded {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 85vh;
        max-height: 85vh;
        z-index: 300;
        background: var(--bg-surface);
        border-top: 2px solid var(--accent-primary);
        border-radius: 20px 20px 0 0;
        box-shadow: 0 -12px 40px rgba(0, 0, 0, 0.5);
        padding: 14px 18px 24px;
        overflow-y: auto;
        -webkit-overflow-scrolling: touch;
        animation: slideUpSheet 0.26s cubic-bezier(0.16, 1, 0.3, 1);
      }}

      .explainer-sheet-backdrop {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.55);
        backdrop-filter: blur(4px);
        display: none;
        z-index: 290;
      }}
      .explainer-sheet-backdrop.active {{
        display: block;
      }}
    }}

    @keyframes slideUpSheet {{
      from {{ transform: translateY(100%); }}
      to {{ transform: translateY(0); }}
    }}

    @media (max-width: 480px) {{
      .top-header {{ padding: 0 12px; }}
      .line-num {{ width: 34px; padding-right: 8px; font-size: 10px; }}
      .btn-pill {{ padding: 4px 8px; font-size: 11px; }}
    }}
  </style>
</head>
<body>

  <!-- Floating Toast Feedback -->
  <div class="toast-pill" id="globalToast">
    <span>✨</span>
    <span id="toastMessage">Action completed</span>
  </div>

  <!-- Particle Celebration Canvas -->
  <canvas id="celebrationCanvas"></canvas>

  <!-- MOBILE SIDEBAR BACKDROP -->
  <div class="sidebar-backdrop" id="sidebarBackdrop" onclick="closeMobileSidebar()"></div>

  <!-- MOBILE EXPLAINER SHEET BACKDROP -->
  <div class="explainer-sheet-backdrop" id="sheetBackdrop" onclick="collapseAllExplainerSheets()"></div>

  <!-- SIDEBAR NAVIGATION -->
  <aside class="sidebar" id="mainSidebar">
    <div class="sidebar-header">
      <div class="sidebar-brand-group">
        <div class="brand-icon">⚡</div>
        <div>
          <div class="brand-title">Android Code Studio</div>
          <div class="brand-sub">Compose vs XML • Clean Arch</div>
        </div>
      </div>
      <button class="sidebar-close-btn" onclick="closeMobileSidebar()" title="Close Navigation">✕</button>
    </div>

    <!-- Architecture Mastery Progress -->
    <div class="mastery-progress-box">
      <div class="mastery-header">
        <span class="mastery-title"><span>🏛️</span> Project Mastery</span>
        <span class="mastery-pct" id="masteryPercentLabel">0 / 52 (0%)</span>
      </div>
      <div class="mastery-bar-bg">
        <div class="mastery-bar-fill" id="masteryBarFill" style="width: 4%;"></div>
      </div>
    </div>

    <div class="sidebar-search">
      <div class="search-input-box">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        <input type="text" id="globalSearchInput" placeholder="Search classes, DAOs & screens..." oninput="filterSidebarFiles(this.value)">
      </div>
    </div>

    <div class="sidebar-nav">
      <!-- Special Tab: App Simulator -->
      <div class="sidebar-special-btn" id="btn_nav_simulator" onclick="openSimulatorView()">
        <span>📱</span>
        <span>Live App Simulator & Trace</span>
      </div>
"""

# Render Category Tree in Sidebar
for cat_name, file_list in categories.items():
    html_out += f"""
      <div class="category-group" data-cat="{cat_name}">
        <div class="category-label">
          <span>{cat_name}</span>
          <span class="category-badge">{len(file_list)}</span>
        </div>
    """
    for f in file_list:
        html_out += f"""
        <div class="file-tree-item" id="nav_item_{f['id']}" onclick="openFile('{f['id']}')">
          <span style="font-size: 11px;">📄</span>
          <span>{f['name']}</span>
          <span class="item-badge">{f['badge']}</span>
        </div>
        """
    html_out += "</div>"

html_out += f"""
    </div>
  </aside>

  <!-- MAIN WRAPPER -->
  <div class="main-wrapper">
    <header class="top-header">
      <div class="header-left">
        <!-- Mobile Drawer Hamburger Toggle -->
        <button class="mobile-nav-toggle" id="mobileMenuBtn" onclick="toggleMobileSidebar()" title="Toggle Files Navigation">
          <span>☰</span>
          <span>Files</span>
        </button>

        <span class="mobile-active-file-pill" id="mobileActiveFileName">MainActivity.kt</span>

        <div class="breadcrumb-trail">
          <span class="breadcrumb-node">Clean Architecture</span>
          <span>/</span>
          <span class="breadcrumb-node" id="headerBreadcrumbLayer">UI Presentation</span>
          <span>/</span>
          <span class="breadcrumb-current" id="headerBreadcrumbFile">MainActivity.kt</span>
        </div>
      </div>

      <div class="header-actions">
        <button class="btn-pill" id="globalLayoutToggleBtn" onclick="toggleCurrentFileLayout()" title="Toggle Split View vs Parallel Table">
          <span id="globalLayoutIcon">📋</span>
          <span id="globalLayoutLabel">Parallel Table</span>
        </button>
        <button class="btn-pill" onclick="toggleTheme()" title="Switch between Light and Dim/Dark modes">
          <span id="themeIcon">🌙</span>
          <span id="themeLabel">Dim Mode</span>
        </button>
      </div>
    </header>

    <!-- EDITOR TABS BAR -->
    <div class="editor-tabs-bar" id="editorTabsBar"></div>

    <!-- MAIN DYNAMIC WORKSPACE -->
    <main class="workspace-content" id="mainWorkspaceContent"></main>
  </div>

  <!-- FIND USAGES FLOATING MODAL -->
  <div class="fu-modal-overlay" id="findUsagesModal" onclick="closeFindUsagesOnBackdrop(event)">
    <div class="fu-modal">
      <div class="fu-header">
        <div class="fu-title-row">
          <span style="font-size: 14px;">🔍</span>
          <div class="fu-title" id="fuSymbolTitle">Find Usages</div>
          <span class="fu-kind-badge" id="fuKindBadge">Class</span>
          <span class="fu-count-badge" id="fuCountBadge">0 usages</span>
        </div>
        <button class="fu-close-btn" onclick="closeFindUsagesModal()" title="Close (Esc)">✕</button>
      </div>

      <div class="fu-filter-box">
        <input type="text" id="fuFilterInput" placeholder="Filter usages by file or symbol..." oninput="filterUsagesList(this.value)">
      </div>

      <div class="fu-body" id="fuBody">
        <div class="fu-decl-card" id="fuDeclCard">
          <div>
            <div class="fu-decl-meta">
              <span>📌 Declaration:</span> <span id="fuDeclLocation">File.kt (Line 1)</span>
            </div>
            <div class="fu-decl-code" id="fuDeclCode">class Example</div>
          </div>
          <button class="fu-jump-btn" id="fuDeclJumpBtn">Jump to Source ↑</button>
        </div>

        <div style="font-size: 10px; font-weight: 700; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.6px; margin-top: 4px;">
          Usages Across Architecture (<span id="fuUsagesCountLabel">0</span>)
        </div>

        <div id="fuUsagesGroupList" style="display: flex; flex-direction: column; gap: 8px;"></div>
      </div>
    </div>
  </div>

  <script>
    const FILES_DATA = {json_files_data};
    const SYMBOL_INDEX = {json_symbols};

    let activeFileId = null;
    let openTabs = [];
    let currentSelectedLines = {{}};
    let activeFileViewModes = {{}};
    let activeSymbolData = null;
    let reviewedFiles = new Set(JSON.parse(localStorage.getItem('reviewed_files') || '[]'));

    function escapeHtml(text) {{
      const map = {{ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }};
      return String(text).replace(/[&<>"']/g, m => map[m]);
    }}

    // ========================================================
    // TASTEFUL TOAST & GOLD PARTICLE CELEBRATION
    // ========================================================
    function showToast(message, icon = '✨') {{
      const toast = document.getElementById('globalToast');
      document.getElementById('toastMessage').innerText = message;
      toast.querySelector('span:first-child').innerText = icon;
      toast.classList.add('show');
      setTimeout(() => {{ toast.classList.remove('show'); }}, 2400);
    }}

    function celebrateGold(originX, originY) {{
      const canvas = document.getElementById('celebrationCanvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;

      const particles = [];
      const colors = ['#F59E0B', '#FBBF24', '#D97706', '#E5E7EB', '#2563EB'];

      for (let i = 0; i < 18; i++) {{
        const angle = Math.random() * Math.PI * 2;
        const speed = 2 + Math.random() * 4;
        particles.push({{
          x: originX || window.innerWidth / 2,
          y: originY || window.innerHeight / 2,
          vx: Math.cos(angle) * speed,
          vy: Math.sin(angle) * speed - 1.5,
          size: 2.5 + Math.random() * 3,
          color: colors[Math.floor(Math.random() * colors.length)],
          alpha: 1,
          decay: 0.02 + Math.random() * 0.02
        }});
      }}

      function animate() {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        let active = false;
        particles.forEach(p => {{
          p.x += p.vx;
          p.y += p.vy;
          p.vy += 0.08; // gravity
          p.alpha -= p.decay;
          if (p.alpha > 0) {{
            active = true;
            ctx.save();
            ctx.globalAlpha = p.alpha;
            ctx.fillStyle = p.color;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
          }}
        }});

        if (active) {{
          requestAnimationFrame(animate);
        }} else {{
          ctx.clearRect(0, 0, canvas.width, canvas.height);
        }}
      }}
      requestAnimationFrame(animate);
    }}

    function toggleFileReview(fileId, event) {{
      if (event) event.stopPropagation();
      const isReviewed = reviewedFiles.has(fileId);
      if (isReviewed) {{
        reviewedFiles.delete(fileId);
        showToast('File marked as unread', '📖');
      }} else {{
        reviewedFiles.add(fileId);
        showToast('Archived as reviewed!', '🏆');
        const rect = event ? event.target.getBoundingClientRect() : {{ left: window.innerWidth / 2, top: window.innerHeight / 2 }};
        celebrateGold(rect.left + 30, rect.top);
      }}
      localStorage.setItem('reviewed_files', JSON.stringify(Array.from(reviewedFiles)));
      updateMasteryProgress();
      updateFileItemClasses();
      renderActiveFileView(FILES_DATA[fileId], currentSelectedLines[fileId] || 1);
    }}

    function updateMasteryProgress() {{
      const total = Object.keys(FILES_DATA).length;
      const done = reviewedFiles.size;
      const pct = Math.round((done / total) * 100);
      document.getElementById('masteryPercentLabel').innerText = `${{done}} / ${{total}} (${{pct}}%)`;
      document.getElementById('masteryBarFill').style.width = `${{Math.max(4, pct)}}%`;
    }}

    function updateFileItemClasses() {{
      Object.keys(FILES_DATA).forEach(fId => {{
        const item = document.getElementById(`nav_item_${{fId}}`);
        if (item) {{
          if (reviewedFiles.has(fId)) {{
            item.classList.add('reviewed');
          }} else {{
            item.classList.remove('reviewed');
          }}
        }}
      }});
    }}

    // ========================================================
    // MOBILE DRAWER MANAGEMENT
    // ========================================================
    function toggleMobileSidebar() {{
      const sidebar = document.getElementById('mainSidebar');
      const backdrop = document.getElementById('sidebarBackdrop');
      const isOpen = sidebar.classList.contains('open');
      if (isOpen) {{
        closeMobileSidebar();
      }} else {{
        sidebar.classList.add('open');
        backdrop.classList.add('open');
      }}
    }}

    function closeMobileSidebar() {{
      const sidebar = document.getElementById('mainSidebar');
      const backdrop = document.getElementById('sidebarBackdrop');
      sidebar.classList.remove('open');
      backdrop.classList.remove('open');
    }}

    // ========================================================
    // FILE NAVIGATION & ARCHITECTURE WORKSPACE
    // ========================================================
    function openFile(fileId, targetLine = 1) {{
      const file = FILES_DATA[fileId];
      if (!file) return;

      activeFileId = fileId;
      closeMobileSidebar();
      collapseAllExplainerSheets();

      // Update sidebar active states
      document.querySelectorAll('.file-tree-item').forEach(el => el.classList.remove('active'));
      const navItem = document.getElementById(`nav_item_${{fileId}}`);
      if (navItem) navItem.classList.add('active');
      document.getElementById('btn_nav_simulator').classList.remove('active');

      // Update top breadcrumbs
      document.getElementById('headerBreadcrumbLayer').innerText = file.arch.layer;
      document.getElementById('headerBreadcrumbFile').innerText = file.name;
      const mobPill = document.getElementById('mobileActiveFileName');
      if (mobPill) mobPill.innerText = file.name;

      // Manage open tabs
      if (!openTabs.includes(fileId)) {{
        openTabs.push(fileId);
      }}
      renderTabsBar();
      renderActiveFileView(file, targetLine);
    }}

    function renderTabsBar() {{
      const bar = document.getElementById('editorTabsBar');
      bar.innerHTML = `
        <div class="editor-tab ${{activeFileId === 'simulator' ? 'active' : ''}}" onclick="openSimulatorView()">
          <span>📱 App Simulator</span>
        </div>
      ` + openTabs.map(fId => {{
        const f = FILES_DATA[fId];
        const isActive = fId === activeFileId;
        const isRev = reviewedFiles.has(fId);
        return `
          <div class="editor-tab ${{isActive ? 'active' : ''}}" onclick="openFile('${{fId}}')">
            <span>${{isRev ? '✓ ' : ''}}${{f.name}}</span>
            <span class="editor-tab-close" onclick="closeTab(event, '${{fId}}')">✕</span>
          </div>
        `;
      }}).join('');
    }}

    function closeTab(event, fileId) {{
      event.stopPropagation();
      openTabs = openTabs.filter(id => id !== fileId);
      if (activeFileId === fileId) {{
        if (openTabs.length > 0) {{
          openFile(openTabs[openTabs.length - 1]);
        }} else {{
          openSimulatorView();
        }}
      }} else {{
        renderTabsBar();
      }}
    }}

    function renderActiveFileView(file, targetLine = 1) {{
      const workspace = document.getElementById('mainWorkspaceContent');
      const mode = activeFileViewModes[file.id] || 'split';
      const firstExp = file.explanations[targetLine - 1] || file.explanations[0];
      const isReviewed = reviewedFiles.has(file.id);

      // Determine Architecture Pipeline Nodes
      const pipelineSteps = [
        {{ label: 'UI Presentation', tier: 1, fileTarget: file.id.startsWith('act') || file.id.startsWith('comp') ? file.id : 'act_task_list_compose' }},
        {{ label: 'ViewModel & State', tier: 2, fileTarget: 'vm_task' }},
        {{ label: 'Domain UseCase', tier: 3, fileTarget: 'uc_get_tasks' }},
        {{ label: 'Data Repository', tier: 4, fileTarget: 'repo_task_impl' }},
        {{ label: 'Room SQLite DAO', tier: 5, fileTarget: 'dao_task' }}
      ];

      workspace.innerHTML = `
        <div class="card-modular">
          <!-- Modular Header -->
          <div class="component-header">
            <div class="file-meta">
              <div class="file-icon">KT</div>
              <div>
                <div class="file-path">${{file.relPath}}</div>
                <div class="file-summary-editorial">${{file.summary}}</div>
              </div>
            </div>
            
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
              <div class="view-mode-toggles">
                <button class="v-btn ${{mode === 'split' ? 'active' : ''}}" id="btn_split_${{file.id}}" onclick="switchActiveFileMode('split')" title="Side-by-side split code & editorial explanation">
                  🔀 Split View
                </button>
                <button class="v-btn ${{mode === 'parallel' ? 'active' : ''}}" id="btn_parallel_${{file.id}}" onclick="switchActiveFileMode('parallel')" title="Parallel comparison table">
                  📋 Table View
                </button>
              </div>

              <button class="btn-pill ${{isReviewed ? 'gold' : ''}}" onclick="toggleFileReview('${{file.id}}', event)">
                <span>${{isReviewed ? '✓ Reviewed' : 'Mark Reviewed'}}</span>
              </button>

              <button class="btn-pill" onclick="copySnippet('${{file.id}}', this)">
                <span>📋 Copy</span>
              </button>
            </div>
          </div>

          <!-- Interactive Clean Architecture Node Pipeline Graph -->
          <div class="architecture-pipeline-strip">
            <span style="font-size: 10px; font-weight: 700; color: var(--text-dim); text-transform: uppercase; margin-right: 4px;">Architecture:</span>
            ${{pipelineSteps.map((node, i) => `
              <div class="pipeline-node ${{node.tier === file.arch.tier ? 'active-tier' : ''}}" onclick="openFile('${{node.fileTarget}}')" title="Jump to ${{node.label}} layer">
                <span>${{node.tier === file.arch.tier ? '📍 ' : ''}}${{node.label}}</span>
              </div>
              ${{i < pipelineSteps.length - 1 ? '<span class="pipeline-arrow">➔</span>' : ''}}
            `).join('')}}
          </div>

          <!-- Compose vs XML Counterpart Banner -->
          ${{file.comparePair ? `
            <div class="compare-banner">
              <div class="compare-desc">
                <span>⚡</span>
                <span><strong>${{file.comparePair.title}}:</strong> Compare declarative Jetpack Compose vs imperative ViewBinding</span>
              </div>
              <button class="compare-btn" onclick="openFile('${{file.comparePair.counterpart}}')">
                View ${{file.comparePair.counterpart_name}} ➔
              </button>
            </div>
          ` : ''}}

          <!-- SIDE-BY-SIDE SPLIT VIEW -->
          <div class="split-view-container" id="view_split_${{file.id}}" style="display: ${{mode === 'split' ? 'grid' : 'none'}};">
            <div class="split-code-pane">
              <div class="code-viewport" id="viewport_${{file.id}}">
                ${{file.formattedCode}}
              </div>
            </div>

            <div class="split-explainer-pane" id="explainer_pane_${{file.id}}">
              <div class="sticky-explainer-box">
                <div class="se-header" onclick="handleExplainerHeaderClick(event, '${{file.id}}')">
                  <div class="se-drag-handle" onclick="toggleExplainerExpand('${{file.id}}', event)">
                    <div class="se-drag-bar"></div>
                  </div>
                  <div class="se-title-row">
                    <span class="se-tag" id="side_tag_${{file.id}}">Line ${{firstExp.line}} of ${{file.lineCount}}</span>
                    <div class="se-nav-group">
                      <button class="se-nav-btn" onclick="stepLine('${{file.id}}', -1)" title="Previous Line (K or ↑)">▲ Prev</button>
                      <button class="se-nav-btn" onclick="stepLine('${{file.id}}', 1)" title="Next Line (J or ↓)">▼ Next</button>
                      <button class="se-expand-btn" id="btn_expand_${{file.id}}" onclick="toggleExplainerExpand('${{file.id}}', event)" title="Expand or collapse full explanation">
                        <span id="expand_icon_${{file.id}}">⤢</span>
                        <span id="expand_label_${{file.id}}">Expand</span>
                      </button>
                    </div>
                  </div>
                  <div class="se-code-chip" id="side_code_${{file.id}}">
                    <code>${{escapeHtml(firstExp.code)}}</code>
                  </div>
                  <div class="se-peek-prompt" onclick="toggleExplainerExpand('${{file.id}}', event)">
                    <span>👆 Tap to view Why Added & What It Does</span>
                  </div>
                </div>

                <div class="se-card why-card">
                  <div class="se-label why-label">
                    <span>🎯 Architectural Rationale</span>
                    <span style="font-size: 9.5px; opacity: 0.8;">Why Added</span>
                  </div>
                  <div class="editorial-reading" id="side_why_${{file.id}}">${{escapeHtml(firstExp.why)}}</div>
                </div>

                <div class="se-card what-card">
                  <div class="se-label what-label">
                    <span>⚙️ Execution Mechanism</span>
                    <span style="font-size: 9.5px; opacity: 0.8;">What It Does</span>
                  </div>
                  <div class="editorial-reading" id="side_what_${{file.id}}">${{escapeHtml(firstExp.what)}}</div>
                </div>

                <div class="se-concept-badge" id="side_concept_${{file.id}}">
                  💡 <strong>Core Concept:</strong> ${{escapeHtml(firstExp.concept || 'Architecture Pattern')}}
                </div>
              </div>
            </div>
          </div>

          <!-- PARALLEL COMPARISON TABLE -->
          <div class="parallel-table-container" id="view_parallel_${{file.id}}" style="display: ${{mode === 'parallel' ? 'block' : 'none'}};">
            <table class="parallel-table">
              <thead>
                <tr>
                  <th style="width: 44%;">Line & Syntax Code</th>
                  <th style="width: 28%;">🎯 Why is this piece of code added?</th>
                  <th style="width: 28%;">⚙️ What does it do?</th>
                </tr>
              </thead>
              <tbody>
                ${{file.parallelRowsHtml}}
              </tbody>
            </table>
          </div>

          <textarea id="${{file.id}}_raw" style="display: none;">${{escapeHtml(file.rawCode)}}</textarea>

          <!-- NESTED CODE REVIEW & ARCHITECTURAL DISCUSSION THREADS -->
          <div class="discussion-section">
            <div class="discussion-header">
              <span>💬</span>
              <span>Architectural Review Notes & Design Decisions</span>
            </div>

            ${{file.reviewNotes.map(th => `
              <div class="discussion-thread">
                <div class="thread-author-bar">
                  <div class="author-meta">
                    <span class="author-avatar">${{th.avatar}}</span>
                    <span class="author-name">${{th.author}}</span>
                    <span class="author-role">${{th.role}}</span>
                  </div>
                  <span class="thread-time">${{th.time}}</span>
                </div>
                <div class="thread-body">${{th.comment}}</div>

                ${{th.replies.length > 0 ? `
                  <div class="thread-replies">
                    ${{th.replies.map(r => `
                      <div class="reply-card">
                        <div class="thread-author-bar" style="margin-bottom: 4px;">
                          <div class="author-meta">
                            <span class="author-avatar">${{r.avatar}}</span>
                            <span class="author-name">${{r.author}}</span>
                            <span class="author-role">${{r.role}}</span>
                          </div>
                          <span class="thread-time">${{r.time}}</span>
                        </div>
                        <div class="thread-body" style="font-size: 13px;">${{r.comment}}</div>
                      </div>
                    `).join('')}}
                  </div>
                ` : ''}}
              </div>
            `).join('')}}
          </div>
        </div>
      `;

      selectCodeLine(file.id, targetLine);
      if (targetLine > 1) {{
        jumpToCodeLine(file.id, targetLine);
      }}
    }}

    function switchActiveFileMode(mode) {{
      if (!activeFileId || activeFileId === 'simulator') return;
      activeFileViewModes[activeFileId] = mode;
      renderActiveFileView(FILES_DATA[activeFileId], currentSelectedLines[activeFileId] || 1);
    }}

    function toggleCurrentFileLayout() {{
      if (!activeFileId || activeFileId === 'simulator') return;
      const current = activeFileViewModes[activeFileId] || 'split';
      const target = current === 'split' ? 'parallel' : 'split';
      switchActiveFileMode(target);
    }}

    function toggleExplainerExpand(fileId, event) {{
      if (event) event.stopPropagation();
      const pane = document.getElementById(`explainer_pane_${{fileId}}`);
      const container = document.getElementById(`view_split_${{fileId}}`);
      const backdrop = document.getElementById('sheetBackdrop');
      const expandIcon = document.getElementById(`expand_icon_${{fileId}}`);
      const expandLabel = document.getElementById(`expand_label_${{fileId}}`);

      if (!pane) return;

      const isMobile = window.innerWidth <= 900;
      if (isMobile) {{
        const isSheetExpanded = pane.classList.contains('sheet-expanded');
        if (isSheetExpanded) {{
          pane.classList.remove('sheet-expanded');
          if (backdrop) backdrop.classList.remove('active');
          if (expandIcon) expandIcon.innerText = '⤢';
          if (expandLabel) expandLabel.innerText = 'Expand';
          showToast('Explanation minimized', '▼');
        }} else {{
          pane.classList.add('sheet-expanded');
          if (backdrop) backdrop.classList.add('active');
          if (expandIcon) expandIcon.innerText = '▼';
          if (expandLabel) expandLabel.innerText = 'Minimize';
          showToast('Full explanation expanded!', '📖');
        }}
      }} else {{
        // Desktop: toggle wide split
        const isExpanded = container && container.classList.contains('pane-expanded');
        if (isExpanded) {{
          container.classList.remove('pane-expanded');
          if (expandIcon) expandIcon.innerText = '⤢';
          if (expandLabel) expandLabel.innerText = 'Expand';
        }} else {{
          container.classList.add('pane-expanded');
          if (expandIcon) expandIcon.innerText = '⤡';
          if (expandLabel) expandLabel.innerText = 'Default';
        }}
      }}
    }}

    function collapseAllExplainerSheets() {{
      document.querySelectorAll('.split-explainer-pane').forEach(el => el.classList.remove('sheet-expanded'));
      const backdrop = document.getElementById('sheetBackdrop');
      if (backdrop) backdrop.classList.remove('active');
      document.querySelectorAll('[id^="expand_icon_"]').forEach(el => el.innerText = '⤢');
      document.querySelectorAll('[id^="expand_label_"]').forEach(el => el.innerText = 'Expand');
    }}

    function handleExplainerHeaderClick(event, fileId) {{
      if (event.target.closest('button')) return;
      if (window.innerWidth <= 900) {{
        toggleExplainerExpand(fileId, event);
      }}
    }}

    function openSimulatorView() {{
      activeFileId = 'simulator';
      closeMobileSidebar();

      document.querySelectorAll('.file-tree-item').forEach(el => el.classList.remove('active'));
      document.getElementById('btn_nav_simulator').classList.add('active');
      renderTabsBar();

      document.getElementById('headerBreadcrumbLayer').innerText = 'Interactive Runtime';
      document.getElementById('headerBreadcrumbFile').innerText = 'Jetpack Compose Simulator';
      const mobPill = document.getElementById('mobileActiveFileName');
      if (mobPill) mobPill.innerText = 'App Simulator';

      const workspace = document.getElementById('mainWorkspaceContent');
      workspace.innerHTML = `
        <div class="simulator-workspace">
          <!-- Mock Phone Screen -->
          <div class="phone-mockup">
            <div class="phone-notch-bar">
              <span>9:41</span>
              <span>📶 5G 100%</span>
            </div>
            
            <div class="phone-screen">
              <div class="sim-topbar">
                <h4><span>⚡</span> Task Manager</h4>
                <div class="sim-controls-row">
                  <button class="sim-btn-icon" onclick="simToggleStats()" title="Toggle Analytics Screen">📊</button>
                  <button class="sim-btn-icon" onclick="simTriggerBackgroundSync()" title="Trigger Background Sync">🔄</button>
                </div>
              </div>

              <!-- Search Bar -->
              <div class="sim-search-bar">
                <input type="text" id="simSearchInput" placeholder="🔍 Search tasks (debounce 200ms)..." oninput="simOnSearchInput(this.value)">
              </div>

              <!-- Category Filter Chips -->
              <div class="sim-chips-scroll">
                <div class="sim-chip active" onclick="simFilterCategory('ALL', this)">All</div>
                <div class="sim-chip" onclick="simFilterCategory('WORK', this)">Work</div>
                <div class="sim-chip" onclick="simFilterCategory('PERSONAL', this)">Personal</div>
                <div class="sim-chip" onclick="simFilterCategory('SHOPPING', this)">Shopping</div>
                <div class="sim-chip" onclick="simFilterCategory('FINANCE', this)">Finance</div>
              </div>

              <!-- Priority Filter Chips -->
              <div class="sim-chips-scroll" style="background: var(--bg-surface-elevated); padding: 4px 12px;">
                <span style="font-size: 8.5px; color: var(--text-dim); text-transform: uppercase; font-weight: 700; align-self: center;">Priority:</span>
                <div class="sim-chip active" onclick="simFilterPriority('ALL', this)">All</div>
                <div class="sim-chip" onclick="simFilterPriority('URGENT', this)">Urgent</div>
                <div class="sim-chip" onclick="simFilterPriority('HIGH', this)">High</div>
                <div class="sim-chip" onclick="simFilterPriority('MEDIUM', this)">Med</div>
                <div class="sim-chip" onclick="simFilterPriority('LOW', this)">Low</div>
              </div>

              <!-- Scrollable Tasks List -->
              <div class="sim-task-list" id="simTaskListContainer"></div>

              <!-- Floating Action Button -->
              <div class="sim-fab" onclick="simOpenAddModal()" title="Add New Task (AddTaskUseCase)">
                +
              </div>

              <!-- Add Task Modal -->
              <div class="sim-modal-overlay" id="simAddModal">
                <div class="sim-modal">
                  <div style="font-size: 13px; font-weight: 700; color: var(--accent-gold);">➕ Add New Task</div>
                  <div class="sim-form-group">
                    <label>Task Title *</label>
                    <input type="text" id="newTaskTitle" placeholder="e.g. Write Compose Unit Tests">
                  </div>
                  <div class="sim-form-group">
                    <label>Description</label>
                    <input type="text" id="newTaskDesc" placeholder="e.g. Test Room DAO and ViewModel StateFlow">
                  </div>
                  <div class="sim-form-group">
                    <label>Priority</label>
                    <select id="newTaskPriority">
                      <option value="URGENT">URGENT</option>
                      <option value="HIGH" selected>HIGH</option>
                      <option value="MEDIUM">MEDIUM</option>
                      <option value="LOW">LOW</option>
                    </select>
                  </div>
                  <div class="sim-form-group">
                    <label>Category</label>
                    <select id="newTaskCategory">
                      <option value="WORK" selected>WORK</option>
                      <option value="PERSONAL">PERSONAL</option>
                      <option value="SHOPPING">SHOPPING</option>
                      <option value="FINANCE">FINANCE</option>
                    </select>
                  </div>
                  <div class="sim-modal-actions">
                    <button class="btn-pill" onclick="simCloseAddModal()">Cancel</button>
                    <button class="btn-pill primary" onclick="simSaveNewTask()">Save Task</button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Live Execution Inspector Panel -->
          <div class="live-inspector-panel">
            <div class="inspector-header">
              <div>
                <h4 style="font-size: 14px; font-weight: 700;">Live Android Execution Pipeline</h4>
                <p style="font-size: 11px; color: var(--text-muted);">Real-time reactive invocation trace matching Android codebase</p>
              </div>
              <div class="live-pulse">
                <div class="pulse-dot"></div>
                <span>LISTENING</span>
              </div>
            </div>

            <div style="background: var(--bg-surface); padding: 10px 14px; border-radius: 8px; border: 1px solid var(--border-subtle);">
              <div style="font-size: 9.5px; font-weight: 700; color: var(--text-dim); text-transform: uppercase;">Current Trigger</div>
              <div id="inspectorTriggerName" style="font-size: 13.5px; font-weight: 700; color: var(--accent-primary); margin-top: 2px;">
                Initial Load: App Started
              </div>
              <div id="inspectorTriggerDesc" style="font-size: 11.5px; color: var(--text-muted); margin-top: 2px; font-family: var(--font-serif);">
                Observing tasks via combine(searchQuery.debounce(200), category, priority) in TaskViewModel.
              </div>
            </div>

            <div class="execution-pipeline-box">
              <div style="font-size: 9.5px; font-weight: 700; color: var(--text-dim); margin-bottom: 8px; text-transform: uppercase;">
                Execution Trace (Layer by Layer)
              </div>
              <div id="inspectorStepsList">
                <div class="pipeline-step">
                  <span class="step-badge badge-ui">1. Presentation</span>
                  <div class="step-desc"><code>TaskListScreen.kt</code> renders Composable with <code>listUiState.collectAsStateWithLifecycle()</code></div>
                </div>
                <div class="pipeline-step">
                  <span class="step-badge badge-vm">2. ViewModel</span>
                  <div class="step-desc"><code>TaskViewModel.kt</code> manages <code>MutableStateFlow&lt;TaskListUiState&gt;</code> surviving rotation</div>
                </div>
                <div class="pipeline-step">
                  <span class="step-badge badge-domain">3. Domain UseCase</span>
                  <div class="step-desc"><code>GetFilteredTasksUseCase.kt</code> filters list by category and priority</div>
                </div>
                <div class="pipeline-step">
                  <span class="step-badge badge-data">4. Data Repository</span>
                  <div class="step-desc"><code>TaskRepositoryImpl.kt</code> emits from Room <code>Flow&lt;List&lt;TaskEntity&gt;&gt;</code> with Offline-First caching</div>
                </div>
                <div class="pipeline-step">
                  <span class="step-badge badge-data">5. Local Database</span>
                  <div class="step-desc"><code>TaskDao.kt</code> executes SQLite query <code>SELECT * FROM tasks ORDER BY createdAt DESC</code></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      `;
      renderSimTaskList();
    }}

    function filterSidebarFiles(query) {{
      const q = query.toLowerCase().trim();
      document.querySelectorAll('.file-tree-item').forEach(item => {{
        const text = item.innerText.toLowerCase();
        item.style.display = (!q || text.includes(q)) ? 'flex' : 'none';
      }});
      document.querySelectorAll('.category-group').forEach(grp => {{
        const visible = grp.querySelectorAll('.file-tree-item[style*="display: flex"]').length > 0 || !q;
        grp.style.display = visible ? 'block' : 'none';
      }});
    }}

    function stepLine(fileId, delta) {{
      const file = FILES_DATA[fileId];
      if (!file) return;
      const current = currentSelectedLines[fileId] || 1;
      let nextLine = current + delta;
      if (nextLine < 1) nextLine = 1;
      if (nextLine > file.explanations.length) nextLine = file.explanations.length;

      selectCodeLine(fileId, nextLine);
      const lineEl = document.getElementById(`line-${{fileId}}-${{nextLine}}`);
      if (lineEl) {{
        lineEl.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
      }}
    }}

    function selectCodeLine(fileId, lineNum) {{
      currentSelectedLines[fileId] = lineNum;

      document.querySelectorAll(`.code-line[data-file="${{fileId}}"]`).forEach(el => el.classList.remove('active-line'));
      const lineEl = document.getElementById(`line-${{fileId}}-${{lineNum}}`);
      if (lineEl) lineEl.classList.add('active-line');

      document.querySelectorAll(`#view_parallel_${{fileId}} .parallel-row`).forEach(r => r.classList.remove('active-row'));
      const prow = document.getElementById(`prow-${{fileId}}-${{lineNum}}`);
      if (prow) prow.classList.add('active-row');

      const file = FILES_DATA[fileId];
      if (!file) return;
      const exp = file.explanations[lineNum - 1] || file.explanations[0];
      if (!exp) return;

      const sideTag = document.getElementById(`side_tag_${{fileId}}`);
      const sideCode = document.getElementById(`side_code_${{fileId}}`);
      const sideWhy = document.getElementById(`side_why_${{fileId}}`);
      const sideWhat = document.getElementById(`side_what_${{fileId}}`);
      const sideConcept = document.getElementById(`side_concept_${{fileId}}`);

      if (sideTag) sideTag.innerText = `Line ${{exp.line}} of ${{file.lineCount}}`;
      if (sideCode) sideCode.innerHTML = `<code>${{escapeHtml(exp.code)}}</code>`;
      if (sideWhy) sideWhy.innerText = exp.why;
      if (sideWhat) sideWhat.innerText = exp.what;
      if (sideConcept) sideConcept.innerHTML = `💡 <strong>Core Concept:</strong> ${{escapeHtml(exp.concept || 'Architecture Pattern')}}`;
    }}

    function jumpToCodeLine(fileId, lineNum) {{
      selectCodeLine(fileId, lineNum);
      const lineEl = document.getElementById(`line-${{fileId}}-${{lineNum}}`);
      if (lineEl) {{
        lineEl.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        lineEl.classList.remove('flash-highlight');
        void lineEl.offsetWidth;
        lineEl.classList.add('flash-highlight');
      }}
    }}

    function copySnippet(fileId, btn) {{
      const file = FILES_DATA[fileId];
      if (!file) return;
      navigator.clipboard.writeText(file.rawCode).then(() => {{
        showToast('Source copied to clipboard!', '📋');
        const rect = btn.getBoundingClientRect();
        celebrateGold(rect.left + 20, rect.top);
      }});
    }}

    // ========================================================
    // FIND USAGES ENGINE (CTRL+CLICK OR MOBILE DIRECT TAP)
    // ========================================================
    window.addEventListener('keydown', (e) => {{
      if (e.key === 'Control' || e.key === 'Meta') {{
        document.body.classList.add('ctrl-pressed');
      }}
      if (e.key === 'Escape') {{
        closeFindUsagesModal();
        closeMobileSidebar();
        collapseAllExplainerSheets();
      }}
      if (activeFileId && activeFileId !== 'simulator') {{
        if (e.key === 'ArrowDown' || e.key === 'j') {{
          stepLine(activeFileId, 1);
        }} else if (e.key === 'ArrowUp' || e.key === 'k') {{
          stepLine(activeFileId, -1);
        }}
      }}
    }});

    window.addEventListener('keyup', (e) => {{
      if (e.key === 'Control' || e.key === 'Meta') {{
        document.body.classList.remove('ctrl-pressed');
      }}
    }});

    function handleSymbolClick(event, symName) {{
      const isTouch = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0) || window.matchMedia('(pointer: coarse)').matches;
      if (isTouch || event.ctrlKey || event.metaKey) {{
        event.stopPropagation();
        event.preventDefault();
        openFindUsages(symName);
      }}
    }}

    function openFindUsages(symName) {{
      const symData = SYMBOL_INDEX[symName];
      if (!symData) return;
      activeSymbolData = symData;

      document.getElementById('fuSymbolTitle').innerText = symName;
      document.getElementById('fuKindBadge').innerText = symData.kind;
      document.getElementById('fuCountBadge').innerText = `${{symData.usageCount}} occurrences`;
      document.getElementById('fuUsagesCountLabel').innerText = symData.usageCount;

      document.getElementById('fuDeclLocation').innerText = `${{symData.fileName}} (Line ${{symData.line}})`;
      document.getElementById('fuDeclCode').innerText = symData.snippet;
      document.getElementById('fuDeclJumpBtn').onclick = () => {{
        openFile(symData.fileId, symData.line);
        closeFindUsagesModal();
      }};

      renderUsagesList(symData.usages, symName);
      document.getElementById('findUsagesModal').classList.add('open');
      document.getElementById('fuFilterInput').value = '';
    }}

    function closeFindUsagesModal() {{
      document.getElementById('findUsagesModal').classList.remove('open');
    }}

    function closeFindUsagesOnBackdrop(e) {{
      if (e.target.id === 'findUsagesModal') {{
        closeFindUsagesModal();
      }}
    }}

    function renderUsagesList(usages, symName, filterText = '') {{
      const listContainer = document.getElementById('fuUsagesGroupList');
      if (!usages || usages.length === 0) {{
        listContainer.innerHTML = '<div style="padding: 16px; text-align: center; color: var(--text-dim); font-size: 11px;">No usages found.</div>';
        return;
      }}

      const groups = {{}};
      usages.forEach(u => {{
        if (filterText && !u.fileName.toLowerCase().includes(filterText) && !u.snippet.toLowerCase().includes(filterText)) {{
          return;
        }}
        if (!groups[u.fileId]) {{
          groups[u.fileId] = {{ fileName: u.fileName, relPath: u.relPath, items: [] }};
        }}
        groups[u.fileId].items.push(u);
      }});

      const fileKeys = Object.keys(groups);
      if (fileKeys.length === 0) {{
        listContainer.innerHTML = '<div style="padding: 16px; text-align: center; color: var(--text-dim); font-size: 11px;">No matching usages found.</div>';
        return;
      }}

      listContainer.innerHTML = fileKeys.map(fId => {{
        const group = groups[fId];
        return `
          <div class="fu-file-group">
            <div class="fu-file-header">
              <span>📄 ${{group.fileName}}</span>
              <span class="category-badge">${{group.items.length}}</span>
            </div>
            ${{group.items.map(item => {{
              const regex = new RegExp(`\\\\b(${{symName}})\\\\b`, 'g');
              const highlightedSnippet = escapeHtml(item.snippet).replace(regex, '<span class="fu-sym-highlight">$1</span>');
              return `
                <div class="fu-usage-row" onclick="jumpToUsage('${{item.fileId}}', ${{item.line}})">
                  <span class="fu-line-badge">Line ${{item.line}}</span>
                  <span class="fu-usage-code">${{highlightedSnippet}}</span>
                  <span style="font-size: 9.5px; color: var(--accent-primary); flex-shrink: 0;">Open ↑</span>
                </div>
              `;
            }}).join('')}}
          </div>
        `;
      }}).join('');
    }}

    function filterUsagesList(text) {{
      if (!activeSymbolData) return;
      renderUsagesList(activeSymbolData.usages, activeSymbolData.name, text.toLowerCase().trim());
    }}

    function jumpToUsage(fileId, lineNum) {{
      closeFindUsagesModal();
      openFile(fileId, lineNum);
    }}

    // ========================================================
    // THEME SWITCHER (Default: Light Mode -> Dim/Dark Mode)
    // ========================================================
    function toggleTheme() {{
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      const target = current === 'light' ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', target);
      document.getElementById('themeIcon').innerText = target === 'light' ? '🌙' : '☀️';
      document.getElementById('themeLabel').innerText = target === 'light' ? 'Dim Mode' : 'Light Mode';
      showToast(target === 'light' ? 'Switched to Editorial Light' : 'Switched to Developer Dim', '🎨');
    }}

    // ========================================================
    // SIMULATOR RUNTIME
    // ========================================================
    let simTasks = [
      {{ id: '1', title: 'Implement Room Migration v3', desc: 'Add new syncStatus column to SQLite tasks table', isCompleted: false, priority: 'URGENT', category: 'WORK', contact: 'Alex Johnson' }},
      {{ id: '2', title: 'Design Jetpack Compose TopAppBar', desc: 'Apply Material 3 theme colors and action icons', isCompleted: true, priority: 'HIGH', category: 'WORK', contact: null }},
      {{ id: '3', title: 'Schedule 15-min SyncWorker', desc: 'Verify NetworkType.CONNECTED constraint in WorkManager', isCompleted: false, priority: 'MEDIUM', category: 'WORK', contact: 'Sarah Smith' }},
      {{ id: '4', title: 'Grocery Shopping & Meal Prep', desc: 'Buy organic vegetables and protein shakes', isCompleted: false, priority: 'LOW', category: 'SHOPPING', contact: null }},
      {{ id: '5', title: 'Monthly Budget Review', desc: 'Check expense reports against financial targets', isCompleted: true, priority: 'HIGH', category: 'FINANCE', contact: 'David Chen' }}
    ];

    let currentCategoryFilter = 'ALL';
    let currentPriorityFilter = 'ALL';
    let currentSearchTerm = '';
    let isShowingStats = false;

    function renderSimTaskList() {{
      const container = document.getElementById('simTaskListContainer');
      if (!container) return;

      const filtered = simTasks.filter(t => {{
        const matchCat = (currentCategoryFilter === 'ALL' || t.category === currentCategoryFilter);
        const matchPri = (currentPriorityFilter === 'ALL' || t.priority === currentPriorityFilter);
        const matchSearch = (!currentSearchTerm || t.title.toLowerCase().includes(currentSearchTerm.toLowerCase()) || t.desc.toLowerCase().includes(currentSearchTerm.toLowerCase()));
        return matchCat && matchPri && matchSearch;
      }});

      if (filtered.length === 0) {{
        container.innerHTML = `
          <div style="text-align: center; padding: 30px 14px; color: var(--text-dim);">
            <div style="font-size: 24px; margin-bottom: 4px;">📋</div>
            <div style="font-size: 11px; font-weight: 600;">No tasks found</div>
          </div>
        `;
        return;
      }}

      container.innerHTML = filtered.map(t => {{
        const priorityClass = 'priority-' + t.priority.toLowerCase();
        return `
          <div class="sim-task-card ${{t.isCompleted ? 'completed' : ''}}" id="sim-task-${{t.id}}">
            <div class="sim-priority-stripe ${{priorityClass}}"></div>
            <div class="sim-checkbox ${{t.isCompleted ? 'checked' : ''}}" onclick="simToggleTask('${{t.id}}', event)">
              ${{t.isCompleted ? '<span style="color:white; font-size:10px;">✓</span>' : ''}}
            </div>
            <div class="sim-task-content" onclick="simToggleTask('${{t.id}}', event)">
              <div class="sim-task-title">${{t.title}}</div>
              <div class="sim-task-desc">${{t.desc}}</div>
              <div class="sim-task-footer">
                <span class="sim-tag">${{t.category}}</span>
                <span class="sim-tag" style="color: var(--accent-gold);">${{t.priority}}</span>
                ${{t.contact ? `<span class="sim-tag" style="color: var(--accent-teal);">👤 ${{t.contact}}</span>` : ''}}
              </div>
            </div>
          </div>
        `;
      }}).join('');
    }}

    function simToggleTask(id, event) {{
      const task = simTasks.find(t => t.id === id);
      if (!task) return;
      task.isCompleted = !task.isCompleted;
      renderSimTaskList();

      if (task.isCompleted) {{
        const rect = event ? event.target.getBoundingClientRect() : {{ left: window.innerWidth / 2, top: window.innerHeight / 2 }};
        celebrateGold(rect.left + 10, rect.top + 10);
        showToast(`Task completed! Room DB synced.`, '🎉');
      }}

      broadcastInspector(
        `User Event: Toggle Task #${{id}}`,
        `ToggleTaskCompletionUseCase executed for "${{task.title}}". New state: ${{task.isCompleted ? 'COMPLETED' : 'PENDING'}}.`,
        [
          {{ badge: 'badge-ui', label: '1. UI Event', code: 'onToggleTaskCompletion(task) invoked from TaskListScreen composable' }},
          {{ badge: 'badge-vm', label: '2. ViewModel', code: 'TaskViewModel.onToggleTaskCompletion() calls ToggleTaskCompletionUseCase(id)' }},
          {{ badge: 'badge-domain', label: '3. Domain', code: `ToggleTaskCompletionUseCase: task.copy(isCompleted = ${{task.isCompleted}})` }},
          {{ badge: 'badge-data', label: '4. Repository', code: 'TaskRepositoryImpl.updateTask(task) updates Room database' }},
          {{ badge: 'badge-data', label: '5. Room DAO', code: `TaskDao.updateTask(entity): UPDATE tasks SET isCompleted = ${{task.isCompleted ? 1 : 0}} WHERE id = '${{id}}'` }}
        ]
      );
    }}

    function simFilterCategory(cat, el) {{
      currentCategoryFilter = cat;
      document.querySelectorAll('.sim-chips-scroll .sim-chip').forEach(c => {{
        if (['All','Work','Personal','Shopping','Finance'].includes(c.innerText)) {{
          c.classList.remove('active');
        }}
      }});
      el.classList.add('active');
      renderSimTaskList();
    }}

    function simFilterPriority(pri, el) {{
      currentPriorityFilter = pri;
      el.parentElement.querySelectorAll('.sim-chip').forEach(c => c.classList.remove('active'));
      el.classList.add('active');
      renderSimTaskList();
    }}

    function simOnSearchInput(val) {{
      currentSearchTerm = val;
      renderSimTaskList();
    }}

    function simToggleStats() {{
      isShowingStats = !isShowingStats;
      const total = simTasks.length;
      const completed = simTasks.filter(t => t.isCompleted).length;
      const rate = total > 0 ? Math.round((completed / total) * 100) : 0;
      alert(`📊 Productivity Analytics:\\n\\nTotal Tasks: ${{total}}\\nCompleted: ${{completed}}\\nPending: ${{total - completed}}\\nCompletion Rate: ${{rate}}%\\n\\n(Corresponds to TaskAnalyticsScreen.kt & GetTaskAnalyticsUseCase.kt)`);
    }}

    function simTriggerBackgroundSync() {{
      broadcastInspector(
        'WorkManager: Manual Sync Triggered',
        'SyncTasksWorker executing immediate background synchronization via Retrofit REST API and Room database.',
        [
          {{ badge: 'badge-vm', label: '1. Trigger', code: 'SettingsScreen -> TaskViewModel.triggerManualSync()' }},
          {{ badge: 'badge-domain', label: '2. WorkManager', code: 'OneTimeWorkRequestBuilder<SyncTasksWorker>().build().enqueue()' }},
          {{ badge: 'badge-data', label: '3. Worker Execution', code: 'SyncTasksWorker.doWork() -> taskRepository.syncTasksWithRemote()' }},
          {{ badge: 'badge-data', label: '4. Retrofit REST', code: 'TaskApiService.batchSync(unsyncedTasks) -> returns RemoteSyncResponse' }},
          {{ badge: 'badge-data', label: '5. Room SQLite', code: 'TaskDao.insertTasks(remoteTasks) with OnConflictStrategy.REPLACE' }}
        ]
      );
      showToast('WorkManager Sync enqueued with CONNECTED constraint', '🔄');
    }}

    function simOpenAddModal() {{
      document.getElementById('simAddModal').classList.add('open');
    }}

    function simCloseAddModal() {{
      document.getElementById('simAddModal').classList.remove('open');
    }}

    function simSaveNewTask() {{
      const titleInput = document.getElementById('newTaskTitle');
      const descInput = document.getElementById('newTaskDesc');
      const priorityInput = document.getElementById('newTaskPriority');
      const categoryInput = document.getElementById('newTaskCategory');

      const title = titleInput.value.trim();
      if (!title) {{
        alert('⚠️ Task title cannot be empty! (Domain AddTaskUseCase validation)');
        return;
      }}

      const newTask = {{
        id: String(Date.now()),
        title: title,
        desc: descInput.value.trim(),
        isCompleted: false,
        priority: priorityInput.value,
        category: categoryInput.value,
        contact: null
      }};

      simTasks.unshift(newTask);
      titleInput.value = '';
      descInput.value = '';
      simCloseAddModal();
      renderSimTaskList();
      showToast('Task added through AddTaskUseCase!', '✅');
    }}

    function broadcastInspector(trigger, desc, steps) {{
      const tName = document.getElementById('inspectorTriggerName');
      const tDesc = document.getElementById('inspectorTriggerDesc');
      if (tName) tName.innerText = trigger;
      if (tDesc) tDesc.innerText = desc;

      const stepsContainer = document.getElementById('inspectorStepsList');
      if (stepsContainer) {{
        stepsContainer.innerHTML = steps.map(s => `
          <div class="pipeline-step">
            <span class="step-badge ${{s.badge}}">${{s.label}}</span>
            <div class="step-desc"><code>${{s.code}}</code></div>
          </div>
        `).join('');
      }}
    }}

    // Initial load: Open MainActivity and render mastery
    updateMasteryProgress();
    updateFileItemClasses();
    openFile('act_main');
  </script>

</body>
</html>
"""

# Write to build_spa_master_suite.py and index.html
with open(os.path.join(ROOT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_out)

print(f"Generated Revamped Editorial-Developer index.html successfully! Size: {len(html_out)} bytes, {len(html_out.splitlines())} lines.")
