from flask import Flask, render_template, request, jsonify
import os
from cerebras.cloud.sdk import Cerebras

app = Flask(__name__)

# Initialize Cerebras client
client = Cerebras(api_key="put-key-here")

class PhysicsTutor:
    def __init__(self):
        self.message_log = [
            {
                "role": "system",
                "content": """You are an AI tutor for physics. Your responses should:
                1. Always expect users to use 2 decimal points and proper significant figures.
                2. Break down complex problems step by step.
                3. Include relevant formulas and their explanations.
                4. Provide analogies when helpful.
                5. Generate practice problems when requested.
                For practice problems, include the solution with detailed explanations.
                """
            }
        ]
    
    def get_response(self, user_input, mode):
        if mode == "question":
            prompt = f"Question: {user_input}"
        elif mode == "practice":
            prompt = f"Generate a practice problem about: {user_input}. Include a detailed solution."
        else:  # learn mode
            prompt = f"Explain the following physics concept in detail: {user_input}"
        
        self.message_log.append({
            "role": "user",
            "content": prompt
        })
        
        response = client.chat.completions.create(
            messages=self.message_log,
            model="llama3.1-8b"
        )
        
        ai_response = response.choices[0].message.content
        self.message_log.append({
            "role": "assistant",
            "content": ai_response
        })
        
        # Ensuring the response includes formatting instructions
        ai_response = ai_response.replace("**", "<strong>").replace("**", "</strong>")  # Bold text
        ai_response = ai_response.replace("\\frac{", "<span class='important'>\\frac{").replace("}", "}</span>")  # Handle fractions
        
        return ai_response

tutor = PhysicsTutor()

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.json
    user_input = data['input']
    mode = data['mode']
    response = tutor.get_response(user_input, mode)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True, port=5002)
