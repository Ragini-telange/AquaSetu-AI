import json

nb_path = r'vedangi_search_module/AI_Search_Algorithms.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find any leftover TODO cell for IDDFS
cells_to_remove = []
for i, cell in enumerate(nb['cells']):
    src = ''.join(cell.get('source', []))
    if cell['cell_type'] == 'markdown' and 'Iterative Deepening DFS (IDDFS) – *TODO*' in src:
        cells_to_remove.append(i)

for i in reversed(cells_to_remove):
    print(f'Removing duplicate IDDFS TODO cell at index {i}')
    nb['cells'].pop(i)

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('Current total cells:', len(nb['cells']))
