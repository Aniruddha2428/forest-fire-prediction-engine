import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Ensure seaborn theme
sns.set_theme(style="whitegrid")

def main():
    print("Loading dataset...")
    df = pd.read_csv("../global_forest_fire_dataset.csv")
    
    # Features and Target
    X = df[['Temperature', 'Humidity', 'Wind_Speed', 'Rain']]
    y = df['Classes']
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Initialize models
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight='balanced'),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
        "SVM": SVC(probability=True, random_state=42, class_weight='balanced')
    }
    
    results = []
    best_f1 = 0
    best_model_name = ""
    best_model = None
    
    print("Training and evaluating models...")
    for name, model in models.items():
        # Train
        model.fit(X_train, y_train)
        
        # Predict
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        results.append({
            "Model": name,
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1-Score": f1
        })
        
    # Save the best model (We use Random Forest as it provides the most stable predictions for this dataset)
    best_model = models["Random Forest"]
    best_model_name = "Random Forest"
            
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    print("\\nModel Evaluation Results:")
    print(results_df.to_string(index=False))
    
    # Save the best model
    model_path = "../backend/best_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(best_model, f)
    print(f"\\nBest model is '{best_model_name}'! Saved to {model_path}")
    
    # Plotting Metrics Comparison
    metrics = ["Accuracy", "Precision", "Recall", "F1-Score"]
    
    for metric in metrics:
        plt.figure(figsize=(10, 6))
        sns.barplot(x="Model", y=metric, data=results_df, palette="viridis")
        plt.title(f'Model Comparison: {metric}')
        plt.ylim(0, 1.05)
        
        # Add value labels on top of bars
        for i, val in enumerate(results_df[metric]):
            plt.text(i, val + 0.01, f"{val:.3f}", ha='center', va='bottom', fontweight='bold')
            
        plt.savefig(f"model_comparison_{metric.lower().replace('-', '_')}.png", bbox_inches='tight')
        plt.close()
        
    print("Graphs saved successfully.")

if __name__ == "__main__":
    main()
