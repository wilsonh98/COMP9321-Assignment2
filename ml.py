# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# import mpl_toolkits
# from sklearn.model_selection import train_test_split   
# from sklearn import linear_model
# from sklearn import preprocessing
# from sklearn.metrics import mean_squared_error

# housing_data = pd.read_csv('melb_data.csv')
# print(melbourne.isnull().sum())     


import pandas as pd
from sklearn import linear_model
from sklearn.metrics import mean_squared_error
from sklearn.utils import shuffle


def load_diet(file_path, split_percentage):
    df = pd.read_csv(file_path, index_col=0)
    df.drop(['Bedroom2', 'Method', 'SellerG', 'CouncilArea', 'Propertycount', 'Regionname'], axis=1, inplace=True)
    df = shuffle(df)
    diet_x = df.drop('Price', axis=1).values
    diet_y = df['Price'].values

    # Split the dataset in train and test data
    # A random permutation, to split the data randomly

    split_point = int(len(diet_x) * split_percentage)
    diet_X_train = diet_x[:split_point]
    diet_y_train = diet_y[:split_point]
    diet_X_test = diet_x[split_point:]
    diet_y_test = diet_y[split_point:]

    return diet_X_train, diet_y_train, diet_X_test, diet_y_test


if __name__ == "__main__":
    diet_X_train, diet_y_train, diet_X_test, diet_y_test = load_diet("melb_data.csv", split_percentage=0.7)
    model = linear_model.LinearRegression()
    # model = linear_model.BayesianRidge(alpha_1=1e-06, alpha_2=1e-06, compute_score=False, copy_X=True,
    #                                    fit_intercept=True, lambda_1=1e-06, lambda_2=1e-06, n_iter=300,
    #                                    normalize=False, tol=0.001, verbose=False)
    model.fit(diet_X_train, diet_y_train)

    y_pred = model.predict(diet_X_test)

    for i in range(len(diet_y_test)):
        print("Expected:", diet_y_test[i], "Predicted:", y_pred[i])

    # The mean squared error
    print("Mean squared error: %.2f"
          % mean_squared_error(diet_y_test, y_pred))



# data.isnull().sum()/len(data)*100
# data = data.dropna()
# data_new=data.drop(['Bedroom2','Method','Date','SellerG','Postcode','CouncilArea','Propertycount'],axis=1)