from utils import load_data, find_condition

def main():
    data = load_data()

    print("HealthBot: Hello! Describe your symptoms.")
    print("DISCLAIMER: I can give you a solution if your symptoms are mild, for serious/severe symptoms,please refer an actual doctor\n")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("HealthBot: Take care!")
            break

        condition, info = find_condition(user_input, data)

        if info:
            if info["severity"] == "high":
                print("HealthBot: WARNING⚠️", info["advice"])
            else:
                print("HealthBot:", info["advice"])
        else:
            print("HealthBot: I'm not sure about this. Please consult a healthcare professional.")

if __name__ == "__main__":
    main()