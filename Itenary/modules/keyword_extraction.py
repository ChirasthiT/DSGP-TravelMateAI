import spacy
from spacy.matcher import Matcher
from collections import defaultdict
from difflib import get_close_matches
from .constants import (VALID_LOCATIONS, VALID_COMPANIONS, VALID_BUDGETS, INTEREST_CATEGORIES)

def fuzzy_match(word, valid_list, threshold=0.85):
    """Find closest match in valid list using fuzzy matching"""
    # Convert multi-word items to lowercase for comparison
    word = word.lower()
    # Try to find close matches
    matches = get_close_matches(word, valid_list, n=1, cutoff=threshold)
    return matches[0] if matches else None

def initialize_spacy():
    """Initialize spaCy with the English language model"""
    try:
        nlp = spacy.load("en_core_web_lg")
    except OSError:
        print("Downloading spaCy model...")
        spacy.cli.download("en_core_web_lg")
        nlp = spacy.load("en_core_web_lg")
    return nlp

def create_matcher(nlp):
    """Create pattern matcher for basic term detection"""
    matcher = Matcher(nlp.vocab)

    # Add basic patterns for initial detection
    for location in VALID_LOCATIONS:
        pattern = [{"LOWER": word.lower()} for word in location.split()]
        matcher.add(f"LOCATION_{location.replace(' ', '_')}", [pattern])

    for companion in VALID_COMPANIONS:
        matcher.add(f"COMPANION_{companion}", [[{"LOWER": companion}]])

    for budget in VALID_BUDGETS:
        matcher.add(f"BUDGET_{budget}", [[{"LOWER": budget}]])

    return matcher

def extract_interests_using_embeddings(doc, nlp):
    """Extract interests using word embeddings and semantic similarity"""
    category_scores = defaultdict(float)

    # Process each sentence in the text
    for sent in doc.sents:
        # Get all nouns, adjectives, and verbs from the sentence
        keywords = [token for token in sent
                   if token.pos_ in ['NOUN', 'ADJ', 'VERB']
                   and not token.is_stop]

        # Compare each keyword against our interest categories and their related terms
        for keyword in keywords:
            for category, related_terms in INTEREST_CATEGORIES.items():
                # Check similarity with each related term
                for term in related_terms:
                    term_doc = nlp(term)
                    similarity = keyword.similarity(term_doc)

                    # If similarity is high enough, consider it a match
                    if similarity > 0.7:  # Threshold can be adjusted
                        category_scores[category] += similarity

    # Filter categories with significant scores
    significant_categories = {cat: score for cat, score in category_scores.items()
                            if score > 0.8}  # Threshold can be adjusted

    return list(significant_categories.keys())

def extract_information(text, nlp, matcher):
    """Extract travel information from the input text"""
    doc = nlp(text.lower())

    # Initialize result containers
    locations = set()
    companions = set()
    budget = set()

    # Extract words that might be locations, companions, or budget levels
    words = text.lower().split()

    # Try fuzzy matching for locations (including multi-word locations)
    text_lower = text.lower()
    for location in VALID_LOCATIONS:
        if location.lower() in text_lower:
            locations.add(location.title())
        else:
            # Try fuzzy matching for parts of multi-word locations
            location_parts = location.split()
            if all(any(get_close_matches(part, words, cutoff=0.85)) for part in location_parts):
                locations.add(location.title())

    # Try fuzzy matching for companions
    for word in words:
        companion_match = fuzzy_match(word, VALID_COMPANIONS)
        if companion_match:
            companions.add(companion_match)

    # Try fuzzy matching for budget
    for word in words:
        budget_match = fuzzy_match(word, VALID_BUDGETS)
        if budget_match:
            budget.add(budget_match)

    # Extract interests using embeddings
    interest_categories = extract_interests_using_embeddings(doc, nlp)

    return {
        "locations": sorted(list(locations)),
        "companion": list(companions)[0] if companions else None,
        "interests": sorted(interest_categories),
        "budget": list(budget)[0] if budget else None
    }

def format_output(results):
    """Format the extracted information for display"""
    output = "\nExtracted Travel Information:\n"
    output += "------------------------\n"
    output += f"Destinations: {', '.join(results['locations'])}\n"
    output += f"Traveling with: {results['companion'].title() if results['companion'] else 'Not specified'}\n"
    output += f"Interest Categories: {', '.join(results['interests']).title()}\n"
    output += f"Budget level: {results['budget'].title() if results['budget'] else 'Not specified'}\n"
    return output

def process_travel_description(text):
    """Main function to process travel descriptions"""
    nlp = initialize_spacy()
    matcher = create_matcher(nlp)
    results = extract_information(text, nlp, matcher)
    return format_output(results)