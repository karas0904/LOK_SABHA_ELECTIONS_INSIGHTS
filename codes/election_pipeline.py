from pyspark.sql import SparkSession
from zenml.pipelines import pipeline
from zenml.steps import step

# Initialize Spark session
spark = SparkSession.builder.appName("ElectionResults").getOrCreate()

# Define ZenML steps and pipeline
@step
def ingest_data():
    df = spark.read.csv('cleaned_election_results.csv', header=True, inferSchema=True)
    return df

@step
def process_data(df):
    # Perform data processing with Spark
    processed_df = df.withColumn('Votes', df['Votes'].cast('int'))
    return processed_df

@step
def analyze_data(df):
    # Analyze data with Spark
    df.createOrReplaceTempView("results")
    insights = spark.sql("SELECT Party, COUNT(*) as Seats FROM results GROUP BY Party")
    insights.show()
    return insights

@pipeline
def election_pipeline(ingest_data, process_data, analyze_data):
    df = ingest_data()
    processed_df = process_data(df)
    analyze_data(processed_df)

if __name__ == "__main__":
    pipeline = election_pipeline(ingest_data(), process_data(), analyze_data())
    pipeline.run()
