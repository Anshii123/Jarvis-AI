from googlesearch import search
from groq import Groq  # Importing the Groq library to use its API.
from json import load,dump  # Importing functions to read and writejson files.
import datetime  # Importing the date time module for realtime data and time information.
from dotenv import dotenv_values # Importing dotenv_values to read environment variables from a .env file.


# load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve environment variables for the chatbot configuration.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client using the provided API Key.
client = Groq(api_key=GroqAPIKey)

# Define the system instructions for the chatbot.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""


# Try to load the chat log from a JSON file , or create an empty one if it doesn't exist.
try:
    with open(r"Data\ChatLog.json","r") as f:
        messages = load(f)    # Load existing messages from the chat log.
except:
    with open(r"Data\ChatLog.json","w") as f:
        dump([],f)

# Function to perform a Google Search and format the results
def GoogleSearch(query):
    results = list(search(query,advanced=True , num_results=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"

    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

    Answer += "[end]"
    return Answer

# Function to clean up the answer by removing empty lines.
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer
    

# Predefined chatbot conversion system message and an initial user message.
SystemChatbot = [
    {"role":"system" , "content":"System"},
    {"role":"user" , "content":"Hi"},
    {"role":"assistant" , "content":"Hello,how can I help you?"}
]

# Function to get real time information like the current date and time.
def Information():
    data =""
    current_date_time = datetime.datetime.now()  # Get the current date and time.
    day = current_date_time.strftime("%A")  # Day of the week.
    date = current_date_time.strftime("%d") # Day of the month.
    month = current_date_time.strftime("%B") # Full Month name
    year = current_date_time.strftime("%Y") # Year
    hour = current_date_time.strftime("%H") # Hour in 24 hr format.
    minute = current_date_time.strftime("%M")  # Minute
    second = current_date_time.strftime("%S") # Second

    # Format the information into a string.
    data += f"Use this Real-time Information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes , {second} seconds.\n"
    return data


# Function to handle real-time search and response generation.
def RealtimeSearchEngine(prompt):
    global SystemChatbot , messages
    # Load the existing chat log from the JSON file.
    with open(r"Data\ChatLog.json","r") as f:
        messages = load(f)

    # Append the user's query to the messages list.
    messages.append({"role":"user" , "content":f"{prompt}"})

    # Add Google search resukts to the system chatbot messages.
    SystemChatbot.append({"role": "system" , "content": GoogleSearch(prompt)})


    # Generate the response using the Groq client.
    completion = client.chat.completions.create(
        model= "llama3-70b-8192", # Specify the AI model to use.
        messages= SystemChatbot + [{"role": "system" , "content": Information()}] + messages, # Include system instructions, real-time info and chat history.
        temperature=0.7, # Adjust response random (higher means more random.)
        max_tokens=2048,  # Limit the maximum tokens in the response.
        top_p=1,  # Use nuclear sampling to control diversity.
        stream= True,  # Enable streaming response.
        stop=None  # Allow the model to determine when to stop.
    )
    Answer = ""  #Initialize an empty string to store the Ai's response.


    # Concatenate response chunks from the streaming output.
    for chunk in completion:
        if chunk.choices[0].delta.content:  # Check if there is content in the current chunk.
            Answer += chunk.choices[0].delta.content  # Append the content to the answer.
    
    # Clean up the response.
    Answer = Answer.strip().replace("</s>","")
    # Append the chatbot's response to the messages list.
    messages.append({"role":"assistant","content":Answer})

    # Save the updated chat log to the JSON file.
    with open(r"Data\ChatLog.json","w") as f:
        dump(messages,f,indent =4)
    
    # Remove the most recent system message from the chatbot conversation.
    SystemChatbot.pop()
    return AnswerModifier(Answer=Answer)

# Main entry point of the program for interactive querying.
if __name__ == "__main__":
    while True:
        prompt = input("Enter your Query: ") # Prompt the user for a query.
        print(RealtimeSearchEngine(prompt)) # Call the Chatbot function and print its response.

