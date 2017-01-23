
"""

This files stores all the essential helper functions for variable pre-processing

"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA

def amount_tsh(X_train, X_test):
    """
    convert this item into a categorical variable
    """
    for i in [X_train, X_test]:
        i['amntsh'] = pd.qcut(X_train[X_train['amount_tsh'] <> 0]['amount_tsh'], 4)
        i['amntshnull'] = i['amntsh'].isnull().apply(lambda x: float(x))
    X_train = pd.concat((X_train, pd.get_dummies(X_train['amntsh'], prefix = 'amntsh')), axis = 1)
    X_test = pd.concat((X_test, pd.get_dummies(X_test['amntsh'], prefix = 'amntsh')), axis = 1)
    del X_train['amntsh']
    del X_test['amntsh']
    return X_train, X_test

def removal(X_train, X_test):
    """
    Here we define all the columns that we want to delete right off the bat.

    # id: we drop the id column because it is not a useful predictor.
    # 'amount_tsh' is mostly blank - delete
    # wpt_name: not useful, delete (too many values)
    # subvillage: too many values, delete
    # scheme_name: this is almost 50% nulls, so we will delete this column
    # num_private: we will delete this column because ~99% of the values are zeros.
    # region: drop this b/c is seems very similar to region_code, though not 100% sure about this one!
    """
    z = ['id','amount_tsh',  'num_private', 'wpt_name', 'subvillage', 'scheme_name', 'region', 
          'recorded_by', 'quantity', 'quality_group', 'source_type', 'payment', 'waterpoint_type_group',
         'extraction_type_group']
    for i in z:
        del X_train[i]
        del X_test[i]
    return X_train, X_test


def construction(X_train, X_test):
    """
    construction_year has 35% nulls, so we impute the nulls with the column mean
    """
    for i in [X_train, X_test]:
        i['construction_year'].replace(0, X_train[X_train['construction_year'] <> 0]['construction_year'].mean(), inplace=True)
    return X_train, X_test

def construction2(X_train, X_test):
    """
    construction_year has 35% nulls, so we impute the nulls with the column mean
    """
    for i in [X_train, X_test]:
        i['construction_year'].replace(0., np.NaN, inplace = True)
        i['construction_year'].replace(1., np.NaN, inplace = True)
        data = X_train.groupby(['funder'])['construction_year']
        i['construction_year'] = data.transform(lambda x: x.fillna(x.mean()))
        data = X_train.groupby(['installer'])['construction_year']
        i['construction_year'] = data.transform(lambda x: x.fillna(x.mean()))
        i['construction_year'].fillna(X_train['construction_year'].mean(), inplace=True)
    return X_train, X_test

def dates(X_train, X_test):
    """
    date_recorded: this might be a useful variable for this analysis, although the year itself would be useless in a practical scenario moving into the future. We will convert this column into a datetime, and we will also create 'year_recorded' and 'month_recorded' columns just in case those levels prove to be useful. A visual inspection of both casts significant doubt on that possibility, but we'll proceed for now. We will delete date_recorded itself, since random forest cannot accept datetime
    """
    for i in [X_train, X_test]:
        i['date_recorded'] = pd.to_datetime(i['date_recorded'])
        i['year_recorded'] = i['date_recorded'].apply(lambda x: x.year)
        i['month_recorded'] = i['date_recorded'].apply(lambda x: x.month)
        i['date_recorded'] = (pd.to_datetime(i['date_recorded'])).apply(lambda x: x.toordinal())
    return X_train, X_test

def locs(X_train, X_test):
    """
    gps_height, latitude, longitude, population
    """
    trans = ['longitude', 'latitude', 'gps_height', 'population']
    for i in [X_train, X_test]:
        i.loc[i.longitude == 0, 'latitude'] = 0
        for z in trans:
            i[z].replace(0., np.NaN, inplace = True)
            i[z].replace(1., np.NaN, inplace = True)
            data = X_train.groupby(['subvillage'])[z]
            i[z] = data.transform(lambda x: x.fillna(x.mean()))
            data = X_train.groupby(['district_code'])[z]
            i[z] = data.transform(lambda x: x.fillna(x.mean()))
            data = X_train.groupby(['basin'])[z]
            i[z] = data.transform(lambda x: x.fillna(x.mean()))
            i[z] = i[z].fillna(X_train[z].mean())
    return X_train, X_test

def bools(X_train, X_test):
    """
    public_meeting: we will fill the nulls as 'False'
    permit: we will fill the nulls as 'False
    """
    z = ['public_meeting', 'permit']
    for i in z:
        X_train[i].fillna(False, inplace = True)
        X_train[i] = X_train[i].apply(lambda x: float(x))
        X_test[i].fillna(False, inplace = True)
        X_test[i] = X_test[i].apply(lambda x: float(x))
    return X_train, X_test


def codes(X_train, X_test):
    """
    convert region_code and district_code to string objects, since they are actually categorical variables
    """
    for i in ['region_code', 'district_code']:
        X_train[i] = X_train[i].apply(lambda x: str(x))
        X_test[i] = X_test[i].apply(lambda x: str(x))
    return X_train, X_test

def dummies(X_train, X_test):
    X_train['district_code'] = X_train['district_code'].apply(lambda x: str(x))
    X_train['region_code'] = X_train['region_code'].apply(lambda x: str(x))
    X_test['district_code'] = X_test['district_code'].apply(lambda x: str(x))
    X_test['region_code'] = X_test['region_code'].apply(lambda x: str(x))
    columns = [i for i in X_train.columns if type(X_train[i].iloc[1]) == str]
    for column in columns:
        X_train[column].fillna('NULL', inplace = True)
        good_cols = [column+'_'+i for i in X_train[column].unique() if i in X_test[column].unique()]
        X_train = pd.concat((X_train, pd.get_dummies(X_train[column], prefix = column)[good_cols]), axis = 1)
        X_test = pd.concat((X_test, pd.get_dummies(X_test[column], prefix = column)[good_cols]), axis = 1)
        del X_train[column]
        del X_test[column]
    return X_train, X_test

def meaningful(X_train, X_test):
    status = pd.get_dummies(y_train['status_group'])
    good_cols = []
    for i in X_train.columns[12:]:
        if status[X_train[i] == 1]['non functional'].mean() > (status['non functional'].mean() + .0510):
            good_cols.append(i)
        elif status[X_train[i] == 1]['functional needs repair'].mean() > (status['functional needs repair'].mean() + .0510):
            good_cols.append(i)
        elif status[X_train[i] == 1]['functional'].mean() > (status['functional'].mean() + .0510):
            good_cols.append(i)
    X_train2 = pd.concat((X_train.iloc[:, :12], X_train[good_cols]), axis = 1)
    X_test2 = pd.concat((X_test.iloc[:, :12], X_test[good_cols]), axis = 1)
    return X_train, X_test

def lda(X_train, X_test, y_train, cols):
    sc = StandardScaler()
    X_train_std = sc.fit_transform(X_train[cols])
    X_test_std = sc.transform(X_test[cols])
    lda = LDA(n_components=None)
    X_train_lda = lda.fit_transform(X_train_std, y_train.values.ravel())
    X_test_lda = lda.transform(X_test_std)
    X_train = pd.concat((pd.DataFrame(X_train_lda), X_train), axis=1)
    X_test = pd.concat((pd.DataFrame(X_test_lda), X_test), axis=1)
    for i in cols:
        del X_train[i]
        del X_test[i]
    return X_train, X_test

def gini(p):
    return 1-(p**2 + (1-p)**2)

def impurity(X_train):
    imp = {}
    for i in X_train.columns[17:]:
        imp[i] = gini(X_train[i].mean())
    return imp