import json
import os
import re


FOLLOW_UP_RULES = {
    "rash": {
        "question": "Okay, what kind of rash? Small rash in a particular area? Or spread across your body?",
        "responses": {

            ("small", "localized", "particular", "neck", "arm", "leg"): {
                "condition": "sweat rash",
                "advice": "This may be a sweat/heat rash. Keep the area dry, avoid tight clothing, and apply calamine lotion or ice packs.",
                "severity": "low"
            },

            ("spread","all", "everywhere", "over", "whole","large"): {
                "condition": "allergy",
                "advice": "This could be an allergic reaction (hives). Avoid possible allergens and consider antihistamines. Seek medical help if breathing issues occur.",
                "severity": "medium"
            }
        }
    }
    
}


conversation_state = None

def reset_state():
    global conversation_state
    conversation_state = None


def load_data():
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, "health_data.json")

    with open(file_path, "r") as file:
        return json.load(file)



def clean_input(user_input):
    user_input = user_input.lower()
    user_input = re.sub(r"[^\w\s]", "", user_input)
    return user_input.split()


def find_condition(user_input, data):
    global conversation_state

    words = clean_input(user_input)

    if conversation_state:

        rule = FOLLOW_UP_RULES[conversation_state]

        for keywords, response in rule["responses"].items():
            for word in words:
                if word in keywords:
                    conversation_state = None
                    return response["condition"], response


        return None, {
            "advice": "Please clarify your answer/be more specific?.",
            "severity": "low"
        }

    for trigger_word in FOLLOW_UP_RULES:
     for word in words:
        if word.startswith(trigger_word):
            conversation_state = trigger_word
            return None, {
                "advice": FOLLOW_UP_RULES[trigger_word]["question"],
                "severity": "low"
            }

    user_input_lower = " ".join(words)

    for condition, info in data.items():


        if condition.lower() in user_input_lower:
            return condition, info


        for symptom in info["symptoms"]:
            if symptom.lower() in words:
                return condition, info

    return None, None