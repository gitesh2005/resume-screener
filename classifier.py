import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# ✅ Make sure outputs folder exists
os.makedirs("outputs", exist_ok=True)

# ✅ Training data (label: 0 = Weak, 1 = Moderate, 2 = Strong)
training_data = [
    ("Experienced in Python, SQL, Power BI, Excel, and statistics", 2),
    ("Fresher with good understanding of Python and Excel", 1),
    ("Basic knowledge of MS Office", 0),
    ("Worked on Excel and Google Sheets", 1),
    ("No technical experience mentioned", 0),
    ("Data Analyst with Python, SQL, and Tableau", 2),
]

# ✅ Split data
texts = [text for text, label in training_data]
labels = [label for text, label in training_data]

# ✅ TF-IDF Vectorizer
vectorizer = TfidfVectorizer(lowercase=True, stop_words="english")
x = vectorizer.fit_transform(texts)

# ✅ Logistic Regression model
model = LogisticRegression()
model.fit(x, labels)

# ✅ Save model & vectorizer
with open("outputs/model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("outputs/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)
