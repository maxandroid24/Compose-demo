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
read_file = build_full_suite.read_file
TOKEN_REGEX = build_full_suite.TOKEN_REGEX

print("Building Symbol Index for Find Usages...")
SYMBOL_DATABASE = generate_symbol_database()
KNOWN_SYMBOLS = set(SYMBOL_DATABASE.keys())
print(f"Loaded {len(KNOWN_SYMBOLS)} symbols into cross-reference index.")

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

# Build line explanations for all files
all_file_explanations = {}

for cfg in ALL_FILES:
    file_id = cfg["id"]
    file_name = cfg["name"]
    file_cat = cfg["category"]
    raw_code = cfg["raw_code"]
    lines = raw_code.splitlines()
    
    file_line_list = []
    
    # Handcrafted explanations check
    handcrafted = ACTIVITY_LINE_EXPLANATIONS.get(file_id, [])
    hc_map = {}
    for item in handcrafted:
        if "line" in item:
            hc_map[item["line"]] = item
        elif "lines" in item:
            start, end = item["lines"]
            for l in range(start, end + 1):
                hc_map[l] = item
                
    for idx, raw_l in enumerate(lines, 1):
        if idx in hc_map:
            hc_item = hc_map[idx]
            file_line_list.append({
                "line": idx,
                "code": raw_l.strip(),
                "why": hc_item["why"],
                "what": hc_item["what"],
                "concept": hc_item.get("concept", "Architecture Rationale")
            })
        else:
            rule_item = get_rule_based_explanation(idx, raw_l, file_name, file_cat)
            if rule_item:
                file_line_list.append(rule_item)
            else:
                file_line_list.append({
                    "line": idx,
                    "code": raw_l.strip(),
                    "why": f"Part of the implementation of {file_name}.",
                    "what": "Evaluated during execution of this component.",
                    "concept": "General Implementation"
                })
                
    all_file_explanations[file_id] = file_line_list

# Generate HTML code lines and parallel table rows
for cfg in ALL_FILES:
    file_id = cfg["id"]
    raw_code = cfg["raw_code"]
    lines = raw_code.splitlines()
    exps = all_file_explanations[file_id]
    
    state = {'in_comment': False, 'in_string': False}
    html_lines = []
    parallel_rows = []
    
    for idx, line in enumerate(lines, 1):
        highlighted = highlight_line_with_symbols(line, state, KNOWN_SYMBOLS)
        exp_item = exps[idx - 1] if idx - 1 < len(exps) else None
        
        # 1. Split View / Code line
        html_lines.append(
            f'<div class="code-line" id="line-{file_id}-{idx}" data-file="{file_id}" data-line="{idx}" '
            f'onclick="selectCodeLine(\'{file_id}\', {idx})" title="Click to inspect Line {idx} in side pane">'
            f'<span class="line-num">{idx}</span><span class="line-code">{highlighted}</span></div>'
        )
        
        # 2. Parallel Table row
        why_text = html.escape(exp_item["why"]) if exp_item else ""
        what_text = html.escape(exp_item["what"]) if exp_item else ""
        concept_text = html.escape(exp_item.get("concept", "")) if exp_item else ""
        
        parallel_rows.append(
            f'<tr class="parallel-row" id="prow-{file_id}-{idx}" onclick="selectCodeLine(\'{file_id}\', {idx})">'
            f'<td class="parallel-col-code"><span class="line-num" style="display:inline-block; width:35px; color:var(--ide-line-num);">{idx}</span><span style="white-space:pre;">{highlighted}</span></td>'
            f'<td class="parallel-col-why"><div class="p-why-label">🎯 Why Added:</div>{why_text}</td>'
            f'<td class="parallel-col-what"><div class="p-what-label">⚙️ What It Does:</div>{what_text}{f"<div class=\'p-concept\'>💡 {concept_text}</div>" if concept_text else ""}</td>'
            f'</tr>'
        )
        
    cfg["interactive_formatted_code"] = "\n".join(html_lines)
    cfg["parallel_rows_html"] = "\n".join(parallel_rows)
    cfg["explanations"] = exps

# Group by category
categories = {}
for cfg in ALL_FILES:
    cat = cfg["category"]
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(cfg)

# Assemble Master HTML
html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Android Task Manager — Complete Code & Architecture Masterclass</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-base: #0E131F;
      --bg-surface: #131A2B;
      --bg-surface-elevated: #1B2438;
      --bg-card: #151D2F;
      --border-subtle: #1F2B45;
      --border-strong: #2D3D60;
      --border-highlight: #4F46E5;

      --accent-primary: #6366F1;
      --accent-primary-hover: #4F46E5;
      --accent-glow: rgba(99, 102, 241, 0.2);
      --accent-secondary: #8B5CF6;
      --accent-cyan: #06B6D4;
      --accent-success: #10B981;
      --accent-warning: #F59E0B;
      --accent-danger: #EF4444;

      --text-main: #F9FAFB;
      --text-muted: #9CA3AF;
      --text-dim: #6B7280;

      /* Android Studio IDE Dark Palette */
      --ide-bg: #1E1F22;
      --ide-border: #2B2D30;
      --ide-line-num: #4E5254;
      --ide-line-hover: #26282E;
      --ide-text: #BCBEC4;

      --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      --font-mono: 'JetBrains Mono', 'Fira Code', Menlo, Consolas, monospace;
      
      --sidebar-width: 320px;
    }}

    [data-theme="light"] {{
      --bg-base: #F8FAFC;
      --bg-surface: #FFFFFF;
      --bg-surface-elevated: #F1F5F9;
      --bg-card: #FFFFFF;
      --border-subtle: #E2E8F0;
      --border-strong: #CBD5E1;
      --border-highlight: #6366F1;
      --text-main: #0F172A;
      --text-muted: #475569;
      --text-dim: #94A3B8;

      /* Android Studio IDE Light Palette */
      --ide-bg: #F7F8FA;
      --ide-border: #E2E8F0;
      --ide-line-num: #9DA0A8;
      --ide-line-hover: #EAECEF;
      --ide-text: #0F172A;
      --accent-glow: rgba(99, 102, 241, 0.1);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      background-color: var(--bg-base); color: var(--text-main); font-family: var(--font-sans);
      line-height: 1.6; display: flex; min-height: 100vh; overflow-x: hidden; transition: background-color 0.3s, color 0.3s;
    }}

    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: var(--bg-base); }}
    ::-webkit-scrollbar-thumb {{ background: var(--border-strong); border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--accent-primary); }}

    .sidebar {{
      width: var(--sidebar-width); background-color: var(--bg-surface); border-right: 1px solid var(--border-subtle);
      height: 100vh; position: fixed; top: 0; left: 0; display: flex; flex-direction: column; z-index: 100;
      transition: transform 0.3s ease;
    }}

    .sidebar-header {{
      padding: 18px 20px 14px; border-bottom: 1px solid var(--border-subtle); display: flex; align-items: center; gap: 12px;
    }}
    .brand-icon {{
      width: 38px; height: 38px; border-radius: 10px; background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
      display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 4px 14px var(--accent-glow);
    }}
    .brand-title {{ font-size: 15px; font-weight: 700; letter-spacing: -0.3px; }}
    .brand-sub {{ font-size: 11px; color: var(--accent-cyan); font-weight: 500; }}

    .sidebar-search {{ padding: 12px 16px; border-bottom: 1px solid var(--border-subtle); }}
    .search-input-box {{ position: relative; width: 100%; }}
    .search-input-box input {{
      width: 100%; background: var(--bg-surface-elevated); border: 1px solid var(--border-strong);
      padding: 7px 12px 7px 34px; border-radius: 8px; color: var(--text-main); font-size: 12px; outline: none;
    }}
    .search-input-box svg {{ position: absolute; left: 10px; top: 50%; transform: translateY(-50%); width: 14px; height: 14px; color: var(--text-dim); }}

    .sidebar-nav {{ flex: 1; overflow-y: auto; padding: 12px 0; }}
    .category-group {{ margin-bottom: 16px; }}
    .category-label {{
      padding: 6px 18px; font-size: 10.5px; font-weight: 700; text-transform: uppercase;
      letter-spacing: 0.8px; color: var(--text-dim); display: flex; align-items: center; justify-content: space-between;
    }}
    .category-badge {{ background: var(--bg-surface-elevated); padding: 1px 6px; border-radius: 10px; font-size: 10px; }}

    .file-tree-item {{
      display: flex; align-items: center; gap: 8px; padding: 7px 18px; font-size: 12.5px;
      color: var(--text-muted); text-decoration: none; transition: all 0.2s; border-left: 2px solid transparent;
    }}
    .file-tree-item:hover {{ background-color: var(--bg-surface-elevated); color: var(--text-main); }}
    .file-tree-item.active {{
      background-color: var(--accent-glow); color: var(--accent-primary);
      border-left-color: var(--accent-primary); font-weight: 600;
    }}
    .item-badge {{ margin-left: auto; font-size: 10px; padding: 1px 5px; border-radius: 4px; background: var(--border-subtle); color: var(--text-dim); }}

    .main-wrapper {{ margin-left: var(--sidebar-width); flex: 1; display: flex; flex-direction: column; min-width: 0; }}

    .top-header {{
      height: 60px; background-color: var(--bg-surface); border-bottom: 1px solid var(--border-subtle);
      position: sticky; top: 0; z-index: 90; display: flex; align-items: center; justify-content: space-between;
      padding: 0 28px; backdrop-filter: blur(8px);
    }}
    .header-actions {{ display: flex; align-items: center; gap: 10px; }}

    .ide-tip-pill {{
      background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.3);
      padding: 5px 12px; border-radius: 16px; font-size: 11.5px; color: #A5B4FC; font-weight: 600; display: flex; align-items: center; gap: 6px;
    }}
    .ide-tip-pill kbd {{
      background: var(--bg-surface-elevated); border: 1px solid var(--border-strong);
      padding: 1px 5px; border-radius: 4px; font-size: 10.5px; color: var(--text-main); font-family: var(--font-mono);
    }}

    .btn-pill {{
      background: var(--bg-surface-elevated); border: 1px solid var(--border-strong); color: var(--text-main);
      padding: 6px 13px; border-radius: 16px; font-size: 11.5px; font-weight: 600; text-decoration: none;
      display: flex; align-items: center; gap: 6px; cursor: pointer; transition: all 0.2s;
    }}
    .btn-pill:hover {{ border-color: var(--accent-primary); background: var(--accent-glow); }}
    .btn-pill.primary {{ background: var(--accent-primary); border-color: var(--accent-primary); color: white; }}

    .content-area {{ padding: 24px; display: flex; flex-direction: column; gap: 32px; max-width: 1600px; margin: 0 auto; width: 100%; }}

    .hero-card {{
      background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(139, 92, 246, 0.05) 100%), var(--bg-card);
      border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 18px; padding: 26px 30px; position: relative; overflow: hidden;
    }}
    .hero-title {{
      font-size: 24px; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 8px;
      background: linear-gradient(90deg, #F9FAFB, #C7D2FE); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    [data-theme="light"] .hero-title {{
      background: linear-gradient(90deg, #0F172A, #4338CA); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    .hero-subtitle {{ font-size: 13.5px; color: var(--text-muted); max-width: 1000px; line-height: 1.6; margin-bottom: 16px; }}

    .hero-badges-row {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .tech-pill {{
      display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; background: var(--bg-surface-elevated);
      border: 1px solid var(--border-strong); border-radius: 12px; font-size: 11px; font-weight: 600; color: var(--text-main);
    }}
    .tech-pill.highlight {{ border-color: rgba(99, 102, 241, 0.5); color: #A5B4FC; background: rgba(99, 102, 241, 0.1); }}

    /* Simulator */
    .simulator-grid {{ display: grid; grid-template-columns: 360px 1fr; gap: 24px; align-items: start; }}
    .phone-mockup {{
      width: 100%; background: #000000; border: 10px solid #1E293B; border-radius: 40px;
      box-shadow: 0 20px 50px -10px rgba(0, 0, 0, 0.5); overflow: hidden; display: flex; flex-direction: column;
      height: 700px; position: sticky; top: 80px;
    }}
    .phone-notch-bar {{
      height: 28px; background: #000000; display: flex; align-items: center; justify-content: space-between;
      padding: 0 20px; font-size: 10px; font-weight: 600; color: #FFFFFF; flex-shrink: 0;
    }}
    .phone-screen {{ flex: 1; background: var(--bg-surface); display: flex; flex-direction: column; overflow: hidden; position: relative; }}
    .sim-topbar {{
      background: var(--bg-surface-elevated); padding: 10px 14px; border-bottom: 1px solid var(--border-subtle);
      display: flex; align-items: center; justify-content: space-between;
    }}
    .sim-topbar h4 {{ font-size: 14px; font-weight: 700; display: flex; align-items: center; gap: 6px; }}
    .sim-controls-row {{ display: flex; gap: 5px; }}
    .sim-btn-icon {{
      background: var(--bg-surface); border: 1px solid var(--border-strong); color: var(--text-muted);
      width: 28px; height: 28px; border-radius: 6px; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 12px;
    }}
    .sim-search-bar {{ padding: 8px 12px; background: var(--bg-surface); border-bottom: 1px solid var(--border-subtle); }}
    .sim-search-bar input {{
      width: 100%; background: var(--bg-surface-elevated); border: 1px solid var(--border-strong);
      padding: 6px 10px; border-radius: 6px; font-size: 11px; color: var(--text-main); outline: none;
    }}
    .sim-chips-scroll {{
      display: flex; gap: 5px; overflow-x: auto; padding: 6px 12px; border-bottom: 1px solid var(--border-subtle); scrollbar-width: none;
    }}
    .sim-chips-scroll::-webkit-scrollbar {{ display: none; }}
    .sim-chip {{
      padding: 3px 8px; background: var(--bg-surface-elevated); border: 1px solid var(--border-strong);
      border-radius: 10px; font-size: 10px; font-weight: 600; color: var(--text-muted); cursor: pointer; white-space: nowrap;
    }}
    .sim-chip.active {{ background: var(--accent-primary); border-color: var(--accent-primary); color: white; }}
    
    .sim-task-list {{ flex: 1; overflow-y: auto; padding: 10px 12px; display: flex; flex-direction: column; gap: 8px; }}
    .sim-task-card {{
      background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); border-radius: 10px;
      padding: 10px 12px; display: flex; align-items: flex-start; gap: 10px; transition: all 0.2s; position: relative; overflow: hidden;
    }}
    .sim-task-card:hover {{ border-color: var(--border-highlight); transform: translateY(-1px); }}
    .sim-task-card.completed {{ opacity: 0.6; }}
    .sim-priority-stripe {{ position: absolute; left: 0; top: 0; bottom: 0; width: 4px; }}
    .priority-urgent {{ background: var(--accent-danger); }}
    .priority-high {{ background: var(--accent-warning); }}
    .priority-medium {{ background: var(--accent-primary); }}
    .priority-low {{ background: var(--accent-cyan); }}

    .sim-checkbox {{
      width: 18px; height: 18px; border-radius: 5px; border: 2px solid var(--border-strong);
      display: flex; align-items: center; justify-content: center; cursor: pointer; margin-top: 2px; flex-shrink: 0;
    }}
    .sim-checkbox.checked {{ background: var(--accent-success); border-color: var(--accent-success); }}
    .sim-task-content {{ flex: 1; cursor: pointer; }}
    .sim-task-title {{ font-size: 12px; font-weight: 600; color: var(--text-main); margin-bottom: 2px; }}
    .sim-task-card.completed .sim-task-title {{ text-decoration: line-through; color: var(--text-dim); }}
    .sim-task-desc {{ font-size: 10px; color: var(--text-muted); margin-bottom: 6px; line-height: 1.4; }}
    .sim-task-footer {{ display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }}
    .sim-tag {{ font-size: 9px; padding: 1px 6px; border-radius: 4px; background: var(--bg-surface); border: 1px solid var(--border-subtle); font-weight: 600; }}

    .sim-fab {{
      position: absolute; right: 14px; bottom: 14px; width: 42px; height: 42px; border-radius: 21px;
      background: var(--accent-primary); color: white; display: flex; align-items: center; justify-content: center;
      font-size: 20px; box-shadow: 0 6px 16px var(--accent-glow); cursor: pointer; transition: transform 0.2s;
    }}
    .sim-fab:hover {{ transform: scale(1.08); }}

    /* Code Component Box */
    .code-component-container {{
      background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 14px; margin-bottom: 30px; overflow: hidden;
    }}
    .component-header {{
      padding: 12px 18px; background: var(--bg-surface-elevated); border-bottom: 1px solid var(--border-subtle);
      display: flex; align-items: center; justify-content: space-between; gap: 14px; flex-wrap: wrap;
    }}
    .file-meta {{ display: flex; align-items: center; gap: 10px; }}
    .file-icon {{
      width: 30px; height: 30px; border-radius: 6px; background: rgba(99, 102, 241, 0.15);
      color: var(--accent-primary); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 12px;
    }}
    .file-path {{ font-family: var(--font-mono); font-size: 13px; font-weight: 600; color: var(--text-main); }}
    .file-subtext {{ font-size: 11px; color: var(--text-dim); }}

    /* Layout Toggle Pills */
    .view-mode-toggles {{
      display: flex; align-items: center; gap: 4px; background: var(--bg-surface); padding: 3px; border-radius: 8px; border: 1px solid var(--border-strong);
    }}
    .v-btn {{
      background: transparent; border: none; color: var(--text-muted); font-size: 11px; font-weight: 600;
      padding: 4px 10px; border-radius: 6px; cursor: pointer; transition: all 0.15s;
    }}
    .v-btn:hover {{ color: var(--text-main); }}
    .v-btn.active {{
      background: var(--accent-primary); color: white; box-shadow: 0 2px 6px var(--accent-glow);
    }}

    .copy-code-btn {{
      background: var(--bg-surface); border: 1px solid var(--border-strong); color: var(--text-muted);
      padding: 5px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 5px;
    }}
    .copy-code-btn:hover {{ border-color: var(--accent-primary); color: var(--text-main); }}

    /* ========================================================
       SIDE-BY-SIDE SPLIT VIEW LAYOUT (Default)
       ======================================================== */
    .split-view-container {{
      display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(360px, 0.85fr);
      border-bottom: 1px solid var(--border-subtle); background: var(--bg-surface);
    }}
    @media (max-width: 1080px) {{
      .split-view-container {{ grid-template-columns: 1fr; }}
    }}

    .split-code-pane {{
      border-right: 1px solid var(--border-subtle); min-width: 0; overflow: hidden;
    }}
    @media (max-width: 1080px) {{
      .split-code-pane {{ border-right: none; border-bottom: 1px solid var(--border-subtle); }}
    }}

    .split-explainer-pane {{
      background: var(--bg-surface-elevated); padding: 16px; position: relative;
    }}

    /* Sticky Side-by-Side Explainer Box */
    .sticky-explainer-box {{
      position: sticky; top: 75px; max-height: calc(100vh - 100px); overflow-y: auto;
      display: flex; flex-direction: column; gap: 12px;
    }}
    .se-header {{
      background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 10px 14px;
    }}
    .se-title-row {{
      display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;
    }}
    .se-tag {{
      font-family: var(--font-mono); font-size: 12px; font-weight: 700; color: var(--accent-primary);
      background: rgba(99, 102, 241, 0.15); padding: 2px 8px; border-radius: 4px;
    }}
    .se-nav-group {{ display: flex; gap: 5px; }}
    .se-nav-btn {{
      background: var(--bg-surface-elevated); border: 1px solid var(--border-strong); color: var(--text-muted);
      font-size: 10.5px; padding: 2px 8px; border-radius: 4px; cursor: pointer; transition: all 0.15s; font-weight: 600;
    }}
    .se-nav-btn:hover {{ border-color: var(--accent-primary); color: var(--text-main); background: var(--accent-glow); }}
    .se-code-chip {{
      font-family: var(--font-mono); font-size: 11.5px; color: var(--text-main); background: var(--ide-bg);
      padding: 6px 10px; border-radius: 6px; border: 1px solid var(--border-subtle); overflow-x: auto;
      white-space: pre-wrap; word-break: break-all; max-height: 80px;
    }}

    .se-card {{
      background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 12px 14px;
    }}
    .se-card.why-card {{ border-left: 3px solid var(--accent-primary); }}
    .se-card.what-card {{ border-left: 3px solid var(--accent-cyan); }}
    .se-label {{
      font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;
    }}
    .why-label {{ color: var(--accent-primary); }}
    .what-label {{ color: var(--accent-cyan); }}
    .se-text {{ font-size: 12px; color: var(--text-muted); line-height: 1.6; }}
    .se-concept-badge {{
      font-size: 11px; color: var(--text-dim); background: var(--bg-surface);
      border: 1px solid var(--border-subtle); padding: 6px 12px; border-radius: 6px;
    }}

    /* ========================================================
       PARALLEL TABLE LAYOUT
       ======================================================== */
    .parallel-table-container {{
      display: none; overflow-x: auto; max-height: 650px; border-bottom: 1px solid var(--border-subtle);
    }}
    .parallel-table {{
      width: 100%; border-collapse: collapse; font-size: 12px;
    }}
    .parallel-table th {{
      position: sticky; top: 0; background: var(--bg-surface-elevated); padding: 10px 14px; text-align: left;
      font-size: 11px; font-weight: 700; color: var(--text-dim); text-transform: uppercase;
      border-bottom: 1px solid var(--border-strong); z-index: 10;
    }}
    .parallel-row {{
      border-bottom: 1px solid var(--border-subtle); transition: background 0.15s; cursor: pointer;
    }}
    .parallel-row:hover {{ background: var(--ide-line-hover); }}
    .parallel-row.active-row {{ background: rgba(99, 102, 241, 0.18) !important; }}
    .parallel-col-code {{
      width: 44%; padding: 8px 12px; font-family: var(--font-mono); font-size: 11.5px;
      vertical-align: top; border-right: 1px solid var(--border-subtle); line-height: 1.5;
    }}
    .parallel-col-why {{
      width: 28%; padding: 8px 12px; color: var(--text-muted); vertical-align: top;
      border-right: 1px solid var(--border-subtle); line-height: 1.55;
    }}
    .parallel-col-what {{
      width: 28%; padding: 8px 12px; color: var(--text-muted); vertical-align: top; line-height: 1.55;
    }}
    .p-why-label {{ font-size: 10px; font-weight: 700; color: var(--accent-primary); margin-bottom: 3px; text-transform: uppercase; }}
    .p-what-label {{ font-size: 10px; font-weight: 700; color: var(--accent-cyan); margin-bottom: 3px; text-transform: uppercase; }}
    .p-concept {{ font-size: 10px; color: var(--text-dim); margin-top: 5px; }}

    /* EXACT ANDROID STUDIO / INTELLIJ IDEA EDITOR STYLING */
    .code-viewport {{
      background: var(--ide-bg); padding: 14px 0; font-family: var(--font-mono); font-size: 12.5px;
      line-height: 1.65; overflow-x: auto; max-height: 650px; color: var(--ide-text);
      position: relative;
    }}
    .code-line {{ display: flex; min-height: 22px; padding: 0 16px 0 0; cursor: pointer; transition: background 0.15s ease; }}
    .code-line:hover {{ background-color: var(--ide-line-hover); }}
    .code-line.active-line {{ background-color: rgba(99, 102, 241, 0.28) !important; border-left: 3px solid var(--accent-primary); }}
    .line-num {{
      display: inline-block; width: 48px; padding-right: 14px; text-align: right;
      color: var(--ide-line-num); user-select: none; font-size: 11px; flex-shrink: 0;
    }}
    .line-code {{ flex: 1; white-space: pre; }}

    /* IDE Syntax Token Colors */
    .tok-kw {{ color: #CF8E6D; font-weight: 600; }}
    .tok-ann {{ color: #E0AC16; }}
    .tok-type {{ color: #56A8F5; }}
    .tok-str {{ color: #6AAB73; }}
    .tok-num {{ color: #2AACB8; }}
    .tok-cmt {{ color: #7A7E85; font-style: italic; }}
    .tok-fn {{ color: #FFC66D; }}

    [data-theme="light"] .tok-kw {{ color: #0033B3; font-weight: 600; }}
    [data-theme="light"] .tok-ann {{ color: #871094; }}
    [data-theme="light"] .tok-type {{ color: #267F99; }}
    [data-theme="light"] .tok-str {{ color: #067D17; }}
    [data-theme="light"] .tok-num {{ color: #1750EB; }}
    [data-theme="light"] .tok-cmt {{ color: #8C8C8C; font-style: italic; }}
    [data-theme="light"] .tok-fn {{ color: #00627A; }}

    /* SYMBOL USAGE & GO-TO-DEFINITION NAVIGATION */
    .sym-link {{
      position: relative; transition: all 0.15s ease; border-radius: 2px;
    }}
    
    /* PC: When holding Ctrl / Cmd */
    body.ctrl-pressed .sym-link {{
      text-decoration: underline !important;
      cursor: pointer !important;
      color: #60A5FA !important;
      background-color: rgba(96, 165, 250, 0.15);
      outline: 1px dashed rgba(96, 165, 250, 0.5);
    }}
    
    /* Mobile / Touch: direct tap styling */
    @media (pointer: coarse), (hover: none) {{
      .sym-link {{
        cursor: pointer !important;
        border-bottom: 1px dashed rgba(86, 168, 245, 0.6);
      }}
    }}

    /* Flash Highlight on Jump */
    @keyframes flashGlow {{
      0% {{ background-color: rgba(99, 102, 241, 0.7); }}
      50% {{ background-color: rgba(99, 102, 241, 0.4); }}
      100% {{ background-color: transparent; }}
    }}
    .flash-highlight {{
      animation: flashGlow 2s ease-out;
    }}

    /* FIND USAGES FLOATING MODAL */
    .fu-modal-overlay {{
      position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(6px); display: none; align-items: center; justify-content: center;
      padding: 20px; z-index: 1000;
    }}
    .fu-modal-overlay.open {{ display: flex; }}
    .fu-modal {{
      background: var(--bg-surface); border: 1px solid var(--border-strong); border-radius: 14px;
      width: 100%; max-width: 780px; max-height: 85vh; display: flex; flex-direction: column;
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6); overflow: hidden;
    }}
    .fu-header {{
      padding: 16px 20px; background: var(--bg-surface-elevated); border-bottom: 1px solid var(--border-subtle);
      display: flex; align-items: center; justify-content: space-between; gap: 12px;
    }}
    .fu-title-row {{ display: flex; align-items: center; gap: 10px; }}
    .fu-title {{ font-size: 16px; font-weight: 700; color: var(--text-main); }}
    .fu-kind-badge {{
      font-size: 10.5px; font-weight: 700; padding: 2px 7px; border-radius: 4px;
      background: rgba(99, 102, 241, 0.2); color: var(--accent-primary);
    }}
    .fu-count-badge {{
      font-size: 11px; color: var(--accent-cyan); background: var(--bg-surface);
      padding: 2px 8px; border-radius: 10px; border: 1px solid var(--border-subtle); font-weight: 600;
    }}
    .fu-close-btn {{
      background: transparent; border: none; color: var(--text-dim); font-size: 20px;
      cursor: pointer; padding: 4px 8px; border-radius: 6px;
    }}
    .fu-close-btn:hover {{ background: var(--bg-surface); color: var(--text-main); }}

    .fu-filter-box {{ padding: 10px 20px; border-bottom: 1px solid var(--border-subtle); background: var(--bg-surface); }}
    .fu-filter-box input {{
      width: 100%; background: var(--bg-surface-elevated); border: 1px solid var(--border-strong);
      padding: 7px 12px; border-radius: 6px; color: var(--text-main); font-size: 12px; outline: none;
    }}

    .fu-body {{ flex: 1; overflow-y: auto; padding: 16px 20px; display: flex; flex-direction: column; gap: 16px; }}

    .fu-decl-card {{
      background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.3);
      border-radius: 10px; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; gap: 12px;
    }}
    .fu-decl-meta {{ font-size: 12px; font-weight: 700; color: var(--accent-primary); margin-bottom: 4px; display: flex; align-items: center; gap: 6px; }}
    .fu-decl-code {{ font-family: var(--font-mono); font-size: 12px; color: var(--text-main); }}
    .fu-jump-btn {{
      background: var(--accent-primary); color: white; border: none; padding: 6px 12px; border-radius: 6px;
      font-size: 11px; font-weight: 600; cursor: pointer; white-space: nowrap; transition: background 0.2s;
    }}
    .fu-jump-btn:hover {{ background: var(--accent-primary-hover); }}

    .fu-file-group {{
      background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); border-radius: 8px; overflow: hidden;
    }}
    .fu-file-header {{
      padding: 8px 12px; background: rgba(255, 255, 255, 0.03); border-bottom: 1px solid var(--border-subtle);
      font-size: 12px; font-weight: 600; color: var(--text-main); display: flex; align-items: center; justify-content: space-between;
    }}
    .fu-usage-row {{
      padding: 8px 14px; display: flex; align-items: center; gap: 12px; cursor: pointer;
      border-bottom: 1px dashed var(--border-subtle); transition: background 0.15s; font-size: 12px;
    }}
    .fu-usage-row:last-child {{ border-bottom: none; }}
    .fu-usage-row:hover {{ background: rgba(99, 102, 241, 0.15); }}
    .fu-line-badge {{
      font-family: var(--font-mono); font-size: 10.5px; color: var(--text-dim); width: 50px; flex-shrink: 0;
    }}
    .fu-usage-code {{
      font-family: var(--font-mono); font-size: 11.5px; color: var(--text-muted); flex: 1;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}
    .fu-sym-highlight {{
      color: #FFD54F; font-weight: 700; background: rgba(255, 213, 79, 0.15); padding: 1px 4px; border-radius: 3px;
    }}

    /* Deep Dive Architecture Explanations */
    .explanation-panel {{ padding: 18px; background: var(--bg-surface); display: flex; flex-direction: column; gap: 12px; }}
    .explain-card {{ background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 10px; padding: 14px 16px; }}
    .explain-card-title {{ font-size: 12.5px; font-weight: 700; color: var(--accent-primary); margin-bottom: 6px; display: flex; align-items: center; gap: 6px; }}
    .explain-card p {{ font-size: 12px; color: var(--text-muted); line-height: 1.6; }}

    /* Modal for Add Task in Simulator */
    .sim-modal-overlay {{
      position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(4px);
      display: none; align-items: center; justify-content: center; padding: 14px; z-index: 50;
    }}
    .sim-modal-overlay.open {{ display: flex; }}
    .sim-modal {{
      background: var(--bg-surface); border: 1px solid var(--border-strong); border-radius: 14px;
      padding: 14px; width: 100%; max-width: 300px; display: flex; flex-direction: column; gap: 10px;
    }}
    .sim-form-group {{ display: flex; flex-direction: column; gap: 3px; }}
    .sim-form-group label {{ font-size: 9.5px; text-transform: uppercase; font-weight: 700; color: var(--text-dim); }}
    .sim-form-group input, .sim-form-group select, .sim-form-group textarea {{
      background: var(--bg-surface-elevated); border: 1px solid var(--border-strong);
      padding: 6px 8px; border-radius: 6px; font-size: 11px; color: var(--text-main); outline: none;
    }}
    .sim-modal-actions {{ display: flex; justify-content: flex-end; gap: 8px; margin-top: 4px; }}

    /* Execution Inspector Box */
    .live-inspector-panel {{
      background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 14px;
      padding: 20px; display: flex; flex-direction: column; gap: 16px;
    }}
    .inspector-header {{ display: flex; align-items: center; justify-content: space-between; }}
    .live-pulse {{
      display: flex; align-items: center; gap: 6px; font-size: 10px; font-weight: 700; color: var(--accent-success);
      background: rgba(16, 185, 129, 0.1); padding: 3px 8px; border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.3);
    }}
    .pulse-dot {{ width: 6px; height: 6px; border-radius: 50%; background: var(--accent-success); box-shadow: 0 0 8px var(--accent-success); }}
    .execution-pipeline-box {{
      background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); border-radius: 10px; padding: 14px;
    }}
    .pipeline-step {{
      display: flex; align-items: flex-start; gap: 10px; padding: 8px 0; border-bottom: 1px dashed var(--border-subtle);
    }}
    .pipeline-step:last-child {{ border-bottom: none; }}
    .step-badge {{
      font-size: 9.5px; font-weight: 700; padding: 2px 6px; border-radius: 4px; white-space: nowrap; flex-shrink: 0;
    }}
    .badge-ui {{ background: rgba(99, 102, 241, 0.2); color: #A5B4FC; }}
    .badge-vm {{ background: rgba(139, 92, 246, 0.2); color: #C4B5FD; }}
    .badge-domain {{ background: rgba(6, 182, 212, 0.2); color: #67E8F9; }}
    .badge-data {{ background: rgba(16, 185, 129, 0.2); color: #6EE7B7; }}
    .step-desc {{ font-size: 11.5px; color: var(--text-muted); }}
    .step-desc code {{ font-family: var(--font-mono); color: var(--text-main); font-size: 11px; }}

  </style>
</head>
<body>

  <!-- SIDEBAR NAVIGATION -->
  <aside class="sidebar" id="mainSidebar">
    <div class="sidebar-header">
      <div class="brand-icon">⚡</div>
      <div>
        <div class="brand-title">Android Masterclass</div>
        <div class="brand-sub">Compose vs XML • Complete Code</div>
      </div>
    </div>

    <div class="sidebar-search">
      <div class="search-input-box">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        <input type="text" id="globalSearchInput" placeholder="Search all 52 files & code...">
      </div>
    </div>

    <div class="sidebar-nav">
      <div style="padding: 0 18px 10px;">
        <a href="#interactive-simulator" class="btn-pill primary" style="justify-content: center; width: 100%;">
          📱 Launch App Simulator
        </a>
      </div>
"""

# Render Category Tree in Sidebar
for cat_name, file_list in categories.items():
    html_out += f"""
      <div class="category-group">
        <div class="category-label">
          <span>{cat_name}</span>
          <span class="category-badge">{len(file_list)}</span>
        </div>
    """
    for f in file_list:
        html_out += f"""
        <a href="#{f['id']}" class="file-tree-item" onclick="highlightSidebarItem(this)">
          <span style="font-size: 10px;">📄</span>
          <span>{f['name']}</span>
          <span class="item-badge">{f['badge']}</span>
        </a>
        """
    html_out += "</div>"

html_out += f"""
    </div>
  </aside>

  <!-- MAIN WRAPPER -->
  <div class="main-wrapper">
    <header class="top-header">
      <div class="ide-tip-pill">
        <span>🔀 Side-by-Side Active</span> • Click line to view explanation beside code • <kbd>Ctrl</kbd>+<strong>Click</strong> symbol for Usages
      </div>
      <div class="header-actions">
        <button class="btn-pill" id="globalLayoutToggleBtn" onclick="toggleGlobalLayout()">
          <span id="globalLayoutIcon">🔀</span>
          <span id="globalLayoutLabel">Switch All to Parallel Table</span>
        </button>
        <button class="btn-pill" onclick="toggleTheme()">
          <span id="themeIcon">☀️</span>
          <span id="themeLabel">Light Mode</span>
        </button>
      </div>
    </header>

    <main class="content-area">

      <!-- HERO BANNER -->
      <section class="hero-card">
        <h1 class="hero-title">Android Clean Architecture & Paradigms Masterclass</h1>
        <p class="hero-subtitle">
          Complete, 100% unabridged source code for all <strong>52 files</strong>. 
          Features <strong>Side-by-Side Code & Explanations</strong> so you never have to scroll back and forth to inspect why each line was added and what it does.
        </p>
        <div class="hero-badges-row">
          <span class="tech-pill highlight">🔀 Side-by-Side Code + Explainer</span>
          <span class="tech-pill highlight">📋 Parallel Line-by-Line Table</span>
          <span class="tech-pill highlight">🔍 Ctrl+Click Find Usages</span>
          <span class="tech-pill">✨ 10 Complete Activities</span>
          <span class="tech-pill">⚡ Jetpack Compose + XML Views</span>
          <span class="tech-pill">🗄️ Room Database v3</span>
          <span class="tech-pill">⚙️ WorkManager 15-Min Sync</span>
        </div>
      </section>

      <!-- LIVE INTERACTIVE SIMULATOR & EXECUTION PIPELINE -->
      <section id="interactive-simulator">
        <div class="simulator-grid">
          
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

              <!-- Priority Chips -->
              <div class="sim-chips-scroll" style="background: var(--bg-surface-elevated); padding: 4px 12px;">
                <span style="font-size: 9px; color: var(--text-dim); text-transform: uppercase; font-weight: 700; align-self: center;">Priority:</span>
                <div class="sim-chip active" onclick="simFilterPriority('ALL', this)">All</div>
                <div class="sim-chip" onclick="simFilterPriority('URGENT', this)">Urgent</div>
                <div class="sim-chip" onclick="simFilterPriority('HIGH', this)">High</div>
                <div class="sim-chip" onclick="simFilterPriority('MEDIUM', this)">Med</div>
                <div class="sim-chip" onclick="simFilterPriority('LOW', this)">Low</div>
              </div>

              <!-- Scrollable Tasks List -->
              <div class="sim-task-list" id="simTaskListContainer">
                <!-- Dynamically populated -->
              </div>

              <!-- Floating Action Button -->
              <div class="sim-fab" onclick="simOpenAddModal()" title="Add New Task (AddTaskUseCase)">
                +
              </div>

              <!-- Add Task Modal -->
              <div class="sim-modal-overlay" id="simAddModal">
                <div class="sim-modal">
                  <div style="font-size: 13px; font-weight: 700; color: var(--accent-primary);">➕ Add New Task</div>
                  <div class="sim-form-group">
                    <label>Task Title *</label>
                    <input type="text" id="newTaskTitle" placeholder="e.g. Write Unit Tests">
                  </div>
                  <div class="sim-form-group">
                    <label>Description</label>
                    <input type="text" id="newTaskDesc" placeholder="e.g. Test Room DAO and ViewModel">
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
                  <div class="sim-form-group">
                    <label>Assigned Contact (ContentProvider)</label>
                    <select id="newTaskContact">
                      <option value="">None (Unassigned)</option>
                      <option value="Alex Johnson">Alex Johnson (+1 555-0192)</option>
                      <option value="Sarah Smith">Sarah Smith (+1 555-0148)</option>
                      <option value="David Chen">David Chen (+1 555-0177)</option>
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
                <h4 style="font-size: 15px; font-weight: 700;">Live Android Execution Pipeline</h4>
                <p style="font-size: 11.5px; color: var(--text-muted);">Real-time reactive invocation trace matching the Android codebase</p>
              </div>
              <div class="live-pulse">
                <div class="pulse-dot"></div>
                <span>LISTENING</span>
              </div>
            </div>

            <div style="background: var(--bg-surface); padding: 12px 16px; border-radius: 10px; border: 1px solid var(--border-subtle);">
              <div style="font-size: 10px; font-weight: 700; color: var(--text-dim); text-transform: uppercase;">Current Trigger</div>
              <div id="inspectorTriggerName" style="font-size: 14px; font-weight: 700; color: var(--accent-primary); margin-top: 2px;">
                Initial Load: App Started
              </div>
              <div id="inspectorTriggerDesc" style="font-size: 11.5px; color: var(--text-muted); margin-top: 3px;">
                Observing tasks via combine(searchQuery.debounce(200), category, priority, completedOnly) in TaskViewModel.
              </div>
            </div>

            <div class="execution-pipeline-box">
              <div style="font-size: 10px; font-weight: 700; color: var(--text-dim); margin-bottom: 8px; text-transform: uppercase;">
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
      </section>
"""

# Render All 52 Files with Side-by-Side & Parallel Table Options
for cfg in ALL_FILES:
    file_id = cfg["id"]
    exps = cfg["explanations"]
    first_exp = exps[0] if exps else {"line": 1, "code": "", "why": "File entry.", "what": "Loaded by Android runtime.", "concept": "File Scope"}
    
    html_out += f"""
      <!-- FILE: {cfg['name']} -->
      <section class="code-component-container" id="{cfg['id']}">
        <div class="component-header">
          <div class="file-meta">
            <div class="file-icon">KT</div>
            <div>
              <div class="file-path">{cfg['rel_path']}</div>
              <div class="file-subtext">{cfg['summary']} ({cfg['line_count']} lines)</div>
            </div>
          </div>
          
          <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <!-- View Mode Switcher -->
            <div class="view-mode-toggles">
              <button class="v-btn active" id="btn_split_{cfg['id']}" onclick="toggleViewLayout('{cfg['id']}', 'split')" title="Side-by-side code and sticky explanation">
                🔀 Side-by-Side
              </button>
              <button class="v-btn" id="btn_parallel_{cfg['id']}" onclick="toggleViewLayout('{cfg['id']}', 'parallel')" title="Line by line table with Code, Why, and What columns">
                📋 Parallel Table
              </button>
            </div>
            
            <span class="tech-pill highlight">{cfg['badge']}</span>
            <button class="copy-code-btn" onclick="copyFullSnippet('{cfg['id']}_raw', this)">
              <span>📋 Copy Code</span>
            </button>
          </div>
        </div>

        <!-- 1. SIDE-BY-SIDE SPLIT VIEW (Default on desktop) -->
        <div class="split-view-container" id="view_split_{cfg['id']}">
          <!-- Left: IDE Code Editor -->
          <div class="split-code-pane">
            <div class="code-viewport" id="viewport_{cfg['id']}">
{cfg['interactive_formatted_code']}
            </div>
          </div>

          <!-- Right: Sticky Side-by-Side Explainer Panel -->
          <div class="split-explainer-pane">
            <div class="sticky-explainer-box">
              <div class="se-header">
                <div class="se-title-row">
                  <span class="se-tag" id="side_tag_{cfg['id']}">Line {first_exp['line']}</span>
                  <div class="se-nav-group">
                    <button class="se-nav-btn" onclick="stepLine('{cfg['id']}', -1)" title="Previous Line">▲ Prev</button>
                    <button class="se-nav-btn" onclick="stepLine('{cfg['id']}', 1)" title="Next Line">▼ Next</button>
                  </div>
                </div>
                <div class="se-code-chip" id="side_code_{cfg['id']}">
                  <code>{html.escape(first_exp['code'][:80])}</code>
                </div>
              </div>

              <div class="se-card why-card">
                <div class="se-label why-label">🎯 Why is this piece of code added?</div>
                <div class="se-text" id="side_why_{cfg['id']}">{html.escape(first_exp['why'])}</div>
              </div>

              <div class="se-card what-card">
                <div class="se-label what-label">⚙️ What does it do?</div>
                <div class="se-text" id="side_what_{cfg['id']}">{html.escape(first_exp['what'])}</div>
              </div>

              <div class="se-concept-badge" id="side_concept_{cfg['id']}">
                💡 <strong>Core Concept:</strong> {html.escape(first_exp.get('concept', 'Architecture Rationale'))}
              </div>
            </div>
          </div>
        </div>

        <!-- 2. PARALLEL TABLE VIEW (Code | Why Added | What It Does) -->
        <div class="parallel-table-container" id="view_parallel_{cfg['id']}">
          <table class="parallel-table">
            <thead>
              <tr>
                <th style="width: 44%;">Line & Source Code</th>
                <th style="width: 28%;">🎯 Why is this piece of code added?</th>
                <th style="width: 28%;">⚙️ What does it do?</th>
              </tr>
            </thead>
            <tbody>
{cfg['parallel_rows_html']}
            </tbody>
          </table>
        </div>

        <textarea id="{cfg['id']}_raw" style="display: none;">{html.escape(cfg['raw_code'])}</textarea>

        <!-- CLEAN ARCHITECTURE ROLE & ANNOTATIONS -->
        <div class="explanation-panel">
          <div class="explain-card" style="border-left: 3px solid var(--accent-primary);">
            <div class="explain-card-title">🏛️ Clean Architecture Role & Annotations</div>
            <p><strong>Layer:</strong> {cfg['category']}</p>
            <p style="margin-top: 4px;"><strong>Annotations Explained:</strong> {cfg['annotations']}</p>
          </div>
    """

    for b in cfg['breakdown']:
        html_out += f"""
          <div class="explain-card">
            <div class="explain-card-title">🔍 {html.escape(b['section'])}</div>
            <p>{html.escape(b['explanation'])}</p>
          </div>
        """

    html_out += """
        </div>
      </section>
    """

# Serialize all file explanations and symbol index to JSON
json_exps = json.dumps(all_file_explanations)
json_symbols = json.dumps(SYMBOL_DATABASE)

html_out += f"""
    </main>
  </div>

  <!-- FIND USAGES FLOATING MODAL (Android Studio IDE Style) -->
  <div class="fu-modal-overlay" id="findUsagesModal" onclick="closeFindUsagesOnBackdrop(event)">
    <div class="fu-modal">
      <div class="fu-header">
        <div class="fu-title-row">
          <span style="font-size: 18px;">🔍</span>
          <div class="fu-title" id="fuSymbolTitle">Find Usages</div>
          <span class="fu-kind-badge" id="fuKindBadge">Class</span>
          <span class="fu-count-badge" id="fuCountBadge">0 usages</span>
        </div>
        <button class="fu-close-btn" onclick="closeFindUsagesModal()" title="Close (Esc)">✕</button>
      </div>

      <div class="fu-filter-box">
        <input type="text" id="fuFilterInput" placeholder="Filter usages by file name or code snippet..." oninput="filterUsagesList(this.value)">
      </div>

      <div class="fu-body" id="fuBody">
        <!-- Declaration Card -->
        <div class="fu-decl-card" id="fuDeclCard">
          <div>
            <div class="fu-decl-meta">
              <span>📌 Declaration:</span> <span id="fuDeclLocation">File.kt (Line 1)</span>
            </div>
            <div class="fu-decl-code" id="fuDeclCode">class Example</div>
          </div>
          <button class="fu-jump-btn" id="fuDeclJumpBtn" onclick="jumpToDecl()">Jump to Declaration ↑</button>
        </div>

        <div style="font-size: 11px; font-weight: 700; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px;">
          Usages in Project (<span id="fuUsagesCountLabel">0</span>)
        </div>

        <div id="fuUsagesGroupList" style="display: flex; flex-direction: column; gap: 10px;">
          <!-- Dynamically populated -->
        </div>
      </div>
    </div>
  </div>

  <script>
    const LINE_EXPLANATIONS = {json_exps};
    const SYMBOL_INDEX = {json_symbols};

    let activeSymbolData = null;
    let currentSelectedLines = {{}};
    let currentGlobalLayout = 'split'; // 'split' or 'parallel'

    function escapeHtml(text) {{
      const map = {{ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }};
      return String(text).replace(/[&<>"']/g, m => map[m]);
    }}

    // Toggle View Layout per file card
    function toggleViewLayout(fileId, mode) {{
      const splitView = document.getElementById(`view_split_${{fileId}}`);
      const parallelView = document.getElementById(`view_parallel_${{fileId}}`);
      const btnSplit = document.getElementById(`btn_split_${{fileId}}`);
      const btnParallel = document.getElementById(`btn_parallel_${{fileId}}`);

      if (mode === 'split') {{
        if (splitView) splitView.style.display = 'grid';
        if (parallelView) parallelView.style.display = 'none';
        if (btnSplit) btnSplit.classList.add('active');
        if (btnParallel) btnParallel.classList.remove('active');
      }} else if (mode === 'parallel') {{
        if (splitView) splitView.style.display = 'none';
        if (parallelView) parallelView.style.display = 'block';
        if (btnSplit) btnSplit.classList.remove('active');
        if (btnParallel) btnParallel.classList.add('active');
      }}
    }}

    // Global layout toggle across all 52 files
    function toggleGlobalLayout() {{
      currentGlobalLayout = currentGlobalLayout === 'split' ? 'parallel' : 'split';
      const label = document.getElementById('globalLayoutLabel');
      const icon = document.getElementById('globalLayoutIcon');

      if (currentGlobalLayout === 'split') {{
        label.innerText = 'Switch All to Parallel Table';
        icon.innerText = '🔀';
      }} else {{
        label.innerText = 'Switch All to Side-by-Side';
        icon.innerText = '📋';
      }}

      document.querySelectorAll('.code-component-container').forEach(card => {{
        toggleViewLayout(card.id, currentGlobalLayout);
      }});
    }}

    // Step Line navigation (Prev / Next) in Side-by-Side Pane
    function stepLine(fileId, delta) {{
      const exps = LINE_EXPLANATIONS[fileId] || [];
      const current = currentSelectedLines[fileId] || 1;
      let nextLine = current + delta;
      if (nextLine < 1) nextLine = 1;
      if (nextLine > exps.length) nextLine = exps.length;

      selectCodeLine(fileId, nextLine);
      const lineEl = document.getElementById(`line-${{fileId}}-${{nextLine}}`);
      if (lineEl) {{
        lineEl.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
      }}
    }}

    // Select code line: updates BOTH Split View side-panel and Parallel Table row
    function selectCodeLine(fileId, lineNum) {{
      currentSelectedLines[fileId] = lineNum;

      // 1. Highlight line in Code Editor
      document.querySelectorAll(`.code-line[data-file="${{fileId}}"]`).forEach(el => el.classList.remove('active-line'));
      const lineEl = document.getElementById(`line-${{fileId}}-${{lineNum}}`);
      if (lineEl) lineEl.classList.add('active-line');

      // 2. Highlight row in Parallel Table
      document.querySelectorAll(`#view_parallel_${{fileId}} .parallel-row`).forEach(r => r.classList.remove('active-row'));
      const prow = document.getElementById(`prow-${{fileId}}-${{lineNum}}`);
      if (prow) prow.classList.add('active-row');

      // 3. Lookup explanation
      const fileExps = LINE_EXPLANATIONS[fileId] || [];
      const exp = fileExps.find(e => e.line === lineNum) || fileExps[0];
      if (!exp) return;

      // 4. Update the Sticky Side-by-Side Explainer Panel
      const sideTag = document.getElementById(`side_tag_${{fileId}}`);
      const sideCode = document.getElementById(`side_code_${{fileId}}`);
      const sideWhy = document.getElementById(`side_why_${{fileId}}`);
      const sideWhat = document.getElementById(`side_what_${{fileId}}`);
      const sideConcept = document.getElementById(`side_concept_${{fileId}}`);

      if (sideTag) sideTag.innerText = `Line ${{exp.line}}`;
      if (sideCode) sideCode.innerHTML = `<code>${{escapeHtml(exp.code)}}</code>`;
      if (sideWhy) sideWhy.innerText = exp.why;
      if (sideWhat) sideWhat.innerText = exp.what;
      if (sideConcept) sideConcept.innerHTML = `💡 <strong>Core Concept:</strong> ${{escapeHtml(exp.concept || 'Architecture Rationale')}}`;
    }}

    function jumpToCodeLine(fileId, lineNum) {{
      selectCodeLine(fileId, lineNum);
      const lineEl = document.getElementById(`line-${{fileId}}-${{lineNum}}`);
      if (lineEl) {{
        lineEl.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        lineEl.classList.remove('flash-highlight');
        void lineEl.offsetWidth; // trigger reflow
        lineEl.classList.add('flash-highlight');
      }}
    }}

    // Track Ctrl/Cmd key for desktop users
    window.addEventListener('keydown', (e) => {{
      if (e.key === 'Control' || e.key === 'Meta') {{
        document.body.classList.add('ctrl-pressed');
      }}
      if (e.key === 'Escape') {{
        closeFindUsagesModal();
      }}
    }});

    window.addEventListener('keyup', (e) => {{
      if (e.key === 'Control' || e.key === 'Meta') {{
        document.body.classList.remove('ctrl-pressed');
      }}
    }});

    // Symbol click handler: Ctrl+Click on PC, Direct Tap on Mobile
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
        jumpToCodeLine(symData.fileId, symData.line);
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
        listContainer.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-dim);">No usages found.</div>';
        return;
      }}

      // Group by file
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
        listContainer.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-dim);">No matching usages found.</div>';
        return;
      }}

      listContainer.innerHTML = fileKeys.map(fId => {{
        const group = groups[fId];
        return `
          <div class="fu-file-group">
            <div class="fu-file-header">
              <span>📄 ${{group.fileName}} <span style="font-size: 10px; color: var(--text-dim);">(${{group.relPath}})</span></span>
              <span class="category-badge">${{group.items.length}}</span>
            </div>
            ${{group.items.map(item => {{
              const regex = new RegExp(`\\\\b(${{symName}})\\\\b`, 'g');
              const highlightedSnippet = escapeHtml(item.snippet).replace(regex, '<span class="fu-sym-highlight">$1</span>');
              return `
                <div class="fu-usage-row" onclick="jumpToUsage('${{item.fileId}}', ${{item.line}})">
                  <span class="fu-line-badge">Line ${{item.line}}</span>
                  <span class="fu-usage-code">${{highlightedSnippet}}</span>
                  <span style="font-size: 10px; color: var(--accent-primary);">Jump ↑</span>
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
      jumpToCodeLine(fileId, lineNum);
    }}

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
          <div style="text-align: center; padding: 40px 20px; color: var(--text-dim);">
            <div style="font-size: 28px; margin-bottom: 6px;">📋</div>
            <div style="font-size: 12px; font-weight: 600;">No tasks found</div>
          </div>
        `;
        return;
      }}

      container.innerHTML = filtered.map(t => {{
        const priorityClass = 'priority-' + t.priority.toLowerCase();
        return `
          <div class="sim-task-card ${{t.isCompleted ? 'completed' : ''}}" id="sim-task-${{t.id}}">
            <div class="sim-priority-stripe ${{priorityClass}}"></div>
            <div class="sim-checkbox ${{t.isCompleted ? 'checked' : ''}}" onclick="simToggleTask('${{t.id}}')">
              ${{t.isCompleted ? '<span style="color:white; font-size:10px;">✓</span>' : ''}}
            </div>
            <div class="sim-task-content" onclick="simToggleTask('${{t.id}}')">
              <div class="sim-task-title">${{t.title}}</div>
              <div class="sim-task-desc">${{t.desc}}</div>
              <div class="sim-task-footer">
                <span class="sim-tag">${{t.category}}</span>
                <span class="sim-tag" style="color: var(--accent-primary);">${{t.priority}}</span>
                ${{t.contact ? `<span class="sim-tag" style="color: var(--accent-cyan);">👤 ${{t.contact}}</span>` : ''}}
              </div>
            </div>
          </div>
        `;
      }}).join('');
    }}

    function simToggleTask(id) {{
      const task = simTasks.find(t => t.id === id);
      if (!task) return;
      task.isCompleted = !task.isCompleted;
      renderSimTaskList();

      broadcastInspector(
        `User Event: Toggle Task #${id}`,
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

      broadcastInspector(
        `Filter Change: Category = ${{cat}}`,
        `TaskViewModel.onCategoryFilterSelected('${{cat}}') updated _selectedCategory StateFlow.`,
        [
          {{ badge: 'badge-ui', label: '1. UI Interaction', code: 'Category filter chip clicked' }},
          {{ badge: 'badge-vm', label: '2. Reactive StateFlow', code: `_selectedCategory.value = ${{cat === 'ALL' ? 'null' : 'Category.' + cat}}` }},
          {{ badge: 'badge-domain', label: '3. Combine Operator', code: 'combine(searchQuery, selectedCategory, priority) emits newly filtered listUiState' }},
          {{ badge: 'badge-ui', label: '4. Recomposition', code: 'TaskListScreen recomposes with ${{simTasks.filter(t => cat === "ALL" || t.category === cat).length}} tasks' }}
        ]
      );
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
      alert('🔄 WorkManager Sync Triggered!\\n\\nWorker enqueued with NetworkType.CONNECTED constraint.\\nTasks synchronized with simulated Retrofit REST API.');
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
      const contactInput = document.getElementById('newTaskContact');

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
        contact: contactInput.value || null
      }};

      simTasks.unshift(newTask);
      titleInput.value = '';
      descInput.value = '';
      simCloseAddModal();
      renderSimTaskList();
    }}

    function broadcastInspector(trigger, desc, steps) {{
      document.getElementById('inspectorTriggerName').innerText = trigger;
      document.getElementById('inspectorTriggerDesc').innerText = desc;

      const stepsContainer = document.getElementById('inspectorStepsList');
      stepsContainer.innerHTML = steps.map(s => `
        <div class="pipeline-step">
          <span class="step-badge ${{s.badge}}">${{s.label}}</span>
          <div class="step-desc"><code>${{s.code}}</code></div>
        </div>
      `).join('');
    }}

    function copyFullSnippet(textareaId, btn) {{
      const text = document.getElementById(textareaId).value;
      navigator.clipboard.writeText(text).then(() => {{
        const original = btn.innerHTML;
        btn.innerHTML = '<span>✅ Copied Full File!</span>';
        setTimeout(() => {{ btn.innerHTML = original; }}, 2000);
      }});
    }}

    function toggleTheme() {{
      const current = document.documentElement.getAttribute('data-theme');
      const target = current === 'light' ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', target);
      document.getElementById('themeIcon').innerText = target === 'light' ? '🌙' : '☀️';
      document.getElementById('themeLabel').innerText = target === 'light' ? 'Dark Mode' : 'Light Mode';
    }}

    function highlightSidebarItem(el) {{
      document.querySelectorAll('.file-tree-item').forEach(item => item.classList.remove('active'));
      el.classList.add('active');
    }}

    document.getElementById('globalSearchInput').addEventListener('input', function(e) {{
      const term = e.target.value.toLowerCase().trim();
      document.querySelectorAll('.code-component-container').forEach(card => {{
        const text = card.innerText.toLowerCase();
        card.style.display = (!term || text.includes(term)) ? 'block' : 'none';
      }});
    }});

    renderSimTaskList();
  </script>

</body>
</html>
"""

with open(os.path.join(ROOT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_out)

print(f"Generated Side-by-Side Master Suite index.html successfully! Size: {len(html_out)} bytes, {len(html_out.splitlines())} lines.")
