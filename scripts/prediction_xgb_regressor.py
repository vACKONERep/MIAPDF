# prediction_xgb_regressor.py
"""
Grade Prediction using XGBoost Regressor
Interactive dashboard for predicting student grades.
"""

import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder

# Load CSV
csv_path = 'data/output/batch_extracted_data.csv'  # Adjust if needed
df = pd.read_csv(csv_path, encoding='utf-8-sig')
df['nota_total'] = pd.to_numeric(df['nota_total'], errors='coerce')
df = df.dropna(subset=['nota_total'])

# Rename columns
df.rename(columns={'nota_total': 'Nota', 'Rotacion': 'Materia'}, inplace=True)

# Encode categoricals
le_materia = LabelEncoder()
le_semestre = LabelEncoder()
df['Materia_cod'] = le_materia.fit_transform(df['Materia'])
df['Semestre_cod'] = le_semestre.fit_transform(df['Semestre'])

# Train XGBoost
X = df[['Semestre_cod', 'Materia_cod']]
y = df['Nota']

model = xgb.XGBRegressor(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=5,
    random_state=42
)
model.fit(X, y)

print("XGBoost Regressor model trained successfully.")

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

boton = widgets.Button(description="Predecir nota")

output = widgets.Output()

def on_click(b):
    with output:
        clear_output()
        est = estudiante_dd.value
        sem_futuro = semestre_futuro_dd.value
        mat = materia_dd.value

        # Historical grades
        df_est = df[df['Nombre_del_estudiante'] == est]
        if df_est.empty:
            print(f"No grades for {est}")
            return

        print(f"\nReal grades of {est}:")
        display(df_est[['Semestre', 'Materia', 'Nota']].sort_values(['Semestre', 'Materia']))
        prom = df_est['Nota'].mean()
        print(f"Historical average: {prom:.2f}")

        # Chart
        plt.figure(figsize=(12, 5))
        df_est.plot(kind='bar', x='Materia', y='Nota', legend=False, color='skyblue')
        plt.title(f"Historical grades of {est} - Average: {prom:.2f}")
        plt.ylim(0, 11)
        plt.axhline(y=7, color='red', linestyle='--', label='Threshold 7.0')
        plt.legend()
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

        # Prediction
        sem_cod = le_semestre.transform([sem_futuro])[0]
        mat_cod = le_materia.transform([mat])[0]

        pred = model.predict([[sem_cod, mat_cod]])[0]
        print(f"\nGrade prediction in '{mat}' for semester '{sem_futuro}': {pred:.1f}")
        print("  (XGBoost model trained with all historical grades)")

        if pred < 7:
            print("⚠️ ALERT: Low prediction (<7) → possible low performance risk")
        elif pred >= 9:
            print("✅ High prediction → good expected performance")

boton.on_click(on_click)

# Display
display(estudiante_dd, semestre_futuro_dd, materia_dd, boton, output)