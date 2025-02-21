import asyncio
import requests
from random import randint
from PIL import Image
from dotenv import get_key
import os
from time import sleep

# Function to open and display images based on a given prompt.
def open_images(prompt):
    folder_path = r"Data"  # Folder where the images are stored.
    prompt = prompt.replace(" ", "_")  # Replace spaces in prompt with underscores.

    # Generate the filenames for the images.
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)

        try:
            # Try to open and display the image.
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)  # Pause for 1 second before showing the new image.
        except IOError:
            print(f"Unable to open {image_path}")

# Ensure the Data folder exists
os.makedirs("Data", exist_ok=True)

# API details for the Hugging Face Stable Diffusion model
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
api_key = get_key('.env', 'HuggingFaceAPIKey')
if not api_key:
    print("Error: API key is missing or not loaded correctly.")
headers = {"Authorization": f"Bearer {api_key}"}

# Async function to send a query to the Hugging Face API with retry mechanism.
async def query(payload):
    retries = 5  # Maximum retries before giving up
    wait_time = 60  # Start with a 60-second wait for rate limit

    for attempt in range(retries):
        try:
            response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                return response.content  # Successful response, return image data

            elif response.status_code == 429:
                print(f"Rate limit exceeded. Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{retries})")
                sleep(wait_time)  # Wait before retrying
                wait_time = min(wait_time * 2, 300)  # Exponential backoff up to 5 minutes

            else:
                print(f"Error: {response.status_code}, Response: {response.text}")
                return None  # Stop retrying for non-429 errors

        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}. Retrying in {wait_time} seconds...")
            sleep(wait_time)
    
    print("Failed to generate image after multiple attempts.")
    return None

# Async function to generate images based on the given prompt.
async def generate_images(prompt: str):
    tasks = []

    # Create 4 image generation tasks.
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality: 4K, sharpness: maximum, Ultra High details, high resolution, seed: {randint(0, 1000000)}"
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    # Wait for all tasks to complete.
    image_bytes_list = await asyncio.gather(*tasks)

    # Save the generated images to files.
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes is None or len(image_bytes) < 1000:  # Small files likely indicate an error
            print(f"Image {i+1} not generated properly.")
            continue  # Skip saving if image data is invalid
        
        file_path = fr"Data\{prompt.replace(' ', '_')}{i+1}.jpg"
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        print(f"Image saved: {file_path}")

# Wrapper function to generate and open images.
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))  # Run the async image generation.
    open_images(prompt)

# Main loop to monitor for image generation requests
while True:
    try:
        # Read the status and prompt from the data files.
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            Data: str = f.read()

        Prompt, Status = Data.split(",")

        # If the status indicates an image generation request.
        if Status.strip() == "True":
            print("Generating Images...")
            GenerateImages(prompt=Prompt)

            # Reset the status in the file after generating images
            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False,False")
            break  # Exit the loop after processing the request.
        else:
            sleep(1)  # Wait for 1 second before checking again.
    except Exception as e:
        print(f"Error encountered: {e}")
