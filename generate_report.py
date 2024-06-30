from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd

from analyze_data import analyze_data

def generate_report(insights):
    c = canvas.Canvas("election_report.pdf", pagesize=letter)
    c.drawString(100, 750, "Election Results Report")
    
    y = 700
    for key, value in insights.items():
        c.drawString(100, y, f"{key}: {value}")
        y -= 20
    
    c.save()

if __name__ == "__main__":
    cleaned_df = pd.read_csv('cleaned_election_results.csv')
    insights = analyze_data(cleaned_df)
    generate_report(insights)
