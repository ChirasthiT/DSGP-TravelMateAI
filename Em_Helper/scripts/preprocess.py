import pandas as pd
import re

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def preprocess_dataset(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    print(f"Missing values:\n{df.isnull().sum()}")
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)

    print(f"Dataset cleaned: {df.shape[0]} rows remaining.")

    if 'Phrases' in df.columns:
        df['Phrases'] = df['Phrases'].apply(clean_text)
    else:
        raise ValueError("The dataset does not contain a 'Phrases' column")

    if 'Risk Level' in df.columns:
        risk_mapping = {"Low": 0, "Medium": 1, "High": 2}
        df["Risk Level"] = df["Risk Level"].map(risk_mapping)
    else:
        raise ValueError("The dataset does not contain a 'Risk Level' column")

    df.to_csv(output_csv, index=False)
    print(f"Cleaned dataset saved as {output_csv}")

if __name__ == "__main__":
   input_csv = "../data/EmPhrasesf.csv"
   output_csv = "../data/cleanedEmPhrasesf.csv"

   preprocess_dataset(input_csv, output_csv)