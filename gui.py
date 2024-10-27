import tkinter as tk
from tkinter import messagebox, Canvas, Frame, Label, Button, Scrollbar
import requests
import threading
import pygame

# Initialize Pygame mixer for audio playback
pygame.mixer.init()

# Flask server URL
SERVER_URL = "http://127.0.0.1:5000"

# Main application window
root = tk.Tk()
root.title("Chatbot")
root.geometry("500x700")

# Canvas and scrollbar for scrolling chat messages
chat_canvas = Canvas(root, bg="#f5f6f8", width=480)
scrollbar = Scrollbar(root, orient="vertical", command=chat_canvas.yview)
scrollbar.pack(side="right", fill="y")

chat_canvas.configure(yscrollcommand=scrollbar.set)
chat_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Frame to contain chat bubbles within the canvas
chat_frame = Frame(chat_canvas, bg="#f5f6f8")
chat_canvas.create_window((0, 0), window=chat_frame, anchor="nw")

# Function to update scroll region
def update_scroll_region(event=None):
    chat_canvas.configure(scrollregion=chat_canvas.bbox("all"))

chat_frame.bind("<Configure>", update_scroll_region)

# User input field
user_input = tk.Entry(root, width=40, font=("Arial", 12))
user_input.pack(side="left", padx=10, pady=10)

# Function to display user and bot messages as separate bubbles
def display_message(text, sender="user"):
    message_frame = Frame(chat_frame, bg="#f5f6f8", padx=10, pady=5)

    # Configure bubble styles
    if sender == "user":
        bubble = Label(message_frame, text=text, bg="#007bff", fg="white",
                       font=("Arial", 12), wraplength=300, justify="left", padx=10, pady=5)
        bubble.pack(anchor="e", padx=5, pady=2)
    else:
        bubble = Label(message_frame, text=text, bg="#e0e0e0", fg="black",
                       font=("Arial", 12), wraplength=300, justify="left", padx=10, pady=5)
        bubble.pack(anchor="w", padx=5, pady=2)

        # Add Play Audio button for bot response
        play_button = Button(message_frame, text="Play Audio", 
                             command=lambda response_text=text: play_audio(response_text, play_button))
        play_button.pack(anchor="w", padx=5, pady=2)

    message_frame.pack(fill="both", expand=True)
    chat_canvas.update_idletasks()
    chat_canvas.yview_moveto(1)

# Send message to the server and display the response
def send_message():
    prompt = user_input.get().strip()
    if not prompt:
        return

    display_message(prompt, sender="user")
    user_input.delete(0, tk.END)

    # Threading for async server request
    threading.Thread(target=get_response, args=(prompt,)).start()

# Get response from the Flask backend
def get_response(prompt):
    try:
        response = requests.post(f"{SERVER_URL}/generate_story", json={"prompt": prompt})
        response_data = response.json()
        
        if "error" in response_data:
            display_message(f"Error: {response_data['error']}", sender="bot")
        else:
            story = response_data["story"]
            display_message(story, sender="bot")
    except Exception as e:
        messagebox.showerror("Error", f"Could not connect to server.\n{e}")

# Request audio generation and playback
def play_audio(text, button):
    try:
        response = requests.post(f"{SERVER_URL}/generate_audio", json={"text": text})
        if response.ok:
            threading.Thread(target=play_audio_file, args=(text, button)).start()
        else:
            messagebox.showerror("Error", "Could not generate audio.")
    except Exception as e:
        messagebox.showerror("Error", f"Could not connect to server.\n{e}")

# Play the audio file
def play_audio_file(text, button):
    try:
        # Download the audio file
        audio_response = requests.get(f"{SERVER_URL}/audio")
        with open("output.mp3", "wb") as f:
            f.write(audio_response.content)

        # Update button to Stop Audio
        button.config(text="Stop Audio", command=lambda: stop_audio(button))

        # Play the audio
        pygame.mixer.music.load("output.mp3")
        pygame.mixer.music.play()

        # Wait until the audio finishes to revert button text
        while pygame.mixer.music.get_busy():
            root.update()  # Keep the GUI responsive
        stop_audio(button, text)

    except Exception as e:
        messagebox.showerror("Error", f"Could not play audio.\n{e}")

# Stop the audio and reset the button to Play Audio
def stop_audio(button, response_text=None):
    pygame.mixer.music.stop()
    if response_text:
        button.config(text="Play Audio", command=lambda: play_audio(response_text, button))
    else:
        button.config(text="Play Audio", command=lambda: play_audio(button.cget("text"), button))

# Send button
send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack(side="left", padx=5, pady=10)

# Start the Tkinter main loop
root.mainloop()
