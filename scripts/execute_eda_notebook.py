"""Executa as células em IPython no processo atual e preserva as saídas reais."""
from pathlib import Path
import os
import sys
import nbformat

ROOT = Path(__file__).resolve().parents[1]

def main():
    runtime = ROOT / '.venv' / 'eda-runtime'
    runtime.mkdir(parents=True, exist_ok=True)
    os.environ['IPYTHONDIR'] = str(runtime)
    os.environ['MPLCONFIGDIR'] = str(runtime)
    from IPython.terminal.interactiveshell import TerminalInteractiveShell
    from IPython.utils.capture import capture_output
    from IPython.display import display
    shell = TerminalInteractiveShell.instance()
    shell.display_formatter.active_types = ['text/plain', 'text/html', 'image/png']
    path = ROOT / 'notebooks/banking77/01_eda_banking77.ipynb'
    nb = nbformat.read(path, as_version=4)
    previous = Path.cwd()
    os.chdir(ROOT)
    try:
        count = 0
        for cell in nb.cells:
            if cell.cell_type != 'code':
                continue
            count += 1
            with capture_output() as captured:
                result = shell.run_cell(cell.source, store_history=True)
                result.raise_error()
                # O display explícito preserva o HTML de DataFrames em execução fora do Jupyter.
                if result.result is not None and not captured.outputs:
                    display(result.result)
            outputs = []
            if captured.stdout:
                outputs.append(nbformat.v4.new_output('stream', name='stdout', text=captured.stdout))
            if captured.stderr:
                outputs.append(nbformat.v4.new_output('stream', name='stderr', text=captured.stderr))
            for rich in captured.outputs:
                outputs.append(nbformat.v4.new_output('display_data', data=rich.data, metadata=rich.metadata))
            cell.execution_count = count
            cell.outputs = outputs
        images = sum('image/png' in o.get('data', {}) for c in nb.cells if c.cell_type == 'code' for o in c.outputs)
        assert images >= 3, f'Esperados 3 gráficos, encontrados {images}'
        nb.metadata.language_info = {'name': 'python', 'version': sys.version.split()[0]}
        nbformat.validate(nb)
        nbformat.write(nb, path)
        print(f'Notebook salvo: {count} células executadas; {images} gráficos incorporados.')
    finally:
        os.chdir(previous)

if __name__ == '__main__':
    main()
