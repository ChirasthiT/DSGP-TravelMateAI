def evaluate_risk(content):

   high_risk_keywords = ["gun", "knife", "attack", "kidnapped", "fire"]
   medium_risk_keywords = ["lost", "stranded", "accident"]

   risk_score = 0
   risk_level = "Low"

   for word in content.lower().split():
       if word in high_risk_keywords:
           risk_score += 10
       elif word in medium_risk_keywords:
           risk_score += 5

   if risk_score >= 10:
       risk_level = "High"
   elif risk_score >= 5:
       risk_level = "Medium"

   return risk_score, risk_level