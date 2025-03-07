def format_extracted_info(extracted_info):
    """Format the extracted information from string output to dictionary"""
    # Initialize default values
    locations = []
    companion = "solo"
    interests = []
    budget = "medium"

    # Extract information from the string
    lines = extracted_info.split('\n')
    for line in lines:
        if "Destinations:" in line:
            locations = [loc.strip() for loc in line.split('Destinations:')[1].strip().split(',')]
        elif "Traveling with:" in line:
            companion = line.split('Traveling with:')[1].strip()
            if companion == "Not specified":
                companion = "solo"
        elif "Interest Categories:" in line:
            interests = [interest.strip().lower() for interest in line.split('Interest Categories:')[1].strip().split(',')]
        elif "Budget level:" in line:
            budget = line.split('Budget level:')[1].strip()
            if budget == "Not specified":
                budget = "medium"

    return {
        'locations': locations,
        'companion': companion,
        'interests': interests,
        'budget': budget
    }