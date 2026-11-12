# Custom AI Assistant
A general purpose AI assistant that can answer questions on virtually any topic and adapt its communication style based on user preferences.

The application uses a locally running AI model through Ollama. Users can customize how the assistant communicates without modifying the Python source code.

## What This Accomplishes
### General AI Conversations
- Accepts questions on any subject
- Generates responses using a locally running AI model
- Maintains context throughout a conversation
- Allows users to start new conversations
- Handles unavailable models or connection errors

### Personality Customization
- Users can choose how the assistant behaves 

| Personality | Behavior|
|---|---|
| Professional | Formal, clear, and informative |
| Casual | Friendly and conversational |
| Teacher | Explains concepts step by step |
| Concise | Gives short, direct answers |
| Creative | More expressive and imaginative |

- Users can also provide their own custom instructions

### Communication Settings
- Allow users to customize:
  - Tone: Formal, casual, friendly, direct
  - Response length: Short, balanced, detailed
  - Language: English, Spansih, French, etc
  - Technical Level: Beginner, intermediate, advanced
  - Creativity: More predictable or more creative responses

### Conversation Management
- Save conversations
- Load previous conversations
- Rename conversations
- Delete conversations
- Maintain separate conversation histories
- Restore conversation settings when loading a saved conversation

### Long-Term Memory
- Store information across application sessions using memory.json
- Manually add information using the `remember` command
- View saved information using the `memories` command
- Delete individual memories using the `forget` command
- Update the assistant's system instructions when memories are added or deleted

## Technologies

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Ollama | Local AI model execution |
| Llama 3.2 | Initial language model |
| SQLite | Conversation and preference storage |
| JSON | Configuration and settings |
| Tkinter | Desktop graphical interface |

## Development Roadmap
### Completed
- Stage 1 - Basic AI Assistant
  - Build a general purpose conversational assistant that accepts questions and returns responses
- Stage 2 - Personality Customization
  - Allow users to select personalities and define custom instructions
- Stage 3 - Communication Settings
  - Add tone, response length, language, and technical-level settings
- Stage 4 - Conversation Management
  - Save, load, rename, and delete conversations using SQLite
- Stage 5 - Long-Term Memory
  - Implement manually managed persistent memory using JSON

### Future Improvements

- Stage 6 - Persistent Preferences
  - Save user customization settings between application sessions
  - Automatically apply saved preferences when the application starts
  - Allow users to reset preferences to defaults
- Stage 7 - Conversation Context Management
  - Add tools for monitoring and managing conversation history as it grows
- Stage 8 - Model Configuration
  - Allow users to select from locally installed AI models
  - Add configurable model parameters
  - Display the currently selected model
- Stage 9 - Graphical Interface
  - Build a desktop application with a chat window and customization panel
- Stage 8 - Advanced Features
  - Explore document analysis and additional AI capabilities