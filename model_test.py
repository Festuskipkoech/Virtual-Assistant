# Import necessary modules
import json  
# For loading and working with JSON files
import pickle 
 # For saving and loading serialized Python objects, trained model
from tensorflow.keras.models import load_model  
# For loading a pre-trained Keras model
from tensorflow.keras.preprocessing.sequence import pad_sequences  
# For padding text sequences to a fixed size
import random 
 # For selecting random responses
import numpy as np 
 # For numerical computations

# Load the intents file, which contains predefined tags and responses for the chatbot
with open("intents.json") as file:
    data = json.load(file) 
    # Parse the JSON data into a Python dictionary

# Load the pre-trained chatbot model from an .h5 file
model = load_model("chat_model.h5")

# Load the tokenizer object for text preprocessing (e.g., converting text to sequences)
with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)

# Load the label encoder object for mapping model predictions back to their corresponding labels
with open("label_encoder.pkl", "rb") as encoder_file:
    label_encoder = pickle.load(encoder_file)

# Start an infinite loop to simulate continuous interaction with the chatbot
while True:
    # Prompt user for input
    input_text = input("Enter your command-> ")  # Get user input from the console

    # Convert the input text to a sequence of tokens, then pad it to a fixed length of 20
    padded_sequences = pad_sequences(
        tokenizer.texts_to_sequences([input_text]), 
        # Convert text to numerical sequences
        maxlen=20,  
        # Ensure all sequences are 20 tokens long
        truncating='post'  
        # If the sequence is too long, truncate it at the end
    )

    # Use the loaded model to predict the intent of the input text
    result = model.predict(padded_sequences)  
    # Get the model's predictions
    # Find the tag corresponding to the highest prediction probability
    tag = label_encoder.inverse_transform([np.argmax(result)])

    # Iterate through the intents to find the matching tag
    for i in data['intents']:
        if i['tag'] == tag:  
            # Check if the predicted tag matches a tag in the intents
            # Select a random response from the list of responses for the matched intent
            print(np.random.choice(i['responses']))
