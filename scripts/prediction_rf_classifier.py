# prediction_rf_classifier.py
"""
Risk Prediction using Random Forest Classifier
Interactive dashboard for predicting grade risk categories.
"""

import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load CSV
df = pd.read_csv('data/output/batch_extracted_data.csv', encoding='utf-8-sig')
df['nota_total'] = pd.to_numeric(df['nota_total'], errors='coerce')
df = df.dropna(subset=['nota_total'])

# Rename
df.rename(columns={'nota_total': 'Nota', 'Rotacion': 'Materia'}, inplace=True)

# Categorize risk
def categorize_risk(nota):
    if nota < 6:
        return 'Baja'
    elif nota < 8:
        return 'Media'
    else:
        return 'Alta'

df['Riesgo'] = df['Nota'].apply(categorize_risk)

# Encode
le_materia = LabelEncoder()
le_semestre = LabelEncoder()
df['Materia_cod'] = le_materia.fit_transform(df['Materia'])
df['Semestre_cod'] = le_semestre.fit_transform(df['Semestre'])

# Train
X = df[['Semestre_cod', 'Materia_cod']]
y = df['Riesgo']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

acc = accuracy_score(y_test, y_pred)
print(f"Model accuracy: {acc * 100:.1f}%")

# Widgets
estudiante_dd = widgets.Dropdown(
    options=sorted(df['Nombre_del_estudiante'].unique()),
    description='Estudiante:',
    value=df['Nombre_del_estudiante'].unique()[0]
)

semestre_dd = widgets.Dropdown(
    options=sorted(df['Semestre'].unique().tolist()),
    description='Semestre futuro:',
)

materia_dd = widgets.Dropdown(
    options=sorted(df['Materia'].unique().tolist()),
    description='Materia a predecir:',
)

boton = widgets.Button(description="Predecir riesgo")

output = widgets.Output()

def on_click(b):
    with output:
        clear_output()
        est = estudiante_dd.value
        sem = semestre_dd.value
        mat = materia_dd.value

        # Historical
        df_est = df[df['Nombre_del_estudiante'] == est]
        if df_est.empty:
            print(f"No grades for {est}")
            return

        print(f"\nReal grades of {est}:")
        display(df_est[['Semestre', 'Materia', 'Nota', 'Riesgo']].sort_values(['Semestre', 'Materia']))
        prom = df_est['Nota'].mean()
        print(f"Historical average: {prom:.2f}")

        # Risk distribution chart
        plt.figure(figsize=(6, 4))
        df_est['Riesgo'].value_counts().plot(kind='pie', autopct='%1.1f%%', colors=['red', 'yellow', 'green'])
        plt.title(f"Historical risk of {est}")
        plt.ylabel('')
        plt.tight_layout()
        plt.show()

        # Prediction
        sem_cod = le_semestre.transform([sem])[0]
        mat_cod = le_materia.transform([mat])[0]

        pred = model.predict([[sem_cod, mat_cod]])[0]
        prob = max(model.predict_proba([[sem_cod, mat_cod]])[0]) * 100

        print(f"\nRisk prediction in '{mat}': {pred}")
        print(f"  (Probability of this category: {prob:.1f}% - Random Forest Classifier trained with all historical grades)")

        if pred == 'Baja':
            print("⚠️ ALERT: Low grade risk (<6)")
        elif pred == 'Media':
            print("🟡 Medium risk (6-8)")
        else:
            print("✅ Low risk - high grade expected (≥8)")

boton.on_click(on_click)

# Display
display(estudiante_dd, semestre_dd, materia_dd, boton, output)