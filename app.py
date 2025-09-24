from flask import Flask, request, jsonify
from services import calculate_rule_score
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
        name=data['name'], #type: ignore
        value_props=data['value_props'], #type: ignore
        ideal_use_cases=data['ideal_use_cases']#type: ignore
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
    new_leads = [Lead(**row) for row in df.to_dict(orient='records')] #type: ignore
    db.session.add_all(new_leads)
    db.session.commit()

    return jsonify({"message": f"{len(new_leads)} leads have been uploaded and are ready for scoring."}), 201

@@app.route("/score", methods=['POST'])
def score_leads():
    """
    Scores all uploaded leads using both rule-based and AI layers.
    """
    current_offer = Offer.query.first()
    if not current_offer:
        return jsonify({"error": "No offer has been set. Please POST to /offer first."}), 400

    leads_to_score = Lead.query.all()
    if not leads_to_score:
        return jsonify({"message": "No leads found to score."}), 200

    scored_count = 0
    for lead in leads_to_score:
        # 1. Get score from the rule-based layer
        rule_score = calculate_rule_score(lead, current_offer)

        # 2. Get score and reasoning from the AI layer
        ai_result = get_ai_score_and_reasoning(lead, current_offer)
        
        # 3. Combine scores and update lead record
        lead.score = rule_score + ai_result["ai_points"]
        lead.intent = ai_result["intent"]
        lead.reasoning = ai_result["reasoning"]
        scored_count += 1
            
    # Commit all the updates to the database
    db.session.commit()

    return jsonify({
        "message": f"Successfully scored {scored_count} leads.",
        "note": "Scores are a combination of rule-based logic and AI analysis."
    })


@app.route("/results", methods=['GET'])
def get_results():
    all_leads = Lead.query.all()
    # Convert lead objects to dictionaries for the JSON response
    results = [lead.to_dict() for lead in all_leads]
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)