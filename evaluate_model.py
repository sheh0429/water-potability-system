import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

print("--- Starting ML Evaluation ---")

# 1. Load the Model
try:
    rf_model = joblib.load("random_forest_sibu.pkl")
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    exit()

# 2. Load Testing Data
# IMPORTANT: Replace 'sibu_water_dataset.csv' with your actual testing data file
try:
    df = pd.read_csv("sibu_water_dataset.csv")

    # Assuming 'Potability' is your target column (1 = Safe, 0 = Unsafe)
    # Adjust column names if your dataset differs
    X_test = df.drop('Potability', axis=1)
    y_test = df['Potability']
except Exception as e:
    print(f"Error loading testing data: {e}")
    exit()

# 3. Generate Predictions
print("Generating predictions...")
y_pred = rf_model.predict(X_test)

# 4. Calculate Core Metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print("\n--- Final Model Metrics ---")
print(f"Accuracy:  {accuracy:.4f} (Overall correctness)")
print(f"Precision: {precision:.4f} (When it says Safe, how often is it actually Safe?)")
print(f"Recall:    {recall:.4f} (Out of all Safe water, how much did it find?)")
print(f"F1-Score:  {f1:.4f} (Balance of Precision and Recall)")

# 5. Generate Confusion Matrix Visualization
print("\nGenerating Visualizations...")
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Unsafe', 'Safe'],
            yticklabels=['Unsafe', 'Safe'])
plt.title('Random Forest Confusion Matrix')
plt.ylabel('Actual Potability')
plt.xlabel('Predicted Potability')
plt.savefig('confusion_matrix.png', dpi=300, bbox_inches='tight')
print("Saved: confusion_matrix.png")

# 6. Generate Feature Importance Visualization
# This proves to the examiners which factors (pH, Turbidity, etc.) drive the AI's decisions
feature_importances = rf_model.feature_importances_
features = X_test.columns

plt.figure(figsize=(10, 6))
sns.barplot(x=feature_importances, y=features, palette='viridis')
plt.title('Feature Importance in Water Potability Prediction')
plt.xlabel('Relative Importance')
plt.ylabel('Water Quality Parameters')
plt.savefig('feature_importance.png', dpi=300, bbox_inches='tight')
print("Saved: feature_importance.png")
print("--- Evaluation Complete ---")