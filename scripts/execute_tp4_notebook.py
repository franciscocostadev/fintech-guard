"""Executa integralmente o notebook do TP4 e preserva outputs."""
if __package__:
    from .run_notebook import execute_notebook
else:
    from run_notebook import execute_notebook

if __name__ == "__main__":
    execute_notebook("notebooks/TP4/security/01_classificacao.ipynb", min_images=5)
