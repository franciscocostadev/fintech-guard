"""Executa o protocolo exploratório registrado para o passo 5 do TP2."""
from datetime import datetime, timezone
import hashlib
import json
import math

import numpy as np
import pandas as pd
import scipy
from scipy.stats import mannwhitneyu


def run_hypothesis(frame, root):
    output = root / 'reports/TP2/hypothesis_test'
    protocol_path = output / 'protocol.json'
    protocol_bytes = protocol_path.read_bytes()
    p = json.loads(protocol_bytes)
    assert hashlib.sha256((root / p['dataset']).read_bytes()).hexdigest() == p['dataset_sha256']
    assert hashlib.sha256((root / p['tp1_source']).read_bytes()).hexdigest() == p['tp1_notebook_sha256']
    source = pd.read_csv(root / p['dataset'])
    pd.testing.assert_frame_equal(frame[['text', 'category']].reset_index(drop=True), source)
    assert (frame.n_chars == frame.text.map(len)).all()
    x = frame.loc[frame.category.eq(p['x_label']), 'n_chars'].to_numpy()
    y = frame.loc[frame.category.eq(p['y_label']), 'n_chars'].to_numpy()
    assert len(x) == p['expected_n_x'] and len(y) == p['expected_n_y']
    assert np.isfinite(x).all() and np.isfinite(y).all()
    result = mannwhitneyu(x, y, alternative=p['alternative'], method=p['method'],
                          use_continuity=p['use_continuity'], nan_policy=p['nan_policy'])
    # Verificação independente da orientação de U e do meio peso dos empates.
    differences = x[:, None] - y[None, :]
    wins = int((differences > 0).sum())
    ties = int((differences == 0).sum())
    losses = int((differences < 0).sum())
    assert wins + ties + losses == len(x) * len(y)
    assert np.isclose(result.statistic, wins + ties / 2)
    superiority = float(result.statistic / (len(x) * len(y)))
    effect = 2 * superiority - 1
    assert np.isclose(effect, (wins - losses) / (len(x) * len(y)))
    # Conferência independente da aproximação normal bilateral usada no protocolo.
    _, tie_counts = np.unique(np.concatenate([x, y]), return_counts=True)
    n = len(x) + len(y)
    variance = len(x) * len(y) / 12 * (
        n + 1 - sum(int(t)**3 - int(t) for t in tie_counts) / (n * (n - 1)))
    z = (abs(result.statistic - len(x) * len(y) / 2) - 0.5) / math.sqrt(variance)
    independent_p = min(1.0, math.erfc(z / math.sqrt(2)))
    assert math.isclose(result.pvalue, independent_p, rel_tol=1e-12)
    rows = []
    for label, values in [(p['x_label'], x), (p['y_label'], y)]:
        q1, median, q3 = np.quantile(values, [.25, .5, .75], method='linear')
        rows.append({'category': label, 'n': len(values), 'median': median,
                     'q1': q1, 'q3': q3, 'iqr': q3-q1,
                     'min': int(values.min()), 'max': int(values.max()),
                     'mean': float(values.mean()), 'sd_sample': float(values.std(ddof=1))})
    descriptive = pd.DataFrame(rows).set_index('category')
    details = {
        'executed_at_utc': datetime.now(timezone.utc).isoformat(),
        'protocol_sha256': hashlib.sha256(protocol_bytes).hexdigest(),
        'dataset_sha256': p['dataset_sha256'],
        'scipy_version': scipy.__version__, 'numpy_version': np.__version__,
        'pandas_version': pd.__version__, 'test': p['test'],
        'alternative': p['alternative'], 'method': p['method'],
        'use_continuity': p['use_continuity'], 'alpha': p['alpha'],
        'x_label': p['x_label'], 'y_label': p['y_label'], 'n_x': len(x), 'n_y': len(y),
        'u_x': float(result.statistic), 'u_y': float(len(x)*len(y)-result.statistic),
        'p_value': float(result.pvalue), 'reject_h0': bool(result.pvalue < p['alpha']),
        'common_language_A': superiority, 'rank_biserial': effect,
        'pairwise_wins_x': wins, 'pairwise_ties': ties, 'pairwise_losses_x': losses,
        'independent_pairwise_check_passed': True,
        'quartile_method': 'numpy.quantile method=linear',
        'scope': 'exploratório; sem confirmação independente nem inferência de desempenho preditivo',
    }
    descriptive.to_csv(output / 'group_summary.csv')
    (output / 'result.json').write_text(json.dumps(details, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    verification = {
        'protocol_precedes_execution': p['registered_at_utc'] < details['executed_at_utc'],
        'protocol_sha256': details['protocol_sha256'],
        'executed_at_utc': details['executed_at_utc'],
        'pairwise_u_verified': True,
        'independent_asymptotic_p': independent_p,
        'matches_scipy_p': True,
    }
    assert verification['protocol_precedes_execution']
    (output / 'verification.json').write_text(json.dumps(verification, indent=2) + '\n', encoding='utf-8')
    return descriptive, details
