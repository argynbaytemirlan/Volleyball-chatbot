#Automatic Video Summary Creation (Difficulty Level: Advanced) - Design a system using computer vision and
#machine learning algorithms which would parse through a volleyball game's footage and create a volleyball theory to user. 
#This can greatly benefit newbies in volleyball.

from flask import Flask, render_template, request, jsonify
import promptlayer
import pandas as pd
from fuzzywuzzy import fuzz

promptlayer.api_key = 'pl_280646f3f64228f982dfd9070128e748'
openai = promptlayer.openai
openai.api_key = "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"


conversation = [{"role": "system", "content": "You are a volleyball matches assistant that provides volleyball tips that user asked."}]

def get_initial_response(message):
    conversation.append({"role": "user", "content": message})
    response = openai.ChatCompletion.create(
        model="gpt-4", 
        messages = conversation, 
        temperature = 0.8,
        pl_tags=["Temirlan"]
    )
    initial_response_content = response['choices'][0]['message']['content']
    conversation.append({"role": "assistant", "content": initial_response_content})
    return initial_response_content


def get_second_response(user_message, initial_response):
    final_response_conversation = [
        {"role": "user", "content": user_message},
        {"role": "system", "content": f"You are checking to make sure a chatbot has answered propely and you doing it step by step. Also, you are making sure if he didn't change the topic and stays focused on volleball." 
         f"The user just asked: {user_message} and the chatbot responded with {initial_response}."
         f"Please improve the answer and return it with no justification other than :) so I know you reviewed the response."}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4", 
        messages = final_response_conversation, 
        temperature = 0.7,
        pl_tags=["Temirlan"])
    return response['choices'][0]['message']['content']

def check_language(user_message, response):
    final_response_conversation = [
        {"role": "user", "content": user_message},
        {"role": "system", "content": f"You are checking to make sure a chatbot has written on a language that user wrote. You are doing it step by step. Also, you are making sure if he didn't change the topic and stays focused on volleball." 
         f"The user just asked: {user_message} and the chatbot responded with {response}."
         f"Please improve the answer and return it with no justification other than * so I know you reviewed the response."}
    ]
    final_response = openai.ChatCompletion.create(
        model="gpt-4", 
        messages = final_response_conversation, 
        temperature = 0.8,
        pl_tags=["Temirlan"])
    return final_response['choices'][0]['message']['content']

# Function to fetch video information from the Excel database
def get_video_info(requested_video):
    # Replace 'your_database.xlsx' with the path to your Excel file
    df = pd.read_excel('C:/Users/temir/OneDrive/Desktop/Deltaschool_AI/Materials/dataset_volleyball.xlsx')

    # Create an empty dictionary to store fuzzy match scores and titles
    matches = {}

    # Iterate through all titles in the Excel file
    for index, row in df.iterrows():
        title = row['Title']
        similarity_score = fuzz.token_sort_ratio(requested_video, title)
        matches[title] = similarity_score

    # Sort the matches by similarity score in descending order
    sorted_matches = sorted(matches.items(), key=lambda x: x[1], reverse=True)

    # If there are close matches
    if sorted_matches[0][1] >= 80:
        closest_match_title = sorted_matches[0][0]
        closest_match_row = df[df['Title'] == closest_match_title]
        youtube_link = closest_match_row.iloc[0]['YouTubeLink']  # Replace with the actual column name
        return {"title": closest_match_title, "link": youtube_link}
    else:
        # If no close match is found, return None
        return None



app = Flask(__name__)
template_folder='C:/Users/temir/OneDrive/Desktop/Deltaschool_AI/Projects/Assistant/templates'
@app.route('/')

def home():
    return render_template('chatbot.html')

@app.route('/ask', methods=['POST'])
def ask():
    message = request.form['message']
    initial_response = get_initial_response(message)
    second_response = get_second_response(message, initial_response)

    # Generate the theory part of the response
    response = check_language(message, second_response)
    video = get_video_info(message)
    
    response_data = {
        "response": response,  
        "video": video
    }
    return jsonify(response_data)

if __name__ == "__main__":
    app.run()