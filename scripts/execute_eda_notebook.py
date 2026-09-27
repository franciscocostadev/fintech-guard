"""Executa o BANKING77 do TP1 e salva as saídas no notebook."""
from scripts.run_notebook import execute_notebook


def main():
    execute_notebook('notebooks/TP1/banking77/01_eda_banking77.ipynb', min_images=3)


if __name__ == '__main__':
    main()
