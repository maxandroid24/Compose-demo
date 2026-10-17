import os
import re
import html

ROOT_DIR = r"c:\Users\navne\StudioProjects\Compose-demo"
from test_read_all import FILES_CONFIG, read_file

TOKEN_REGEX = re.compile(
    r'(?P<COMMENT>/\*[\s\S]*?\*/|//[^\n]*)'
    r'|(?P<STRING>"""[\s\S]*?"""|"(?:\\.|[^"\\])*")'
    r'|(?P<ANNOTATION>@[A-Za-z0-9_]+)'
    r'|(?P<KEYWORD>\b(?:package|import|class|interface|object|data|enum|abstract|sealed|open|fun|val|var|override|suspend|operator|private|protected|public|internal|constructor|init|return|if|else|when|try|catch|finally|throw|null|true|false|this|super|by|in|is|as|typealias|companion)\b)'
    r'|(?P<NUMBER>\b\d+(?:\.\d+)?[LlfF]?\b)'
    r'|(?P<TYPE>\b[A-Z][A-Za-z0-9_]*\b)'
    r'|(?P<FUNCTION>\b[a-zA-Z_][A-Za-z0-9_]*(?=\s*\())'
)

def highlight_line(line, state):
    in_comment = state['in_comment']
    in_string = state['in_string']
    
    # If currently in a multi-line comment
    if in_comment:
        if '*/' in line:
            idx = line.find('*/') + 2
            cmt_part = html.escape(line[:idx])
            rest = line[idx:]
            state['in_comment'] = False
            return f'<span class="tok-cmt">{cmt_part}</span>' + highlight_line(rest, state)
        else:
            return f'<span class="tok-cmt">{html.escape(line)}</span>'
            
    # If currently in a multi-line string
    if in_string:
        if '"""' in line:
            idx = line.find('"""') + 3
            str_part = html.escape(line[:idx])
            rest = line[idx:]
            state['in_string'] = False
            return f'<span class="tok-str">{str_part}</span>' + highlight_line(rest, state)
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
            out.append(f'<span class="tok-type">{escaped}</span>')
        elif group == 'FUNCTION':
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

def format_code_with_ide_lines(raw_code):
    lines = raw_code.splitlines()
    state = {'in_comment': False, 'in_string': False}
    html_lines = []
    for idx, line in enumerate(lines, 1):
        highlighted = highlight_line(line, state)
        html_lines.append(f'<div class="code-line"><span class="line-num">{idx}</span><span class="line-code">{highlighted}</span></div>')
    return "\n".join(html_lines)

print("Reading and formatting all 38 files with IDE colors and line numbers...")
for cfg in FILES_CONFIG:
    full_path = os.path.join(ROOT_DIR, cfg["rel_path"].replace("/", os.sep))
    raw_code = read_file(full_path)
    cfg["raw_code"] = raw_code
    cfg["formatted_code"] = format_code_with_ide_lines(raw_code)
    cfg["line_count"] = len(raw_code.splitlines())

# Group files by category
categories = {}
for cfg in FILES_CONFIG:
    cat = cfg["category"]
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(cfg)

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
      
      --sidebar-width: 330px;
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

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    html {{
      scroll-behavior: smooth;
    }}

    body {{
      background-color: var(--bg-base);
      color: var(--text-main);
      font-family: var(--font-sans);
      line-height: 1.6;
      display: flex;
      min-height: 100vh;
      overflow-x: hidden;
      transition: background-color 0.3s, color 0.3s;
    }}

    /* Scrollbars */
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: var(--bg-base); }}
    ::-webkit-scrollbar-thumb {{ background: var(--border-strong); border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--accent-primary); }}

    /* Sidebar Navigation */
    .sidebar {{
      width: var(--sidebar-width);
      background-color: var(--bg-surface);
      border-right: 1px solid var(--border-subtle);
      height: 100vh;
      position: fixed;
      top: 0;
      left: 0;
      display: flex;
      flex-direction: column;
      z-index: 100;
      transition: transform 0.3s ease;
    }}

    .sidebar-header {{
      padding: 18px 20px 14px;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .brand-icon {{
      width: 36px;
      height: 36px;
      background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      box-shadow: 0 4px 12px var(--accent-glow);
    }}
    .brand-icon svg {{ width: 20px; height: 20px; fill: currentColor; }}

    .brand-title h1 {{ font-size: 14.5px; font-weight: 700; letter-spacing: -0.3px; line-height: 1.2; }}
    .brand-title span {{ font-size: 11px; color: var(--accent-cyan); font-weight: 500; }}

    .sidebar-content {{
      flex: 1;
      overflow-y: auto;
      padding: 14px 12px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    .nav-section-title {{
      font-size: 10.5px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: var(--accent-primary);
      padding: 6px 10px 4px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .file-tree-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding: 7px 10px;
      border-radius: 6px;
      color: var(--text-muted);
      text-decoration: none;
      font-size: 12.5px;
      font-family: var(--font-mono);
      cursor: pointer;
      transition: all 0.15s ease;
      border-left: 2px solid transparent;
    }}
    .file-tree-item:hover {{
      background: var(--bg-surface-elevated);
      color: var(--text-main);
      transform: translateX(2px);
    }}
    .file-tree-item.active {{
      background: rgba(99, 102, 241, 0.12);
      border-left-color: var(--accent-primary);
      color: var(--accent-primary);
      font-weight: 600;
    }}

    .file-badge {{
      font-size: 9.5px;
      padding: 1px 6px;
      border-radius: 8px;
      background: var(--bg-surface-elevated);
      color: var(--text-dim);
      font-family: var(--font-sans);
    }}

    .sidebar-footer {{
      padding: 14px 18px;
      border-top: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .theme-toggle-btn {{
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-strong);
      color: var(--text-main);
      padding: 5px 10px;
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: 500;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    /* Main Container */
    .main-wrapper {{
      margin-left: var(--sidebar-width);
      flex: 1;
      display: flex;
      flex-direction: column;
      min-width: 0;
    }}

    /* Top Sticky Header */
    .top-header {{
      position: sticky;
      top: 0;
      background: rgba(19, 26, 43, 0.92);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border-subtle);
      padding: 12px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      z-index: 90;
    }}
    [data-theme="light"] .top-header {{
      background: rgba(255, 255, 255, 0.92);
    }}

    .header-search {{
      position: relative;
      flex: 1;
      max-width: 480px;
    }}
    .header-search input {{
      width: 100%;
      background: var(--bg-surface);
      border: 1px solid var(--border-strong);
      padding: 8px 14px 8px 36px;
      border-radius: 8px;
      color: var(--text-main);
      font-size: 12.5px;
      outline: none;
    }}
    .header-search svg {{
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      width: 15px;
      height: 15px;
      color: var(--text-dim);
    }}

    .btn-pill {{
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-strong);
      color: var(--text-main);
      padding: 6px 13px;
      border-radius: 16px;
      font-size: 11.5px;
      font-weight: 600;
      text-decoration: none;
      display: flex;
      align-items: center;
      gap: 6px;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .btn-pill:hover {{
      border-color: var(--accent-primary);
      background: var(--accent-glow);
    }}
    .btn-pill.primary {{
      background: var(--accent-primary);
      border-color: var(--accent-primary);
      color: white;
    }}

    /* Content Area */
    .content-area {{
      padding: 28px;
      display: flex;
      flex-direction: column;
      gap: 36px;
      max-width: 1440px;
      margin: 0 auto;
      width: 100%;
    }}

    /* Hero Card */
    .hero-card {{
      background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(139, 92, 246, 0.05) 100%), var(--bg-card);
      border: 1px solid rgba(99, 102, 241, 0.25);
      border-radius: 18px;
      padding: 28px 32px;
      position: relative;
      overflow: hidden;
    }}
    .hero-title {{
      font-size: 24px;
      font-weight: 800;
      letter-spacing: -0.5px;
      margin-bottom: 8px;
      background: linear-gradient(90deg, #F9FAFB, #C7D2FE);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    [data-theme="light"] .hero-title {{
      background: linear-gradient(90deg, #0F172A, #4338CA);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .hero-subtitle {{
      font-size: 14px;
      color: var(--text-muted);
      max-width: 900px;
      line-height: 1.6;
      margin-bottom: 18px;
    }}

    .hero-badges-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .tech-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-strong);
      border-radius: 12px;
      font-size: 11px;
      font-weight: 600;
      color: var(--text-main);
    }}
    .tech-pill.highlight {{
      border-color: rgba(99, 102, 241, 0.5);
      color: #A5B4FC;
      background: rgba(99, 102, 241, 0.1);
    }}

    /* Phone Simulator Grid */
    .simulator-grid {{
      display: grid;
      grid-template-columns: 360px 1fr;
      gap: 24px;
      align-items: start;
    }}

    .phone-mockup {{
      width: 100%;
      background: #000000;
      border: 10px solid #1E293B;
      border-radius: 40px;
      box-shadow: 0 20px 50px -10px rgba(0, 0, 0, 0.5);
      overflow: hidden;
      display: flex;
      flex-direction: column;
      height: 700px;
      position: sticky;
      top: 80px;
    }}

    .phone-notch-bar {{
      height: 28px;
      background: #000000;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 20px;
      font-size: 10px;
      font-weight: 600;
      color: #FFFFFF;
      flex-shrink: 0;
    }}

    .phone-screen {{
      flex: 1;
      background: var(--bg-surface);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      position: relative;
    }}

    .sim-topbar {{
      background: var(--bg-surface-elevated);
      padding: 10px 14px;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .sim-topbar h4 {{ font-size: 14px; font-weight: 700; display: flex; align-items: center; gap: 6px; }}

    .sim-controls-row {{ display: flex; gap: 5px; }}
    .sim-btn-icon {{
      background: var(--bg-surface);
      border: 1px solid var(--border-strong);
      color: var(--text-muted);
      width: 28px;
      height: 28px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 12px;
    }}

    .sim-search-bar {{ padding: 8px 12px; background: var(--bg-surface); border-bottom: 1px solid var(--border-subtle); }}
    .sim-search-bar input {{
      width: 100%;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-strong);
      padding: 6px 10px;
      border-radius: 6px;
      font-size: 11px;
      color: var(--text-main);
      outline: none;
    }}

    .sim-chips-scroll {{
      display: flex;
      gap: 5px;
      overflow-x: auto;
      padding: 6px 12px;
      border-bottom: 1px solid var(--border-subtle);
      scrollbar-width: none;
    }}
    .sim-chips-scroll::-webkit-scrollbar {{ display: none; }}

    .sim-chip {{
      padding: 3px 8px;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-strong);
      border-radius: 10px;
      font-size: 10px;
      font-weight: 600;
      color: var(--text-muted);
      cursor: pointer;
      white-space: nowrap;
    }}
    .sim-chip.active {{ background: var(--accent-primary); border-color: var(--accent-primary); color: white; }}

    .sim-task-list {{ flex: 1; overflow-y: auto; padding: 10px; display: flex; flex-direction: column; gap: 6px; }}

    .sim-task-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      padding: 10px;
      display: flex;
      gap: 8px;
      align-items: flex-start;
      position: relative;
    }}
    .sim-task-card.completed {{ opacity: 0.6; }}

    .sim-priority-stripe {{
      width: 3px; height: 100%; position: absolute; left: 0; top: 0; bottom: 0;
      border-top-left-radius: 10px; border-bottom-left-radius: 10px;
    }}
    .priority-urgent {{ background-color: var(--accent-danger); }}
    .priority-high {{ background-color: var(--accent-warning); }}
    .priority-medium {{ background-color: var(--accent-cyan); }}
    .priority-low {{ background-color: var(--accent-success); }}

    .sim-checkbox {{
      width: 16px; height: 16px; border: 2px solid var(--border-strong);
      border-radius: 4px; cursor: pointer; display: flex; align-items: center; justify-content: center;
      margin-top: 2px; flex-shrink: 0;
    }}
    .sim-checkbox.checked {{ background: var(--accent-primary); border-color: var(--accent-primary); }}

    .sim-task-content {{ flex: 1; min-width: 0; cursor: pointer; }}
    .sim-task-title {{ font-size: 12px; font-weight: 600; margin-bottom: 2px; }}
    .sim-task-card.completed .sim-task-title {{ text-decoration: line-through; color: var(--text-dim); }}
    .sim-task-desc {{ font-size: 10.5px; color: var(--text-muted); line-height: 1.3; margin-bottom: 4px; }}
    .sim-task-footer {{ display: flex; gap: 4px; flex-wrap: wrap; }}
    .sim-tag {{ font-size: 8.5px; font-weight: 700; padding: 1px 5px; border-radius: 3px; background: var(--bg-surface-elevated); color: var(--text-dim); }}
    .sim-del-btn {{ background: none; border: none; color: var(--text-dim); cursor: pointer; opacity: 0.6; font-size: 11px; }}
    .sim-del-btn:hover {{ opacity: 1; }}

    .sim-fab {{
      position: absolute; bottom: 14px; right: 14px; width: 42px; height: 42px; border-radius: 12px;
      background: var(--accent-primary); color: white; border: none; display: flex; align-items: center;
      justify-content: center; cursor: pointer; box-shadow: 0 4px 12px var(--accent-glow);
    }}

    /* Live Inspector Console */
    .live-inspector-panel {{
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: 16px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .inspector-header {{ display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border-subtle); padding-bottom: 10px; }}
    .live-pulse {{ display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 700; color: var(--accent-success); }}
    .pulse-dot {{ width: 8px; height: 8px; background: var(--accent-success); border-radius: 50%; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); animation: pulse 1.8s infinite; }}
    @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }} 70% {{ box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }} }}

    .execution-pipeline-box {{
      background: #090D16;
      border: 1px solid var(--border-strong);
      border-radius: 10px;
      padding: 14px;
      font-family: var(--font-mono);
      font-size: 11.5px;
    }}
    .pipeline-step {{ display: flex; align-items: flex-start; gap: 10px; padding: 7px 0; border-bottom: 1px dashed var(--border-subtle); }}
    .pipeline-step:last-child {{ border-bottom: none; }}
    .step-badge {{ font-size: 9.5px; font-weight: 700; padding: 2px 5px; border-radius: 4px; white-space: nowrap; }}
    .badge-ui {{ background: rgba(99, 102, 241, 0.2); color: #A5B4FC; }}
    .badge-vm {{ background: rgba(139, 92, 246, 0.2); color: #C084FC; }}
    .badge-domain {{ background: rgba(16, 185, 129, 0.2); color: #6EE7B7; }}
    .badge-data {{ background: rgba(6, 182, 212, 0.2); color: #67E8F9; }}
    .badge-worker {{ background: rgba(245, 158, 11, 0.2); color: #FCD34D; }}

    /* Section Cards */
    .section-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: 18px;
      padding: 28px;
      position: relative;
    }}
    .section-header {{ margin-bottom: 20px; }}
    .section-tag {{ font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: var(--accent-primary); }}
    .section-title {{ font-size: 20px; font-weight: 800; letter-spacing: -0.4px; display: flex; align-items: center; gap: 8px; }}
    .section-subtitle {{ font-size: 13.5px; color: var(--text-muted); line-height: 1.6; margin-top: 4px; }}

    /* Code Component Box with Complete Unabridged Code */
    .code-component-container {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 14px;
      margin-bottom: 30px;
      overflow: hidden;
    }}
    .component-header {{
      padding: 14px 18px;
      background: var(--bg-surface-elevated);
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
    }}
    .file-meta {{ display: flex; align-items: center; gap: 10px; }}
    .file-icon {{
      width: 30px; height: 30px; border-radius: 6px; background: rgba(99, 102, 241, 0.15);
      color: var(--accent-primary); display: flex; align-items: center; justify-content: center;
      font-weight: 700; font-size: 12px;
    }}
    .file-path {{ font-family: var(--font-mono); font-size: 13px; font-weight: 600; color: var(--text-main); }}
    .file-subtext {{ font-size: 11px; color: var(--text-dim); }}

    .copy-code-btn {{
      background: var(--bg-surface);
      border: 1px solid var(--border-strong);
      color: var(--text-muted);
      padding: 5px 10px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 5px;
    }}
    .copy-code-btn:hover {{ border-color: var(--accent-primary); color: var(--text-main); }}

    /* EXACT ANDROID STUDIO / INTELLIJ IDEA EDITOR STYLING */
    .code-viewport {{
      background: var(--ide-bg);
      padding: 14px 0;
      font-family: var(--font-mono);
      font-size: 12.5px;
      line-height: 1.65;
      overflow-x: auto;
      max-height: 620px;
      color: var(--ide-text);
      border-bottom: 1px solid var(--border-subtle);
    }}

    .code-line {{
      display: flex;
      min-height: 21px;
      padding: 0 16px 0 0;
    }}
    .code-line:hover {{
      background-color: var(--ide-line-hover);
    }}

    .line-num {{
      display: inline-block;
      width: 52px;
      padding-right: 16px;
      text-align: right;
      color: var(--ide-line-num);
      user-select: none;
      font-size: 11px;
      flex-shrink: 0;
    }}

    .line-code {{
      flex: 1;
      white-space: pre;
    }}

    /* IDE Syntax Token Colors - Android Studio New UI & Darcula */
    .tok-kw {{ color: #CF8E6D; font-weight: 600; }}       /* Keywords: fun, val, var, class, return, override */
    .tok-ann {{ color: #E0AC16; }}                        /* Annotations: @Entity, @Dao, @Composable */
    .tok-type {{ color: #56A8F5; }}                       /* Types & Classes: Task, String, Flow, TaskDao */
    .tok-str {{ color: #6AAB73; }}                        /* Strings: double quotes */
    .tok-num {{ color: #2AACB8; }}                        /* Numbers: 0, 1, 200, 15L */
    .tok-cmt {{ color: #7A7E85; font-style: italic; }}    /* Comments: slashes and asterisks */
    .tok-fn {{ color: #FFC66D; }}                         /* Functions: getTasks, invoke, observe */

    /* IDE Syntax Token Colors - Light Mode (IntelliJ Light) */
    [data-theme="light"] .tok-kw {{ color: #0033B3; font-weight: 600; }}
    [data-theme="light"] .tok-ann {{ color: #871094; }}
    [data-theme="light"] .tok-type {{ color: #267F99; }}
    [data-theme="light"] .tok-str {{ color: #067D17; }}
    [data-theme="light"] .tok-num {{ color: #1750EB; }}
    [data-theme="light"] .tok-cmt {{ color: #8C8C8C; font-style: italic; }}
    [data-theme="light"] .tok-fn {{ color: #00627A; }}

    /* Deep Dive Explanations */
    .explanation-panel {{
      padding: 18px;
      background: var(--bg-surface);
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .explain-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      padding: 14px 16px;
    }}
    .explain-card-title {{
      font-size: 12.5px;
      font-weight: 700;
      color: var(--accent-primary);
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .explain-card p {{ font-size: 12px; color: var(--text-muted); line-height: 1.6; }}

    /* Modal for Add Task in Simulator */
    .sim-modal-overlay {{
      position: absolute; top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(4px); display: none;
      align-items: center; justify-content: center; padding: 14px; z-index: 50;
    }}
    .sim-modal-overlay.open {{ display: flex; }}
    .sim-modal {{
      background: var(--bg-surface); border: 1px solid var(--border-strong);
      border-radius: 14px; padding: 14px; width: 100%; max-width: 300px;
      display: flex; flex-direction: column; gap: 10px;
    }}
    .sim-form-group {{ display: flex; flex-direction: column; gap: 3px; }}
    .sim-form-group label {{ font-size: 9.5px; text-transform: uppercase; font-weight: 700; color: var(--text-dim); }}
    .sim-form-group input, .sim-form-group select, .sim-form-group textarea {{
      background: var(--bg-surface-elevated); border: 1px solid var(--border-strong);
      border-radius: 6px; padding: 5px 8px; color: var(--text-main); font-size: 11px; outline: none; font-family: inherit;
    }}
    .sim-modal-actions {{ display: flex; justify-content: flex-end; gap: 6px; margin-top: 4px; }}

    @media (max-width: 1100px) {{
      .simulator-grid {{ grid-template-columns: 1fr; }}
      .phone-mockup {{ max-width: 360px; margin: 0 auto; position: static; }}
    }}
    @media (max-width: 768px) {{
      .sidebar {{ transform: translateX(-100%); }}
      .main-wrapper {{ margin-left: 0; }}
      .content-area {{ padding: 14px; }}
    }}
  </style>
</head>
<body>

  <!-- Sidebar File Explorer -->
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-header">
      <div class="brand-icon">
        <svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
      </div>
      <div class="brand-title">
        <h1>Android Arch Explorer</h1>
        <span>38 Source Files Unabridged</span>
      </div>
    </div>

    <div class="sidebar-content">
      <div>
        <div class="nav-section-title">📱 Interactive Simulator</div>
        <a href="#simulator" class="file-tree-item" style="font-family: var(--font-sans); font-weight: 600;">
          <span>⚡ Live Phone Simulator</span>
          <span class="file-badge" style="background: rgba(16, 185, 129, 0.2); color: #10B981;">Active</span>
        </a>
      </div>
"""

for cat, file_list in categories.items():
    html_out += f"""
      <div>
        <div class="nav-section-title">
          <span>{cat}</span>
          <span style="font-size: 9px; opacity: 0.7;">{len(file_list)} files</span>
        </div>
    """
    for f in file_list:
        html_out += f"""
        <a href="#{f['id']}" class="file-tree-item" onclick="highlightSidebarItem(this)">
          <span>{f['name']}</span>
          <span class="file-badge">{f['line_count']}L</span>
        </a>
        """
    html_out += "</div>"

html_out += f"""
    </div>

    <div class="sidebar-footer">
      <button class="theme-toggle-btn" onclick="toggleTheme()">
        <span id="themeIcon">☀️</span>
        <span id="themeLabel">Light Mode</span>
      </button>
      <span style="font-size: 11px; color: var(--text-dim);">Android Studio Colors</span>
    </div>
  </aside>

  <!-- Main Content -->
  <div class="main-wrapper">
    <header class="top-header">
      <div class="header-search">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
        <input type="text" id="globalSearchInput" placeholder="Search files, functions, lines, concepts (e.g. SavedStateHandle, Room, WorkManager)...">
      </div>
      <div style="display: flex; gap: 8px;">
        <a href="#simulator" class="btn-pill primary">📱 Simulator</a>
        <a href="https://developer.android.com/topic/architecture" target="_blank" class="btn-pill">Docs ↗</a>
      </div>
    </header>

    <main class="content-area">
      <!-- Hero -->
      <section class="hero-card">
        <h2 class="hero-title">Android Personal Task Manager: Complete Unabridged Codebase & Deep-Dive Explanation</h2>
        <p class="hero-subtitle">
          Every single line of code used in the Android application is presented below in full, unabridged detail with Android Studio IDE color coding and comprehensive, line-by-line and section-by-section breakdowns explaining <strong>what each part does</strong>, <strong>why it was designed this way</strong>, and <strong>how it executes under the hood</strong> across Presentation (Compose & XML), Domain (UseCases), Data (Room & Retrofit), System (WorkManager, Receivers, ContentProvider), and Dependency Injection.
        </p>
        <div class="hero-badges-row">
          <span class="tech-pill highlight">Android Studio IDE Theme</span>
          <span class="tech-pill highlight">38 Full Source Files</span>
          <span class="tech-pill highlight">Every Line of Code Included</span>
          <span class="tech-pill">Jetpack Compose Material 3</span>
          <span class="tech-pill">Room SQLite ORM</span>
          <span class="tech-pill">Retrofit REST & Mock OkHttp</span>
          <span class="tech-pill">Offline-First Sync</span>
          <span class="tech-pill">WorkManager CoroutineWorker</span>
          <span class="tech-pill">SavedStateHandle</span>
          <span class="tech-pill">AppContainer & Hilt</span>
        </div>
      </section>

      <!-- Interactive Simulator & Console -->
      <section class="section-card" id="simulator">
        <div class="section-header">
          <span class="section-tag">Interactive Environment</span>
          <h3 class="section-title">Live Android App Web Simulator & Execution Trace Inspector</h3>
          <p class="section-subtitle">
            Interact with the working Personal Task Manager app below. Every action triggers the exact Android Kotlin execution pipeline in the live console!
          </p>
        </div>

        <div class="simulator-grid">
          <!-- Mobile Phone Device Replica -->
          <div class="phone-mockup">
            <div class="phone-notch-bar">
              <span id="phoneClock">12:00</span>
              <div style="width: 10px; height: 10px; background: #111827; border-radius: 50%;"></div>
              <span>📶 5G 100%</span>
            </div>

            <div class="phone-screen">
              <div class="sim-topbar">
                <h4><span style="color: var(--accent-primary);">⚡</span> <span id="simScreenTitle">My Tasks</span></h4>
                <div class="sim-controls-row">
                  <button class="sim-btn-icon" title="Trigger Remote Sync" onclick="simTriggerSync()">🔄</button>
                  <button class="sim-btn-icon" title="Toggle Stats View" onclick="simToggleStats()">📊</button>
                </div>
              </div>

              <div class="sim-search-bar" id="simSearchBar">
                <input type="text" id="simSearchInput" placeholder="🔍 Search tasks..." oninput="simOnSearch(this.value)">
              </div>

              <div class="sim-chips-scroll" id="simCategoryChips">
                <button class="sim-chip active" onclick="simFilterCategory('ALL', this)">All</button>
                <button class="sim-chip" onclick="simFilterCategory('WORK', this)">Work</button>
                <button class="sim-chip" onclick="simFilterCategory('PERSONAL', this)">Personal</button>
                <button class="sim-chip" onclick="simFilterCategory('HEALTH', this)">Health</button>
                <button class="sim-chip" onclick="simFilterCategory('FINANCE', this)">Finance</button>
                <button class="sim-chip" onclick="simFilterCategory('SHOPPING', this)">Shopping</button>
              </div>

              <div class="sim-chips-scroll" style="background: rgba(0,0,0,0.1); padding: 4px 12px;">
                <span style="font-size: 9.5px; color: var(--text-dim); align-self: center; font-weight: 600;">Priority:</span>
                <button class="sim-chip active" onclick="simFilterPriority('ALL', this)">All</button>
                <button class="sim-chip" onclick="simFilterPriority('URGENT', this)">Urgent</button>
                <button class="sim-chip" onclick="simFilterPriority('HIGH', this)">High</button>
                <button class="sim-chip" onclick="simFilterPriority('MEDIUM', this)">Medium</button>
                <button class="sim-chip" onclick="simFilterPriority('LOW', this)">Low</button>
              </div>

              <div class="sim-task-list" id="simTaskListContainer"></div>

              <div id="simStatsView" style="display: none; padding: 14px; overflow-y: auto; height: 100%;">
                <div style="background: var(--bg-card); border-radius: 10px; padding: 14px; border: 1px solid var(--border-subtle); margin-bottom: 10px;">
                  <h5 style="font-size: 12px; font-weight: 700; color: var(--accent-cyan); margin-bottom: 6px;">Productivity Analytics</h5>
                  <div style="font-size: 22px; font-weight: 800; color: var(--text-main);" id="simStatsPercent">0%</div>
                  <div style="font-size: 10.5px; color: var(--text-muted); margin-bottom: 10px;">Overall Completion Rate</div>
                  <div style="height: 5px; background: var(--bg-surface-elevated); border-radius: 3px; overflow: hidden;">
                    <div id="simStatsProgressBar" style="height: 100%; width: 0%; background: var(--accent-primary); transition: width 0.3s;"></div>
                  </div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px;">
                  <div style="background: var(--bg-card); padding: 10px; border-radius: 8px; border: 1px solid var(--border-subtle);">
                    <div style="font-size: 10px; color: var(--text-muted);">Completed</div>
                    <div style="font-size: 16px; font-weight: 700; color: var(--accent-success);" id="simStatsCompleted">0</div>
                  </div>
                  <div style="background: var(--bg-card); padding: 10px; border-radius: 8px; border: 1px solid var(--border-subtle);">
                    <div style="font-size: 10px; color: var(--text-muted);">Pending</div>
                    <div style="font-size: 16px; font-weight: 700; color: var(--accent-warning);" id="simStatsPending">0</div>
                  </div>
                </div>

                <button class="btn-pill primary" style="width: 100%; justify-content: center; margin-top: 6px;" onclick="simToggleStats()">← Back to Tasks</button>
              </div>

              <button class="sim-fab" title="Add New Task" onclick="simOpenAddModal()">
                <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"/></svg>
              </button>

              <div class="sim-modal-overlay" id="simAddModal">
                <div class="sim-modal">
                  <h5 style="font-size: 13px; font-weight: 700;">Add Personal Task</h5>
                  <div class="sim-form-group">
                    <label>Task Title *</label>
                    <input type="text" id="newTaskTitle" placeholder="e.g. Implement Room Migration">
                  </div>
                  <div class="sim-form-group">
                    <label>Description</label>
                    <textarea id="newTaskDesc" rows="2" placeholder="Details and technical steps..."></textarea>
                  </div>
                  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px;">
                    <div class="sim-form-group">
                      <label>Priority</label>
                      <select id="newTaskPriority">
                        <option value="MEDIUM">MEDIUM</option>
                        <option value="LOW">LOW</option>
                        <option value="HIGH">HIGH</option>
                        <option value="URGENT">URGENT</option>
                      </select>
                    </div>
                    <div class="sim-form-group">
                      <label>Category</label>
                      <select id="newTaskCategory">
                        <option value="WORK">WORK</option>
                        <option value="PERSONAL">PERSONAL</option>
                        <option value="HEALTH">HEALTH</option>
                        <option value="FINANCE">FINANCE</option>
                        <option value="SHOPPING">SHOPPING</option>
                      </select>
                    </div>
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
                  <div class="step-desc"><code>TaskViewModel.kt::observeTasks()</code> triggers reactive coroutine flow query</div>
                </div>
                <div class="pipeline-step">
                  <span class="step-badge badge-domain">3. Domain</span>
                  <div class="step-desc"><code>GetTasksUseCase.kt::invoke()</code> queries <code>TaskRepository.getFilteredTasks()</code></div>
                </div>
                <div class="pipeline-step">
                  <span class="step-badge badge-data">4. Data (Room)</span>
                  <div class="step-desc"><code>TaskRepositoryImpl.kt</code> emits from <code>TaskDao.getAllTasks()</code> via SQLite InvalidationTracker</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
"""

# Render Every Single One of the 38 Files in Full Detail!
for cfg in FILES_CONFIG:
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
          <div style="display: flex; gap: 8px;">
            <span class="tech-pill highlight">{cfg['badge']}</span>
            <button class="copy-code-btn" onclick="copyFullSnippet('{cfg['id']}_raw', this)">
              <span>📋 Copy Full Code</span>
            </button>
          </div>
        </div>

        <!-- Full Code Viewport with Line Numbers and IDE Colors -->
        <div class="code-viewport">
{cfg['formatted_code']}
        </div>

        <!-- Hidden Raw Code for Copying -->
        <textarea id="{cfg['id']}_raw" style="display: none;">{html.escape(cfg['raw_code'])}</textarea>

        <!-- Deep Dive Explanation Panel -->
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

# Add Scripts and Close Tags
html_out += """
    </main>
  </div>

  <script>
    let simTasks = [
      { id: '1', title: 'Implement Room Migration v3', desc: 'Add new syncStatus column to SQLite tasks table', isCompleted: false, priority: 'URGENT', category: 'WORK', contact: 'Alex Johnson' },
      { id: '2', title: 'Design Jetpack Compose TopAppBar', desc: 'Apply Material 3 theme colors and action icons', isCompleted: true, priority: 'HIGH', category: 'WORK', contact: null },
      { id: '3', title: 'Schedule 15-min SyncWorker', desc: 'Verify NetworkType.CONNECTED constraint in WorkManager', isCompleted: false, priority: 'MEDIUM', category: 'WORK', contact: 'Sarah Smith' },
      { id: '4', title: 'Grocery Shopping & Meal Prep', desc: 'Buy organic vegetables and protein shakes', isCompleted: false, priority: 'LOW', category: 'SHOPPING', contact: null },
      { id: '5', title: 'Monthly Budget Review', desc: 'Check expense reports against financial targets', isCompleted: true, priority: 'HIGH', category: 'FINANCE', contact: 'David Chen' }
    ];

    let currentCategoryFilter = 'ALL';
    let currentPriorityFilter = 'ALL';
    let currentSearchTerm = '';
    let isShowingStats = false;

    function renderSimTaskList() {
      const container = document.getElementById('simTaskListContainer');
      if (!container) return;

      const filtered = simTasks.filter(t => {
        const matchCat = (currentCategoryFilter === 'ALL' || t.category === currentCategoryFilter);
        const matchPri = (currentPriorityFilter === 'ALL' || t.priority === currentPriorityFilter);
        const matchSearch = (!currentSearchTerm || t.title.toLowerCase().includes(currentSearchTerm.toLowerCase()) || t.desc.toLowerCase().includes(currentSearchTerm.toLowerCase()));
        return matchCat && matchPri && matchSearch;
      });

      if (filtered.length === 0) {
        container.innerHTML = `
          <div style="text-align: center; padding: 40px 20px; color: var(--text-dim);">
            <div style="font-size: 28px; margin-bottom: 6px;">📋</div>
            <div style="font-size: 12px; font-weight: 600;">No tasks found</div>
          </div>
        `;
        return;
      }

      container.innerHTML = filtered.map(t => {
        const priorityClass = 'priority-' + t.priority.toLowerCase();
        return `
          <div class="sim-task-card ${t.isCompleted ? 'completed' : ''}" id="sim-task-${t.id}">
            <div class="sim-priority-stripe ${priorityClass}"></div>
            <div class="sim-checkbox ${t.isCompleted ? 'checked' : ''}" onclick="simToggleTask('${t.id}')">
              ${t.isCompleted ? '<span style="color:white; font-size:10px;">✓</span>' : ''}
            </div>
            <div class="sim-task-content" onclick="simToggleTask('${t.id}')">
              <div class="sim-task-title">${t.title}</div>
              <div class="sim-task-desc">${t.desc}</div>
              <div class="sim-task-footer">
                <span class="sim-tag">${t.category}</span>
                <span class="sim-tag" style="color: var(--accent-primary);">${t.priority}</span>
                ${t.contact ? `<span class="sim-tag" style="color: var(--accent-cyan);">👤 ${t.contact}</span>` : ''}
              </div>
            </div>
            <button class="sim-del-btn" title="Delete" onclick="simDeleteTask('${t.id}')">🗑️</button>
          </div>
        `;
      }).join('');

      updateStatsDisplay();
    }

    function simToggleTask(id) {
      const task = simTasks.find(t => t.id === id);
      if (!task) return;
      task.isCompleted = !task.isCompleted;
      renderSimTaskList();

      broadcastInspector(
        `Task Completed Toggled: "${task.title}"`,
        `Invoked TaskViewModel.onToggleTaskCompletion(task) -> UpdateTaskUseCase.invoke()`,
        [
          { badge: 'badge-ui', label: '1. Compose UI', code: 'TaskListScreen.kt: onToggleTaskCompletion(task)' },
          { badge: 'badge-vm', label: '2. TaskViewModel', code: 'updateTaskUseCase(task.copy(isCompleted = ' + task.isCompleted + '))' },
          { badge: 'badge-domain', label: '3. Domain UseCase', code: 'UpdateTaskUseCase.kt: validates constraints & delegates to repo' },
          { badge: 'badge-data', label: '4. Data Layer (Room)', code: 'TaskDao.updateTask(task.toEntity()) -> status: PENDING_UPDATE' },
          { badge: 'badge-worker', label: '5. WorkManager', code: 'WorkManagerScheduler.scheduleOneTimeSync() enqueued with REPLACE' }
        ]
      );
    }

    function simDeleteTask(id) {
      const task = simTasks.find(t => t.id === id);
      const title = task ? task.title : id;
      simTasks = simTasks.filter(t => t.id !== id);
      renderSimTaskList();

      broadcastInspector(
        `Task Deleted: "${title}"`,
        `Invoked TaskViewModel.onDeleteTask("${id}") -> DeleteTaskUseCase.invoke()`,
        [
          { badge: 'badge-ui', label: '1. Presentation', code: 'TaskListScreen.kt: onDeleteTask(taskId)' },
          { badge: 'badge-vm', label: '2. TaskViewModel', code: 'viewModelScope.launch { deleteTaskUseCase(taskId) }' },
          { badge: 'badge-domain', label: '3. Domain Layer', code: 'DeleteTaskUseCase.kt: delegates to TaskRepository.deleteTask()' },
          { badge: 'badge-data', label: '4. Soft/Hard Delete', code: 'TaskDao.updateTask(PENDING_DELETE) or deleteTaskById() locally' },
          { badge: 'badge-worker', label: '5. Reminder Cancel', code: 'WorkManagerScheduler.cancelTaskReminder(taskId)' }
        ]
      );
    }

    let searchTimeout = null;
    function simOnSearch(term) {
      currentSearchTerm = term;
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        renderSimTaskList();
        broadcastInspector(
          `Search Query Filter: "${term}"`,
          `TaskViewModel._searchQuery.debounce(200) triggered query in Room database`,
          [
            { badge: 'badge-ui', label: '1. UI Input', code: 'OutlinedTextField valueChange -> onSearchQueryChanged("' + term + '")' },
            { badge: 'badge-vm', label: '2. SavedStateHandle', code: 'savedStateHandle["search_query"] = "' + term + '" (survives process death)' },
            { badge: 'badge-domain', label: '3. Reactive Combine', code: 'combine(_searchQuery.debounce(200), category, priority) emits new FilterParams' },
            { badge: 'badge-data', label: '4. Room Query', code: 'TaskDao.getAllTasks().map { filter(query) } executes on Dispatchers.IO' }
          ]
        );
      }, 200);
    }

    function simFilterCategory(cat, el) {
      currentCategoryFilter = cat;
      document.querySelectorAll('#simCategoryChips .sim-chip').forEach(c => c.classList.remove('active'));
      el.classList.add('active');
      renderSimTaskList();
    }

    function simFilterPriority(pri, el) {
      currentPriorityFilter = pri;
      el.parentElement.querySelectorAll('.sim-chip').forEach(c => c.classList.remove('active'));
      el.classList.add('active');
      renderSimTaskList();
    }

    function simTriggerSync() {
      const btn = event.currentTarget;
      btn.style.transform = 'rotate(360deg)';
      btn.style.transition = 'transform 0.5s';

      broadcastInspector(
        `Manual Sync Triggered (Retrofit 2 REST API)`,
        `TaskViewModel.triggerManualSync() -> SyncTasksUseCase() -> TaskRepositoryImpl.syncTasks()`,
        [
          { badge: 'badge-vm', label: '1. ViewModel', code: '_syncUiState.update { it.copy(isSyncing = true) }' },
          { badge: 'badge-data', label: '2. Unsynced Query', code: 'TaskDao.getUnsyncedTasks() queries PENDING_INSERT / PENDING_UPDATE' },
          { badge: 'badge-data', label: '3. Retrofit HTTP', code: 'TaskApiService.syncBatch() -> POST /api/v1/tasks/sync (200ms latency)' },
          { badge: 'badge-data', label: '4. Local Cache Commit', code: 'Room Database marks local records as SYNCED on 200 OK' }
        ]
      );

      setTimeout(() => {
        btn.style.transform = 'none';
        btn.style.transition = 'none';
        alert('✅ Retrofit REST API Sync Complete!\\nLocal database is synchronized with cloud server.');
      }, 300);
    }

    function simToggleStats() {
      isShowingStats = !isShowingStats;
      const listContainer = document.getElementById('simTaskListContainer');
      const searchBar = document.getElementById('simSearchBar');
      const categoryChips = document.getElementById('simCategoryChips');
      const statsView = document.getElementById('simStatsView');
      const title = document.getElementById('simScreenTitle');

      if (isShowingStats) {
        listContainer.style.display = 'none';
        searchBar.style.display = 'none';
        categoryChips.style.display = 'none';
        statsView.style.display = 'block';
        title.innerText = 'Productivity Stats';
      } else {
        listContainer.style.display = 'flex';
        searchBar.style.display = 'block';
        categoryChips.style.display = 'flex';
        statsView.style.display = 'none';
        title.innerText = 'My Tasks';
      }
    }

    function updateStatsDisplay() {
      const total = simTasks.length;
      const completed = simTasks.filter(t => t.isCompleted).length;
      const pending = total - completed;
      const pct = total > 0 ? Math.round((completed / total) * 100) : 0;

      const pctEl = document.getElementById('simStatsPercent');
      const barEl = document.getElementById('simStatsProgressBar');
      const compEl = document.getElementById('simStatsCompleted');
      const pendEl = document.getElementById('simStatsPending');

      if (pctEl) pctEl.innerText = pct + '%';
      if (barEl) barEl.style.width = pct + '%';
      if (compEl) compEl.innerText = completed;
      if (pendEl) pendEl.innerText = pending;
    }

    function simOpenAddModal() {
      document.getElementById('simAddModal').classList.add('open');
    }

    function simCloseAddModal() {
      document.getElementById('simAddModal').classList.remove('open');
    }

    function simSaveNewTask() {
      const titleInput = document.getElementById('newTaskTitle');
      const descInput = document.getElementById('newTaskDesc');
      const priorityInput = document.getElementById('newTaskPriority');
      const categoryInput = document.getElementById('newTaskCategory');
      const contactInput = document.getElementById('newTaskContact');

      const title = titleInput.value.trim();
      if (!title) {
        alert('⚠️ Task title cannot be empty! (Domain AddTaskUseCase validation)');
        return;
      }

      const newTask = {
        id: String(Date.now()),
        title: title,
        desc: descInput.value.trim(),
        isCompleted: false,
        priority: priorityInput.value,
        category: categoryInput.value,
        contact: contactInput.value || null
      };

      simTasks.unshift(newTask);
      titleInput.value = '';
      descInput.value = '';
      simCloseAddModal();
      renderSimTaskList();
    }

    function broadcastInspector(trigger, desc, steps) {
      document.getElementById('inspectorTriggerName').innerText = trigger;
      document.getElementById('inspectorTriggerDesc').innerText = desc;

      const stepsContainer = document.getElementById('inspectorStepsList');
      stepsContainer.innerHTML = steps.map(s => `
        <div class="pipeline-step">
          <span class="step-badge ${s.badge}">${s.label}</span>
          <div class="step-desc"><code>${s.code}</code></div>
        </div>
      `).join('');
    }

    function copyFullSnippet(textareaId, btn) {
      const text = document.getElementById(textareaId).value;
      navigator.clipboard.writeText(text).then(() => {
        const original = btn.innerHTML;
        btn.innerHTML = '<span>✅ Copied Full File!</span>';
        setTimeout(() => { btn.innerHTML = original; }, 2000);
      });
    }

    function toggleTheme() {
      const current = document.documentElement.getAttribute('data-theme');
      const target = current === 'light' ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', target);
      document.getElementById('themeIcon').innerText = target === 'light' ? '🌙' : '☀️';
      document.getElementById('themeLabel').innerText = target === 'light' ? 'Dark Mode' : 'Light Mode';
    }

    function highlightSidebarItem(el) {
      document.querySelectorAll('.file-tree-item').forEach(item => item.classList.remove('active'));
      el.classList.add('active');
    }

    document.getElementById('globalSearchInput').addEventListener('input', function(e) {
      const term = e.target.value.toLowerCase().trim();
      document.querySelectorAll('.code-component-container').forEach(card => {
        const text = card.innerText.toLowerCase();
        card.style.display = (!term || text.includes(term)) ? 'block' : 'none';
      });
    });

    renderSimTaskList();
  </script>

</body>
</html>
"""

# Write out index.html
with open(os.path.join(ROOT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_out)

print(f"Generated index.html with IDE color-coding successfully! Size: {len(html_out)} bytes, {len(html_out.splitlines())} lines.")
