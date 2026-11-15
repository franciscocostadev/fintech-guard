"""Verificações de dados, métricas, artefato e composição do TP4."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import random

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import f1_score, roc_auc_score
from threadpoolctl import threadpool_limits

from ml.banking_classifier import BankingClassifier
from ml.classification_service import ClassificationService
from scripts.tp4_banking77 import make_groups
from scripts.tp4_classification import template

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/TP4/banking77'


def test_banking_prefix_candidates_match_exhaustive_jaccard_components():
    rng=random.Random(42)
    bases=[''.join(rng.choices('abcdef ghijk lmnop qrstuv',k=100)) for _ in range(12)]
    texts=[]
    for base in bases:
        texts.extend([base,base[:40]+'x'+base[41:],base[:70]+'y'+base[71:]])
    texts += ['number 100','number 200','different short text']
    optimized,_=make_groups(texts)
    normalized=[template(t) for t in texts]
    grams=[set(t[i:i+5] for i in range(max(0,len(t)-4))) for t in normalized]
    parent=list(range(len(texts)))
    def find(i):
        while parent[i]!=i: i=parent[i]
        return i
    for i,a in enumerate(normalized):
        for j,b in enumerate(normalized[:i]):
            equal=a==b
            similar=min(len(a),len(b))>=40 and len(grams[i]&grams[j])/len(grams[i]|grams[j])>=.9
            if equal or similar: parent[find(i)]=find(j)
    for i in range(len(texts)):
        for j in range(len(texts)):
            assert (optimized[i]==optimized[j])==(find(i)==find(j))


def test_banking_manifest_covers_sources_and_protects_test():
    manifest=pd.read_csv(OUT/'split_manifest.csv')
    train=pd.read_csv(ROOT/'data/processed/banking77/train.csv')
    test=pd.read_csv(ROOT/'data/processed/banking77/test.csv')
    for name,source in [('train',train),('test',test)]:
        part=manifest[manifest.source_split.eq(name)]
        assert part.source_row_id.tolist()==list(range(len(source)))
        assert part.category.tolist()==source.category.tolist()
        assert part.text_sha256.tolist()==[hashlib.sha256(t.encode()).hexdigest() for t in source.text]
    retained=manifest[manifest.status.eq('train')]
    heldout=manifest[manifest.status.eq('test')]
    excluded=manifest[manifest.status.eq('excluded_test_overlap')]
    assert len(retained)==9985 and len(heldout)==3079 and len(excluded)==8
    assert not set(retained.group_id)&set(heldout.group_id)
    assert set(excluded.group_id).issubset(set(heldout.group_id))
    assert retained.groupby('group_id').validation_fold.nunique().max()==1
    assert heldout.validation_fold.eq(-1).all()
    for fold in range(5):
        assert retained[retained.validation_fold.eq(fold)].category.nunique()==77
    derived=pd.read_csv(ROOT/'data/processed/TP4/banking77/train.csv')
    assert derived.equals(train.iloc[retained.source_row_id].reset_index(drop=True))


@pytest.fixture(scope='module')
def model():
    return BankingClassifier()


def test_banking_artifact_idf_uses_training_only(model):
    train=pd.read_csv(ROOT/'data/processed/TP4/banking77/train.csv')
    vec=model.pipeline.named_steps['tfidf'];analyze=vec.build_analyzer()
    counts=np.zeros(len(vec.vocabulary_),dtype=int)
    for text in train.text:
        for term in set(analyze(text)):
            if term in vec.vocabulary_: counts[vec.vocabulary_[term]]+=1
    assert counts.min()>=2
    np.testing.assert_allclose(vec.idf_,np.log((1+len(train))/(1+counts))+1)
    assert model.metadata['fitted_on_test'] is False


def test_banking_serialization_matches_all_saved_probabilities(model):
    test=pd.read_csv(ROOT/'data/processed/banking77/test.csv')
    with np.load(OUT/'test_probabilities.npz',allow_pickle=False) as stored:
        assert stored['labels'].tolist()==model.labels
        assert stored['test_row_ids'].tolist()==list(range(len(test)))
        assert stored['actual'].tolist()==test.category.tolist()
        with threadpool_limits(limits=1): proba=model.pipeline.predict_proba(test.text)
        np.testing.assert_allclose(proba,stored['tuned'])
    prediction=pd.read_csv(OUT/'predictions.csv').query("model == 'tuned'")
    assert prediction.predicted.tolist()==np.asarray(model.labels)[proba.argmax(axis=1)].tolist()


def test_banking_metrics_recompute_from_scores_and_labels():
    metrics=pd.read_csv(OUT/'metrics.csv').set_index('model')
    with np.load(OUT/'test_probabilities.npz',allow_pickle=False) as stored:
        labels=stored['labels'];actual=stored['actual']
        for name in ('majority','initial','tuned'):
            predicted=labels[stored[name].argmax(axis=1)]
            assert metrics.loc[name,'test_macro_f1']==pytest.approx(f1_score(actual,predicted,average='macro'))
            assert metrics.loc[name,'test_roc_auc_ovr_macro']==pytest.approx(roc_auc_score(actual,stored[name],labels=labels,multi_class='ovr',average='macro'))
            assert metrics.loc[name,'test_roc_auc_ovr_weighted']==pytest.approx(roc_auc_score(actual,stored[name],labels=labels,multi_class='ovr',average='weighted'))


@pytest.mark.parametrize('text',[None,23,'',' \n','x'*4001],ids=['none','number','empty','whitespace','over_limit'])
def test_banking_input_rejected_without_silent_truncation(model,text):
    with pytest.raises(ValueError): model.classify(text)


def test_banking_corruption_blocks_deserialization(tmp_path,monkeypatch):
    meta=json.loads((ROOT/'models/TP4/banking77/metadata.json').read_text(encoding='utf-8'))
    (tmp_path/'metadata.json').write_text(json.dumps(meta),encoding='utf-8')
    (tmp_path/'classifier.joblib').write_bytes(b'corrupt')
    def forbidden(*args,**kwargs): pytest.fail('Artefato corrompido não pode carregar.')
    monkeypatch.setattr('ml.banking_classifier.joblib.load',forbidden)
    with pytest.raises(ValueError,match='Integridade'): BankingClassifier(tmp_path)


def test_composition_calls_both_models_with_identical_text_and_separate_scores(monkeypatch):
    seen=[]
    banking={'intent':'lost_or_stolen_card','probability':.7,'model_version':'banking-test'}
    security={'task':'security_binary','label':'threat','probability':.9,
              'probabilities':{'benign':.1,'threat':.9},'model_version':'security-test'}
    class FakeBank:
        def __init__(self,*args): pass
        def classify(self,text): seen.append(('banking',text));return banking.copy()
    class FakeSecurity:
        def __init__(self,*args): pass
        def classify(self,text): seen.append(('security',text));return security.copy()
    monkeypatch.setattr('ml.classification_service.BankingClassifier',FakeBank)
    monkeypatch.setattr('ml.classification_service.SecurityClassifier',FakeSecurity)
    result=ClassificationService().classify('  original text!  ')
    assert seen==[('banking','  original text!  '),('security','  original text!  ')]
    assert result=={'task':'banking_intent_with_security',**banking,'security':security}


def test_composed_service_with_actual_models_matches_individual_predictions():
    service=ClassificationService()
    text='I made a transfer by mistake and want to cancel it.'
    result=service.classify(text)
    assert result['intent']==service.banking.classify(text)['intent']
    assert result['security']==service.security.classify(text)
    assert result['probability']==service.banking.classify(text)['probability']


def test_composed_service_does_not_initialize_if_one_artifact_missing(tmp_path):
    with pytest.raises(FileNotFoundError): ClassificationService(security_dir=tmp_path)


def test_banking_notebook_executed_and_has_all_class_metrics():
    notebook=json.loads((ROOT/'notebooks/TP4/banking77/01_classificacao_intencoes.ipynb').read_text(encoding='utf-8'))
    cells=[c for c in notebook['cells'] if c['cell_type']=='code']
    assert all(isinstance(c['execution_count'],int) for c in cells)
    assert not any(o['output_type']=='error' for c in cells for o in c['outputs'])
    assert sum('image/png' in o.get('data',{}) for c in cells for o in c['outputs'])>=6
    per_class=pd.read_csv(OUT/'per_class_tuned.csv')
    assert len(per_class)==77 and per_class.support.sum()==3079
