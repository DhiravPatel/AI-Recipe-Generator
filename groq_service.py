import requests
from bs4 import BeautifulSoup
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import json
import config
import re

class GroqService:
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=config.GROQ_API_KEY,
            model=config.MODEL,
            temperature=0.7,
        )

    def generate_recipe(self, recipe_name, num_servings, main_ingredients):
        """
        Generate a recipe based on the provided details.
        """
        prompt_generate_recipe = PromptTemplate.from_template(
            """
            ### RECIPE GENERATION INSTRUCTIONS:
            Generate a recipe with the following details:
            
            Dish Name: {recipe_name}
            Number of Servings: {num_servings}
            Main Ingredients: {main_ingredients}
            
            Provide the following structure:
            1. Title of the dish
            2. Ingredients with exact measurements for {num_servings} servings
            3. Step-by-step cooking instructions
            4. Estimated cooking time in minutes
            
            ONLY return valid JSON with the following keys:
            - title (string): The name of the dish.
            - ingredients (list of strings): List of ingredients with quantities.
            - instructions (list of strings): List of step-by-step instructions.
            - estimated_time (int): Estimated cooking time in minutes.
            ### JSON FORMAT ONLY:
            """
        )

        chain_generate_recipe = prompt_generate_recipe | self.llm
        response = chain_generate_recipe.invoke(
            input={
                'recipe_name': recipe_name,
                'num_servings': num_servings,
                'main_ingredients': main_ingredients,
            }
        )

        try:
            recipe_response = response.content
            start_index = recipe_response.find("{")
            end_index = recipe_response.rfind("}") + 1
            json_string = recipe_response[start_index:end_index]
            recipe = json.loads(json_string)
            return recipe
        except json.JSONDecodeError as e:
            return {"error": f"Error decoding JSON: {e}"} 

    def fetch_recipe_image(self, recipe_name):
        """
        Fetch multiple images from Google Image search.
        This is a simple scraping method that extracts image URLs.
        """
        query = f"{recipe_name} recipe image"
        search_url = f"https://www.google.com/search?hl=en&tbm=isch&q={query}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(search_url, headers=headers)

        if response.status_code != 200:
            return []  # Return empty list if request fails
        
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract image URLs using regex
        image_urls = re.findall(r'\"https://[^"]+?\.jpg\"', str(soup))
        
        # Return the first 4 images if available
        return [url.strip('"') for url in image_urls[:4]]  # Get up to 4 images
