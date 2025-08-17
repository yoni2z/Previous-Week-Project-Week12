import pandas as pd
import glob
import logging

logging.basicConfig(filename='logs/preprocessor.log', level=logging.INFO)

def preprocess_reviews():
    # Load all raw CSVs
    all_files = glob.glob('data/raw/*.csv')
    df_list = [pd.read_csv(file) for file in all_files if pd.read_csv(file).shape[0] > 0]  # Skip empty
    if not df_list:
        logging.error("No raw data found.")
        return None
    
    df = pd.concat(df_list, ignore_index=True)
    
    # Preprocess
    df.drop_duplicates(subset=['review_text', 'date'], inplace=True)
    df.dropna(subset=['review_text', 'rating'], inplace=True)
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')  # Normalize
    
    # Save
    output = 'data/processed/all_banks_reviews_clean.csv'
    df.to_csv(output, index=False)
    logging.info(f"Processed {len(df)} reviews to {output}")
    return output

if __name__ == "__main__":
    preprocess_reviews()