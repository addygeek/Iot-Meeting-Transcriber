import os
import difflib
import string

# ---------------------------
# CONFIGURATION
# ---------------------------
TRANSCRIPT_FOLDER = "transcriptions"
ORIGINAL_FILE = "original.txt"  # Ground truth
OUTPUT_FILE = "accuracy_results.txt"

# ---------------------------
# FUNCTION TO CLEAN TEXT
# ---------------------------
def clean_text(text):
    # Lowercase
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Remove extra spaces and split into words
    words = text.strip().split()
    return words

# ---------------------------
# FUNCTION TO CALCULATE ACCURACY
# ---------------------------
def word_accuracy(original_words, transcribed_words):
    seq = difflib.SequenceMatcher(None, original_words, transcribed_words)
    return seq.ratio() * 100  # percentage

# ---------------------------
# READ ORIGINAL TEXT
# ---------------------------
with open(ORIGINAL_FILE, "r", encoding="utf-8") as f:
    original_text = f.read()
original_words = clean_text(original_text)

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

        transcribed_words = clean_text(transcribed_text)
        accuracy = word_accuracy(original_words, transcribed_words)

        # Format result
        result_text = (
            f"File: {file_name}\n"
            f"Model used: {model_name}\n"
            f"Time taken: {time_taken}\n"
            f"Accuracy: {accuracy:.2f}%\n"
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

print(f"Accuracy evaluation completed. Results saved to {OUTPUT_FILE}")
