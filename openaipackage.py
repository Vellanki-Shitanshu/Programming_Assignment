import openai
import os

class OpenAIEngine:
    def __init__(self):
        # Load the OpenAI API key from environment variables
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key

    def change(self, generation_type, model, prompt=None):
        # This method would configure the engine based on generation type, model, and prompt
        self.generation_type = generation_type
        self.model = model
        self.prompt = prompt

    def generate_answer(self, prompt):
        # Generate a text response
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message['content']

    def generate_image(self, prompt):
        # Generate an image URL
        response = openai.Image.create(
            prompt=prompt,
            model=self.model,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        return image_url
