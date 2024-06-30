import pandas as pd

def clean_data(df):
    # Convert numerical columns to appropriate data types
    df['Votes'] = df['Votes'].str.replace(',', '').astype(int)
    
    # Additional cleaning steps as necessary
    return df

if __name__ == "__main__":
    election_results_df = pd.read_csv('election_results.csv')
    cleaned_df = clean_data(election_results_df)
    cleaned_df.to_csv('cleaned_election_results.csv', index=False)
