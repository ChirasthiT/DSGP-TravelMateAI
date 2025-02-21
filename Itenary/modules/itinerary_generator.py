import groq
from datetime import datetime
import json

class ItineraryGenerator:
    def __init__(self, api_key):
        self.client = groq.Client(api_key=api_key)

    def create_prompt(self, formatted_info, recommendations, arrival_date_str, arrival_time, departure_date_str, departure_time, additional_details=""):
        """Create a structured prompt for the LLM with JSON response format"""
        try:
            # Parse dates and calculate duration
            arrival_date = datetime.strptime(arrival_date_str, '%Y-%m-%d')
            departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d')
            days = (departure_date - arrival_date).days + 1

            # Prepare recommended activities section
            location_activities = [
                f"{loc}: {', '.join(acts)}" 
                for loc, acts in recommendations.items()
            ]

            # Build the structured prompt
            prompt = f"""You are a tourism company. Create a very detailed and attractive Sri Lanka travel itinerary based on these specifications for the customers:
            
            The customer will be arriving from the airport and departing from the airport at the end
            Whenever applicable start with 'Welcome at the airport and transfer to a hotel near airport for a short stay.'
            When appropriate let the customer rest at the hotel. (But don't need to provide information about hotels)

Travel Details:
- Locations: {', '.join(formatted_info['locations'])}
- Traveling with: {formatted_info['companion']}
- Interest Categories: {', '.join(formatted_info['interests'])}
- Budget Level: {formatted_info['budget']}
- Duration: {days} days
- Arrival: {arrival_date.strftime('%Y-%m-%d')} ({arrival_time})
- Departure: {departure_date.strftime('%Y-%m-%d')} ({departure_time})
- Additional Notes: {additional_details or 'None'}

Recommended Activities:
{chr(10).join(location_activities)}

Create a very logical and practical itinerary with:
1. Travel times between locations in parentheses. Consider the order of the locations very practically (based on the distances and etc)
2. Daily activities using recommended activities
3. Clear day-by-day structure
4. Entrance fees where applicable


Return only valid JSON in this exact structure:
{{
    "itinerary": [
        {{
            "location": "Location (Approx: Xhrs from previous) [ex: Galle (Approx: travel time 2.5hrs from airport)]",
            "check_in": "YYYY-MM-DD",
            "check_out": "YYYY-MM-DD",
            "nights": X,
            "details": "Extremely detailed and impressive day-by-day activities [ex: Day 1: Welcome at the airport and transfer to a hotel near airport for a short stay. Visit Pinnawala elephant orphanage en-route Sigiriya. Engage in elephant walking, bathing & feeding at Millennium Foundation. Reach Sigiriya in the afternoon and engage in a Jeep safari in the wilderness.  \\nDay 2: After breakfast, climb Sigiriya rock fortress. Climb Dambulla cave temple & visit Golden temple. Engage in a Village tour - experience authentic village life including visiting a farm, climbing a tree house, catamaran ride through village's lake and help prepare lunch.]"
        }}
    ],
    "fees": [
        {{
            "location": "Location [ex: Galle]",
            "activity": "Activity [ex: Galle Fort visit]",
            "rate": XX
        }}
    ]
}}
(NO PREAMBLE)"""
            return prompt
        except Exception as e:
            return f"Error creating prompt: {str(e)}"

    def generate_itinerary(self, prompt):
        """Generate and validate JSON itinerary"""
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert tourism planner specializing in Sri Lanka. Create very detailed itineraries with clear day-by-day structure and practical travel times"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2500
            )

            # Extract and clean JSON response
            response = completion.choices[0].message.content
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                response = response.split('```')[1]
            
            # Validate and return parsed JSON
            itinerary = json.loads(response.strip())
            if not isinstance(itinerary.get('itinerary', []), list):
                raise ValueError("Invalid itinerary structure")
            return itinerary
        except Exception as e:
            return {"error": f"Generation failed: {str(e)}"}