import os
from google import genai
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

#-- Initialize the model --#

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


#-- Load and split the transcript --#
def load_transcript(file_path):
    with open(file_path, "r") as file:
        return file.read()

def split_transcript(transcript):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
    chunk_overlap=200,
    add_start_index= True
    )
    return text_splitter.split_text(transcript)

#--NEW : THE RETRIEVER --#

def get_relevant_context(question,chunks):
    question_words = set(question.lower().split())
    best_chunk=chunks[0]
    max_overlap=-1

    for chunk in chunks:
        chunk_words = set(chunk.lower().split())
        overlap= len(question_words.intersection(chunk_words))
        if overlap > max_overlap:
            max_overlap=overlap
            best_chunk=chunk
    return best_chunk

#-- NEW : THE CHAT FUNCTION --#
def chat():
    raw_text = load_transcript("transcript.txt")
    chunks = split_transcript(raw_text)
    print("Chatbot Ready! (Type 'exit' to quit)")

    while True:
        query= input("\n You: ")
        if query.lower() == "exit":
            break
        
        #1. Get right page from the transcript
        context=get_relevant_context(query,chunks)

        #2. Build the prompt
        prompt= f"""
        You are a helpful assistant. Use the following piece of a meeting transcript to answer the user's question.
        If the answer is not in the context, say "I don't have that information in this part of the transcript."

        CONTEXT:
        {context}

        QUESTION: 
        {query}
        """

        #3. Ask the model

        response=client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )

        print(f" Assistant: {response.text}")

if __name__ == "__main__":
    chat()