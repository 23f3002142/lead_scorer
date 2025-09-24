from flask_sqlalchemy import SQLAlchemy

# We will create the 'db' instance in our main app.py and import it here
# To avoid circular imports, we initialize it in a separate file or within the app factory.
# For simplicity in this project, we will define it in app.py and import it.
db = SQLAlchemy()

class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    value_props = db.Column(db.JSON, nullable=False)
    ideal_use_cases = db.Column(db.JSON, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "value_props": self.value_props,
            "ideal_use_cases": self.ideal_use_cases,
        }

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100))
    company = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    location = db.Column(db.String(100))
    linkedin_bio = db.Column(db.Text)
    
    # Fields to be populated by the scoring logic
    score = db.Column(db.Integer, nullable=True)
    intent = db.Column(db.String(50), nullable=True)
    reasoning = db.Column(db.String(300), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "company": self.company,
            "industry": self.industry,
            "location": self.location,
            "linkedin_bio": self.linkedin_bio,
            "score": self.score,
            "intent": self.intent,
            "reasoning": self.reasoning,
        }