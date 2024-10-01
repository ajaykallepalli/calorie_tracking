import os
import weave
from PIL import Image
from pydantic import BaseModel
from openai import OpenAI
from datetime import datetime
import json
import base64
from dotenv import load_dotenv
load_dotenv()


weave.init("together-weave")



class CalorieEstimate(BaseModel):
    food_name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    serving_size: str
    confidence: float
    additional_info: str

client = OpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)
def encode_image(image_path):
    with Image.open(image_path) as img:
        # Resize the image to 1024x1024
        img = img.resize((1024, 1024))
        # Save the resized image to a byte array
        from io import BytesIO
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        # Encode the byte array to base64
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

def get_calorie_estimate_text(food_description: str) -> CalorieEstimate:
    response = client.beta.chat.completions.parse(
        model="openai/gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are a nutritionist. Provide calorie and macronutrient estimates for the given food. Take into account camera intrinsics and camera angles. Try to best guess the food from the available information including food that is covered."},
            {"role": "user", "content": f"Estimate calories and macronutrients for: {food_description}"}
        ],
        response_format=CalorieEstimate,
        temperature=0
    )
    
    # Parse the response and create a CalorieEstimate object
    # This is a simplified example and would need more robust parsing in practice
    calorie_estimate = response.choices[0].message.parsed
    return CalorieEstimate(
        food_name=calorie_estimate.food_name,
        calories=calorie_estimate.calories,
        protein=calorie_estimate.protein,
        carbs=calorie_estimate.carbs,
        fat=calorie_estimate.fat,
        serving_size=calorie_estimate.serving_size,
        confidence=calorie_estimate.confidence,
        additional_info=calorie_estimate.additional_info
    )

def get_calorie_estimate_image(image_path: str) -> CalorieEstimate:
    response = client.beta.chat.completions.parse(
        model="openai/gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are a nutritionist. Provide calorie and macronutrient estimates for the given food. Take into account camera intrinsics and camera angles. Try to best guess the food from the available information including food that is covered."},
            {"role": "user", "content": [
                {"type": "text", "text": "What are the calories for the food in this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_path}",
                        "detail": "high"
                    }
                }
            ]
            }
        ],
        response_format=CalorieEstimate,
        temperature=0
    )
    
    # Implement parsing logic here to extract values from content
    # Parse the structured output directly into a CalorieEstimate object
    calorie_estimate = response.choices[0].message.parsed

    return CalorieEstimate(
        food_name=calorie_estimate.food_name,
        calories=calorie_estimate.calories,
        protein=calorie_estimate.protein,
        carbs=calorie_estimate.carbs,
        fat=calorie_estimate.fat,
        serving_size=calorie_estimate.serving_size,
        confidence=calorie_estimate.confidence,
        additional_info=calorie_estimate.additional_info
    )

if __name__ == "__main__":
    # Assuming get_calorie_estimate_image is the correct function name
    # and that it takes a food description as an argument
    base64_image = encode_image("/Users/ajaykallepalli/data/food_images/bananas.png")
    calorie_estimate = get_calorie_estimate_image(base64_image)
    print(calorie_estimate)
    
    # Example usage for text-based calorie estimation
    food_description = "A large cheese pizza with pepperoni and mushrooms"
    calorie_estimate_text = get_calorie_estimate_text(food_description)
    print(f"Calorie estimate for '{food_description}':")
    print(calorie_estimate_text)