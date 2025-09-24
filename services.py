from models import Lead, Offer

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