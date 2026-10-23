from pathlib import Path
import nbformat
from scripts.run_notebook import execute_notebook

if __name__ == '__main__':
    execute_notebook('notebooks/TP3/security/01_regressao_e_transicao.ipynb',min_images=3)
    # Só remove a nota histórica de bloqueio após execução completa bem-sucedida.
    path=Path(__file__).resolve().parents[1]/'notebooks/TP3/security/01_regressao_e_transicao.ipynb'
    notebook=nbformat.read(path,as_version=4)
    marker='\n\n**Estado da entrega:** execução pendente.'
    notebook.cells[0].source=notebook.cells[0].source.split(marker)[0]
    nbformat.write(notebook,path)
