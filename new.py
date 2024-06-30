import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt


def scrape_eci_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: Status code {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', class_='table')

    if not table:
        raise Exception("Could not find the results table on the page")

    data = []
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) == 4:
            party = cols[0].text.strip()
            won = int(cols[1].text.strip())
            leading = int(cols[2].text.strip())
            total = int(cols[3].text.strip())
            party_link = cols[1].find('a')['href']
            data.append({
                'Party': party,
                'Won': won,
                'Leading': leading,
                'Total': total,
                'Link': party_link
            })

    return pd.DataFrame(data)


def scrape_candidate_data(url, party_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch data from {url}: {str(e)}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', class_='table-striped')

    if not table:
        print(f"Could not find the candidate data table on the page: {url}")
        return pd.DataFrame()

    data = []
    rows = table.find_all('tr')

    for row in rows[1:]:
        cols = row.find_all('td')
        if len(cols) >= 5:
            total_votes = cols[3].text.strip().replace(',', '')
            margin = cols[4].text.strip().replace(',', '')

            data.append({
                'Serial Number': cols[0].text.strip(),
                'Constituency': cols[1].text.strip(),
                'Winning Candidate': cols[2].text.strip(),
                'Total Votes': int(total_votes) if total_votes != '-' else 0,
                'Margin': int(margin) if margin != '-' else 0,
                'Party': party_name
            })

    if not data:
        print(f"No data found in the table for URL: {url}")

    return pd.DataFrame(data)


def independent_candidates_won(df):
    independents = df[df['Party'].str.contains('Independent', case=False, na=False)]
    total_independents = independents['Total'].sum()
    plt.figure(figsize=(8, 6))
    bars = plt.bar(['Independent Candidates'], [total_independents])
    plt.title('Number of Independent Candidates Who Won')

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, int(yval), va='bottom',
                 ha='center')

    plt.savefig('independent_candidates_won.png')
    return f"Number of independent candidates who won: {total_independents}"


def overall_election_statistics(df):
    total_seats = df['Total'].sum()
    total_parties = len(df)
    avg_seats = df['Total'].mean()

    stats = ['Total Seats', 'Total Parties', 'Avg Seats per Party']
    values = [total_seats, total_parties, avg_seats]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(stats, values, color='skyblue', edgecolor='black')

    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                 f'{value:.2f}' if isinstance(value, float) else f'{value}',
                 ha='center', va='bottom', fontsize=12)

    plt.title('Overall Election Statistics', fontsize=16)
    plt.ylabel('Count', fontsize=14)
    plt.tight_layout()
    plt.savefig('overall_election_statistics.png')

    return (f"Overall Election Statistics:\n"
            f"Total Seats: {total_seats}\n"
            f"Total Parties: {total_parties}\n"
            f"Average Seats per Party: {avg_seats:.2f}")


def party_size_distribution(df):
    df_filtered = df[df['Party'] != 'Independent - IND']

    size_bins = [0, 2, 6, 11, 51, 101, float('inf')]
    labels = ['1', '2-5', '6-10', '11-50', '51-100', '100+']
    df_filtered['Size Category'] = pd.cut(df_filtered['Total'], bins=size_bins, labels=labels, right=False)

    distribution = df_filtered['Size Category'].value_counts().sort_index()

    plt.figure(figsize=(10, 6))
    ax = distribution.plot(kind='bar', color='skyblue', edgecolor='black')

    for p in ax.patches:
        ax.annotate(str(p.get_height()), (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontsize=12)

    plt.title('Party Size Distribution', fontsize=16)
    plt.xlabel('Number of Seats', fontsize=14)
    plt.ylabel('Number of Parties', fontsize=14)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle=':', linewidth=0.5)
    plt.tight_layout()
    plt.savefig('party_size_distribution.png')

    return f"Party size distribution:\n{distribution.to_string()}"


def forming_government(df):
    total_seats = df['Total'].sum()
    majority = total_seats // 2 + 1
    top_party = df.loc[df['Total'].idxmax()]

    plt.figure(figsize=(18, 12))
    bars = plt.bar(df['Party'], df['Total'], color='skyblue', width=0.6,
                   edgecolor='black')

    plt.bar(top_party['Party'], top_party['Total'], color='orange', label='Likely to form government',
            edgecolor='black')

    plt.axhline(y=majority, color='red', linestyle='--', label='Majority')

    for bar in bars:
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                 f"{int(bar.get_height())}", ha='center', va='bottom')

    plt.ylim(0, max(df['Total']) + 10)  # Increase space above the highest bar
    plt.yticks(range(0, max(df['Total']) + 50, 10))  # Increase y-axis ticks by 10

    plt.title('Forming Government Analysis')
    plt.ylabel('Number of Seats')
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.savefig('forming_government.png')

    if top_party['Total'] >= majority:
        return f"{top_party['Party']} is likely to form the government with {top_party['Total']} seats (Majority: {majority})"
    else:
        return f"No single party has a majority. Coalition government likely. (Majority required: {majority})"


def election_closeness(df):
    top_two = df.nlargest(2, 'Total')
    difference = top_two.iloc[0]['Total'] - top_two.iloc[1]['Total']
    total_seats = df['Total'].sum()
    closeness_percentage = (difference / total_seats) * 100

    plt.figure(figsize=(10, 6))
    bars = plt.bar(top_two['Party'], top_two['Total'])

    for i, bar in enumerate(bars):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                 f"{int(bar.get_height())}", ha='center', va='bottom')

    text_box_y = (max(top_two.iloc[0]['Total'], top_two.iloc[1]['Total']) + min(top_two.iloc[0]['Total'],
                                                                                top_two.iloc[1]['Total'])) / 2
    plt.text(0.5, text_box_y,
             f"Difference: {difference} seats\n({closeness_percentage:.2f}%)", ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="b", lw=1, alpha=0.5))

    plt.title('Election Closeness: Top Two Parties')
    plt.ylabel('Number of Seats')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('election_closeness.png')

    return f"The election was decided by a margin of {difference} seats ({closeness_percentage:.2f}% of total seats)"


def potential_kingmakers(df):
    total_seats = df['Total'].sum()
    majority = total_seats // 2 + 1
    top_party_seats = df['Total'].max()
    kingmakers = df[(df['Total'] > 0) & (df['Total'] < (majority - top_party_seats))]
    kingmakers = kingmakers.sort_values('Total', ascending=False).head()

    plt.figure(figsize=(14, 8))
    bars = plt.bar(kingmakers['Party'], kingmakers['Total'], color='skyblue')

    plt.suptitle(
        'Potential Kingmakers',
        fontsize=16)
    plt.title('( Kingmakers are parties with enough seats to influence the formation of a majority coalition )',
              fontsize=14)
    plt.ylabel('Number of Seats', fontsize=14)
    plt.xlabel('Party', fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(fontsize=12)

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, height, f'{height}', ha='center', va='bottom', fontsize=12)

    plt.tight_layout()
    plt.savefig('potential_kingmakers.png')

    return f"Potential kingmakers:\n{kingmakers[['Party', 'Total']].to_string(index=False)}"


def top_5_candidates_by_votes(candidate_df):
    top_5 = candidate_df.nlargest(5, 'Total Votes')

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(top_5['Winning Candidate'], top_5['Total Votes'])
    ax.set_title("Top 5 Candidates by Total Votes")
    ax.set_ylabel("Total Votes")
    plt.xticks(rotation=45, ha='right')
    for i, v in enumerate(top_5['Total Votes']):
        ax.text(i, v, f'{v:,}', ha='center', va='bottom')
    plt.tight_layout()
    fig.savefig('top_5_candidates_by_votes.png')

    return f"Top 5 candidates by total votes:\n{top_5[['Winning Candidate', 'Party', 'Constituency', 'Total Votes']].to_string(index=False)}"


def least_5_candidates_by_votes(candidate_df):
    bottom_5 = candidate_df.nsmallest(5, 'Total Votes')

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(bottom_5['Winning Candidate'], bottom_5['Total Votes'])
    ax.set_title("Bottom 5 Candidates by Total Votes")
    ax.set_ylabel("Total Votes")
    plt.xticks(rotation=45, ha='right')
    for i, v in enumerate(bottom_5['Total Votes']):
        ax.text(i, v, f'{v:,}', ha='center', va='bottom')
    plt.tight_layout()
    fig.savefig('least_5_candidates_by_votes.png')

    return f"Bottom 5 candidates by total votes:\n{bottom_5[['Winning Candidate', 'Party', 'Constituency', 'Total Votes']].to_string(index=False)}"


def top_5_candidates_by_votes_top_10_parties(df, candidate_df):
    top_10_parties = df.nlargest(10, 'Total')['Party'].tolist()
    results = []
    fig, axs = plt.subplots(5, 2, figsize=(20, 25))
    axs = axs.ravel()

    for i, party in enumerate(top_10_parties):
        party_candidates = candidate_df[candidate_df['Party'] == party]
        top_5 = party_candidates.nlargest(5, 'Total Votes')
        results.append(
            f"\n{party}:\n{top_5[['Winning Candidate', 'Constituency', 'Total Votes']].to_string(index=False)}")

        axs[i].bar(top_5['Winning Candidate'], top_5['Total Votes'])
        axs[i].set_title(f"{party}")
        axs[i].set_xticklabels(top_5['Winning Candidate'], rotation=45, ha='right')
        axs[i].set_ylabel('Total Votes')
        for j, v in enumerate(top_5['Total Votes']):
            axs[i].text(j, v, f'{v:,}', ha='center', va='bottom')

    plt.tight_layout()
    fig.savefig('top_5_candidates_by_votes_top_10_parties.png')
    return "Top 5 candidates by total votes for each top 10 party:" + '\n'.join(results)


def least_5_candidates_by_votes_top_10_parties(df, candidate_df):
    top_10_parties = df.nlargest(10, 'Total')['Party'].tolist()
    results = []
    fig, axs = plt.subplots(5, 2, figsize=(20, 25))
    axs = axs.ravel()

    for i, party in enumerate(top_10_parties):
        party_candidates = candidate_df[candidate_df['Party'] == party]
        least_5 = party_candidates.nsmallest(5, 'Total Votes')
        results.append(
            f"\n{party}:\n{least_5[['Winning Candidate', 'Constituency', 'Total Votes']].to_string(index=False)}")

        axs[i].bar(least_5['Winning Candidate'], least_5['Total Votes'])
        axs[i].set_title(f"{party}")
        axs[i].set_xticklabels(least_5['Winning Candidate'], rotation=45, ha='right')
        axs[i].set_ylabel('Total Votes')
        for j, v in enumerate(least_5['Total Votes']):
            axs[i].text(j, v, f'{v:,}', ha='center', va='bottom')

    plt.tight_layout()
    fig.savefig('least_5_candidates_by_votes_top_10_parties.png')
    return "Least 5 candidates by total votes for each top 10 party:" + '\n'.join(results)


def main():
    url = "https://results.eci.gov.in/PcResultGenJune2024/index.htm"
    df = scrape_eci_data(url)

    candidate_data = []
    for _, row in df.iterrows():
        try:
            party_url = f"https://results.eci.gov.in/PcResultGenJune2024/{row['Link']}"
            print(f"Scraping data for party {row['Party']} from URL: {party_url}")
            party_data = scrape_candidate_data(party_url, row['Party'])
            if not party_data.empty:
                candidate_data.append(party_data)
            else:
                print(f"No data found for party {row['Party']}")
        except Exception as e:
            print(f"Error scraping data for party {row['Party']}: {str(e)}")

    if not candidate_data:
        print("No candidate data could be scraped. Please check the website structure and URLs.")
        candidate_df = pd.DataFrame()
    else:
        candidate_df = pd.concat(candidate_data, ignore_index=True)

    insights = [
        election_closeness(df),
        forming_government(df),
        overall_election_statistics(df),
        party_size_distribution(df),
        potential_kingmakers(df),
        independent_candidates_won(df),
    ]

    if not candidate_df.empty:
        insights.extend([
            top_5_candidates_by_votes(candidate_df),
            top_5_candidates_by_votes_top_10_parties(df, candidate_df),
            least_5_candidates_by_votes(candidate_df),
            least_5_candidates_by_votes_top_10_parties(df, candidate_df),
        ])
    else:
        print("No candidate-specific insights could be generated due to lack of data.")

    with open('election_insights.txt', 'w') as f:
        for insight in insights:
            print(insight)
            f.write(insight + '\n\n')


if __name__ == "__main__":
    main()