# prediction_xgb_classifier.py
"""
Risk Prediction using XGBoost Classifier
Interactive dashboard for predicting grade risk categories.
"""

import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Load CSV
csv_path = 'data/output/batch_extracted_data.csv'  # Adjust if needed
df = pd.read_csv(csv_path, encoding='utf-8-sig')
df['nota_total'] = pd.to_numeric(df['nota_total'], errors='coerce')
df = df.dropna(subset=['nota_total'])

# Rename
df.rename(columns={'nota_total': 'Nota', 'Rotacion': 'Materia'}, inplace=True)

# Categorize risk
def categorize_risk(nota):
    if nota < 6:
        return 0  # Baja
    elif nota < 8:
        return 1  # Media
    else:
        return 2  # Alta

df['Riesgo'] = df['Nota'].apply(categorize_risk)

# Encode
le_materia = LabelEncoder()
le_semestre = LabelEncoder()
df['Materia_cod'] = le_materia.fit_transform(df['Materia'])
df['Semestre_cod'] = le_semestre.fit_transform(df['Semestre'])

# Train XGBoost Classifier
X = df[['Semestre_cod', 'Materia_cod']]
y = df['Riesgo']

model = xgb.XGBClassifier(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=5,
    random_state=42,
    objective='multi:softprob',
    num_class=3
)
model.fit(X, y)

print("XGBoost Classifier model trained successfully.")

# Widgets
estudiante_dd = widgets.Dropdown(
    options=sorted(df['Nombre_del_estudiante'].unique()),
    description='Estudiante:',
    value=df['Nombre_del_estudiante'].unique()[0]
)

semestre_futuro_dd = widgets.Dropdown(
    options=sorted(df['Semestre'].unique().tolist()),
    description='Semestre futuro:',
    value=df['Semestre'].max()
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
        sem_futuro = semestre_futuro_dd.value
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

        # Chart
        plt.figure(figsize=(6, 4))
        df_est['Riesgo'].value_counts().plot(kind='pie', autopct='%1.1f%%', colors=['red', 'yellow', 'green'])
        plt.title(f"Historical risk of {est}")
        plt.ylabel('')
        plt.tight_layout()
        plt.show()

        # Prediction
        sem_cod = le_semestre.transform([sem_futuro])[0]
        mat_cod = le_materia.transform([mat])[0]

        pred = model.predict([[sem_cod, mat_cod]])[0]
        prob = model.predict_proba([[sem_cod, mat_cod]])[0]
        prob_max = max(prob) * 100

        riesgo_labels = {0: 'Baja (<6)', 1: 'Media (6-8)', 2: 'Alta (≥8)'}
        pred_label = riesgo_labels[pred]

        print(f"\nRisk prediction in '{mat}': {pred_label}")
        print(f"  Probability of this category: {prob_max:.1f}%")
        print("  (XGBoost Classifier trained with all historical grades)")

        if pred == 0:
            print("⚠️ ALERT: Low grade risk (<6)")
        elif pred == 1:
            print("🟡 Medium risk (6-8)")
        else:
            print("✅ Low risk - high grade expected (≥8)")

boton.on_click(on_click)

# Display
display(estudiante_dd, semestre_futuro_dd, materia_dd, boton, output)