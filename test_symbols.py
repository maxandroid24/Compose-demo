import build_full_suite
import re

symbols = {}
for f in build_full_suite.ALL_FILES:
    code = f['raw_code']
    lines = code.splitlines()
    for idx, l in enumerate(lines, 1):
        m = re.search(r'(?:class|interface|object)\s+([A-Z][a-zA-Z0-9_]+)', l)
        if m:
            sym = m.group(1)
            if sym not in symbols:
                kind = "Interface" if "interface " in l else ("Object" if "object " in l else "Class")
                symbols[sym] = {
                    'name': sym,
                    'fileId': f['id'],
                    'fileName': f['name'],
                    'line': idx,
                    'snippet': l.strip(),
                    'kind': kind
                }
        m2 = re.search(r'fun\s+([A-Z][a-zA-Z0-9_]+)', l)
        if m2:
            sym = m2.group(1)
            if sym not in symbols:
                symbols[sym] = {
                    'name': sym,
                    'fileId': f['id'],
                    'fileName': f['name'],
                    'line': idx,
                    'snippet': l.strip(),
                    'kind': 'Composable'
                }

print(f"Total symbols declared in codebase: {len(symbols)}")
# Now find usages of these symbols across all files
symbol_usages = {}
for sym in symbols:
    symbol_usages[sym] = []
    pattern = re.compile(rf'\b{sym}\b')
    for f in build_full_suite.ALL_FILES:
        lines = f['raw_code'].splitlines()
        for idx, l in enumerate(lines, 1):
            if pattern.search(l):
                # Is it declaration line?
                is_decl = (f['id'] == symbols[sym]['fileId'] and idx == symbols[sym]['line'])
                symbol_usages[sym].append({
                    'fileId': f['id'],
                    'fileName': f['name'],
                    'line': idx,
                    'snippet': l.strip(),
                    'isDeclaration': is_decl
                })

print("Sample Symbol Usages:")
sample_keys = ['TaskViewModel', 'Task', 'TaskListComposeActivity', 'TaskRepository', 'GetFilteredTasksUseCase', 'SyncTasksWorker', 'CustomViewModelStoreOwner', 'TaskListScreen']
for k in sample_keys:
    if k in symbol_usages:
        print(f"  {k}: {len(symbol_usages[k])} occurrences across files (Declared in {symbols[k]['fileName']}:{symbols[k]['line']})")

