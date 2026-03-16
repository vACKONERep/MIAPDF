import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import shap
import lime
import lime.lime_tabular
import numpy as np


# Carga el CSV (ajusta la ruta si es necesario)
df = pd.read_csv(r'C:\Users\juan.carrillo\PDFintoCSV\data\output\unificado_final_anonimo.csv', encoding='utf-8-sig')
df['Nota'] = pd.to_numeric(df['Nota'], errors='coerce')
df = df.dropna(subset=['Nota'])

# Crear categorías de riesgo: Baja (<6), Media (6-8), Alta (≥8)
def categorize_risk(nota):
    if nota < 6:
        return 'Baja'
    elif nota < 8:
        return 'Media'
    else:
        return 'Alta'

df['Riesgo'] = df['Nota'].apply(categorize_risk)

# Codificar categóricas
le_materia = LabelEncoder()
le_semestre = LabelEncoder()
le_riesgo = LabelEncoder()

df['Materia_cod'] = le_materia.fit_transform(df['Materia'])
df['Semestre_cod'] = le_semestre.fit_transform(df['Semestre'])
df['Riesgo_cod'] = le_riesgo.fit_transform(df['Riesgo'])

# Features y target
X = df[['Semestre_cod', 'Materia_cod']]
y_coded = df['Riesgo_cod']  # Usamos códigos numéricos para el modelo

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_coded, test_size=0.2, random_state=42, stratify=y_coded
)

# Modelo
model = RandomForestClassifier(n_estimators=100, random_state=42)
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
# SHAP - Versión ultra-diagnóstica y corregida
# ────────────────────────────────────────────────

print("\n--- Generando Gráficos SHAP ---")

explainer = shap.TreeExplainer(model)

print("Calculando shap_values...")
shap_values = explainer.shap_values(X_test)

print("\nTipo de shap_values:", type(shap_values))
print("Longitud si es lista:", len(shap_values) if isinstance(shap_values, list) else "No es lista")

if isinstance(shap_values, list):
    for idx, sv in enumerate(shap_values):
        print(f"shap_values[{idx}].shape = {sv.shape}  (dtype: {sv.dtype})")
else:
    print("shap_values.shape =", shap_values.shape)

# Usamos numpy para consistencia
X_test_np = X_test.values
print("X_test_np.shape =", X_test_np.shape)

class_names = le_riesgo.classes_
print("Clases:", class_names)

# Intentamos graficar solo si shapes son coherentes
if isinstance(shap_values, list) and len(shap_values) == len(class_names):
    for i, cls in enumerate(class_names):
        print(f"\n→ Intentando SHAP Summary para clase '{cls}'")
        
        sv_class = shap_values[i]
        print(f"  sv_class.shape original = {sv_class.shape}")
        
        if sv_class.ndim == 2 and sv_class.shape[1] == 3:  # (samples, features+1)
            sv_class = sv_class[:, :-1]
            print(f"  → Corte bias aplicado, nuevo shape = {sv_class.shape}")
        
        if sv_class.shape[0] != X_test_np.shape[0]:
            print(f"  ERROR: Filas no coinciden → SHAP {sv_class.shape[0]} vs X_test {X_test_np.shape[0]}")
            print("  → Posible bug en SHAP o datos corruptos. Saltando gráfico.")
            continue
        
        try:
            shap.summary_plot(
                sv_class,
                X_test_np,
                feature_names=['Semestre_cod', 'Materia_cod'],
                show=False
            )
            plt.title(f"SHAP Summary - Clase: {cls}")
            plt.show()
        except Exception as e:
            print(f"  Falló al graficar: {str(e)}")
else:
    print("Formato de shap_values inesperado → no se puede graficar summary por clase.")

# ────────────────────────────────────────────────
# LIME
# ────────────────────────────────────────────────

print("\n--- Generando Gráfico LIME ---")

explainer_lime = lime.lime_tabular.LimeTabularExplainer(
    training_data=X_train.values,
    feature_names=['Semestre_cod', 'Materia_cod'],
    class_names=class_names,
    mode='classification'
)

instance_idx_lime = np.random.randint(0, len(X_test_np))
X_instance_lime = X_test_np[instance_idx_lime]
y_true_coded = y_test.iloc[instance_idx_lime]
y_true_label = le_riesgo.inverse_transform([y_true_coded])[0]

print(f"\nExplicando instancia:\nSemestre_cod: {X_instance_lime[0]}, Materia_cod: {X_instance_lime[1]}")
print(f"Riesgo real: {y_true_label}")

explanation = explainer_lime.explain_instance(
    data_row=X_instance_lime,
    predict_fn=model.predict_proba,
    num_features=2
)

print("Explicación LIME (texto):")
print(explanation.as_list())

print("\nGráfico LIME:")
explanation.as_pyplot_figure()
plt.show()
# Si show_in_notebook no funciona bien, el pyplot_figure es más confiable