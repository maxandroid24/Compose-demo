import re
import html
import build_full_suite

def generate_symbol_database():
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
                        'relPath': f['rel_path'],
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
                        'relPath': f['rel_path'],
                        'line': idx,
                        'snippet': l.strip(),
                        'kind': 'Composable'
                    }

    symbol_index = {}
    for sym, decl in symbols.items():
        pattern = re.compile(rf'\b{sym}\b')
        usages = []
        for f in build_full_suite.ALL_FILES:
            lines = f['raw_code'].splitlines()
            for idx, l in enumerate(lines, 1):
                if pattern.search(l):
                    is_decl = (f['id'] == decl['fileId'] and idx == decl['line'])
                    usages.append({
                        'fileId': f['id'],
                        'fileName': f['name'],
                        'relPath': f['rel_path'],
                        'line': idx,
                        'snippet': l.strip(),
                        'isDeclaration': is_decl
                    })
        symbol_index[sym] = {
            'name': sym,
            'kind': decl['kind'],
            'fileId': decl['fileId'],
            'fileName': decl['fileName'],
            'relPath': decl['relPath'],
            'line': decl['line'],
            'snippet': decl['snippet'],
            'usages': usages,
            'usageCount': len(usages)
        }
    return symbol_index

if __name__ == '__main__':
    db = generate_symbol_database()
    print(f"Generated symbol database with {len(db)} symbols.")
    for s in ['TaskViewModel', 'Task', 'TaskListComposeActivity', 'TaskRepository', 'CustomViewModelStoreOwner']:
        print(f"  {s}: {db[s]['usageCount']} usages across files.")

