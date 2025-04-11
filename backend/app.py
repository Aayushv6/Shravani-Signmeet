from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
import os
import json

app = Flask(__name__)
CORS(app)

# === Load the trained gesture recognition model ===
model_path = os.path.join(os.path.dirname(__file__), '../frontend/model/gesture_model.pkl')
model = None

try:
    model = joblib.load(model_path)
    print(f"✅ Model loaded successfully from: {model_path}")
except Exception as e:
    print(f"❌ Failed to load model from {model_path}: {e}")

# === API route to recognize gesture from landmarks ===
@app.route('/api/recognize', methods=['POST'])
def recognize():
    if model is None:
        print("❌ Model not available.")
        return jsonify({"error": "Model not loaded"}), 500

    data = request.get_json()

    if not data or 'landmarks' not in data:
        print("⚠️ Invalid request: 'landmarks' not provided.")
        return jsonify({"error": "Missing landmarks in request"}), 400

    try:
        landmarks = np.array(data['landmarks']).flatten()
        print(f"👉 Received landmarks: {landmarks.tolist()}")
        print(f"👉 Landmark shape: {landmarks.shape}")

        if landmarks.shape[0] != 63:
            msg = f"Invalid landmark shape: expected 63 values, got {landmarks.shape[0]}"
            print(f"⚠️ {msg}")
            return jsonify({"error": msg}), 400

        gesture = model.predict([landmarks])[0]
        print(f"✅ Predicted gesture: {gesture}")
        return jsonify({"name": gesture})

    except Exception as e:
        print(f"❌ Error during prediction: {e}")
        return jsonify({"error": str(e)}), 500
    
    
# === API route to delete gesture data ===
@app.route('/api/delete-data', methods=['DELETE'])
def delete_data():
    try:
        save_path = os.path.join(os.path.dirname(__file__), 'gesture_data.json')

        # If the file exists, overwrite it with empty list
        if os.path.exists(save_path):
            with open(save_path, 'w') as f:
                json.dump([], f, indent=2)
            print(f"🗑️ Gesture data deleted from: {save_path}")
        else:
            print("ℹ️ No gesture data file found to delete.")

        return jsonify({"message": "Gesture data deleted successfully"}), 200

    except Exception as e:
        print(f"❌ Error deleting gesture data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/save-data', methods=['POST'])
def save_data():
    data = request.get_json()

    if not data or not isinstance(data, list):
        print("⚠️ Invalid or empty data received.")
        return jsonify({"error": "Invalid data format"}), 400

    try:
        save_path = os.path.join(os.path.dirname(__file__), 'gesture_data.json')

        # Load existing data
        if os.path.exists(save_path):
            with open(save_path, 'r') as f:
                existing_data = json.load(f)
        else:
            existing_data = []

        # Convert existing data to a dict for fast label lookup
        data_dict = {
            item["label"]: item["landmarks"]
            for item in existing_data
            if "label" in item and "landmarks" in item
        }

        # Process and update entries
        for entry in data:
            label = entry.get("label")
            landmarks = entry.get("landmarks")

            if label and landmarks:
                # Flatten landmarks if in {x,y,z} format
                if isinstance(landmarks[0], dict):
                    flattened = []
                    for point in landmarks:
                        flattened.extend([point["x"], point["y"], point["z"]])
                    landmarks = flattened

                # Update dictionary with new or overridden label
                data_dict[label] = landmarks

        # Convert back to list format
        final_data = [{"label": label, "landmarks": landmarks} for label, landmarks in data_dict.items()]

        # Save final data
        with open(save_path, 'w') as f:
            json.dump(final_data, f, indent=2)

        print(f"✅ Gesture data saved (1 per label, flattened) to: {save_path}")
        return jsonify({"message": "Data saved successfully"}), 200

    except Exception as e:
        print(f"❌ Error saving data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/get-labels', methods=['GET'])
def get_labels():
    try:
        save_path = os.path.join(os.path.dirname(__file__), 'gesture_data.json')
        if not os.path.exists(save_path):
            return jsonify([])

        with open(save_path, 'r') as f:
            data = json.load(f)

        labels = [item['label'] for item in data if 'label' in item]
        return jsonify(labels)

    except Exception as e:
        print(f"❌ Error reading labels: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
