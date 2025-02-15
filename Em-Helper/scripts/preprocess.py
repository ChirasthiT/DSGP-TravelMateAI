import pandas as pd
import re

def clean_text(text):
   text = str(text).lower()
   text = re.sub(r'[^\w\s]', '', text)  #punctuations
   text = re.sub(r'\s+', ' ', text).strip()  #extra spaces
   return text

def preprocess_dataset(input_csv, output_csv):
   df = pd.read_csv(input_csv)

   if 'Phrases' not in df.columns:
       raise ValueError("The dataset does not contain a 'Phrases' column")

   columns_to_drop = ['Keywords from survey', 'Situations']
   df = df.drop(columns=[col for col in columns_to_drop if col in df.columns], errors='ignore')

   df['Phrases'] = df['Phrases'].apply(clean_text)

   df.to_csv(output_csv, index=False)
   print(f" Cleaned dataset saved as {output_csv}")

if __name__ == "__main__":
   input_csv = "../data/EmPh_full.csv"
   output_csv = "../data/cleaned_EmPh_full.csv"

   preprocess_dataset(input_csv, output_csv)