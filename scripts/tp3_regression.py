"""Experimento pedagógico de regressão. Não implementa detecção de ameaças."""
from pathlib import Path
import hashlib
import json
import platform
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy
from scipy import stats
import sklearn
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.dummy import DummyRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, root_mean_squared_error
from scripts.security_features import extract_features

ROOT = Path(__file__).resolve().parents[1]
SEED = 42
TARGET = 'n_chars'
SIMPLE = ['n_words']
MULTIPLE = ['n_words', 'mean_word_length', 'uppercase_ratio', 'n_exclamations']

def load_data(root=ROOT):
    path = root / 'data/processed/security/phishing_nlp_dataset.csv'
    data = pd.read_csv(path)
    assert data.shape[0] == 603 and data.category.nunique() == 6
    assert data[['text', 'category']].notna().all().all()
    assert not data.text.duplicated().any()
    features = pd.DataFrame([extract_features(t) for t in data.text])
    assert (features.n_links == 0).all()
    return data, features, hashlib.sha256(path.read_bytes()).hexdigest()

def partition(data):
    return train_test_split(np.arange(len(data)),test_size=.2,random_state=SEED,
                            stratify=data.category)

def pipeline():
    return Pipeline([('imputer',SimpleImputer(strategy='median')),
                     ('scaler',StandardScaler()),('regressor',LinearRegression())])

def run(root=ROOT):
    data, features, digest = load_data(root)
    train, test = partition(data)
    out = root/'reports/TP3/regression';out.mkdir(parents=True,exist_ok=True)
    y = features[TARGET]
    models = {'media_treino': (DummyRegressor(strategy='mean'), SIMPLE),
              'linear_simples': (pipeline(), SIMPLE),
              'linear_multipla': (pipeline(), MULTIPLE)}
    records=[];predictions=[];coefficients=[]
    for name,(model,columns) in models.items():
        model.fit(features.loc[train,columns],y.iloc[train])
        for split,ids in [('treino',train),('avaliacao',test)]:
            pred=model.predict(features.loc[ids,columns])
            records.append({'modelo':name,'particao':split,'n':len(ids),
                            'r2':r2_score(y.iloc[ids],pred),
                            'rmse_caracteres':root_mean_squared_error(y.iloc[ids],pred)})
            if split=='avaliacao':
                for idx,yp in zip(ids,pred):
                    predictions.append({'row_id':int(idx),'modelo':name,
                                        'observado':int(y.iloc[idx]),'previsto':float(yp),
                                        'residuo':float(y.iloc[idx]-yp)})
        if name!='media_treino':
            coefficients.extend({'modelo':name,'atributo':col,'coef_por_desvio_padrao':float(coef)}
                                for col,coef in zip(columns,model[-1].coef_))
    metrics=pd.DataFrame(records);predictions=pd.DataFrame(predictions)
    metrics.to_csv(out/'metrics.csv',index=False)
    predictions.to_csv(out/'predictions.csv',index=False)
    pd.DataFrame(coefficients).to_csv(out/'coefficients.csv',index=False)
    manifest=pd.DataFrame({'row_id':np.arange(len(data)),
                          'text_sha256':data.text.map(lambda t:hashlib.sha256(t.encode()).hexdigest()),
                          'category':data.category,'particao':'treino'})
    manifest.loc[test,'particao']='avaliacao'
    manifest.to_csv(out/'split_manifest.csv',index=False)
    data.category.value_counts().rename_axis('classe').to_frame('n').to_csv(out/'classes.csv')
    features.describe().to_csv(out/'describe_features.csv')
    details={'seed':SEED,'test_size':.2,'train_n':len(train),'evaluation_n':len(test),
             'dataset_sha256':digest,'target':TARGET,'simple':SIMPLE,'multiple':MULTIPLE,
             'versions':{'python':platform.python_version(),'sklearn':sklearn.__version__,
                         'pandas':pd.__version__,'numpy':np.__version__,'scipy':scipy.__version__},
             'interpretation_scope':'Avaliação interna pedagógica; base já explorada no TP1/TP2. Não é teste externo de classificação.'}
    details['max_chars']=int(y.max())
    details['evaluation_max_chars']=int(y.iloc[test].max())
    details['train_max_chars']=int(y.iloc[train].max())
    (out/'protocol.json').write_text(json.dumps(details,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return data,features,metrics,predictions,models,details

def plot_results(predictions,out=None):
    figures=[]
    names=['linear_simples','linear_multipla']
    titles=['Regressão simples','Regressão múltipla']
    for kind in ['observado_previsto','residuos','qq']:
        fig,axes=plt.subplots(1,2,figsize=(12,4.5))
        for ax,name,title in zip(axes,names,titles):
            d=predictions.loc[predictions.modelo.eq(name)]
            if kind=='observado_previsto':
                ax.scatter(d.observado,d.previsto,alpha=.6,label='Mensagens de avaliação')
                lo=min(d.observado.min(),d.previsto.min());hi=max(d.observado.max(),d.previsto.max())
                ax.plot([lo,hi],[lo,hi],'k--',label='Predição perfeita')
                ax.set(xlabel='Observado (caracteres)',ylabel='Previsto (caracteres)');ax.legend()
            elif kind=='residuos':
                ax.scatter(d.previsto,d.residuo,alpha=.6,label='Resíduo = observado - previsto')
                ax.axhline(0,color='black',linestyle='--')
                ax.set(xlabel='Previsto (caracteres)',ylabel='Resíduo (caracteres)');ax.legend()
            else:
                stats.probplot(d.residuo,dist='norm',plot=ax)
                ax.set(xlabel='Quantis teóricos normais',ylabel='Resíduos ordenados (caracteres)')
            ax.set_title(title);ax.grid(alpha=.15)
        fig.suptitle({'observado_previsto':'Comprimento: observado e previsto',
                      'residuos':'Diagnóstico de resíduos - avaliação interna',
                      'qq':'Q-Q plot - comparação dos resíduos com a distribuição normal'}[kind])
        fig.tight_layout()
        if out:
            Path(out).mkdir(parents=True,exist_ok=True)
            fig.savefig(Path(out)/f'{kind}.png',dpi=160,bbox_inches='tight')
        figures.append(fig)
    return figures

if __name__=='__main__':
    _,_,metrics,predictions,_,details=run()
    plot_results(predictions,ROOT/'reports/TP3/figures')
    print(metrics.to_string(index=False))
