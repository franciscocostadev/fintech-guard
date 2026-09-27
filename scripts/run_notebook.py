"""Executor compartilhado para os notebooks organizados por entrega."""
from pathlib import Path
import os
import sys

import nbformat

ROOT = Path(__file__).resolve().parents[1]


def execute_notebook(relative_path: str, min_images: int = 0) -> None:
    path = (ROOT / relative_path).resolve()
    if not path.is_relative_to((ROOT / 'notebooks').resolve()):
        raise ValueError('O notebook deve estar dentro de notebooks/.')
    runtime = ROOT / '.venv' / 'notebook-runtime'
    runtime.mkdir(parents=True, exist_ok=True)
    os.environ['IPYTHONDIR'] = str(runtime)
    os.environ['MPLCONFIGDIR'] = str(runtime)
    from IPython.terminal.interactiveshell import TerminalInteractiveShell
    from IPython.utils.capture import capture_output
    from IPython.display import display

    shell = TerminalInteractiveShell.instance()
    shell.display_formatter.active_types = ['text/plain', 'text/html', 'image/png']
    shell.user_ns['display'] = display
    with capture_output():
        shell.run_cell('%matplotlib inline').raise_error()
    notebook = nbformat.read(path, as_version=4)
    previous = Path.cwd()
    os.chdir(ROOT)
    try:
        count = 0
        for cell in notebook.cells:
            if cell.cell_type != 'code':
                continue
            count += 1
            with capture_output() as captured:
                result = shell.run_cell(cell.source, store_history=True)
                result.raise_error()
                if result.result is not None and not captured.outputs:
                    display(result.result)
            outputs = []
            for name, value in [('stdout', captured.stdout), ('stderr', captured.stderr)]:
                if value:
                    value = value.replace(str(ROOT), '.').replace(ROOT.as_posix(), '.')
                    outputs.append(nbformat.v4.new_output('stream', name=name, text=value))
            outputs.extend(nbformat.v4.new_output('display_data', data=o.data, metadata=o.metadata)
                           for o in captured.outputs)
            cell.execution_count = count
            cell.outputs = outputs
        images = sum('image/png' in o.get('data', {}) for c in notebook.cells
                     if c.cell_type == 'code' for o in c.outputs)
        if images < min_images:
            raise ValueError(f'Esperadas pelo menos {min_images} imagens; encontradas {images}.')
        notebook.metadata.language_info = {'name': 'python', 'version': sys.version.split()[0]}
        nbformat.validate(notebook)
        nbformat.write(notebook, path)
        print(f'{relative_path}: {count} células executadas; {images} imagens incorporadas.')
    finally:
        os.chdir(previous)
