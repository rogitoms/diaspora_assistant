def calculate_risk(intent: str, entities: dict) -> tuple:
    """
    Calculate risk score (0-100) for a diaspora task request.
    Returns (total_score, breakdown_dict)

    Scoring logic designed for Kenyan diaspora context:
    - Land title fraud is very common in Kenya → high base risk for verify_document
    - Large urgent money transfers are a common scam vector → stacked risk
    - Unknown recipients for money transfers are a red flag
    - High urgency across any intent inflates risk
    """

    score = 0
    breakdown = {}

    # -------------------------------------------------------
    # 1. Base risk by intent
    # Land/document fraud is rampant in Kenya (high base)
    # Money transfers carry inherent financial risk (medium-high)
    # Service hires and logistics are lower risk
    # -------------------------------------------------------
    base_scores = {
        "send_money":       30,
        "verify_document":  25,
        "hire_service":     15,
        "airport_transfer": 10,
        "check_status":      0,
    }
    breakdown["intent_base"] = base_scores.get(intent, 10)
    score += breakdown["intent_base"]

    # -------------------------------------------------------
    # 2. Amount risk (only relevant for send_money)
    # Large transfers are higher risk — potential fraud or error
    # -------------------------------------------------------
    amount = entities.get("amount") or 0
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        amount = 0

    if amount > 100000:
        breakdown["amount_risk"] = 25   # very large transfer
    elif amount > 50000:
        breakdown["amount_risk"] = 15   # significant transfer
    elif amount > 10000:
        breakdown["amount_risk"] = 8    # moderate transfer
    else:
        breakdown["amount_risk"] = 0    # small or no amount
    score += breakdown["amount_risk"]

    # -------------------------------------------------------
    # 3. Urgency risk
    # High urgency + large amount is a classic fraud pattern
    # "Send money urgently" requests need extra scrutiny
    # -------------------------------------------------------
    urgency_scores = {
        "high":   20,
        "medium": 10,
        "low":     0,
    }
    breakdown["urgency_risk"] = urgency_scores.get(
        entities.get("urgency", "low"), 0
    )
    score += breakdown["urgency_risk"]

    # -------------------------------------------------------
    # 4. Document type risk
    # Land titles in Kenya are frequently forged or disputed
    # National IDs and certificates carry moderate risk
    # -------------------------------------------------------
    doc_type = (entities.get("document_type") or "").lower()
    if any(word in doc_type for word in ["land", "title", "deed", "plot"]):
        breakdown["document_risk"] = 20    # land fraud is very common
    elif any(word in doc_type for word in ["id", "passport", "certificate"]):
        breakdown["document_risk"] = 10    # identity documents moderate risk
    elif doc_type:
        breakdown["document_risk"] = 5     # any other document
    else:
        breakdown["document_risk"] = 0
    score += breakdown["document_risk"]

    # -------------------------------------------------------
    # 5. Unknown recipient risk (send_money only)
    # No named recipient = cannot verify who money is going to
    # -------------------------------------------------------
    if intent == "send_money" and not entities.get("recipient"):
        breakdown["unknown_recipient"] = 15
    else:
        breakdown["unknown_recipient"] = 0
    score += breakdown["unknown_recipient"]

    # -------------------------------------------------------
    # 6. No location provided
    # Missing location makes it harder to verify or action
    # -------------------------------------------------------
    if not entities.get("location"):
        breakdown["no_location"] = 5
    else:
        breakdown["no_location"] = 0
    score += breakdown["no_location"]

    # Cap at 100
    final_score = min(score, 100)

    return final_score, breakdown


def get_risk_label(score: int) -> str:
    """
    Convert numeric score to human readable label for the UI.
    """
    if score >= 70:
        return "High"
    elif score >= 40:
        return "Medium"
    else:
        return "Low"