import os
import string
from sentence_transformers import SentenceTransformer, util

# ---------------------------
# CONFIGURATION
# ---------------------------
TRANSCRIPT_FOLDER = "transcriptions"
ORIGINAL_FILE = "original.txt"
OUTPUT_FILE = "semantic_accuracy_results.txt"

# ---------------------------
# FUNCTION TO CLEAN TEXT
# ---------------------------
def clean_text(text):
    # Lowercase
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Remove extra spaces
    text = ' '.join(text.split())
    return text

# ---------------------------
# LOAD ORIGINAL TEXT AND EMBEDDING
# ---------------------------
with open(ORIGINAL_FILE, "r", encoding="utf-8") as f:
    original_text = clean_text(f.read())

# Load pre-trained sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')
original_embedding = model.encode(original_text, convert_to_tensor=True)

# ---------------------------
# PROCESS TRANSCRIPTS
# ---------------------------
results = []

for file_name in sorted(os.listdir(TRANSCRIPT_FOLDER)):
    if file_name.endswith(".txt"):
        file_path = os.path.join(TRANSCRIPT_FOLDER, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract model used
        model_line = content.splitlines()[0]
        model_name = model_line.split(":")[-1].strip() if ":" in model_line else "Unknown"

        # Extract time taken
        time_line = content.splitlines()[1]
        time_taken = time_line.split(":")[-1].strip() if ":" in time_line else "Unknown"

        # Extract transcription text (after "Text:")
        if "Text:" in content:
            transcribed_text = content.split("Text:")[-1].strip()
        else:
            transcribed_text = content.strip()

        # Clean and embed transcribed text
        transcribed_clean = clean_text(transcribed_text)
        transcribed_embedding = model.encode(transcribed_clean, convert_to_tensor=True)

        # Compute semantic similarity (cosine similarity)
        similarity_score = util.cos_sim(original_embedding, transcribed_embedding).item()
        semantic_accuracy = similarity_score * 100  # convert to percentage

        # Format result
        result_text = (
            f"File: {file_name}\n"
            f"Model used: {model_name}\n"
            f"Time taken: {time_taken}\n"
            f"Semantic Accuracy: {semantic_accuracy:.2f}%\n"
            f"{'-'*50}\n"
        )

        # Print on terminal
        print(result_text)
        # Store result
        results.append(result_text)

# ---------------------------
# SAVE RESULTS TO FILE
# ---------------------------
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(results)

print(f"Semantic accuracy evaluation completed. Results saved to {OUTPUT_FILE}")
