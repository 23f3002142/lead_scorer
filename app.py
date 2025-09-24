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

@app.route("/score", methods=['POST'])
def score_leads():
    """
    Scores all uploaded leads using the rule-based and AI layers.
    (Currently, only the rule-based layer is implemented).
    """
    # 1. Fetch the current offer context
    current_offer = Offer.query.first()
    if not current_offer:
        return jsonify({"error": "No offer has been set. Please POST to /offer first."}), 400

    # 2. Fetch all leads that haven't been scored yet
    leads_to_score = Lead.query.all()
    if not leads_to_score:
        return jsonify({"message": "No leads found to score."}), 200

    # 3. Score each lead and update its record
    for lead in leads_to_score:
        rule_score = calculate_rule_score(lead, current_offer)
        
        # For now, the total score is just the rule score.
        # We will add the AI score in the next step.
        lead.score = rule_score
        
        # We'll update intent and reasoning later.
            
    # 4. Commit all the score updates to the database
    db.session.commit()

    return jsonify({
        "message": f"Successfully scored {len(leads_to_score)} leads.",
        "note": "Currently using rule-based scoring only."
    })
@app.route("/results", methods=['GET'])
def get_results():
    all_leads = Lead.query.all()
    # Convert lead objects to dictionaries for the JSON response
    results = [lead.to_dict() for lead in all_leads]
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)