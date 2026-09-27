"""Executa segurança do TP2 por padrão; --tp TP1 executa a análise histórica."""
import argparse
from scripts.run_notebook import execute_notebook


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tp', choices=['TP1', 'TP2'], default='TP2')
    args = parser.parse_args()
    if args.tp == 'TP1':
        execute_notebook('notebooks/TP1/security/01_dataset_understanding.ipynb', min_images=1)
    else:
        execute_notebook('notebooks/TP2/security/01_validacao_e_eda_estatistica.ipynb', min_images=5)


if __name__ == '__main__':
    main()
