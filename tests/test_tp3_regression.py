"""Invariantes de dados e isolamento do pré-processamento do experimento TP3."""
import numpy as np
import pandas as pd
from scripts.tp3_regression import load_data, partition, pipeline, TARGET, MULTIPLE

def test_partition_disjoint_and_complete():
    data, _, _ = load_data()
    train, test = partition(data)
    assert not set(train) & set(test)
    assert set(train) | set(test) == set(range(603))
    assert set(data.iloc[train].category)==set(data.iloc[test].category)

def test_partition_reproducible():
    data, _, _ = load_data()
    first=partition(data);second=partition(data)
    assert all(np.array_equal(a,b) for a,b in zip(first,second))

def test_scaler_only_learns_training_values():
    model=pipeline().fit(pd.DataFrame({'x':[0.,2.,4.]}),[1.,3.,5.])
    before=model.named_steps['scaler'].mean_.copy()
    model.predict(pd.DataFrame({'x':[100000.]}))
    np.testing.assert_array_equal(before,[2.])
    np.testing.assert_array_equal(model.named_steps['scaler'].mean_,before)

def test_predictors_exclude_target_labels_and_constant_links():
    _,features,_=load_data()
    assert not {TARGET,'category','n_links','digit_ratio'} & set(MULTIPLE)
    assert np.isfinite(features[MULTIPLE].to_numpy()).all()
    assert (features[TARGET]>0).all()
