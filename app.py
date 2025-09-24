from flask import Flask, request, jsonify
import pandas as pd
import io
import os

# Import the 'db' object and our models from model.py
from models import db, Offer, Lead

app = Flask(__name__)

# --- Database Configuration ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with our app
db.init_app(app)

# Create the database tables if they don't exist
with app.app_context():
    db.create_all()
# --- End Configuration ---


@app.route("/")
def index():
    return jsonify({"status": "Flask API with SQLAlchemy is running"})

@app.route("/offer", methods=['POST'])
def set_offer():
    data = request.get_json()
    if not data or not all(k in data for k in ["name", "value_props", "ideal_use_cases"]):
        return jsonify({"error": "Invalid or incomplete offer data provided."}), 400

    # For this assignment, we assume only one offer. Clear the old one.
    Offer.query.delete()
    
    new_offer = Offer(
        name=data['name'], 
        value_props=data['value_props'], 
        ideal_use_cases=data['ideal_use_cases']
    )
    db.session.add(new_offer)
    db.session.commit()
    
    return jsonify({"message": "Offer details have been set successfully.", "offer": new_offer.to_dict()}), 201

@app.route("/leads/upload", methods=['POST'])
def upload_leads_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request."}), 400
    
    file = request.files['file']
    # ... (file name and type checks remain the same) ...

    # Clear old leads before uploading new ones
    Lead.query.delete()

    df = pd.read_csv(io.StringIO(file.read().decode('utf-8')))
    # ... (column validation remains the same) ...
    
    # Create Lead objects and add to the database session
    new_leads = [Lead(**row) for row in df.to_dict(orient='records')]
    db.session.add_all(new_leads)
    db.session.commit()

    return jsonify({"message": f"{len(new_leads)} leads have been uploaded and are ready for scoring."}), 201

@app.route("/score", methods=['POST'])
def score_leads():
    # TODO: Implement scoring logic by querying leads, scoring them, and updating the DB.
    return jsonify({"message": "Scoring initiated (logic to be implemented)."})

@app.route("/results", methods=['GET'])
def get_results():
    all_leads = Lead.query.all()
    # Convert lead objects to dictionaries for the JSON response
    results = [lead.to_dict() for lead in all_leads]
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)