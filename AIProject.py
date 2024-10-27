import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import google.generativeai as genai
from gtts import gTTS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Google Generative AI with API key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("API key for Google Generative AI is missing!")

genai.configure(api_key=api_key)

# Initialize the chat session
def init_chat_session():
    try:
        generation_config = {
            "temperature": 1.5,
            "top_p": 0.95,
            "top_k": 85,
            "max_output_tokens": 1000,
            "response_mime_type": "text/plain",
        }

        
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            system_instruction="You are a storytelling bot tasked with generating captivating narratives. Follow these instructions closely:\n\n1. **Genre and Style**: Choose a genre (e.g., fantasy, mystery, romance, sci-fi) and define the tone (e.g., humorous, dark, uplifting) of the story. Make sure it aligns with the user’s interests.\n\n2. **Character Development**:\n   - Introduce at least two main characters. Provide their names, a brief description (age, appearance, personality), and their relationship to each other.\n   - Include a character arc, showing how the characters evolve throughout the story.\n\n3. **Setting**:\n   - Describe the setting in detail, including time (past, present, future) and place (town, city, otherworldly realm).\n   - Use sensory language to create a vivid atmosphere that immerses the reader.\n\n4. **Conflict**:\n   - Introduce a central conflict or challenge that drives the plot. This could be internal (character vs. self) or external (character vs. character, society, nature).\n   - Make sure the conflict is significant enough to engage the reader's emotions.\n\n5. **Plot Structure**:\n   - Follow a clear narrative arc: introduction, rising action, climax, falling action, and resolution.\n   - Ensure that the climax is suspenseful and leads to a satisfying conclusion.\n\n6. **Themes and Messages**:\n   - Weave in themes that resonate with readers, such as love, friendship, sacrifice, or self-discovery.\n   - Conclude with a meaningful takeaway or reflection that adds depth to the story.\n\n7. **Length and Detail**:\n   - Generate a story that is approximately [insert word count, e.g., 800-1200 words]. Provide enough detail to enrich the narrative but avoid excessive length that detracts from pacing.\n\n**Example Starter**: \"Once upon a time in a bustling city where the sun always shone, there lived a curious girl named Elara, who dreamed of exploring the world beyond her neighborhood...\"\n\nEnsure that your story is original, engaging, and suitable for a wide audience. Create a story that readers will want to share and remember.\n",
        )

        chat_session = model.start_chat(
            history=[
            ]
        )
        return chat_session
    except Exception as e:
        print("Error initializing chat session:", e)
        return None

chat_session = init_chat_session()

# Endpoint to generate story
@app.route('/generate_story', methods=['POST'])
def generate_story():
    data = request.get_json()
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    if not chat_session:
        return jsonify({"error": "Chat session initialization failed"}), 500

    try:
        response = chat_session.send_message(prompt).text
        return jsonify({"story": response})  # Return the story text
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to generate audio from text
@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    data = request.get_json()
    text = data.get("text")

    if not text:
        return jsonify({"error": "Text is required to generate audio"}), 400

    try:
        tts = gTTS(text=text, lang='en', tld='com.au')
        tts.save("output.mp3")
        return jsonify({"message": "Audio generated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to serve generated audio file
@app.route('/audio', methods=['GET'])
def get_audio():
    audio_path = "output.mp3"
    if os.path.exists(audio_path):
        return send_file(audio_path, as_attachment=True)
    return jsonify({"error": "Audio file not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
