# List of valid locations, companions, and budget levels
VALID_LOCATIONS = [
    "kandy", "sigiriya", "nuwara eliya", "ella",
    "hatton", "bentota", "galle", "yala", "colombo", "anuradhapura",
    "polonnaruwa", "trincomalee", "jaffna", "pasikuda", "arugam bay",
    "negombo", "weligama", "mirissa", "tangalle", "hambantota",
    "Udawalawe", "Mannar", "Wilpattu"
]

VALID_COMPANIONS = ["family", "friends", "partner", "solo"]

VALID_BUDGETS = ["low", "medium", "high"]

# Expanded interest categories with comprehensive related terms
INTEREST_CATEGORIES = {
    "nature & wildlife": ["nature", "wildlife", "landscapes", "scenery", "mountains", "forest", "hiking",
                         "trekking", "camping", "outdoors", "flora", "fauna", "environment", "ecology",
                         "birds", "animals", "safari", "national park", "botanical", "garden", "waterfall"],

    "culture & heritage": ["culture", "heritage", "traditions", "customs", "local", "traditional", "cultural",
                          "temples", "religion", "spiritual", "meditation", "buddhist", "historical", "ancient",
                          "ruins", "architecture", "museum", "art", "crafts", "festival", "ceremony"],

    "adventure & sports": ["adventure", "hiking", "trekking", "climbing", "surfing", "diving", "snorkeling",
                          "water sports", "safari", "camping", "kayaking", "rafting", "adrenaline",
                          "extreme sports", "cycling", "mountain biking", "parasailing", "zip lining"],

    "wellness & relaxation": ["relaxation", "peaceful", "calm", "quiet", "serene", "spa", "wellness", "yoga",
                             "meditation", "mindfulness", "retreat", "beach", "resort", "luxury", "ayurveda",
                             "massage", "healing", "therapy", "rejuvenation"],

    "food & cuisine": ["food", "cuisine", "culinary", "gastronomy", "restaurants", "dining", "cooking",
                      "street food", "local food", "traditional food", "seafood", "spices", "tea", "market",
                      "authentic", "flavors", "tastes", "dishes", "desserts", "beverages"],

    "photography & arts": ["photography", "photos", "camera", "scenic", "landscapes", "portraits",
                          "wildlife photography", "nature photography", "photogenic", "sunset", "sunrise",
                          "views", "composition", "lighting", "artistic", "creative"],

    "beach & water activities": ["beach", "swimming", "surfing", "snorkeling", "diving", "water sports",
                                "boat", "sailing", "kayaking", "fishing", "marine", "ocean", "sea", "coast",
                                "waves", "coral", "reef", "island", "beach walking"],

    "entertainment & nightlife": ["nightlife", "entertainment", "music", "dancing", "parties", "festivals",
                                 "shows", "concerts", "bars", "clubs", "social", "shopping", "markets",
                                 "cinema", "theater", "performances"],

    "education & learning": ["education", "learning", "workshop", "class", "cooking class", "language",
                            "history", "culture", "archaeology", "architecture", "art class", "craft workshop",
                            "tea plantation", "spice garden", "heritage site"],

    "spiritual & religious": ["spiritual", "religious", "temple", "meditation", "buddhist", "hindu",
                             "christian", "muslim", "sacred", "pilgrimage", "worship", "ritual", "ceremony",
                             "blessing", "prayer"]
}