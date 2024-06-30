import pandas as pd

def analyze_data(df):
    insights = {}

    # Insight 1: Total number of seats contested
    insights['total_seats'] = df['Constituency'].nunique()

    # Insight 2: Total number of votes cast
    insights['total_votes'] = df['Votes'].sum()

    # Insight 3: Party-wise number of seats won
    insights['party_wise_seats'] = df.groupby('Party')['Constituency'].count().to_dict()

    # Insight 4: Candidate with the highest number of votes
    insights['top_candidate_votes'] = df.loc[df['Votes'].idxmax()]['Candidate']

    # Insight 5: Average number of votes per constituency
    insights['avg_votes_per_constituency'] = df.groupby('Constituency')['Votes'].mean().mean()

    # Insight 6: Number of constituencies won by margin greater than 10,000 votes
    df['Vote Margin'] = df['Votes'] - df['Votes'].shift(-1)
    insights['constituencies_margin_gt_10000'] = df[df['Vote Margin'] > 10000]['Constituency'].nunique()

    # Insight 7: Party with the highest average votes per candidate
    insights['party_highest_avg_votes'] = df.groupby('Party')['Votes'].mean().idxmax()

    # Insight 8: Total number of candidates
    insights['total_candidates'] = df['Candidate'].nunique()

    # Insight 9: Top 5 parties by total votes received
    insights['top_5_parties_by_votes'] = df.groupby('Party')['Votes'].sum().nlargest(5).to_dict()

    # Insight 10: Percentage of votes won by the winning candidate in each constituency
    df['Vote Percentage'] = (df['Votes'] / df.groupby('Constituency')['Votes'].transform('sum')) * 100
    insights['avg_vote_percentage_winning_candidate'] = df.groupby('Constituency').first()['Vote Percentage'].mean()

    return insights

if __name__ == "__main__":
    cleaned_df = pd.read_csv('cleaned_election_results.csv')
    insights = analyze_data(cleaned_df)
    print(insights)
