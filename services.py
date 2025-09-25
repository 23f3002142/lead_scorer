from models import Lead, Offer
import os
from dotenv import load_dotenv
import google.generativeai as genai 
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY) #type:ignore

# --- Rule-Based Scoring Configuration ---
# You can easily adjust these keywords to refine the scoring logic
DECISION_MAKER_KEYWORDS = ['head', 'vp', 'director', 'chief', 'founder', 'ceo', 'manager']
INFLUENCER_KEYWORDS = ['lead', 'senior', 'principal', 'architect']

def calculate_rule_score(lead: Lead, offer: Offer) -> int:
    """
    Calculates a score for a lead based on a set of predefined rules.
    Maximum possible score is 50.
    """
    score = 0
    
    # Rule 1: Role Relevance (max 20 points)
    if lead.role:
        role_lower = lead.role.lower()
        if any(keyword in role_lower for keyword in DECISION_MAKER_KEYWORDS):
            score += 20
        elif any(keyword in role_lower for keyword in INFLUENCER_KEYWORDS):
            score += 10

    # Rule 2: Industry Match (max 20 points)
    if lead.industry and offer and offer.ideal_use_cases:
        lead_industry_lower = lead.industry.lower()
        # Check for exact or partial matches in the list of ideal use cases
        for icp in offer.ideal_use_cases:
            icp_lower = icp.lower()
            if icp_lower in lead_industry_lower: # Exact or substring match
                score += 20
                break 
        #adjacent option is still yet to be made

    # Rule 3: Data Completeness (max 10 points)
    required_fields = [
        lead.name, 
        lead.role, 
        lead.company, 
        lead.industry, 
        lead.location, 
        lead.linkedin_bio
    ]
    # Check if all fields are not None and not just empty strings
    if all(field and str(field).strip() for field in required_fields):
        score += 10

    return score

def get_ai_score_and_reasoning(lead: Lead, offer: Offer) -> dict:
    """
    Uses Google's Gemini model to score a lead's intent and provide reasoning.
    """
    if not GEMINI_API_KEY:
        return {
            "ai_points": 0,
            "intent": "Error",
            "reasoning": "Gemini API key is not configured."
        }
    
    # The prompt is the same! We just send it to a different model.
    prompt = f"""
    You are an expert B2B sales development representative. Your task is to analyze a prospect (lead) and determine their buying intent for a specific product/offer.

    **Product/Offer Information:**
    - Name: "{offer.name}"
    - Value Propositions: {', '.join(offer.value_props)}
    - Ideal Customer Profile / Use Cases: {', '.join(offer.ideal_use_cases)}

    **Prospect (Lead) Information:**
    - Name: {lead.name}
    - Role: {lead.role}
    - Company: {lead.company}
    - Industry: {lead.industry}
    - LinkedIn Bio: {lead.linkedin_bio}

    **Your Task:**
    Based on all the information above, classify the prospect's buying intent as High, Medium, or Low. Then, provide a concise 1-2 sentence explanation for your classification.

    **Output Format (Strictly follow this):**
    Intent: [High/Medium/Low]
    Reasoning: [Your 1-2 sentence explanation here]
    """

    try:
        # Initialize the Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash') #type: ignore
        # Send the prompt to the model
        response = model.generate_content(prompt)
        
        content = response.text.strip()
        
        # Parse the response (this logic remains the same)
        intent_line = [line for line in content.split('\n') if 'Intent:' in line][0]
        reasoning_line = [line for line in content.split('\n') if 'Reasoning:' in line][0]
        
        intent = intent_line.split(':')[1].strip()
        reasoning = reasoning_line.split(':', 1)[1].strip()

        # Map intent to points (this logic remains the same)
        points_map = {"High": 50, "Medium": 30, "Low": 10}
        ai_points = points_map.get(intent, 0)

        return {
            "ai_points": ai_points,
            "intent": intent,
            "reasoning": reasoning
        }

    except Exception as e:
        print(f"An error occurred with the Gemini API: {e}")
        return {
            "ai_points": 0,
            "intent": "Error",
            "reasoning": str(e)
        }