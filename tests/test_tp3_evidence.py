"""Simula inconsistências nos CSVs em memória, sem alterar as evidências."""
from pathlib import Path

import pytest

from scripts import verify_tp3_evidence as evidence

ROOT = Path(__file__).resolve().parents[1]


def test_accepts_reproducible_evidence():
    result = evidence.validate_numeric_evidence(ROOT)
    assert result['dataset_rows'] == 603
    assert result['train_rows'] == 482 and result['evaluation_rows'] == 121
    assert result['prediction_rows'] == 363 and result['metric_rows_recomputed'] == 6


@pytest.mark.parametrize('filename,column,value,error', [
    ('metrics.csv', 'n', '1', 'n incorreto'),
    ('metrics.csv', 'r2', '0.123456789', 'R²'),
    ('metrics.csv', 'rmse_caracteres', '999999', 'RMSE'),
    ('split_manifest.csv', 'row_id', '1', 'todos os IDs'),
    ('split_manifest.csv', 'text_sha256', '0' * 64, 'Hash do texto'),
    ('split_manifest.csv', 'category', 'Pretexting', 'Rótulo divergente'),
    ('predictions.csv', 'row_id', '-1', 'cada ID de avaliação'),
    ('predictions.csv', 'observado', '999999', 'Observado'),
    ('predictions.csv', 'previsto', '999999', 'Previsão recalculada'),
    ('predictions.csv', 'residuo', '999999', 'Resíduo'),
])
def test_rejects_inconsistent_evidence(monkeypatch, filename, column, value, error):
    original_read = evidence.read_csv

    def altered_read(path):
        # O parser lê os arquivos reais; somente uma célula da cópia em memória muda.
        # A função completa de validação e os cálculos permanecem os de produção.
        rows = original_read(path)
        if path.name == filename:
            rows[0][column] = value
        return rows

    monkeypatch.setattr(evidence, 'read_csv', altered_read)
    with pytest.raises(ValueError, match=error):
        evidence.validate_numeric_evidence(ROOT)
