import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import sys, os
nb_path = r'C:\Users\Vedangi\Documents\AquaGuard_AI1\vedangi_search_module\AI_Search_Algorithms.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)
ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
try:
    ep.preprocess(nb, {'metadata': {'path': os.path.dirname(nb_path)}})
    # Save executed notebook
    exec_path = nb_path.replace('.ipynb', '_executed.ipynb')
    with open(exec_path, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)
    print('Notebook executed and saved to', exec_path)
except Exception as e:
    print('Error during notebook execution:', e)
    sys.exit(1)
