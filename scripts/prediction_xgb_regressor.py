# prediction_xgb_regressor.py
"""
Grade Prediction using XGBoost Regressor
Interactive dashboard for predicting student grades.
Enhanced with student encoding and performance history.
"""

import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.feature_selection import SelectKBest, f_regression
import numpy as np

# Load CSV
df = pd.read_csv('data/output/unificado_final_anonimo.csv', encoding='utf-8-sig')
df['Nota'] = pd.to_numeric(df['Nota'], errors='coerce')
df = df.dropna(subset=['Nota'])

# Map semesters to numbers for ordering
semester_map = {
    'QUINTO': 5, 'SEXTO': 6, 'SEPTIMO': 7, 'OCTAVO': 8, 'NOVENO': 9, 'DECIMO': 10
}
df['Semestre_num'] = df['Semestre'].map(semester_map)

# Encode categoricals
le_materia = LabelEncoder()
le_semestre = LabelEncoder()
le_estudiante = LabelEncoder()
df['Materia_cod'] = le_materia.fit_transform(df['Materia'])
df['Semestre_cod'] = le_semestre.fit_transform(df['Semestre'])
df['Estudiante_cod'] = le_estudiante.fit_transform(df['Nombre_del_estudiante'])

# Add historical features
def add_historical_features(df):
    df = df.sort_values(['Nombre_del_estudiante', 'Semestre_num', 'Materia'])
    df['Hist_avg_grade'] = df.groupby('Nombre_del_estudiante')['Nota'].transform(lambda x: x.expanding().mean().shift(1))
    df['Hist_subject_count'] = df.groupby('Nombre_del_estudiante').cumcount()
    df['Hist_avg_grade'] = df['Hist_avg_grade'].fillna(df['Nota'].mean())  # Impute with global mean for sparsity
    df['Hist_subject_count'] = df['Hist_subject_count'].fillna(0)
    return df

df = add_historical_features(df)

# Features
X = df[['Semestre_cod', 'Materia_cod', 'Estudiante_cod', 'Hist_avg_grade', 'Hist_subject_count']]
y = df['Nota']

# Feature selection to handle sparsity
selector = SelectKBest(score_func=f_regression, k='all')
X_selected = selector.fit_transform(X, y)

# Train XGBoost with cross-validation
X_train, X_test, y_train, y_test = train_test_split(X_selected, y, test_size=0.2, random_state=42)

model = xgb.XGBRegressor(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=5,
    random_state=42,
    reg_lambda=1.0  # L2 regularization for sparsity
)
cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
print(f"Cross-validation R² scores: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")

model.fit(X_train, y_train)
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"Test MSE: {mse:.3f}, R²: {r2:.3f}")
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
        sem_num = semester_map[sem_futuro]
        est_cod = le_estudiante.transform([est])[0]
        sem_cod = le_semestre.transform([sem_futuro])[0]
        mat_cod = le_materia.transform([mat])[0]

        # Compute historical features
        df_est_hist = df_est[df_est['Semestre_num'] < sem_num]
        hist_avg = df_est_hist['Nota'].mean() if not df_est_hist.empty else df['Nota'].mean()
        hist_count = len(df_est_hist)

        # Features for prediction
        features = np.array([[sem_cod, mat_cod, est_cod, hist_avg, hist_count]])
        features_selected = selector.transform(features)

        pred = model.predict(features_selected)[0]
        print(f"\nGrade prediction in '{mat}' for semester '{sem_futuro}': {pred:.1f}")
        print(f"  (Based on historical avg: {hist_avg:.2f}, subjects: {hist_count} - XGBoost model)")

        if pred < 7:
            print("⚠️ ALERT: Low prediction (<7) → possible low performance risk")
        elif pred >= 9:
            print("✅ High prediction → good expected performance")

boton.on_click(on_click)

# Display
display(estudiante_dd, semestre_futuro_dd, materia_dd, boton, output)