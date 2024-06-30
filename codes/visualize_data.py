import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def visualize_data(df):
    plt.figure(figsize=(10, 6))
    sns.countplot(y='Party', data=df, order=df['Party'].value_counts().index)
    plt.title('Number of Seats Won by Each Party')
    plt.show()

if __name__ == "__main__":
    cleaned_df = pd.read_csv('cleaned_election_results.csv')
    visualize_data(cleaned_df)
