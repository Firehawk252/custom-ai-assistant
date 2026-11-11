# Custom AI Assistant
A general purpose AI assistant that can answer questions on virtually any topic and adapt its communication style based on user preferences.

The user should be able to customize how the AI communicates without having to modify the Python source code.

## What This Accomplishes
### General AI Conversations
- Accepts questions on any subject
- Generates responses using a locally running AI model
- Maintains context throughout a conversation
- Allows users to start new conversations
- Handles unavailable models or connection errors

### Personality Customization
- Users should be able to choose how the assistant behaves 

| Personality | Behavior|
|---|---|
| Professional | Formal, clear, and informative |
| Casual | Friendly and conversational |
| Teacher | Explains concepts step by step |
| Concise | Gives short, direct answers |
| Creative | More expressive and imaginative |

- Users should also be able to write their own custom instructions

### Communication Settings
- Allow users to customize:
  - Tone: Formal, casual, friendly, direct
  - Response length: Short, balanced, detailed
  - Language: English, Spansih, French, etc
  - Technical Level: Beginner, intermediate, advanced
  - Creativity: More predictable or more creative responses

### Conversation Manaagement
- Save conversations
- Load previous conversations
- Rename conversations
- Delete conversations
- Maintain separate conversation histories

### User Preferences
- Save customization settings
- Remember preferences between application sessions
- Allow users to reset settings to defaults
- Apply preferences to new conversations

### Model Configuration
- Select from locally installed AI models
- Adjust model parameteres such as temperate
- Configure the assistant's system instructions
- Display which model is currently being used

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
- Stage 1 - Basic AI Assistant
  - Build a general purpose conversational assistant that accepts questions and returns responses
- Stage 2 - Personality Customization
  - Allow users to select personalities and define custom instructions
- Stage 3 - Communication Settings
  - Add tone, response length, language, and technical-level settings
- Stage 4 - Conversation Management
  - Save, load, rename, and delete conversations using SQLite
- Stage 5 - Persistent Preferences
  - Save user settings and automatically apply them when the application starts
- Stage 6 - Graphical Interface
  - Build a desktop application with a chat window and customization panel
- Stage 7 - Advanced Features
  - Add model selection, additional configuration options, and potentially document analysis
