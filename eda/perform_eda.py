import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style for seaborn
sns.set_theme(style="whitegrid")

# Load the data
df = pd.read_csv("../global_forest_fire_dataset.csv")

# Create text report
with open("summary_report.txt", "w") as f:
    f.write("Dataset Info:\\n")
    df.info(buf=f)
    f.write("\\n\\nMissing Values:\\n")
    f.write(df.isnull().sum().to_string())
    f.write("\\n\\nDescriptive Statistics:\\n")
    f.write(df.describe().to_string())
    f.write("\\n\\nClass Distribution:\\n")
    f.write((df['Classes'].value_counts(normalize=True).mul(100).round(2).astype(str) + '%').to_string())

print("Generating Class Distribution plot...")
plt.figure(figsize=(8, 6))
sns.countplot(data=df, x='Classes', palette='Set2')
plt.title('Class Distribution (0 = Safe, 1 = Fire)')
plt.savefig('class_distribution.png', bbox_inches='tight')
plt.close()

print("Generating Correlation Heatmap...")
plt.figure(figsize=(10, 8))
# Only correlate numeric columns
numeric_df = df[['Temperature', 'Humidity', 'Wind_Speed', 'Rain', 'Classes']]
corr = numeric_df.corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, fmt=".2f")
plt.title('Correlation Heatmap')
plt.savefig('correlation_heatmap.png', bbox_inches='tight')
plt.close()

print("Generating Temperature vs Classes plot...")
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='Classes', y='Temperature', palette='Set2')
plt.title('Temperature Distribution by Fire Occurrence')
plt.savefig('temperature_vs_fire.png', bbox_inches='tight')
plt.close()

print("Generating Rain vs Classes plot...")
plt.figure(figsize=(10, 6))
sns.violinplot(data=df, x='Classes', y='Rain', palette='Set2')
plt.title('Rain Distribution by Fire Occurrence')
plt.savefig('rain_vs_fire.png', bbox_inches='tight')
plt.close()

print("EDA Complete. Images saved in eda/ folder.")
