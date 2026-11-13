"""Executa o notebook BANKING77, preservando métricas e seis figuras."""
if __package__:
    from .run_notebook import execute_notebook
else:
    from run_notebook import execute_notebook

if __name__ == '__main__':
    execute_notebook('notebooks/TP4/banking77/01_classificacao_intencoes.ipynb', min_images=6)
