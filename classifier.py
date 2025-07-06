from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.linear_model import LogisticRegression
import pickle

training_data = [
    ("Experinced in Pyhton, SQL, PoweR BI, Excel, and statistics",2),
    ("Fresher with good undersatnding of pyhton and Excel",1),
    ("Basic knowledge of MS Office",0),
    ("Worked on Excel and Google sheets",1),
    ("No technical experince mentioned",0),
    ("Data Analyst with pyhton , SQL , and Tableau",2),
]

texts = [x[0] for x in training_data]
labels = [x[1] for x in training_data]

vectorizer = TfidfVectorizer()
x = vectorizer.fit_transform(texts)

model = LogisticRegression()
model.fit(x,labels)

with open("outputs/model.pkl","wb") as f:
    pickle.dump(model, f)

with open("outputs/vectorizer.pkl","wb") as f:
    pickle.dump(vectorizer, f)



