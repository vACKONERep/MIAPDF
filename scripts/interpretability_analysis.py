import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
from sklearn.feature_selection import SelectKBest, f_classif
import shap
import lime
import lime.lime_tabular
import numpy as np
import os

# Load CSV
df = pd.read_csv(r'C:\Users\juan.carrillo\PDFintoCSV\data\output\unificado_final_anonimo.csv', encoding='utf-8-sig')
df['Nota'] = pd.to_numeric(df['Nota'], errors='coerce')
df = df.dropna(subset=['Nota'])

# Map semesters to numbers for ordering
semester_map = {
    'QUINTO': 5, 'SEXTO': 6, 'SEPTIMO': 7, 'OCTAVO': 8, 'NOVENO': 9, 'DECIMO': 10
}
df['Semestre_num'] = df['Semestre'].map(semester_map)

# Categorize risk
def categorize_risk(nota):
    if nota < 6:
        return 'Baja'
    elif nota < 8:
        return 'Media'
    else:
        return 'Alta'

df['Riesgo'] = df['Nota'].apply(categorize_risk)

# Encode categoricals
le_materia = LabelEncoder()
le_semestre = LabelEncoder()
le_estudiante = LabelEncoder()
le_riesgo = LabelEncoder()

df['Materia_cod'] = le_materia.fit_transform(df['Materia'])
df['Semestre_cod'] = le_semestre.fit_transform(df['Semestre'])
df['Estudiante_cod'] = le_estudiante.fit_transform(df['Nombre_del_estudiante'])
df['Riesgo_cod'] = le_riesgo.fit_transform(df['Riesgo'])

# Add historical features
def add_historical_features(df):
    df = df.sort_values(['Nombre_del_estudiante', 'Semestre_num', 'Materia'])
    df['Hist_avg_grade'] = df.groupby('Nombre_del_estudiante')['Nota'].transform(lambda x: x.expanding().mean().shift(1))
    df['Hist_subject_count'] = df.groupby('Nombre_del_estudiante').cumcount()
    df['Hist_avg_grade'] = df['Hist_avg_grade'].fillna(df['Nota'].mean())  # Impute with global mean for sparsity
    df['Hist_subject_count'] = df['Hist_subject_count'].fillna(0)
    return df

df = add_historical_features(df)

# Features and target
X = df[['Semestre_cod', 'Materia_cod', 'Estudiante_cod', 'Hist_avg_grade', 'Hist_subject_count']]
y_coded = df['Riesgo_cod']

# Feature selection to handle sparsity
selector = SelectKBest(score_func=f_classif, k='all')
X_selected = selector.fit_transform(X, y_coded)

# Get selected feature names
selected_features = X.columns[selector.get_support()].tolist()

# Train/test split with cross-validation
X_train, X_test, y_train, y_test = train_test_split(
    X_selected, y_coded, test_size=0.2, random_state=42, stratify=y_coded
)

# Model with regularization
model = RandomForestClassifier(n_estimators=200, random_state=42, max_depth=10)
cv_scores = cross_val_score(model, X_train, y_train, cv=5)
print(f"Cross-validation accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")

model.fit(X_train, y_train)
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Model accuracy: {acc * 100:.1f}%")
print(classification_report(y_test, y_pred))
model.fit(X_train, y_train)

# Evaluación
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Precisión del modelo: {acc * 100:.1f}%")

# Widgets para predicción interactiva (comentado para ejecución en terminal)
# estudiante_dd = widgets.Dropdown(
#     options=sorted(df['Nombre_del_estudiante'].unique()),
#     description='Estudiante:',
#     value=df['Nombre_del_estudiante'].unique()[0]
# )

# semestre_dd = widgets.Dropdown(
#     options=sorted(df['Semestre'].unique().tolist()),
#     description='Semestre futuro:'
# )

# materia_dd = widgets.Dropdown(
#     options=sorted(df['Materia'].unique().tolist()),
#     description='Materia a predecir:'
# )

# boton = widgets.Button(description="Predecir riesgo")
# output = widgets.Output()

# def on_click(b):
#     with output:
#         clear_output()
#         est = estudiante_dd.value
#         sem = semestre_dd.value
#         mat = materia_dd.value

#         df_est = df[df['Nombre_del_estudiante'] == est]
#         if df_est.empty:
#             print(f"No hay notas para {est}")
#             return

#         print(f"\nNotas reales de {est}:")
#         display(df_est[['Semestre', 'Materia', 'Nota', 'Riesgo']].sort_values(['Semestre', 'Materia']))
#         prom = df_est['Nota'].mean()
#         print(f"Promedio histórico: {prom:.2f}")

#         # Gráfico histórico
#         plt.figure(figsize=(6, 4))
#         df_est['Riesgo'].value_counts().plot(kind='pie', autopct='%1.1f%%', colors=['red', 'yellow', 'green'])
#         plt.title(f"Riesgo histórico de {est}")
#         plt.ylabel('')
#         plt.tight_layout()
#         plt.show()

#         # Predicción
#         sem_cod = le_semestre.transform([sem])[0]
#         mat_cod = le_materia.transform([mat])[0]

#         pred_coded = model.predict([[sem_cod, mat_cod]])[0]
#         pred_label = le_riesgo.inverse_transform([pred_coded])[0]
        
#         prob = model.predict_proba([[sem_cod, mat_cod]])[0]
#         prob_max = max(prob) * 100

#         print(f"\nPredicción de riesgo en '{mat}': {pred_label}")
#         print(f"  (Probabilidad: {prob_max:.1f}%)")

#         if pred_label == 'Baja':
#             print("⚠️ ALERTA: Riesgo de nota baja (<6)")
#         elif pred_label == 'Media':
#             print("🟡 Riesgo medio (6-8)")
#         else:
#             print("✅ Riesgo bajo - nota alta esperada (≥8)")

# boton.on_click(on_click)
# display(estudiante_dd, semestre_dd, materia_dd, boton, output)

# ────────────────────────────────────────────────
# SHAP - Simplified and Robust Version
# ────────────────────────────────────────────────

print("\n--- Generando Gráficos SHAP ---")

# Create output directory
os.makedirs('interpretability_plots', exist_ok=True)

# Use TreeExplainer for Random Forest
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

print(f"Type of shap_values: {type(shap_values)}")
if isinstance(shap_values, list):
    print(f"SHAP values is list with {len(shap_values)} elements")
    for i, sv in enumerate(shap_values):
        print(f"  shap_values[{i}].shape = {sv.shape}")
else:
    print(f"shap_values.shape = {shap_values.shape}")

# Handle different SHAP output formats
if isinstance(shap_values, list):
    # Multi-class case - take the first class or average across classes
    if len(shap_values) > 1:
        # For multi-class, shap_values is list of arrays, each (n_samples, n_features)
        shap_values_to_plot = shap_values[1]  # Use class 1 (Media) as example
    else:
        shap_values_to_plot = shap_values[0]
elif shap_values.ndim == 3:
    # 3D array case: (n_samples, n_features, n_classes)
    shap_values_to_plot = shap_values[:, :, 1]  # Take class 1 (Media)

# 1. Global Feature Importance Bar Plot
plt.figure(figsize=(10, 6))
feature_names = selected_features
importance = np.abs(shap_values_to_plot).mean(axis=0)  # Mean across samples
plt.bar(feature_names, importance)
plt.title('Importancia Global de Features (SHAP)')
plt.ylabel('Importancia Media |SHAP|')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('interpretability_plots/shap_global_importance.png', dpi=300, bbox_inches='tight')
plt.show()

# 2. SHAP Summary Plot
plt.figure(figsize=(10, 6))
if shap_values.ndim == 3:
    # For 3D shap_values, use shap.summary_plot with the 2D slice
    shap.summary_plot(shap_values_to_plot, X_test, feature_names=selected_features, show=False)
else:
    shap.summary_plot(shap_values_to_plot, X_test, feature_names=selected_features, show=False)
plt.title('SHAP Summary Plot')
plt.tight_layout()
plt.savefig('interpretability_plots/shap_summary.png', dpi=300, bbox_inches='tight')
plt.show()

# 3. SHAP Waterfall Plot for first instance
if len(X_test) > 0:
    plt.figure(figsize=(10, 6))
    # Create explanation object for waterfall
    if shap_values.ndim == 3:
        # For 3D case, take values for one class
        values_for_instance = shap_values[0, :, 1]  # First instance, all features, class 1
        base_value = explainer.expected_value[1] if hasattr(explainer.expected_value, '__len__') else explainer.expected_value
    else:
        values_for_instance = shap_values_to_plot[0]
        base_value = explainer.expected_value
    
    exp = shap.Explanation(
        values=values_for_instance,
        base_values=base_value,
        data=X_test[0],
        feature_names=selected_features
    )
    shap.waterfall_plot(exp, show=False)
    plt.title('SHAP Waterfall Plot - Primera Instancia')
    plt.tight_layout()
    plt.savefig('interpretability_plots/shap_waterfall.png', dpi=300, bbox_inches='tight')
    plt.show()

print("✅ Gráficos SHAP generados y guardados en 'interpretability_plots/'")

# ────────────────────────────────────────────────
# LIME - Local Explanations
# ────────────────────────────────────────────────

print("\n--- Generando Explicación LIME ---")

# LIME Explainer
lime_explainer = lime.lime_tabular.LimeTabularExplainer(
    training_data=X_train,
    feature_names=selected_features,
    class_names=le_riesgo.classes_,
    mode='classification'
)

# Explain a random instance
instance_idx = np.random.randint(0, len(X_test))
instance = X_test[instance_idx]
true_label = le_riesgo.inverse_transform([y_test.iloc[instance_idx]])[0]

print(f"Explicando instancia {instance_idx}:")
print(f"Features: {dict(zip(selected_features, instance))}")
print(f"Etiqueta real: {true_label}")

# Generate LIME explanation
explanation = lime_explainer.explain_instance(
    data_row=instance,
    predict_fn=model.predict_proba,
    num_features=len(selected_features)
)

# Show text explanation
print("\nExplicación LIME:")
for feature, weight in explanation.as_list():
    print(f"  {feature}: {weight:.3f}")

# Show plot
plt.figure(figsize=(10, 6))
explanation.as_pyplot_figure()
plt.title(f'LIME Explanation - Instancia {instance_idx}')
plt.tight_layout()
plt.savefig('interpretability_plots/lime_explanation.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ Explicación LIME generada y guardada")
plt.show()
# Si show_in_notebook no funciona bien, el pyplot_figure es más confiable