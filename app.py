import streamlit as st
import pandas as pd
from groq_service import GroqService

groq_service = GroqService()

st.set_page_config(page_title="Recipe Generator", page_icon="🍳", layout="centered")
st.title("🍳 AI Recipe Generator")

with st.sidebar:
    st.header("Recipe Customization 📝")
    recipe_name = st.text_input("Dish Name", placeholder="e.g., Spicy Tuver Totha Delight")
    num_servings = st.slider("Number of Servings", min_value=1, max_value=10, value=4)
    main_ingredients = st.text_area(
        "Main Ingredients",                                        
        placeholder="e.g., tuver beans, onions, tomatoes"
    )
    generate_button = st.button("Generate Recipe 🍽️")

if generate_button:
    if recipe_name:
        st.info(f"Generating recipe for **{recipe_name}**...")
        with st.spinner("Contacting Groq Cloud..."):
            recipe = groq_service.generate_recipe(recipe_name, num_servings, main_ingredients or "")
        

        recipe_image_urls = groq_service.fetch_recipe_image(recipe_name)
        
        
        if recipe_image_urls:
            st.subheader("Recipe Images")
            cols = st.columns(3) 
            for i, image_url in enumerate(recipe_image_urls):
                with cols[i % 3]:  
                    st.image(image_url, caption=f"{recipe_name} - Recipe Image {i+1}", use_container_width=True)
        else:
            st.warning("No images found for this recipe.")
        
        if "error" in recipe:
            st.error(f"Failed to generate recipe. {recipe['error']}")
        else:
            st.markdown(
                f"""
                ### ✨ {recipe['title']} ✨  
                **Servings**: {num_servings}  
                **Main Ingredients**: {main_ingredients if main_ingredients else "Not specified"}  
                **Estimated Cooking Time**: {recipe['estimated_time']} minutes  
                ---
                """
            )

            st.markdown("### 🥗 Ingredients")
            for ingredient in recipe["ingredients"]:
                st.write(f"- {ingredient}")

            st.markdown("### 🍴 Instructions")
            instructions_data = [
                { "Step": idx + 1, "Instruction": step} 
                for idx, step in enumerate(recipe["instructions"])
            ]
            st.table(pd.DataFrame(instructions_data))
    else:
        st.warning("Please provide a dish name.")
else:
    st.markdown(
        """
        ### Welcome to AI Recipe Generator! 🌟
        - Generate recipes tailored to your choice of ingredients.
        - Adjust servings to fit your needs.
        - Get easy-to-follow instructions and a full list of ingredients.

        **Start by customizing your recipe in the sidebar!**
        """
    )
