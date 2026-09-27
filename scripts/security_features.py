"""Atributos textuais exploratórios, versão 1. Sem acesso a URLs ou uso de rótulos."""
import re
import hashlib
from pathlib import Path
import pandas as pd

FEATURES = ['n_chars', 'n_words', 'mean_word_length', 'digit_ratio',
            'uppercase_ratio', 'n_links', 'n_exclamations']
# Prefixo explícito e conteúdo após ele; domínios nus e URLs ofuscadas não entram.
LINK_RE = re.compile(r"(?<![\w@])(?:https?://|www\.)[^\s<>\"']+", re.IGNORECASE)
WORD_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", re.UNICODE)

def extract_features(text):
    if not isinstance(text, str):
        raise TypeError('text deve ser uma string; ausentes não são convertidos em texto.')
    words = WORD_RE.findall(LINK_RE.sub(' ', text))
    letters = sum(c.isalpha() for c in text)
    return {
        'n_chars': len(text),
        'n_words': len(words),
        'mean_word_length': sum(sum(c.isalpha() for c in word) for word in words) / len(words) if words else 0.0,
        'digit_ratio': sum(c.isdecimal() for c in text) / len(text) if text else 0.0,
        'uppercase_ratio': sum(c.isalpha() and c.isupper() for c in text) / letters if letters else 0.0,
        'n_links': len(LINK_RE.findall(text)),
        'n_exclamations': text.count('!'),
    }

def build_features(cleaned, audit):
    """Mantém ordem e conteúdo; junta proveniência validada a sete medidas."""
    kept = audit.loc[audit.decision.eq('kept')].sort_values('processed_csv_row').reset_index(drop=True)
    if len(kept) != len(cleaned):
        raise ValueError('Auditoria e dataset com dimensões diferentes.')
    base = cleaned.reset_index(drop=True).copy()
    hashes = base.text.map(lambda value: hashlib.sha256(value.encode('utf-8')).hexdigest())
    if hashes.tolist() != kept.text_sha256.tolist() or base.category.tolist() != kept.category.tolist():
        raise ValueError('Textos/rótulos não correspondem à auditoria.')
    metadata = kept[['excel_row', 'processed_csv_row', 'text_sha256']].copy()
    numeric = pd.DataFrame([extract_features(text) for text in base.text], columns=FEATURES)
    return pd.concat([metadata, base, numeric], axis=1)

def export_features(frame, root):
    output = Path(root) / 'reports/TP2/security_features'
    output.mkdir(parents=True, exist_ok=True)
    # Sem duplicar mensagens: IDs/hash permitem a junção ao dataset tratado.
    frame.drop(columns='text').to_csv(output / 'features.csv', index=False)
    frame[FEATURES].describe().to_csv(output / 'describe.csv', index_label='statistic')
    quality = pd.DataFrame({'dtype': frame[FEATURES].dtypes.astype(str),
                            'missing': frame[FEATURES].isna().sum(),
                            'unique_values': frame[FEATURES].nunique(),
                            'zero_count': frame[FEATURES].eq(0).sum()})
    quality.to_csv(output / 'quality.csv', index_label='feature')
    return quality
