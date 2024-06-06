from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, col, udf
from pyspark.ml.feature import MinHashLSH, VectorAssembler
from pyspark.ml.linalg import Vectors, VectorUDT

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("MusicRecommendation") \
    .config("spark.mongodb.input.uri", "mongodb://localhost:27017/music_database.music_collection") \
    .config("spark.mongodb.output.uri", "mongodb://localhost:27017/music_database.music_collection") \
    .getOrCreate()

# Loading data from MongoDB into a Spark DataFrame
data = spark.read.format("com.mongodb.spark.sql.DefaultSource") \
    .option("uri", "mongodb://localhost:27017/music_database.music_collection") \
    .option("collection", "music_collection") \
    .load()

exploded_data = data.withColumn("exploded_features", explode(col("features")))

# Explode the inner array
exploded_data = exploded_data.withColumn("feature", explode(col("exploded_features")))

# Convert the array of doubles into a VectorUDT
assembler = VectorAssembler(inputCols=["feature"], outputCol="vector")
exploded_data = assembler.transform(exploded_data).select("audio_file", "vector")

# Create LSH model
lsh = MinHashLSH(inputCol="vector", outputCol="hashes", numHashTables=5)
lsh_model = lsh.fit(exploded_data)

# Define function to get similar items
def get_similar_items(audio_file, model, num_items):
    # Get the feature vector of the input audio file
    audio_features_list = exploded_data.filter(col("audio_file") == audio_file).select("vector").collect()[0][0]
    # Get similar items using the LSH model
    similar_items = model.approxNearestNeighbors(exploded_data, audio_features_list, num_items)
    return similar_items

# Example usage
input_audio_file = "062355.mp3"  # Replace with the name of the input audio file
num_similar_items = 50 # Number of similar items to retrieve
print("Recommended audios along with audio file entered",input_audio_file,"  are:")
# Get similar items for the input audio file
similar_items = get_similar_items(input_audio_file, lsh_model, num_similar_items)

# Show similar items
similar_items.show()

# Stop SparkSession
spark.stop()

