import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, GridSearchCV

class BoxOfficePredticion:
    def __init__(self):
        self.df = pd.read_csv("Final_data.csv")
        self.database = pd.read_csv("search_data.csv")
        self.database = self.database.drop(columns=['Unnamed: 0'])
        self.database.primaryTitle= self.database.primaryTitle.str.lower()
        self.preprocessing()
        self.modeling()
    
    def get_tconst(self,movie_name):
        movie = self.database[self.database.primaryTitle == movie_name]
        if len(movie) == 0:
            return ""
        else:
            return movie.tconst.iloc[0]
        
    def get_movie(self, tconst):
        data = self.database[self.database.tconst == tconst] # Hossam Galal
        data = data.drop(columns=['tconst','primaryTitle'])
        print(data)
        data = data.values
        return self.predict(data)
    
    def preprocessing(self):
        self.df = self.df[['startYear','runtimeMinutes','genres','world_revenue','averageRating','numVotes']]                                 # Hossam Galal
        self.df.genres  = self.df.genres.apply(lambda x: x.split(",")[0])
        self.df = pd.get_dummies(self.df,prefix=['genres'], columns = ['genres'], drop_first=True)
        self.df = self.df[self.df.runtimeMinutes < 300]
        self.df = self.df[self.df.startYear > 2000]
        self.df = self.df[self.df.world_revenue > 1e4]
    

    def modeling(self):
        X = self.df.drop(['world_revenue'], axis=1).values
        y = self.df.world_revenue.values
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2, random_state=42)
        parm_grid = {
            'min_samples_split':[6],
            'min_samples_leaf':[4],
            'n_jobs':[-1],
            'min_impurity_decrease':[0.25],
            'max_features':['auto'],
            'random_state':[42]
        }
        model = RandomForestRegressor()
        self.model_cv = GridSearchCV(model, param_grid = parm_grid, cv=10)
        self.model_cv.fit(X_train, y_train)

    def predict(self, data):
        print(data)
        y = self.model_cv.predict(data)
        return y
    
