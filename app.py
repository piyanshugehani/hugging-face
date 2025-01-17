from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch

app = Flask(__name__)
cors = CORS(app, origins="*")

# Load Hugging Face model and tokenizer for embeddings
model_name = "sentence-transformers/all-MiniLM-L6-v2"  # You can choose a different model if needed
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Sample items with descriptions
items = [
    {"id": 1, "name": "Smartphone", "category": "tech", "description": "A high-performance smartphone with the latest features like 5G connectivity, a powerful processor, and an amazing camera."},
    {"id": 2, "name": "Novel Book", "category": "Books", "description": "A captivating novel by a famous author, filled with twists and turns. A must-read for fiction lovers."},
    {"id": 3, "name": "Laptop", "category": "Tech", "description": "A lightweight laptop with long battery life, ideal for students and professionals alike. Equipped with the latest specs for high productivity."},
    {"id": 4, "name": "Wireless Earbuds", "category": "tech", "description": "Noise-cancelling wireless earbuds with exceptional sound quality and a comfortable fit. Great for on-the-go listening."},
    {"id": 5, "name": "Cookbook", "category": "Books", "description": "A cookbook with hundreds of recipes for every occasion. Perfect for beginner and expert chefs alike."},
    {"id": 6, "name": "Gaming Console", "category": "tech", "description": "A state-of-the-art gaming console offering an immersive experience with the latest games, high-resolution graphics, and fast loading times."},
    {"id": 7, "name": "Smartwatch", "category": "tech", "description": "A smartwatch with health tracking features, customizable bands, and long battery life. Ideal for fitness enthusiasts."},
    {"id": 8, "name": "Bluetooth Speaker", "category": "tech", "description": "Portable Bluetooth speaker with deep bass and water-resistant design. Perfect for outdoor adventures and parties."},
    {"id": 9, "name": "Electric Bike", "category": "tech", "description": "A modern electric bike with fast speeds, long battery range, and a lightweight frame for easy commuting."},
    {"id": 10, "name": "Air Purifier", "category": "home", "description": "A smart air purifier that helps to remove dust, allergens, and pollutants from your home environment."},
    {"id": 11, "name": "Vacuum Cleaner", "category": "home", "description": "A powerful vacuum cleaner with multiple attachments for deep cleaning and a long-lasting battery."},
    {"id": 12, "name": "Smart Thermostat", "category": "home", "description": "A smart thermostat that learns your temperature preferences and optimizes energy usage, saving on utility bills."},
    {"id": 13, "name": "Portable Power Bank", "category": "tech", "description": "A high-capacity power bank that provides reliable charging for your devices while on the go."},
    {"id": 14, "name": "Electric Grill", "category": "home", "description": "A compact electric grill for indoor grilling, with adjustable temperature control and non-stick surfaces."},
    {"id": 15, "name": "Robot Vacuum", "category": "home", "description": "A smart robot vacuum that cleans your home autonomously, with obstacle detection and automatic charging."},
    {"id": 16, "name": "Kindle", "category": "Books", "description": "An e-reader with a glare-free display and access to thousands of e-books and audiobooks."},
    {"id": 17, "name": "Noise Cancelling Headphones", "category": "tech", "description": "Wireless noise-cancelling headphones with immersive sound quality and a comfortable fit for long hours of listening."},
    {"id": 18, "name": "Digital Camera", "category": "tech", "description": "A high-resolution digital camera perfect for photography enthusiasts, with customizable settings and excellent low-light performance."},
    {"id": 19, "name": "Electric Scooter", "category": "tech", "description": "A foldable electric scooter for easy commuting, with a long battery range and smooth ride on different terrains."},
    {"id": 20, "name": "Smart Refrigerator", "category": "home", "description": "A smart refrigerator with Wi-Fi connectivity, a touch screen, and the ability to monitor food storage and expiration dates."},
    {"id": 21, "name": "Electric Kettle", "category": "home", "description": "A quick-boiling electric kettle with an automatic shut-off feature and adjustable temperature settings."},
    {"id": 22, "name": "Fitness Tracker", "category": "tech", "description": "A wearable fitness tracker that monitors your steps, heart rate, and sleep patterns to help you stay healthy."},
    {"id": 23, "name": "Smart Speaker", "category": "tech", "description": "A voice-activated smart speaker that integrates with your home automation system and plays music, answers questions, and more."},
    {"id": 24, "name": "Drone", "category": "tech", "description": "A high-quality drone with 4K camera for aerial photography and stable flight performance."},
    {"id": 25, "name": "Smart Light Bulbs", "category": "home", "description": "Energy-efficient smart light bulbs that can be controlled remotely and change color based on your mood."}
]


def cosine_similarity(vec1, vec2):
    # Compute the cosine similarity between two vectors
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def get_embeddings(texts):
    embeddings = []
    
    for text in texts:
        try:
            # Tokenize the text and get embeddings from Hugging Face model
            inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
            with torch.no_grad():
                outputs = model(**inputs)
            # Mean pooling to get a single vector for the sentence
            embeddings.append(outputs.last_hidden_state.mean(dim=1).squeeze().numpy())
        except Exception as e:
            print(f"Error fetching embedding for text: {text}, Error: {e}")
            embeddings.append(np.zeros(768))  # If error occurs, use zero vector (768 for MiniLM)
    
    return embeddings

@app.route('/recommend', methods=['POST'])
def recommend():
    user_preferences = request.json.get('preferences', [])
    print("User Preferences:", user_preferences)  # Debugging line

    # Get embeddings for the user preferences
    preference_embeddings = get_embeddings(user_preferences)

    # Get embeddings for item descriptions
    item_descriptions = [item["description"] for item in items]
    item_embeddings = get_embeddings(item_descriptions)

    # Find the best matching items based on cosine similarity
    recommendations = []
    for i, item_embedding in enumerate(item_embeddings):
        similarities = [cosine_similarity(item_embedding, pref_emb) for pref_emb in preference_embeddings]
        avg_similarity = np.mean(similarities)
        
        # Append to recommendations if similarity is greater than 0.7
        if avg_similarity > 0.:
            recommendations.append((items[i], avg_similarity))
    
    # Sort recommendations by similarity (highest first)
    recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)

    # Convert numpy float32 to native float and filter out low-similarity recommendations
    top_recommendations = [
        {"id": rec[0]["id"], "name": rec[0]["name"], "similarity": float(rec[1])}
        for rec in recommendations[:3]  # Adjust the number of top recommendations as needed
    ]

    return jsonify({"recommendations": top_recommendations})


if __name__ == '__main__':
    app.run(debug=True)
