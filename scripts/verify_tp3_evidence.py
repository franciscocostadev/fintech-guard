"""Confere rastreabilidade e recalcula as seis métricas com NumPy."""
import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import nbformat
import numpy as np
from scripts.security_features import extract_features

ROOT = Path(__file__).resolve().parents[1]
MODELS = ('media_treino', 'linear_simples', 'linear_multipla')
PARTITIONS = ('treino', 'avaliacao')
SIMPLE = ['n_words']
MULTIPLE = ['n_words', 'mean_word_length', 'uppercase_ratio', 'n_exclamations']
CLASS_COUNTS = {'NOT-Malicious General Class': 171, 'Phishing': 110, 'Scareware': 100,
                'Baiting': 80, 'Malware': 77, 'Pretexting': 65}
REQUIRED_TESTS = {'test_partition_disjoint_and_complete', 'test_partition_reproducible',
                  'test_scaler_only_learns_training_values',
                  'test_predictors_exclude_target_labels_and_constant_links'}


def require(condition, message):
    # ValueError mantém a conferência ativa também em python -O.
    if not condition:
        raise ValueError(message)


def read_csv(path):
    with path.open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def close(actual, expected, context):
    actual = float(actual)
    require(math.isfinite(actual) and math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-8),
            f'{context}: recebido {actual}, esperado {expected}')


def integer(value):
    number = float(value)
    require(math.isfinite(number) and number.is_integer(), f'Inteiro inválido: {value}')
    return int(number)


def validate_numeric_evidence(root=ROOT):
    """Confere CSV/JSON sem depender do notebook, JUnit, SciPy ou scikit-learn."""
    root = Path(root)
    out = root / 'reports/TP3/regression'
    path = root / 'data/processed/security/phishing_nlp_dataset.csv'
    data = read_csv(path)
    require(len(data) == 603, 'Dataset deve conter 603 registros')
    require(all(r.get('text') and r.get('category') for r in data), 'Texto/rótulo ausente')
    require(len({r['text'] for r in data}) == 603, 'Dataset com textos duplicados')
    require(Counter(r['category'] for r in data) == CLASS_COUNTS, 'Distribuição de classes divergente')
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    protocol = json.loads((out / 'protocol.json').read_text(encoding='utf-8'))
    require(protocol['dataset_sha256'] == digest, 'Hash do dataset divergente')
    require(protocol['seed'] == 42 and protocol['test_size'] == .2, 'Protocolo de separação divergente')
    require(protocol['train_n'] == 482 and protocol['evaluation_n'] == 121, 'Contagens do protocolo divergentes')
    require(protocol['target'] == 'n_chars' and protocol['simple'] == SIMPLE
            and protocol['multiple'] == MULTIPLE, 'Alvo/atributos do protocolo divergentes')

    manifest = read_csv(out / 'split_manifest.csv')
    ids = [integer(r['row_id']) for r in manifest]
    require(len(ids) == 603 and len(set(ids)) == 603 and set(ids) == set(range(603)),
            'Manifesto deve conter todos os IDs exatamente uma vez')
    split = {part: [] for part in PARTITIONS}
    for row, idx in zip(manifest, ids):
        require(row['particao'] in PARTITIONS, 'Partição desconhecida no manifesto')
        require(row['text_sha256'] == hashlib.sha256(data[idx]['text'].encode('utf-8')).hexdigest(),
                f'Hash do texto divergente no ID {idx}')
        require(row['category'] == data[idx]['category'], f'Rótulo divergente no ID {idx}')
        split[row['particao']].append(idx)
    for part, count in [('treino', 482), ('avaliacao', 121)]:
        require(len(split[part]) == count, f'Contagem da partição {part} divergente')
        require({data[idx]['category'] for idx in split[part]} == set(CLASS_COUNTS),
                f'Classes ausentes em {part}')
        split[part] = np.array(sorted(split[part]), dtype=int)

    features = [extract_features(row['text']) for row in data]
    require(all(row['n_links'] == 0 for row in features), 'n_links deixou de ser constante zero')
    y = np.array([row['n_chars'] for row in features], dtype=float)
    for field, value in [('max_chars', y.max()), ('train_max_chars', y[split['treino']].max()),
                         ('evaluation_max_chars', y[split['avaliacao']].max())]:
        close(protocol[field], value, field)
    predicted = {'media_treino': np.full(len(y), y[split['treino']].mean())}
    for model, columns in [('linear_simples', SIMPLE), ('linear_multipla', MULTIPLE)]:
        x = np.array([[row[column] for column in columns] for row in features], dtype=float)
        require(np.isfinite(x).all(), 'Atributos não finitos')
        # Como não há ausentes, a imputação do pipeline original é identidade.
        # Média/escala são calculadas só no treino; ddof=0 equivale a StandardScaler.
        mean = x[split['treino']].mean(axis=0)
        scale = x[split['treino']].std(axis=0)
        scale[scale == 0] = 1
        design = np.column_stack((np.ones(len(x)), (x - mean) / scale))
        coefficients = np.linalg.lstsq(design[split['treino']], y[split['treino']], rcond=None)[0]
        predicted[model] = design @ coefficients

    exported = read_csv(out / 'predictions.csv')
    pairs = [(r['modelo'], integer(r['row_id'])) for r in exported]
    expected = {(model, idx) for model in MODELS for idx in split['avaliacao']}
    require(len(pairs) == 363 and len(set(pairs)) == 363 and set(pairs) == expected,
            'Previsões devem conter uma vez cada ID de avaliação por modelo')
    for row, (model, idx) in zip(exported, pairs):
        close(row['observado'], y[idx], f'Observado {model}/{idx}')
        close(row['previsto'], predicted[model][idx], f'Previsão recalculada {model}/{idx}')
        close(row['residuo'], y[idx] - float(row['previsto']), f'Resíduo {model}/{idx}')

    metrics = read_csv(out / 'metrics.csv')
    require(len(metrics) == 6 and {(r['modelo'], r['particao']) for r in metrics}
            == {(model, part) for model in MODELS for part in PARTITIONS},
            'Devem existir seis combinações únicas de modelo/partição')
    for row in metrics:
        model, part = row['modelo'], row['particao']
        indexes = split[part]
        require(integer(row['n']) == len(indexes), f'n incorreto em {model}/{part}')
        observed = y[indexes]
        residual = observed - predicted[model][indexes]
        rmse = float(np.sqrt(np.mean(residual ** 2)))
        r2 = float(1 - np.sum(residual ** 2) / np.sum((observed - observed.mean()) ** 2))
        close(row['rmse_caracteres'], rmse, f'RMSE {model}/{part}')
        close(row['r2'], r2, f'R² {model}/{part}')
    return {'dataset_sha256': digest, 'dataset_rows': 603, 'classes': 6, 'train_rows': 482,
            'evaluation_rows': 121, 'prediction_rows': len(exported), 'metric_rows_recomputed': len(metrics)}


def verify(root=ROOT, test_report=None, output=None):
    root = Path(root)
    numeric = validate_numeric_evidence(root)
    nb = nbformat.read(root / 'notebooks/TP3/security/01_regressao_e_transicao.ipynb', as_version=4)
    nbformat.validate(nb)
    code = [c for c in nb.cells if c.cell_type == 'code']
    require(len(code) >= 7 and [c.execution_count for c in code] == list(range(1, len(code) + 1)),
            'Notebook incompleto ou contagens de execução fora de ordem')
    require(not any(o.output_type == 'error' for c in code for o in c.outputs), 'Notebook com erro')
    images = sum('image/png' in o.get('data', {}) for c in code for o in c.outputs)
    require(images >= 3, 'Faltam gráficos incorporados')
    for name in ['observado_previsto', 'residuos', 'qq']:
        require((root / f'reports/TP3/figures/{name}.png').read_bytes().startswith(b'\x89PNG\r\n\x1a\n'),
                f'Figura PNG inválida: {name}')
    test_report = Path(test_report) if test_report else root / 'reports/TP3/ci/pytest.xml'
    suites = ET.parse(test_report).getroot()
    cases = suites.findall('.//testcase')
    require(cases and not suites.findall('.//failure') and not suites.findall('.//error'),
            'Relatório pytest vazio ou com falhas')
    own = [c for c in cases if 'test_tp3_regression' in c.attrib.get('classname', '')]
    require(REQUIRED_TESTS.issubset({c.attrib.get('name') for c in own})
            and not any(c.find('skipped') is not None for c in own),
            'Os quatro testes de regressão exigidos devem estar presentes e aprovados')
    evidence = [c for c in cases if 'test_tp3_evidence' in c.attrib.get('classname', '')]
    require(not any(c.find('skipped') is not None for c in evidence), 'Testes de evidências ignorados')
    result = {'status': 'evidencias_automaticas_validadas_revisao_humana_pendente',
              'code_cells': len(code), 'embedded_images': images, 'test_cases': len(cases),
              'tp3_test_cases': len(own), 'evidence_test_cases': len(evidence), **numeric}
    output = Path(output) if output else root / 'reports/TP3/ci/validation.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--test-report', type=Path, help='JUnit a conferir; padrão: reports/TP3/ci/pytest.xml')
    parser.add_argument('--output', type=Path, help='JSON de saída; padrão: reports/TP3/ci/validation.json')
    args = parser.parse_args()
    verify(test_report=args.test_report, output=args.output)
