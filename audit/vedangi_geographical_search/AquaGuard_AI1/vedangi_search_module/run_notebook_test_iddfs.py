import json, sys, os, io, contextlib

nb_path = r'C:\Users\Vedangi\Documents\AquaGuard_AI1\vedangi_search_module\AI_Search_Algorithms.ipynb'

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Global namespace for execution
global_vars = {}
output = io.StringIO()

with contextlib.redirect_stdout(output):
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'code':
            src = ''.join(cell.get('source', []))
            try:
                exec(src, global_vars)
            except Exception as e:
                print('Error executing cell:', e)
                sys.exit(1)

print('Notebook execution completed. Captured output:')
print(output.getvalue())
