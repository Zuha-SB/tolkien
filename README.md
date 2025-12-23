# 🧙 Middle-Earth Messenger

A Streamlit chat application that lets you converse with characters from The Lord of the Rings. Each character speaks in their authentic voice, drawing from their movie quotes and wiki lore.

## ✨ Features

- **Character Selection**: Chat with iconic characters like Gandalf, Frodo, Aragorn, Gollum, and many more
- **Authentic Voices**: Characters respond in their movie-accurate speech patterns using actual quotes from the films
- **Rich Lore Integration**: Character backgrounds from wiki data inform responses
- **Beautiful UI**: Middle-Earth themed interface with custom styling
- **Conversation Memory**: Maintains chat history within a session
- **Production Ready**: Secure error handling and input validation

## 🚀 Quick Start

### Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables** (required):
   ```bash
   export GOOGLE_CLOUD_PROJECT=your-project-id
   export GOOGLE_CLOUD_LOCATION=us-central1
   ```

   Or use a `.env` file:
   ```
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## 📁 Project Structure

```
tolkien/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── lotr_scripts.csv      # Movie quotes organized by character
├── characters/           # Character wiki information
│   ├── Gandalf.txt
│   ├── Frodo_Baggins.txt
│   ├── Aragorn_II_Elessar.txt
│   └── ... (140+ character files)
└── logs/                 # Conversation logs (auto-generated)
```

## 🎭 Available Characters

The app includes major characters who have both movie quotes and wiki information:

- **The Fellowship**: Frodo, Sam, Merry, Pippin, Gandalf, Aragorn, Legolas, Gimli, Boromir
- **Elves**: Galadriel, Elrond, Arwen, Haldir, Celeborn
- **Rohan**: Théoden, Éowyn, Éomer, Gamling
- **Gondor**: Faramir, Denethor II
- **Others**: Gollum, Saruman, Treebeard, Bilbo, and more!

## ⚙️ Configuration

The application requires the following environment variables:

| Variable | Description |
|----------|-------------|
| `GOOGLE_CLOUD_PROJECT` | Your Google Cloud project ID (required) |
| `GOOGLE_CLOUD_LOCATION` | Vertex AI region (default: `us-central1`) |

## 🛠️ Troubleshooting

### "Service temporarily unavailable"
- Check that Vertex AI is properly configured in your deployment environment
- Verify environment variables are set correctly
- Check application logs for detailed error information

### "No characters found"
- Ensure the `characters/` folder exists with `.txt` files
- Ensure `lotr_scripts.csv` is present in the project root

### Character responses are generic
- The model uses quotes and wiki data to inform responses
- Characters with more movie quotes tend to have more authentic voices

## 📚 Data Sources

The character information and movie scripts used in this application were sourced from:

- **[Analyzing Lord of The Rings with Data Science](https://nab-88.github.io/social-graphs-and-interactions/)** - A social graphs and interactions project that provided:
  - Character wiki pages from "One Wiki to Rule Them All"
  - Movie transcripts from the Peter Jackson trilogy
  - Character network analysis and sentiment data

The original data includes 152 characters from the Lord of the Rings trilogy, with detailed wiki information and complete movie dialogue transcripts.

## 🔒 Security

- User input is validated and sanitized
- Error messages do not expose sensitive system information
- Conversation logs are stored locally for debugging purposes
- All sensitive configuration is handled via environment variables

## 📜 License

This project is for educational purposes. The Lord of the Rings content belongs to the Tolkien Estate and respective rights holders.

---

*"All we have to decide is what to do with the time that is given us."* — Gandalf
