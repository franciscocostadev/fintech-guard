"""Diagnóstico descritivo posterior, sem ler textos de teste ou reajustar modelos."""
from pathlib import Path
import json

import numpy as np
import pandas as pd

from tp4_classification import write_json


def main():
    root = Path(__file__).resolve().parents[1]
    import sys
    sys.path.insert(0, str(root))
    from ml.security_classifier import SecurityClassifier
    output = root / 'reports/TP4/classification'
    df = pd.read_csv(root / 'data/processed/security/phishing_nlp_dataset.csv')
    manifest = pd.read_csv(output / 'split_manifest.csv')
    train = df[manifest.split.eq('train')].copy()
    train['label'] = manifest.loc[manifest.split.eq('train'), 'label']
    vec = SecurityClassifier().pipeline.named_steps['tfidf']
    analyze = vec.build_analyzer()
    frequencies = np.zeros(len(vec.vocabulary_), dtype=int)
    for text in train.text:
        for term in set(analyze(text)):
            if term in vec.vocabulary_:
                frequencies[vec.vocabulary_[term]] += 1
    expected = np.log((1 + len(train)) / (1 + frequencies)) + 1
    counts = {token: {label: int(train.loc[train.label.eq(label), 'text'].str.contains(token, case=False, regex=False).sum())
                      for label in ['benign', 'threat']}
              for token in ['download', 'attachment', 'click', 'password']}
    audit = {'purpose': 'Diagnóstico posterior ao treino; sem seleção, retreino ou leitura textual de teste.',
             'rows_examined': len(train), 'vocabulary_size': len(vec.vocabulary_),
             'idf_max_absolute_difference_from_training_only': float(np.max(np.abs(expected - vec.idf_))),
             'minimum_document_frequency': int(frequencies.min()),
             'substring_message_counts_training_only': counts,
             'limitation': 'Associações lexicais podem refletir estilo/coleta; não provam origem sintética nem generalização.'}
    if not np.allclose(expected, vec.idf_):
        raise ValueError('IDF não corresponde ao treino registrado.')
    write_json(output / 'lexical_audit.json', audit)
    print(json.dumps(audit, ensure_ascii=True))


if __name__ == '__main__':
    main()
