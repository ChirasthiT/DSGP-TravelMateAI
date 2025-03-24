def determine_action(risk_level):
   actions = {
       "High": "Contact police and emergency services immediately",
       "Medium": "Alert emergency contacts and provide safety instructions",
       "Low": "Provide safety instructions and option to call for help"
   }
   return actions.get(risk_level, "No action required")