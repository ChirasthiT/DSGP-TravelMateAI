import pandas as pd
import spacy
from keybert import KeyBERT

#spaCy NER
nlp = spacy.load("en_core_web_sm")
#KeyBERT
kw_model = KeyBERT()

def extract_spacy_ner(text):
   doc = nlp(text)
   return [ent.text for ent in doc.ents]

def extract_keybert_keywords(text, top_n=5):
   keywords = kw_model.extract_keywords(text, top_n=top_n)
   return [kw[0] for kw in keywords]

def process_keywords(input_csv, output_csv):
   df = pd.read_csv(input_csv)

   df['spaCy_NER'] = df['Phrases'].apply(extract_spacy_ner)
   df['KeyBERT'] = df['Phrases'].apply(lambda x: extract_keybert_keywords(x, top_n=5))

   df.to_csv(output_csv, index=False)
   print(f" Extracted keywords saved to {output_csv}")

if __name__ == "__main__":
   input_csv = "../data/cleaned_EmPh_full.csv"
   output_csv = "../data/keywords_extracted.csv"

   process_keywords(input_csv, output_csv)