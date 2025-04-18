# chatbot.py

def chatbot_response(user_input):
    responses = {
        "hello": "Hi there!",
        "how are you": "I'm a bot, so I don't have feelings, but thanks for asking!",
        "bye": "Goodbye! Have a great day!",
    }
    return responses.get(user_input.lower(), "I don't understand that.")

def main():
    print("Welcome to the Terminal Chatbot! Type 'bye' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "bye":
            print("Chatbot: Goodbye! Have a great day!")
            break
        response = chatbot_response(user_input)
        print(f"Chatbot: {response}")

if __name__ == "__main__":
    main()
