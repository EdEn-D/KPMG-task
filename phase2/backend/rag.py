import os
import numpy as np
from openai import AzureOpenAI
from sklearn.metrics.pairwise import cosine_similarity
import logging
from dotenv import load_dotenv, find_dotenv
import sys

load_dotenv(find_dotenv())
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class RAGProcessor:
    def __init__(self):
        """
        Initialize the RAG processor with an OpenAI client and deployment name
        If not provided, it will use the client from the caller
        """
        self.embedding_deployment_name = os.getenv("AZURE_EMBEDDING_DEPLOYMENT")
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_EMBEDDING_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version=os.getenv("AZURE_EMBEDDING_API_VERSION"),
        )
        self.file_embeddings = {}
        self.file_contents = {}  # Add this line to store file contents

    def read_files_from_directory(self, directory_path):
        """
        Read all text files from a directory
        Returns a dictionary with filenames as keys and file contents as values
        """
        file_contents = {}

        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        file_contents[filename] = file.read()
                except Exception as e:
                    logger.error(f"Error reading {filename}: {e}")

        # Store the file contents in the class attribute
        self.file_contents = file_contents
        return file_contents

    def generate_embeddings(self, texts):
        """
        Generate embeddings for a list of texts
        Returns a dictionary mapping each text to its embedding vector
        """

        embeddings = {}

        for key, text in texts.items():
            try:
                response = self.client.embeddings.create(
                    input=text, model=self.embedding_deployment_name
                )
                embeddings[key] = response.data[0].embedding
            except Exception as e:
                logger.error(f"Error generating embedding for {key}: {e}")

        self.file_embeddings = embeddings
        return embeddings

    def find_similar_documents(self, query, num_results=3):
        """
        Find documents similar to the query using cosine similarity
        Returns sorted list of (filename, similarity_score) tuples
        """
        # Generate embedding for the query
        try:
            query_response = self.client.embeddings.create(
                input=query, model=self.embedding_deployment_name
            )
            query_embedding = query_response.data[0].embedding

            # Calculate cosine similarity with each document
            similarities = {}
            for filename, embedding in self.file_embeddings.items():
                # Convert embeddings to numpy arrays for cosine similarity calculation
                similarity = cosine_similarity([query_embedding], [embedding])[0][0]
                similarities[filename] = similarity

            # Sort by similarity score (highest first)
            sorted_results = sorted(
                similarities.items(), key=lambda x: x[1], reverse=True
            )

            # Return the top num_results
            return sorted_results[:num_results]
        except Exception as e:
            logger.error(f"Error finding similar documents: {e}")
            return []

    def get_relevant_context(self, query, num_results=3, include_scores=False):
        """
        Get relevant context from the documents for a given query
        Returns the combined text of the most relevant documents
        """
        results = self.find_similar_documents(query, num_results)

        if not results:
            return ""

        relevant_context = ""
        for filename, score in results:
            if filename in self.file_contents:
                if include_scores:
                    relevant_context += (
                        f"\n[Source: {filename}, Similarity: {score:.4f}]\n"
                    )
                else:
                    relevant_context += f"\n[Source: {filename}]\n"
                relevant_context += self.file_contents[filename] + "\n"

        return relevant_context

    def initialize_from_directory(self, directory_path):
        """
        Initialize the RAG processor by reading files and generating embeddings
        """
        logger.info(f"Reading files from {directory_path}")
        contents = self.read_files_from_directory(directory_path)
        logger.info(f"Found {len(contents)} files")

        logger.info("Generating embeddings")
        self.generate_embeddings(contents)
        logger.info(f"Generated embeddings for {len(self.file_embeddings)} files")
