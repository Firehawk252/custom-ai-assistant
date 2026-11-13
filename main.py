# Custom AI Assistant
# Firehawk252 11/11/2026
# v.1.0

import ollama
import os
import json

# This function:
#   Accepts the conversation history as an argument
#   Uses ollama.chat() to send the messages to llama3.2
#   Retrieves the response from response["message"]["content"]
#   Adds the AI response to the existing messages list
#   Prints the response

def ask_ai(messages):

    try:
        response = ollama.chat(
            model="llama3.2",
            messages=messages
        )
        answer = response["message"]["content"]
        messages.append({"role": "assistant", "content": answer})
        print(answer)
        return answer
    except Exception as error:
            print(error)
            print("AI service is unavailable. Please try again later.")

# This function gives the ability to let the assistant display the response as it's being generated
def ask_ai_stream(messages):
    full_response = ""

    try:
        # Request a streamed response from the local Ollama model
        stream = ollama.chat(
            model = "llama3.2",
            messages = messages,
            stream = True
        )

        # Process each piece of the response as it arrives
        for chunk in stream:
            token = chunk["message"]["content"]
            full_response += token

            # Send each piece back to the GUI
            yield token

        # Save the completed response to the conversation history
        messages.append({"role": "assistant", "content": full_response})

    except Exception as error:
        print(error)
        yield "\nAI service is unavailable. Please try again later."

# This function handles message creation based on user input for personality, tone, language, technical level
def create_messages(personality, tone, response_length, language, technical_level, creativity, custom_instructions, memories):

    # Personality options
    if personality == "Professional":
        instructions = "Communicate formally and provide informative responses."
    elif personality == "Casual":
        instructions = "Use friendly, conversational language."
    elif personality == "Teacher":
        instructions = "Explain concepts step by step with examples when necessary, be helpful."
    elif personality == "Concise":
        instructions = "Keep responses short and direct."
    elif personality == "Creative":
        instructions = "Use imaginative language and explore creative ideas."

    # Tone options
    if tone == "Formal":
        tone_instructions = "Use professional language and avoid slang."
    elif tone == "Friendly":
        tone_instructions = "Be warm, approachable, and conversational."
    elif tone == "Direct":
        tone_instructions = "Be straight to the point and avoid unnecessary details and filler words."
    elif tone == "Humorous":
        tone_instructions = "Use appropriate humor while remaining helpful. Be light-hearted and funny."

    # Response length options
    if response_length == "Short":
        length_instructions = "Brief answers with only the essential information."
    elif response_length == "Normal":
        length_instructions = "Balanced explanations with useful detail."
    elif response_length == "Detailed":
        length_instructions = "Thorough explanations with examples when necessary."

    # Language options
    language_instructions = "Respond in " + language + "."

    # Technical level options
    if technical_level == "Beginner":
        technical_level_instructions = "Assume little or no prior knowledge; explain terminology."
    elif technical_level == "Intermediate":
        technical_level_instructions = "Assume basic familiarity with the subject."
    elif technical_level == "Advanced":
        technical_level_instructions = "Use technical terminology and in-depth explanations"

    # Creative responses options
    if creativity == "Low":
        creativity_instructions = "Focus on factual, predictable, and straightforward responses."
    elif creativity == "Medium":
        creativity_instructions = "Balance factual responses with creative ideas."
    elif creativity == "High":
        creativity_instructions = "Encourage imaginative thinking and explore unconventional ideas."

    # Custom instructions
    custom_instructions_text = "Additional instructions: " + custom_instructions if custom_instructions else ""

    # Long-term memory
    memory_instructions = "Remembered information: " + str(memories) if memories else ""

    messages = [
        {"role": "system", "content": "Answer questions on any topic. Be helpful and explain things clearly. " +
        instructions + " " + tone_instructions + " " + length_instructions + " " + language_instructions + " "
                                      + technical_level_instructions + " " + creativity_instructions + " "
                                      + custom_instructions_text + " " + memory_instructions},
    ]

    return messages

# This function lets users enter their own instructions, which the AI will follow in addition to the selected personality and communication settings.
def select_custom_instructions():
    instructions = input("Enter custom instructions (or press Enter to skip): ")
    return instructions

# This function allows users to select a personality from five different options
def select_personality():
    while True:
        print("Which of the following personality options would you like to use?")
        print("1. Professional - Formal and informative")
        print("2. Casual - Friendly and conversational")
        print("3. Teacher - Explains concepts step by step")
        print("4. Concise - Gives short, direct answers")
        print("5. Creative - Imaginative and expressive")

        try:
            choice = int(input("Enter your choice: "))
            if choice == 1:
                return "Professional"
            elif choice == 2:
                return "Casual"
            elif choice == 3:
                return "Teacher"
            elif choice == 4:
                return "Concise"
            elif choice == 5:
                return "Creative"
            else:
                print("Invalid choice. Please select 1-5.")

        except ValueError:
            print("Invalid input. Please select 1-5.")

# This function allows users to choose how the assistant speaks, independently of its personality
def select_tone():
    while True:
        print("Which of the following tone options would you like to use?")
        print("1. Formal")
        print("2. Friendly")
        print("3. Direct")
        print("4. Humorous")

        try:
            choice = int(input("Enter your choice: "))
            if choice == 1:
                return "Formal"
            elif choice == 2:
                return "Friendly"
            elif choice == 3:
                return "Direct"
            elif choice == 4:
                return "Humorous"
            else:
                print("Invalid choice. Please select 1-4.")
        except ValueError:
            print("Invalid input. Please select 1-4.")

# This function lets users choose how detailed the responses should be
def select_response_length():
    while True:
        print("Which of the following response length options would you like to use?")
        print("1. Short - Brief answers with only the essential information")
        print("2. Normal - Balanced explanations with useful detail")
        print("3. Detailed - Thorough explanations with examples when necessary")

        try:
            choice = int(input("Enter your choice: "))
            if choice == 1:
                return "Short"
            elif choice == 2:
                return "Normal"
            elif choice == 3:
                return "Detailed"
            else:
                print("Invalid choice. Please select 1-3.")
        except ValueError:
            print("Invalid input. Please select 1-3.")

# This function allows users to choose the language the assistant responds in
def select_language():
    while True:
        print("Which of the following language options would you like to use?")
        print("1. English")
        print("2. French")
        print("3. Spanish")
        print("4. German")
        print("5. Other")

        try:
            choice = int(input("Enter your choice: "))
            if choice == 1:
                return "English"
            elif choice == 2:
                return "French"
            elif choice == 3:
                return "Spanish"
            elif choice == 4:
                return "German"
            elif choice == 5:
                return input("Enter the language you would like to use: ")
            else:
                print("Invalid choice. Please select 1-5.")
        except ValueError:
            print("Invalid input. Please select 1-5.")

# This function lets users choose how advanced the assistant's explanations should be
def select_technical_level():
    while True:
        print("Which of the following technical level options would you like to use?")
        print("1. Beginner - Assume little or no prior knowledge; explain terminology")
        print("2. Intermediate - Assume basic familiarity with the subject")
        print("3. Advanced - Use technical terminology and in-depth explanations")

        try:
            choice = int(input("Enter your choice: "))
            if choice == 1:
                return "Beginner"
            elif choice == 2:
                return "Intermediate"
            elif choice == 3:
                return "Advanced"
            else:
                print("Invalid choice. Please select 1-3.")
        except ValueError:
            print("Invalid input. Please select 1-3.")

# This function lets users control how imaginative or conventional the assistant's responses are
def select_creativity():
    while True:
        print("Which of the following creativity options would you like to use?")
        print("1. Low - Focus on factual, predictable, and straightforward responses")
        print("2. Medium - Balance factual responses with creative ideas")
        print("3. High - Encourage imaginative thinking and explore unconventional ideas")

        try:
            choice = int(input("Enter your choice: "))
            if choice == 1:
                return "Low"
            elif choice == 2:
                return "Medium"
            elif choice == 3:
                return "High"
            else:
                print("Invalid choice. Please select 1-3.")
        except ValueError:
            print("Invalid input. Please select 1-3.")

# This function will write the conversation history when the user types 'save'
def save_conversation(messages, settings, filename):
    if filename == "":
        print("Filename cannot be empty.")
        return

    elif os.path.exists(filename + ".json"):
        print("A conversation with that filename already exists.")
        return

    with open(filename + ".json", "w") as file:
        json.dump({"messages": messages,
                   "settings": settings
        }, file, indent=4)

    print("Conversation saved!")

# This function will let users open and resume previously saved conversations from the application
def load_conversation(filename):
    try:
        with open(filename + ".json", "r") as file:
            conversation = json.load(file)
            if not isinstance(conversation, dict):
                print("Invalid conversation file.")
                return None

            if "messages" not in conversation or "settings" not in conversation:
                print("Invalid conversation file.")
                return None

            messages = conversation["messages"]
            settings = conversation["settings"]

            if not isinstance(messages, list) or not isinstance(settings, dict):
                print("Invalid conversation file.")
                return None

            required_settings = [
                "personality",
                "tone",
                "response_length",
                "language",
                "technical_level",
                "creativity",
                "custom_instructions"
            ]

            for setting in required_settings:
                if setting not in settings:
                    print("Invalid conversation file.")
                    return None

            for message in messages:
                if (not isinstance(message, dict)
                    or "role" not in message
                    or "content" not in message
                    or not isinstance(message["role"], str)
                    or not isinstance(message["content"], str)):
                    print("Invalid conversation file.")
                    return None
            return conversation
    except FileNotFoundError:
        print("File not found.")
        return None
    except json.JSONDecodeError:
        print("Unable to load conversation.")
        return None

# This function will display the list of saved conversations
def list_saved_conversations():
    saved_files = []

    for filename in os.listdir():
        if filename.endswith(".json") and filename != "memory.json":
            saved_files.append(filename)

    for index, filename in enumerate(saved_files, start=1):
        print(str(index) + ". " + filename)

    return saved_files

# This function lets users delete a saved conversation by filename
def delete_conversation(filename):
    if os.path.exists(filename + ".json"):
        os.remove(filename + ".json")
        print("Conversation deleted!")
    else:
        print("File not found.")

# This function allows users to rename an existing saved conversation without opening or changing its contents
def rename_conversation(filename, new_filename):
    if os.path.exists(filename + ".json"):
        os.rename(filename + ".json", new_filename + ".json")
        print("Conversation renamed!")
    else:
        print("File not found.")

# This function will open memory.json and retrieve the saved memories then return them as a Python list
def load_memory():
    with open("memory.json", "r") as file:
        memory_data = json.load(file)

    return memory_data["memories"]

# This function saved memories to memory.json
def save_memory(memories):
    memory_data = {
        "_description": "Stores information the assistant should remember across conversations.",
        "memories": memories
    }

    with open("memory.json", "w") as file:
        json.dump(memory_data, file, indent=4)

def main():


    print("=============================")
    print("     Custom AI Assistant")
    print("=============================")

    # Initialize a new conversation
    # Accept a chosen personality
    personality = select_personality()
    tone = select_tone()
    response_length = select_response_length()
    language = select_language()
    technical_level = select_technical_level()
    creativity = select_creativity()
    custom_instructions = select_custom_instructions()
    memories = load_memory()
    messages = create_messages(personality, tone, response_length, language, technical_level, creativity, custom_instructions, memories)

    # Dictionary for saved settings so they can be restored alongside conversation history
    settings = {
        "personality": personality,
        "tone": tone,
        "response_length": response_length,
        "language": language,
        "technical_level": technical_level,
        "creativity": creativity,
        "custom_instructions": custom_instructions
    }

    # Keep the application running until told otherwise
    while True:
        question = input("You: \n").lower()

        if question == "help":
            print("'exit' will quit the application.")
            print("'settings' will allow you to change the assistant's personality settings.")
            print("'remember' will tell the assistant to remember across conversations.")
            print("'forget' will remove selected information from the assistant's memory.")
            print("'memories' will display everything the assistant currently remembers.")
            print("'clear' will start a fresh conversation.")
            print("'show' will display all current preferences.")
            print("'save' will save the conversation to a json file.")
            print("'load' will load a saved conversation.")
            print("'list' will list all saved conversations.")
            print("'delete' will delete a saved conversation.")
            print("'rename' will rename a saved conversation.")
            print("'help' will display available commands.")
            continue
        elif question == "exit":
            print("Goodbye!")
            break
        elif question == "settings":
            print("1. Personality")
            print("2. Tone")
            print("3. Response length")
            print("4. Language")
            print("5. Technical level")
            print("6. Creativity")
            print("7. Custom instructions")

            try:
                choice = int(input("Which setting would you like to change? "))

                if choice == 1:
                    personality = select_personality()
                elif choice == 2:
                    tone = select_tone()
                elif choice == 3:
                    response_length = select_response_length()
                elif choice == 4:
                    language = select_language()
                elif choice == 5:
                    technical_level = select_technical_level()
                elif choice == 6:
                    creativity = select_creativity()
                elif choice == 7:
                    custom_instructions = select_custom_instructions()
                else:
                    print("Invalid choice. Please select 1-7.")
            except ValueError:
                print("Invalid input. Please select 1-7.")

            # Update system instructions
            new_messages = create_messages(personality, tone, response_length, language, technical_level, creativity, custom_instructions, memories)
            messages[0] = new_messages[0]

            settings = {
                "personality": personality,
                "tone": tone,
                "response_length": response_length,
                "language": language,
                "technical_level": technical_level,
                "creativity": creativity,
                "custom_instructions": custom_instructions
            }

            continue

        elif question == "remember":
            memory = input("What would you like me to remember? \n")
            memories.append(memory)
            save_memory(memories)
            new_messages = create_messages(personality, tone, response_length, language, technical_level, creativity, custom_instructions, memories)
            messages[0] = new_messages[0]
            print("Memory saved!")
            continue

        elif question == 'forget':
            if len(memories) == 0:
                print("No memories to delete.")
                continue
            for index, memory in enumerate(memories, start=1):
                print(str(index) + ". " + memory)

            try:
                choice = int(input("Select a memory to delete: "))

                if choice < 1 or choice > len(memories):
                    print("Invalid choice.")
                    continue

                deleted_memory = memories.pop(choice - 1)
                save_memory(memories)

                new_messages = create_messages(personality, tone, response_length, language, technical_level, creativity, custom_instructions, memories)
                messages[0] = new_messages[0]

                print("Memory deleted:", deleted_memory)

            except ValueError:
                print("Invalid input.")

            continue

        elif question == "memories":
            if len(memories) == 0:
                print("No memories saved.")
            else:
                print("Saved Memories:")
                for index, memory in enumerate(memories, start=1):
                    print(str(index) + ". " + memory)
            continue

        elif question == "clear":
            messages = create_messages(personality, tone, response_length, language, technical_level, creativity, custom_instructions, memories)
            print("Conversation history cleared!")
            continue

        elif question == "show":
            print("Current Assistant Settings:")
            print("Personality:", personality)
            print("Tone:", tone)
            print("Response length:", response_length)
            print("Language:", language)
            print("Technical level:", technical_level)
            print("Creativity:", creativity)
            print("Custom instructions:", custom_instructions)
            continue

        elif question == "save":
            filename = input("Enter a filename: ")
            save_conversation(messages, settings, filename)
            continue

        elif question == "load":
            saved_files = list_saved_conversations()
            if len(saved_files) == 0:
                print("No saved conversations found.")
                continue
            try:
                choice = int(input("Select a conversation: "))
                if choice < 1 or choice > len(saved_files):
                    print("Invalid choice.")
                    continue
            except ValueError:
                print("Invalid choice.")
                continue
            filename = saved_files[choice - 1]
            loaded_conversation = load_conversation(filename[:-5])

            if loaded_conversation is not None:
                messages = loaded_conversation["messages"]
                settings = loaded_conversation["settings"]
                custom_instructions = settings["custom_instructions"]
                personality = settings["personality"]
                tone = settings["tone"]
                response_length = settings["response_length"]
                language = settings["language"]
                technical_level = settings["technical_level"]
                creativity = settings["creativity"]
                print("Conversation loaded!")
            continue

        elif question == "list":
            saved_files = list_saved_conversations()
            if len(saved_files) == 0:
                print("No saved conversations found.")
            continue

        elif question == "delete":
            saved_files = list_saved_conversations()
            if len(saved_files) == 0:
                print("No saved conversations found.")
                continue
            try:
                choice = int(input("Select a conversation to delete: "))
                if choice < 1 or choice > len(saved_files):
                    print("Invalid choice.")
                    continue
            except ValueError:
                print("Invalid choice.")
                continue
            filename = saved_files[choice - 1]
            print("Deleting conversation " + filename)
            confirm = input("Are you sure you want to delete this conversation? (yes/no): ").lower()
            if confirm == "yes":
                delete_conversation(filename[:-5])
            elif confirm == "no":
                print("Deletion cancelled.")
            else:
                print("Invalid response. Please enter yes or no.")
            continue

        elif question == "rename":
            saved_files = list_saved_conversations()
            if len(saved_files) == 0:
                print("No saved conversations found.")
                continue
            try:
                choice = int(input("Select a conversation to rename: "))
                if choice < 1 or choice > len(saved_files):
                    print("Invalid choice.")
                    continue
            except ValueError:
                print("Invalid choice.")
                continue
            filename = saved_files[choice - 1]
            new_filename = input("Enter a new filename: ")
            if new_filename == "":
                print("New filename cannot be empty.")
                continue
            elif os.path.exists(new_filename + ".json"):
                print("A conversation with that filename already exists.")
                continue
            rename_conversation(filename[:-5], new_filename)
            continue

        # Adds the user's question to the conversation and sends it to the AI
        messages.append({"role": "user", "content": question})
        ask_ai(messages)

if __name__ == "__main__":
    main()