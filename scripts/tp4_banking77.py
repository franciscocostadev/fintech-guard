"""BANKING77: preparo rastreável, seleção no treino e avaliação multiclasse."""
from __future__ import annotations

from collections import Counter, defaultdict
from importlib.metadata import version
from pathlib import Path
import hashlib
import json
import math
import time
import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, balanced_accuracy_score, classification_report,
                             confusion_matrix, f1_score, roc_auc_score)
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold, cross_val_score
from sklearn.pipeline import Pipeline
from threadpoolctl import threadpool_limits

from scripts.tp4_classification import template, write_json, digest

SEED = 42
GRID = {'classifier__C': [0.1, 1.0, 10.0], 'tfidf__ngram_range': [(1, 1), (1, 2), (1, 3)]}
MODEL_VERSION = 'tp4-banking77-v1'
SOURCE_PATHS = {split: f'data/processed/banking77/{split}.csv' for split in ('train', 'test')}


def make_groups(texts, threshold=0.9, minimum_length=40):
    """Join exato de Jaccard com filtro por prefixos; nenhuma feature aprendida pelo modelo.

    Ordem global: frequência crescente de gramas e desempate lexical. Se Jaccard>=t,
    os prefixos de tamanho |S|-ceil(t*|S|)+1 se intersectam. O filtro apenas gera
    candidatos; a decisão usa o Jaccard exato dos conjuntos completos.
    """
    normalized = [template(text) for text in texts]
    grams = [set(s[i:i+5] for i in range(max(0, len(s)-4))) for s in normalized]
    frequencies = Counter(g for row in grams for g in row)
    parents = list(range(len(texts)))
    def find(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i
    def union(i, j):
        parents[find(i)] = find(j)
    exact = {}
    index = defaultdict(list)
    pairs = []
    for i, (text, row) in enumerate(zip(normalized, grams)):
        if text in exact:
            j = exact[text]
            union(i, j)
            pairs.append((j, i, 1.0, 'template_equal'))
        else:
            exact[text] = i
        if len(text) < minimum_length or not row:
            continue
        ordered = sorted(row, key=lambda g: (frequencies[g], g))
        prefix = ordered[:len(row) - math.ceil(threshold * len(row)) + 1]
        candidates = {j for gram in prefix for j in index[gram]}
        for j in sorted(candidates):
            if text == normalized[j]:
                continue
            other = grams[j]
            if min(len(row), len(other)) / max(len(row), len(other)) < threshold:
                continue
            similarity = len(row & other) / len(row | other)
            if similarity >= threshold:
                union(i, j)
                pairs.append((j, i, similarity, 'char5_jaccard'))
        for gram in prefix:
            index[gram].append(i)
    roots = defaultdict(list)
    for i in range(len(texts)):
        roots[find(i)].append(i)
    component = {i: min(members) for members in roots.values() for i in members}
    return [f'b{component[i]:05d}' for i in range(len(texts))], pd.DataFrame(pairs, columns=['row_a','row_b','similarity','reason'])


def prepare(root: Path):
    output = root/'reports/TP4/banking77'
    output.mkdir(parents=True, exist_ok=True)
    prior_audit = json.loads((root/'reports/TP4/auditoria_dados.json').read_text(encoding='utf-8'))
    frames, source_hashes = [], {}
    for split, name in SOURCE_PATHS.items():
        path = root/name
        source_hashes[split] = digest(path)
        if source_hashes[split] != prior_audit['datasets'][f'banking_{split}']['sha256']:
            raise ValueError('Base do BANKING77 diverge da auditoria inicial; revisar antes do treino.')
        frame = pd.read_csv(path, keep_default_na=False)
        if list(frame.columns) != ['text','category'] or frame.text.str.strip().eq('').any():
            raise ValueError('Dados inválidos no BANKING77.')
        frame['source_split'], frame['source_row_id'] = split, np.arange(len(frame))
        frames.append(frame)
    df = pd.concat(frames, ignore_index=True)
    labels = json.loads((root/'ml/banking77_labels.json').read_text(encoding='utf-8'))
    if len(labels) != 77 or any(set(frame.category) != set(labels) for frame in frames):
        raise ValueError('As 77 classes precisam estar presentes nos dois splits originais.')
    df['text_sha256'] = df.text.map(lambda text: hashlib.sha256(text.encode('utf-8')).hexdigest())
    df['group_id'], pairs = make_groups(df.text.tolist())
    test_groups = set(df.loc[df.source_split.eq('test'),'group_id'])
    exclude = df.source_split.eq('train') & df.group_id.isin(test_groups)
    df['status'] = df.source_split
    df.loc[exclude,'status'] = 'excluded_test_overlap'
    train, test = df[df.status.eq('train')].copy(), df[df.status.eq('test')].copy()
    if set(train.category) != set(labels):
        raise ValueError('Exclusão removeu toda uma classe; não continuar silenciosamente.')
    cv = list(StratifiedGroupKFold(5,shuffle=True,random_state=SEED).split(train.text,train.category,train.group_id))
    df['validation_fold'] = -1
    for i, (fit, val) in enumerate(cv):
        assert set(train.iloc[fit].group_id).isdisjoint(train.iloc[val].group_id)
        assert set(train.iloc[fit].category) == set(train.iloc[val].category) == set(labels)
        df.loc[train.iloc[val].index,'validation_fold'] = i
    assert set(train.group_id).isdisjoint(test.group_id)
    manifest = df[['source_split','source_row_id','text_sha256','category','group_id','status','validation_fold']]
    protocol = {'experiment':MODEL_VERSION,'recorded_before_model_evaluation':True,'source_sha256':source_hashes,
                'target':'77 original BANKING77 intents','labels':labels,'seed':SEED,
                'test_policy':'Preserve all 3079 TP1-cleaned test rows; remove every training row in a component touching test. Test already seen in EDA; in-domain benchmark, not external validation.',
                'groups':'Label-blind NFKC/casefold/space + URL/email/number templates; exact templates at any length or char5 Jaccard>=0.9 for both >=40 chars. Connected components; exact candidate prefix join.',
                'cv':'5 StratifiedGroupKFold within retained training rows; all 77 classes in every fit/validation fold',
                'pipeline':{'tfidf':{'min_df':2,'sublinear_tf':True,'max_features':30000,'stop_words':None,'lowercase':True},
                            'classifier':{'solver':'lbfgs','max_iter':1000,'l1_ratio':0.0,'initial_C':1.0,'initial_ngram_range':[1,2]}},
                'grid':{k:[list(v) if isinstance(v,tuple) else v for v in values] for k,values in GRID.items()},
                'candidates':9,'selection_metric':'f1_macro','decision':'argmax probability; no confidence threshold selected on test',
                'comparison':'majority-prior, initial pipeline, selected pipeline; final refit on retained train only',
                'post_test_policy':'No feature/grid/threshold change based on test. Identical reruns are reproduction, not new independent evaluation.'}
    serialized = manifest.to_csv(index=False,lineterminator='\n')
    protocol_path, manifest_path = output/'protocol.json', output/'split_manifest.csv'
    if protocol_path.exists() and json.loads(protocol_path.read_text(encoding='utf-8')) != protocol:
        raise ValueError('Protocolo mudou: registrar outro experimento, sem sobrescrever este.')
    if manifest_path.exists() and manifest_path.read_text(encoding='utf-8') != serialized:
        raise ValueError('Partição diverge da congelada.')
    write_json(protocol_path,protocol)
    manifest_path.write_text(serialized,encoding='utf-8')
    pairs.to_csv(output/'similar_pairs.csv',index=False)
    exclusions = manifest[manifest.status.eq('excluded_test_overlap')].copy()
    exclusions['reason']='component_contains_test_row'
    exclusions.to_csv(output/'excluded_training_rows.csv',index=False)
    counts = df.groupby('group_id').size()
    write_json(output/'data_audit.json',{
        'source_train_rows':len(frames[0]),'test_rows':len(test),'retained_train_rows':len(train),
        'excluded_train_rows':int(exclude.sum()),'classes':len(labels),'groups':len(counts),
        'multirow_groups':int(counts.gt(1).sum()),'largest_group':int(counts.max()),'similar_pairs':len(pairs),
        'mixed_label_groups_total':int(df.groupby('group_id').category.nunique().gt(1).sum()),
        'mixed_label_groups_retained_train':int(train.groupby('group_id').category.nunique().gt(1).sum()),
        'test_groups_with_multiple_rows':int(test.groupby('group_id').size().gt(1).sum()),
        'cross_split_groups_after_exclusion':0,'test_rows_modified':0,
        'note':'Similar cases with different labels are retained within one CV group; no relabeling. Exclusions depend on text similarity, not model output.'})
    distribution = pd.crosstab(df.category,df.status).reindex(labels,fill_value=0)
    distribution.to_csv(output/'class_distribution.csv')
    derived=root/'data/processed/TP4/banking77/train.csv'
    derived.parent.mkdir(parents=True,exist_ok=True)
    train[['text','category']].to_csv(derived,index=False)
    return train,test,cv,labels


def build_pipeline():
    return Pipeline([('tfidf',TfidfVectorizer(ngram_range=(1,2),min_df=2,sublinear_tf=True,
                                            max_features=30000,stop_words=None,lowercase=True)),
                     ('classifier',LogisticRegression(C=1.0,solver='lbfgs',max_iter=1000,random_state=SEED))])


def train_models(root, train, cv, pipeline=None):
    pipeline = pipeline if pipeline is not None else build_pipeline()
    baseline = DummyClassifier(strategy='prior')
    initial = clone(pipeline)
    with threadpool_limits(limits=1), warnings.catch_warnings():
        warnings.simplefilter('error',ConvergenceWarning)
        baseline_cv=cross_val_score(baseline,train.text,train.category,cv=cv,scoring='f1_macro',n_jobs=1,error_score='raise')
        initial_cv=cross_val_score(initial,train.text,train.category,cv=cv,scoring='f1_macro',n_jobs=1,error_score='raise')
        baseline.fit(train.text,train.category)
        initial.fit(train.text,train.category)
        search = GridSearchCV(pipeline,GRID,scoring='f1_macro',cv=cv,refit=True,n_jobs=1,error_score='raise',verbose=2)
        start=time.perf_counter()
        search.fit(train.text,train.category)
        elapsed=time.perf_counter()-start
    output=root/'reports/TP4/banking77'
    write_json(output/'selection.json',{'best_params':search.best_params_,'best_cv_macro_f1':float(search.best_score_),
                                     'selection_uses_test':False,'grid_seconds':elapsed})
    scores={'majority':baseline_cv,'initial':initial_cv,
            'tuned':np.array([search.cv_results_[f'split{i}_test_score'][search.best_index_] for i in range(5)])}
    cv_results=pd.DataFrame(search.cv_results_)
    cols=[c for c in cv_results if c.startswith('param_') or c.endswith('test_score') or c=='params']
    cv_results[cols].to_csv(output/'cv_results.csv',index=False)
    return {'majority':baseline,'initial':initial,'tuned':search.best_estimator_}, scores, search


def evaluate(root, train, test, labels, models, scores, search):
    output=root/'reports/TP4/banking77'
    rows, reports, predictions, probabilities = [],{},[],{}
    for name,model in models.items():
        if list(model.classes_) != labels:
            raise ValueError('Ordem das classes incompatível com scores da ROC.')
        with threadpool_limits(limits=1):
            proba=model.predict_proba(test.text)
        predicted=np.asarray(labels)[np.argmax(proba,axis=1)]
        probabilities[name]=proba
        rows.append({'model':name,'cv_macro_f1_mean':float(scores[name].mean()),'cv_macro_f1_std':float(scores[name].std()),
                     'test_accuracy':accuracy_score(test.category,predicted),
                     'test_macro_f1':f1_score(test.category,predicted,average='macro',zero_division=0),
                     'test_weighted_f1':f1_score(test.category,predicted,average='weighted',zero_division=0),
                     'test_balanced_accuracy':balanced_accuracy_score(test.category,predicted),
                     'test_roc_auc_ovr_macro':roc_auc_score(test.category,proba,labels=labels,multi_class='ovr',average='macro'),
                     'test_roc_auc_ovr_weighted':roc_auc_score(test.category,proba,labels=labels,multi_class='ovr',average='weighted')})
        report=classification_report(test.category,predicted,labels=labels,output_dict=True,zero_division=0)
        auc=roc_auc_score(test.category,proba,labels=labels,multi_class='ovr',average=None)
        per_class=pd.DataFrame({label:report[label] for label in labels}).T
        per_class['roc_auc_ovr']=auc
        per_class.to_csv(output/f'per_class_{name}.csv',index_label='intent')
        reports[name]={'classification_report':report,'cv_fold_macro_f1':scores[name].tolist()}
        matrix=confusion_matrix(test.category,predicted,labels=labels)
        pd.DataFrame(matrix,index=labels,columns=labels).to_csv(output/f'confusion_{name}.csv',index_label='actual')
        for i,(_,row) in enumerate(test.iterrows()):
            predictions.append({'model':name,'test_row_id':int(row.source_row_id),'text_sha256':row.text_sha256,
                                'actual':row.category,'predicted':str(predicted[i]),'probability':float(proba[i].max()),
                                'error':bool(predicted[i]!=row.category)})
    metrics=pd.DataFrame(rows); metrics.to_csv(output/'metrics.csv',index=False)
    write_json(output/'reports.json',reports)
    predicted_frame=pd.DataFrame(predictions);predicted_frame.to_csv(output/'predictions.csv',index=False)
    # Scores completos permitem recalcular ROC-AUC; nenhum texto bruto é duplicado aqui.
    np.savez_compressed(output/'test_probabilities.npz',labels=np.asarray(labels,dtype=str),
                        actual=test.category.to_numpy(dtype=str),test_row_ids=test.source_row_id.to_numpy(),**probabilities)
    errors=predicted_frame.query("model == 'tuned' and error")
    errors.groupby(['actual','predicted']).size().sort_values(ascending=False).rename('count').to_csv(output/'confusion_pairs.csv')
    model_dir=root/'models/TP4/banking77';model_dir.mkdir(parents=True,exist_ok=True)
    joblib.dump(models['tuned'],model_dir/'classifier.joblib',compress=3)
    write_json(model_dir/'metadata.json',{'model_version':MODEL_VERSION,'task':'banking77_intent','classes':labels,
                'max_text_characters':4000,'probability_calibrated':False,'fitted_on_test':False,
                'training_rows':len(train),'test_rows':len(test),'best_params':search.best_params_,
                'dependencies':{pkg:version(pkg) for pkg in ['scikit-learn','numpy','scipy','joblib']},
                'artifact_sha256':digest(model_dir/'classifier.joblib'),
                'split_manifest_sha256':digest(output/'split_manifest.csv'),'protocol_sha256':digest(output/'protocol.json'),
                'training_script_sha256':digest(Path(__file__)),'language':'English; Portuguese and out-of-domain inputs not validated'})
    return metrics,reports,predicted_frame,probabilities


def main():
    root=Path(__file__).resolve().parents[1]
    train,test,cv,labels=prepare(root)
    print(f'Protocolo congelado: treino={len(train)}, teste={len(test)}, classes={len(labels)}',flush=True)
    models,scores,search=train_models(root,train,cv)
    metrics,*_=evaluate(root,train,test,labels,models,scores,search)
    print(metrics.to_string(index=False),flush=True)


if __name__ == '__main__':
    # python -m scripts.tp4_banking77 mantém os imports do pacote na raiz.
    main()
