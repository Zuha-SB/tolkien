"""
Lord of the Rings Character Chat Application
Chat with your favorite LOTR characters using Vertex AI's Gemini 2.5 Flash
"""

import streamlit as st
import pandas as pd
import json
import os
import re
import logging
from pathlib import Path
from datetime import datetime

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, skip

import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession

# =============================================================================
# Logging Configuration
# =============================================================================

# Set up logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

# Create log file with timestamp
log_file = log_dir / f"conversations_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()  # Also log to console
    ]
)

logger = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================

# Update these with your Google Cloud settings
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-project-id")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
MODEL_NAME = "gemini-2.5-flash"

# Paths
CHARACTERS_DIR = Path(__file__).parent / "characters"
SCRIPTS_CSV = Path(__file__).parent / "lotr_scripts.csv"

# =============================================================================
# Page Configuration
# =============================================================================

st.set_page_config(
    page_title="Middle-Earth Messenger",
    page_icon="🧙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# Custom CSS - Middle-Earth Theme
# =============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d2d44 0%, #1a1a2e 100%);
        border-right: 2px solid #c9a227;
    }
    
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        font-family: 'Cinzel', serif;
        color: #c9a227;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown {
        font-family: 'Crimson Text', serif;
        color: #e8d5b7;
    }
    
    /* Main title */
    .main-title {
        font-family: 'Cinzel', serif;
        color: #c9a227;
        text-align: center;
        font-size: 2.5rem;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.7);
        margin-bottom: 0.5rem;
        letter-spacing: 3px;
    }
    
    .subtitle {
        font-family: 'Crimson Text', serif;
        color: #a89a7c;
        text-align: center;
        font-size: 1.2rem;
        font-style: italic;
        margin-bottom: 2rem;
    }
    
    /* Chat messages */
    [data-testid="stChatMessage"] {
        background: rgba(45, 45, 68, 0.8);
        border: 1px solid #4a4a6a;
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stChatMessage"] p {
        font-family: 'Crimson Text', serif;
        color: #e8d5b7;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    /* User messages */
    [data-testid="stChatMessage"][data-testid*="user"] {
        background: rgba(201, 162, 39, 0.15);
        border-color: #c9a227;
    }
    
    /* Chat input */
    [data-testid="stChatInput"] {
        border: none !important;
    }
    
    [data-testid="stChatInput"] > div {
        border: none !important;
        background: transparent !important;
    }
    
    [data-testid="stChatInput"] textarea {
        font-family: 'Crimson Text', serif !important;
        background: rgba(45, 45, 68, 0.9) !important;
        border: 2px solid #4a4a6a !important;
        color: #e8d5b7 !important;
        border-radius: 10px !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    [data-testid="stChatInput"] textarea:focus {
        border: 2px solid #c9a227 !important;
        box-shadow: 0 0 10px rgba(201, 162, 39, 0.3) !important;
        outline: none !important;
    }
    
    [data-testid="stChatInput"] textarea:hover {
        border: 2px solid #5a5a7a !important;
    }
    
    /* Selectbox */
    [data-testid="stSelectbox"] > div > div {
        background: rgba(45, 45, 68, 0.9);
        border: 2px solid #c9a227;
        border-radius: 10px;
        color: #e8d5b7;
        font-family: 'Crimson Text', serif;
    }
    
    /* Character info box */
    .character-info {
        background: rgba(45, 45, 68, 0.7);
        border: 1px solid #c9a227;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        font-family: 'Crimson Text', serif;
        color: #e8d5b7;
    }
    
    .character-info h4 {
        font-family: 'Cinzel', serif;
        color: #c9a227;
        margin-bottom: 0.5rem;
    }
    
    /* Decorative elements */
    .ring-divider {
        text-align: center;
        color: #c9a227;
        font-size: 1.5rem;
        margin: 1rem 0;
        letter-spacing: 10px;
    }
    
    /* Buttons */
    .stButton > button {
        font-family: 'Cinzel', serif;
        background: linear-gradient(135deg, #c9a227 0%, #8b7355 100%);
        color: #1a1a2e;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #dbb845 0%, #a08566 100%);
        box-shadow: 0 0 15px rgba(201, 162, 39, 0.5);
        transform: translateY(-2px);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a2e;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #c9a227;
        border-radius: 4px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .quote-box {
        background: rgba(201, 162, 39, 0.1);
        border-left: 3px solid #c9a227;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        font-style: italic;
        font-family: 'Crimson Text', serif;
        color: #a89a7c;
    }
    
    /* ============================================================================
       Mobile Responsive Styles
       ============================================================================ */
    
    @media screen and (max-width: 768px) {
        /* Main title - smaller on mobile */
        .main-title {
            font-size: 1.8rem;
            letter-spacing: 2px;
            padding: 0 0.5rem;
        }
        
        .subtitle {
            font-size: 1rem;
            padding: 0 0.5rem;
            margin-bottom: 1rem;
        }
        
        /* Ring divider - smaller spacing */
        .ring-divider {
            font-size: 1.2rem;
            letter-spacing: 5px;
            margin: 0.5rem 0;
        }
        
        /* Sidebar adjustments */
        [data-testid="stSidebar"] {
            min-width: 100% !important;
            max-width: 100% !important;
        }
        
        [data-testid="stSidebar"] .stMarkdown h1,
        [data-testid="stSidebar"] .stMarkdown h2,
        [data-testid="stSidebar"] .stMarkdown h3 {
            font-size: 1.2rem;
        }
        
        /* Character info box - less padding on mobile */
        .character-info {
            padding: 1rem;
            margin: 0.75rem 0;
            font-size: 0.95rem;
        }
        
        .character-info h4 {
            font-size: 1.1rem;
        }
        
        /* Chat messages - better mobile spacing */
        [data-testid="stChatMessage"] {
            padding: 0.75rem;
            margin: 0.4rem 0;
            border-radius: 12px;
        }
        
        [data-testid="stChatMessage"] p {
            font-size: 1rem;
            line-height: 1.5;
        }
        
        /* Chat input - larger touch target */
        [data-testid="stChatInput"] textarea {
            font-size: 16px !important; /* Prevents zoom on iOS */
            min-height: 48px !important; /* Touch-friendly */
            padding: 0.75rem !important;
        }
        
        /* Buttons - larger touch targets */
        .stButton > button {
            min-height: 44px;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
        }
        
        /* Selectbox - larger touch target */
        [data-testid="stSelectbox"] > div > div {
            min-height: 44px;
            padding: 0.75rem;
            font-size: 1rem;
        }
        
        /* Quote box - adjust for mobile */
        .quote-box {
            padding: 0.75rem;
            font-size: 0.95rem;
        }
        
        /* Main content area - better padding */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        /* Chat container - full width on mobile */
        [data-testid="stChatMessageContainer"] {
            width: 100%;
        }
    }
    
    /* Extra small devices (phones in portrait) */
    @media screen and (max-width: 480px) {
        .main-title {
            font-size: 1.5rem;
            letter-spacing: 1px;
        }
        
        .subtitle {
            font-size: 0.9rem;
        }
        
        .ring-divider {
            font-size: 1rem;
            letter-spacing: 3px;
        }
        
        .character-info {
            padding: 0.75rem;
            font-size: 0.9rem;
        }
        
        [data-testid="stChatMessage"] {
            padding: 0.6rem;
        }
        
        [data-testid="stChatMessage"] p {
            font-size: 0.95rem;
        }
    }
    
    /* Ensure proper viewport on mobile */
    @media screen and (max-width: 768px) {
        .stApp {
            overflow-x: hidden;
        }
        
        /* Prevent horizontal scrolling */
        body {
            overflow-x: hidden;
        }
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# Data Loading Functions
# =============================================================================

@st.cache_data
def load_scripts():
    """Load the movie scripts CSV file."""
    try:
        df = pd.read_csv(SCRIPTS_CSV)
        # Clean up column names
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        logger.error(f"Error loading scripts: {str(e)}", exc_info=True)
        st.error("Unable to load movie scripts. Please try again later.")
        return pd.DataFrame()

@st.cache_data
def load_character_info(character_filename):
    """Load character information from text file."""
    try:
        # Security: Prevent path traversal attacks
        if '..' in character_filename or '/' in character_filename or '\\' in character_filename:
            logger.warning(f"Invalid character filename detected: {character_filename}")
            return None, None
        
        filepath = CHARACTERS_DIR / character_filename
        
        # Security: Ensure file is within the characters directory
        if not str(filepath.resolve()).startswith(str(CHARACTERS_DIR.resolve())):
            logger.warning(f"Path traversal attempt detected: {character_filename}")
            return None, None
        
        if not filepath.exists():
            logger.warning(f"Character file not found: {character_filename}")
            return None, None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse JSON content
        data = json.loads(content)
        
        # Extract the wiki content
        pages = data.get('query', {}).get('pages', {})
        for page_id, page_data in pages.items():
            revisions = page_data.get('revisions', [])
            if revisions:
                wiki_content = revisions[0].get('*', '')
                title = page_data.get('title', '')
                return title, wiki_content
        
        return None, None
    except Exception as e:
        logger.error(f"Error loading character info for {character_filename}: {str(e)}", exc_info=True)
        return None, None

@st.cache_data
def get_character_quotes(scripts_df, character_name):
    """Get all quotes for a specific character."""
    if scripts_df.empty:
        return []
    
    # Normalize character name for matching
    char_upper = character_name.upper()
    
    # Filter quotes for this character
    char_quotes = scripts_df[scripts_df['char'].str.upper().str.strip() == char_upper]
    
    quotes = []
    for _, row in char_quotes.iterrows():
        dialog = str(row.get('dialog', '')).strip()
        movie = str(row.get('movie', '')).strip()
        if dialog and dialog != 'nan':
            quotes.append({'dialog': dialog, 'movie': movie})
    
    return quotes

@st.cache_data
def get_available_characters():
    """Get list of characters that have both wiki info and movie quotes."""
    scripts_df = load_scripts()
    
    # Get characters from scripts
    script_characters = set()
    if not scripts_df.empty:
        script_characters = set(scripts_df['char'].str.strip().str.upper().unique())
    
    # Get characters from txt files
    file_characters = {}
    if CHARACTERS_DIR.exists():
        for filepath in CHARACTERS_DIR.glob("*.txt"):
            # Convert filename to character name
            name = filepath.stem.replace("_", " ")
            file_characters[name.upper()] = filepath.name
    
    # Build list of characters with proper display names
    available = []
    
    # Map script names to file names
    name_mapping = {
        "GANDALF": ("Gandalf", "Gandalf.txt"),
        "FRODO": ("Frodo Baggins", "Frodo_Baggins.txt"),
        "SAM": ("Samwise Gamgee", "Samwise_Gamgee.txt"),
        "ARAGORN": ("Aragorn", "Aragorn_II_Elessar.txt"),
        "LEGOLAS": ("Legolas", "Legolas.txt"),
        "GIMLI": ("Gimli", "Gimli.txt"),
        "BOROMIR": ("Boromir", "Boromir.txt"),
        "MERRY": ("Meriadoc Brandybuck", "Meriadoc_Brandybuck.txt"),
        "PIPPIN": ("Peregrin Took", "Peregrin_Took.txt"),
        "GOLLUM": ("Gollum", "Gollum.txt"),
        "SARUMAN": ("Saruman", "Saruman.txt"),
        "ELROND": ("Elrond", "Elrond.txt"),
        "GALADRIEL": ("Galadriel", "Galadriel.txt"),
        "ARWEN": ("Arwen", "Arwen.txt"),
        "THÉODEN": ("Théoden", "Théoden.txt"),
        "THEODEN": ("Théoden", "Théoden.txt"),
        "ÉOWYN": ("Éowyn", "Éowyn.txt"),
        "EOWYN": ("Éowyn", "Éowyn.txt"),
        "ÉOMER": ("Éomer", "Éomer.txt"),
        "EOMER": ("Éomer", "Éomer.txt"),
        "FARAMIR": ("Faramir", "Faramir.txt"),
        "DENETHOR": ("Denethor II", "Denethor_II.txt"),
        "TREEBEARD": ("Treebeard", "Treebeard.txt"),
        "BILBO": ("Bilbo Baggins", "Bilbo_Baggins.txt"),
        "WITCH-KING": ("Witch-king of Angmar", "Witch-king_of_Angmar.txt"),
        "GRIMA": ("Gríma Wormtongue", "Gríma_Wormtongue.txt"),
        "WORMTONGUE": ("Gríma Wormtongue", "Gríma_Wormtongue.txt"),
        "CELEBORN": ("Celeborn", "Celeborn.txt"),
        "HALDIR": ("Haldir", "Haldir_(Lorien).txt"),
        "GAMLING": ("Gamling", "Gamling.txt"),
        "BARLIMAN": ("Barliman Butterbur", "Barliman_Butterbur.txt"),
    }
    
    for script_name in script_characters:
        if script_name in name_mapping:
            display_name, filename = name_mapping[script_name]
            if (CHARACTERS_DIR / filename).exists():
                available.append({
                    'display_name': display_name,
                    'script_name': script_name,
                    'filename': filename
                })
    
    # Sort by display name
    available.sort(key=lambda x: x['display_name'])
    
    return available

def extract_character_summary(wiki_content):
    """Extract a brief summary from wiki content."""
    if not wiki_content:
        return ""
    
    # Remove wiki markup
    text = re.sub(r'\{\{[^}]+\}\}', '', wiki_content)
    text = re.sub(r'\[\[[^\]|]+\|([^\]]+)\]\]', r'\1', text)
    text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)
    text = re.sub(r"'''?", '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    # Get first few sentences
    sentences = text.split('.')
    summary = '. '.join(sentences[:3]) + '.'
    
    return summary[:500] if len(summary) > 500 else summary

# =============================================================================
# Vertex AI Integration
# =============================================================================

@st.cache_resource
def initialize_vertex_ai():
    """Initialize Vertex AI."""
    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI: {str(e)}", exc_info=True)
        # Don't expose error details to users in production
        return False

def get_model():
    """Get the Gemini model."""
    return GenerativeModel(MODEL_NAME)

def create_character_prompt(character_info, quotes, character_name):
    """Create the system prompt for the character."""
    
    # Extract summary from wiki content
    _, wiki_content = character_info if character_info else (None, None)
    summary = extract_character_summary(wiki_content) if wiki_content else ""
    
    # Format some example quotes
    quote_examples = ""
    if quotes:
        sample_quotes = quotes[:15]  # Take up to 15 quotes
        quote_examples = "\n".join([f'- "{q["dialog"]}" ({q["movie"]})' for q in sample_quotes])
    
    prompt = f"""You are {character_name} from J.R.R. Tolkien's "The Lord of the Rings" as portrayed in Peter Jackson's film trilogy.

CHARACTER BACKGROUND:
{summary}

EXAMPLE QUOTES FROM THE FILMS (use these to understand speech patterns and vocabulary):
{quote_examples}

ROLEPLAY INSTRUCTIONS:
1. Stay completely in character as {character_name} at all times
2. Speak in the same manner and style as shown in the films - match the vocabulary, tone, and speech patterns from the quotes above
3. Reference events, places, and people from Middle-Earth appropriately based on what {character_name} would know
4. Express the personality, wisdom, fears, hopes, and motivations that {character_name} displays in the films
5. Use appropriate expressions, oaths, or phrases the character might use (e.g., Gandalf might say "Fool of a Took!" or reference his pipe-weed)
6. If asked about things outside Middle-Earth or the character's knowledge, respond as the character would - with confusion, curiosity, or by relating it to something they do understand
7. Keep responses conversational and engaging, as if truly speaking with someone
8. Never break character or acknowledge being an AI

Remember: You ARE {character_name}. Respond as they would, with their voice, their concerns, and their perspective on the world."""

    return prompt

def generate_response(character_name, user_message, character_info, quotes, chat_history):
    """Generate a character response using Gemini."""
    
    try:
        logger.info(f"[{character_name}] Generating response... (conversation history: {len(chat_history)} messages)")
        model = get_model()
        
        # Create the character system prompt
        system_prompt = create_character_prompt(character_info, quotes, character_name)
        
        # Build conversation history
        conversation = f"{system_prompt}\n\n"
        
        for msg in chat_history[-10:]:  # Keep last 10 messages for context
            role = "User" if msg["role"] == "user" else character_name
            conversation += f"{role}: {msg['content']}\n\n"
        
        conversation += f"User: {user_message}\n\n{character_name}:"
        
        # Generate response
        response = model.generate_content(
            conversation,
            generation_config={
                "max_output_tokens": 1024,
                "temperature": 0.9,
                "top_p": 0.95,
            }
        )
        
        logger.info(f"[{character_name}] Response generated successfully (length: {len(response.text)} chars)")
        return response.text
        
    except Exception as e:
        logger.error(f"[{character_name}] Error generating response: {str(e)}", exc_info=True)
        # Return user-friendly message without exposing error details
        return f"*{character_name} seems lost in thought* Forgive me, I cannot speak clearly at this moment. Please try again."

# =============================================================================
# Main Application
# =============================================================================

def main():
    # Header
    st.markdown('<h1 class="main-title">⚔️ Middle-Earth Messenger ⚔️</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">"Not all those who wander are lost"</p>', unsafe_allow_html=True)
    st.markdown('<div class="ring-divider">◆ ◇ ◆ ◇ ◆</div>', unsafe_allow_html=True)
    
    # Initialize Vertex AI
    if not initialize_vertex_ai():
        st.error("⚠️ Service temporarily unavailable. Please try again later.")
        logger.error("Vertex AI initialization failed - service unavailable")
        st.stop()
    
    # Load data
    scripts_df = load_scripts()
    available_characters = get_available_characters()
    
    if not available_characters:
        st.error("No characters found. Please ensure the data files are present.")
        return
    
    # Sidebar - Character Selection
    with st.sidebar:
        st.markdown("## 🏰 Choose Your Companion")
        st.markdown('<div class="ring-divider">◇ ◆ ◇</div>', unsafe_allow_html=True)
        
        # Character selector
        character_options = [c['display_name'] for c in available_characters]
        
        # Find Gandalf's index for default selection
        default_index = 0
        try:
            gandalf_index = character_options.index("Gandalf")
            default_index = gandalf_index
        except ValueError:
            pass  # Gandalf not found, use index 0
        
        selected_display_name = st.selectbox(
            "Select a character to speak with:",
            options=character_options,
            index=default_index
        )
        
        # Find the selected character info
        selected_char = next(
            (c for c in available_characters if c['display_name'] == selected_display_name),
            None
        )
        
        st.markdown("---")
        
        # Clear chat button (moved above About section)
        if st.button("🗡️ Start New Conversation", use_container_width=True):
            current_char = st.session_state.get('current_character_name', 'Unknown')
            logger.info(f"=== Conversation cleared by user for character: {current_char} ===")
            logger.info(f"Previous conversation had {len(st.session_state.messages)} messages")
            st.session_state.messages = []
            # Keep current character but clear conversation
            st.rerun()
        
        st.markdown("---")
        
        if selected_char:
            # Load character data
            char_info = load_character_info(selected_char['filename'])
            char_quotes = get_character_quotes(scripts_df, selected_char['script_name'])
            
            # Store in session state
            st.session_state.current_character = selected_char
            st.session_state.character_info = char_info
            st.session_state.character_quotes = char_quotes
            
            st.markdown(f"### About {selected_display_name}")
            
            # Show character summary
            if char_info[1]:
                summary = extract_character_summary(char_info[1])
                st.markdown(f'<div class="character-info">{summary}</div>', unsafe_allow_html=True)
            
            # Show quote count
            st.markdown(f"📜 **Movie quotes loaded:** {len(char_quotes)}")
            
            # Sample quote
            if char_quotes:
                sample = char_quotes[0]
                st.markdown("**Sample quote:**")
                st.markdown(f'<div class="quote-box">"{sample["dialog"]}"<br><small>— {sample["movie"]}</small></div>', unsafe_allow_html=True)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        logger.info("=== New session started ===")
    
    if "current_character_name" not in st.session_state:
        st.session_state.current_character_name = None
        logger.info("=== Character tracking initialized ===")
    
    # Check if character changed - clear conversation history when switching
    current_char_name = selected_display_name if selected_char else None
    if st.session_state.current_character_name != current_char_name:
        old_char = st.session_state.current_character_name
        old_message_count = len(st.session_state.messages)
        logger.info(f"=== Character switched: {old_char} -> {current_char_name} ===")
        logger.info(f"Previous conversation had {old_message_count} messages")
        st.session_state.messages = []
        st.session_state.current_character_name = current_char_name
        logger.info(f"New conversation started with {current_char_name}")
    
    # Main chat area
    chat_container = st.container()
    
    with chat_container:
        # Welcome message if no messages yet
        if not st.session_state.messages and selected_char:
            st.markdown(f"""
            <div class="character-info">
                <h4>🌟 You are now speaking with {selected_display_name}</h4>
                <p>Begin your conversation below. Ask questions, seek wisdom, or simply chat with this legendary character from Middle-Earth.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Display chat messages
        for message in st.session_state.messages:
            avatar = "🧝" if message["role"] == "assistant" else "🗡️"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input(f"Speak to {selected_display_name}..."):
        # Sanitize and validate user input
        prompt = prompt.strip()
        if not prompt:
            st.warning("Please enter a message.")
            st.stop()
        
        # Limit input length to prevent abuse
        MAX_INPUT_LENGTH = 2000
        if len(prompt) > MAX_INPUT_LENGTH:
            st.warning(f"Message too long. Please keep messages under {MAX_INPUT_LENGTH} characters.")
            st.stop()
        
        # Log user message
        logger.info(f"[{selected_display_name}] User: {prompt}")
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user", avatar="🗡️"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant", avatar="🧝"):
            with st.spinner(f"{selected_display_name} is thinking..."):
                response = generate_response(
                    selected_display_name,
                    prompt,
                    st.session_state.get('character_info'),
                    st.session_state.get('character_quotes', []),
                    st.session_state.messages
                )
                st.markdown(response)
        
        # Log assistant response
        logger.info(f"[{selected_display_name}] Assistant: {response[:200]}..." if len(response) > 200 else f"[{selected_display_name}] Assistant: {response}")
        logger.info(f"Conversation now has {len(st.session_state.messages)} messages")
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()

