import streamlit as st
import os
from agno.agent import Agent
from agno.models.openai.like import OpenAILike
import google.generativeai as genai
from mem0 import MemoryClient
import time

# Configure page
st.set_page_config(
    page_title="Diabetes Health Assistant",
    page_icon="🩺",
    layout="centered"
)

# Language definitions
languages = [
    "English", "Hindi", "Gujarati", "Bengali", "Tamil", 
    "Telugu", "Kannada", "Malayalam", "Punjabi", "Marathi", 
    "Urdu", "Assamese", "Odia", "Sanskrit"
]

# Language codes mapping
language_codes = {
    "English": "en",
    "Hindi": "hi",
    "Gujarati": "gu",
    "Bengali": "bn",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Punjabi": "pa",
    "Marathi": "mr",
    "Urdu": "ur",
    "Assamese": "as",
    "Odia": "or",
    "Sanskrit": "sa"
}

# Initialize APIs
@st.cache_resource
def initialize_apis(sutra_api_key, mem0_api_key):
    # Configure Gemini
    genai.configure(api_key="AIzaSyAPtLzvHnXRuNUwKSGZyYpfU3sBYdQoCLs")
    gemini = genai.GenerativeModel("gemini-1.5-flash")

    # Initialize Mem0 Client
    client = MemoryClient(api_key=mem0_api_key)

    # Initialize SUTRA Agent
    sutra_agent = Agent(
        model=OpenAILike(
            id="sutra-v2",
            api_key=sutra_api_key,
            base_url="https://api.two.ai/v2"
        ),
        markdown=True,
        description="A multilingual medical assistant powered by SUTRA-V2",
        instructions=["Answer concisely in the requested language."]
    )

    return gemini, client, sutra_agent

# Initialize session state
def init_session_state():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'is_new_user' not in st.session_state:
        st.session_state.is_new_user = None
    if 'registration_step' not in st.session_state:
        st.session_state.registration_step = 0
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {}
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'registration_complete' not in st.session_state:
        st.session_state.registration_complete = False
    if 'apis_initialized' not in st.session_state:
        st.session_state.apis_initialized = False
    if 'selected_language' not in st.session_state:
        st.session_state.selected_language = "English"

def detect_language(text, sutra_agent):
    """Detect language of input text"""
    try:
        detect_prompt = f"Detect the language of this text and return only the language name: {text}"
        response = sutra_agent.run(detect_prompt)
        detected_lang = response.content.strip()
        return detected_lang
    except Exception as e:
        st.error(f"Language detection error: {str(e)}")
        return "English"

def translate_text(text, target_language, sutra_agent):
    """Translate text to target language"""
    try:
        if target_language == "English":
            return text
        
        translate_prompt = f"Translate this text to {target_language}: {text}"
        response = sutra_agent.run(translate_prompt)
        return response.content.strip()
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return text

def process_input_with_translation(text, target_language, sutra_agent):
    """Process input with language detection and translation"""
    try:
        # Detect language of input
        detected_lang = detect_language(text, sutra_agent)
        
        # If input is not in English, translate to English for processing
        if detected_lang != "English":
            translate_prompt = f"Translate this text to English: {text}"
            response = sutra_agent.run(translate_prompt)
            english_text = response.content.strip()
        else:
            english_text = text
            
        return english_text, detected_lang
    except Exception as e:
        st.error(f"Processing error: {str(e)}")
        return text, "English"

def check_existing_user(user_id, client):
    """Check if user exists in Mem0 database"""
    try:
        search_results = client.search("check", user_id=user_id)
        return len(search_results) > 0, search_results
    except Exception as e:
        st.error(f"Error checking user: {str(e)}")
        return False, []

def save_user_info(user_id, user_info, client):
    """Save user information to Mem0"""
    try:
        messages = [
            {"role": "user", "content": f"My name is {user_info['name']}."},
            {"role": "user", "content": f"I am {user_info['age']} years old."},
            {"role": "user", "content": f"I am a {user_info['gender']}."},
            {"role": "user", "content": f"I have {user_info['diabetes_type']} diabetes."},
            {"role": "user", "content": f"My medications include: {user_info['medication']}."},
            {"role": "user", "content": f"My symptoms include: {user_info['symptoms']}."},
            {"role": "user", "content": f"I currently live in: {user_info['location']}."},
            {"role": "assistant", "content": f"Thanks {user_info['name']}, your health info is stored for personalized support."}
        ]
        client.add(messages, user_id=user_id)
        return True
    except Exception as e:
        st.error(f"Error saving user info: {str(e)}")
        return False

def get_chat_response(query, user_id, selected_language, gemini, client, sutra_agent):
    """Get response from AI models with context"""
    try:
        # Process input and translate to English if needed
        query_en, detected_lang = process_input_with_translation(query, selected_language, sutra_agent)

        # Retrieve Mem0 context
        search_results = client.search(query_en, user_id=user_id)

        # Collect context from both 'message' and 'memory'
        mem0_memories = []
        for r in search_results:
            if 'message' in r and 'content' in r['message']:
                role = r['message'].get('role', 'user').capitalize()
                content = r['message']['content']
                mem0_memories.append(f"{role}: {content}")
            elif 'memory' in r:
                mem0_memories.append(f"Memory: {r['memory']}")

        context = "\n".join(mem0_memories)

        # Extract Personal Info
        user_name = "User"
        diabetes_type = "Not specified"
        location = "Not specified"

        for r in search_results:
            memory_text = ''
            if 'message' in r and 'content' in r['message']:
                memory_text = r['message']['content'].lower()
            elif 'memory' in r:
                memory_text = r['memory'].lower()

            if memory_text:
                if "name is" in memory_text:
                    user_name = memory_text.split("name is")[-1].split()[0].capitalize()
                if "type 1" in memory_text or "type 2" in memory_text:
                    diabetes_type = "Type 2" if "type 2" in memory_text else "Type 1"
                if "live in" in memory_text:
                    location = memory_text.split("live in")[-1].split(".")[0].strip().capitalize()

        # Create prompt for the selected language
        final_prompt = f"""
        You are a diabetes-friendly AI assistant helping {user_name}, a patient from {location} diagnosed with {diabetes_type} Diabetes.

        Past memories from previous chats:
        {context}

        User's new query:
        "{query_en}"

        Provide a helpful, India-specific, diabetes-safe, and practical response in {selected_language}.
        Important: Respond ONLY in {selected_language} language.
        """

        # Generate response with Gemini
        response = gemini.generate_content(final_prompt)
        
        # If response is not in selected language, translate it
        if selected_language != "English":
            final_response = translate_text(response.text, selected_language, sutra_agent)
        else:
            final_response = response.text

        # Store the conversation in memory
        new_messages = [
            {"role": "user", "content": query},
            {"role": "assistant", "content": final_response}
        ]
        client.add(new_messages, user_id=user_id)

        return final_response

    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        error_msg = "Sorry, I encountered an error while processing your request. Please try again."
        if selected_language != "English":
            error_msg = translate_text(error_msg, selected_language, sutra_agent)
        return error_msg

# Initialize session state
init_session_state()

# Sidebar UI
st.sidebar.image("https://framerusercontent.com/images/3Ca34Pogzn9I3a7uTsNSlfs9Bdk.png", use_container_width=True)
st.sidebar.title("Configurations")

# Language selection
selected_language = st.sidebar.selectbox("Select language for responses:", languages)
st.session_state.selected_language = selected_language

# API Key inputs
st.sidebar.markdown("### API Keys")
st.sidebar.markdown("🔑 Get your API key from [Two AI Sutra](https://www.two.ai/sutra/api)")
sutra_api_key = st.sidebar.text_input("Enter your SUTRA API Key", type="password")

st.sidebar.markdown("🔑 Get your API key from [Mem0](https://app.mem0.ai/dashboard/)")
mem0_api_key = st.sidebar.text_input("Enter your MEM0 API Key", type="password")

# API Key validation
if not sutra_api_key or not mem0_api_key:
    st.sidebar.error("⚠️ Please enter both API keys to continue!")
    st.warning("Please enter your SUTRA and MEM0 API keys in the sidebar to use the application.")
    st.stop()

# Initialize APIs
if not st.session_state.apis_initialized:
    with st.spinner("Initializing AI systems..."):
        try:
            gemini, client, sutra_agent = initialize_apis(sutra_api_key, mem0_api_key)
            st.session_state.gemini = gemini
            st.session_state.client = client
            st.session_state.sutra_agent = sutra_agent
            st.session_state.apis_initialized = True
        except Exception as e:
            st.error(f"Failed to initialize APIs: {str(e)}")
            st.stop()

# Main app header
st.title("🩺 Diabetes Health Assistant")
st.markdown("*Your personalized diabetes management companion*")
st.markdown("---")

# Step 1: User ID Input (always shown first)
if st.session_state.user_id is None:
    st.markdown("### Welcome! Please enter your details to continue")

    with st.form("user_login_form"):
        user_id = st.text_input(
            "Enter your unique username or ID:",
            placeholder="e.g., john_doe_123",
            help="This helps us personalize your experience"
        )
        submit_login = st.form_submit_button("Continue", use_container_width=True)

        if submit_login and user_id.strip():
            with st.spinner("Checking user database..."):
                st.session_state.user_id = user_id.strip()

                # Check if user exists
                user_exists, search_results = check_existing_user(
                    st.session_state.user_id,
                    st.session_state.client
                )

                if user_exists:
                    st.session_state.is_new_user = False
                    st.session_state.registration_complete = True
                    st.success("✅ Existing user detected. Welcome back!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.session_state.is_new_user = True
                    st.info("New user detected. Let's collect some basic information.")
                    time.sleep(1)
                    st.rerun()
        elif submit_login:
            st.error("Please enter a valid username or ID")

# Step 2: New User Registration (step by step)
elif st.session_state.is_new_user and not st.session_state.registration_complete:
    st.markdown(f"### Registration - Step {st.session_state.registration_step + 1} of 7")
    st.markdown(f"**User ID:** {st.session_state.user_id}")

    # Progress bar
    progress = (st.session_state.registration_step) / 7
    st.progress(progress)

    # Translate questions to selected language
    questions = [
        {
            "key": "name",
            "question": "What's your full name?",
            "placeholder": "Enter your full name",
            "input_type": "text"
        },
        {
            "key": "age",
            "question": "What is your age?",
            "placeholder": "Enter your age",
            "input_type": "number"
        },
        {
            "key": "gender",
            "question": "What is your gender?",
            "placeholder": "e.g., Male, Female, Other",
            "input_type": "text"
        },
        {
            "key": "diabetes_type",
            "question": "What type of Diabetes do you have?",
            "placeholder": "e.g., Type 1, Type 2, Gestational",
            "input_type": "text"
        },
        {
            "key": "medication",
            "question": "What medications are you currently taking?",
            "placeholder": "List your current medications",
            "input_type": "text_area"
        },
        {
            "key": "symptoms",
            "question": "Are you experiencing any unusual symptoms?",
            "placeholder": "Describe any symptoms you're experiencing",
            "input_type": "text_area"
        },
        {
            "key": "location",
            "question": "Where are you currently living?",
            "placeholder": "City, State",
            "input_type": "text"
        }
    ]

    if st.session_state.registration_step < len(questions):
        current_q = questions[st.session_state.registration_step]
        
        # Translate question and placeholder to selected language
        translated_question = translate_text(current_q['question'], selected_language, st.session_state.sutra_agent)
        translated_placeholder = translate_text(current_q['placeholder'], selected_language, st.session_state.sutra_agent)

        with st.form(f"registration_step_{st.session_state.registration_step}"):
            st.markdown(f"**{translated_question}**")

            # Different input types based on question
            if current_q['input_type'] == 'number':
                answer = st.number_input(
                    "Your answer:",
                    min_value=1,
                    max_value=120,
                    value=None,
                    placeholder=translated_placeholder,
                    label_visibility="collapsed"
                )
                answer = str(answer) if answer is not None else ""
            elif current_q['input_type'] == 'text_area':
                answer = st.text_area(
                    "Your answer:",
                    placeholder=translated_placeholder,
                    label_visibility="collapsed",
                    height=100
                )
            else:
                answer = st.text_input(
                    "Your answer:",
                    placeholder=translated_placeholder,
                    label_visibility="collapsed"
                )

            col1, col2 = st.columns([1, 1])
            with col1:
                prev_text = translate_text("Previous", selected_language, st.session_state.sutra_agent)
                if st.form_submit_button(f"⬅️ {prev_text}") and st.session_state.registration_step > 0:
                    st.session_state.registration_step -= 1
                    st.rerun()

            with col2:
                next_text = translate_text("Next", selected_language, st.session_state.sutra_agent)
                if st.form_submit_button(f"{next_text} ➡️", use_container_width=True):
                    if str(answer).strip():
                        # Process and translate answer to English for storage
                        with st.spinner("Processing..."):
                            processed_answer, detected_lang = process_input_with_translation(
                                str(answer),
                                "English",
                                st.session_state.sutra_agent
                            )
                            st.session_state.user_info[current_q['key']] = processed_answer
                            st.session_state.registration_step += 1
                            st.rerun()
                    else:
                        error_msg = translate_text("Please provide an answer before continuing", selected_language, st.session_state.sutra_agent)
                        st.error(error_msg)

    # Registration complete
    if st.session_state.registration_step >= len(questions):
        success_msg = translate_text("Registration Complete!", selected_language, st.session_state.sutra_agent)
        st.success(f"🎉 {success_msg}")
        
        summary_title = translate_text("Your Information Summary:", selected_language, st.session_state.sutra_agent)
        st.markdown(f"### {summary_title}")

        info_display = {
            "name": translate_text("Full Name", selected_language, st.session_state.sutra_agent),
            "age": translate_text("Age", selected_language, st.session_state.sutra_agent),
            "gender": translate_text("Gender", selected_language, st.session_state.sutra_agent),
            "diabetes_type": translate_text("Diabetes Type", selected_language, st.session_state.sutra_agent),
            "medication": translate_text("Current Medications", selected_language, st.session_state.sutra_agent),
            "symptoms": translate_text("Symptoms", selected_language, st.session_state.sutra_agent),
            "location": translate_text("Location", selected_language, st.session_state.sutra_agent)
        }

        for key, label in info_display.items():
            if key in st.session_state.user_info:
                st.markdown(f"**{label}:** {st.session_state.user_info[key]}")

        start_chat_text = translate_text("Start Chatting!", selected_language, st.session_state.sutra_agent)
        if st.button(f"{start_chat_text} 💬", use_container_width=True):
            with st.spinner("Saving your information..."):
                # Save user info to database
                success = save_user_info(
                    st.session_state.user_id,
                    st.session_state.user_info,
                    st.session_state.client
                )

                if success:
                    st.session_state.registration_complete = True
                    welcome_msg = translate_text(
                        f"Thanks {st.session_state.user_info.get('name', 'there')}, your health info is stored for personalized support. How can I help you today?",
                        selected_language,
                        st.session_state.sutra_agent
                    )
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": welcome_msg
                    })
                    st.rerun()
                else:
                    error_msg = translate_text("Failed to save your information. Please try again.", selected_language, st.session_state.sutra_agent)
                    st.error(error_msg)

# Step 3: Chat Interface (for registered users)
elif st.session_state.registration_complete:
    # Welcome message for existing users
    if st.session_state.is_new_user == False and len(st.session_state.chat_history) == 0:
        welcome_msg = translate_text(
            "Welcome back! How can I assist you with your diabetes management today?",
            selected_language,
            st.session_state.sutra_agent
        )
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": welcome_msg
        })

    # Display user info in sidebar
    with st.sidebar:
        st.markdown("---")
        profile_title = translate_text("Your Profile", selected_language, st.session_state.sutra_agent)
        st.markdown(f"### {profile_title}")
        st.markdown(f"**User ID:** {st.session_state.user_id}")
        if st.session_state.user_info:
            st.markdown(f"**{translate_text('Name', selected_language, st.session_state.sutra_agent)}:** {st.session_state.user_info.get('name', 'N/A')}")
            st.markdown(f"**{translate_text('Age', selected_language, st.session_state.sutra_agent)}:** {st.session_state.user_info.get('age', 'N/A')}")
            st.markdown(f"**{translate_text('Gender', selected_language, st.session_state.sutra_agent)}:** {st.session_state.user_info.get('gender', 'N/A')}")
            st.markdown(f"**{translate_text('Diabetes Type', selected_language, st.session_state.sutra_agent)}:** {st.session_state.user_info.get('diabetes_type', 'N/A')}")
            st.markdown(f"**{translate_text('Location', selected_language, st.session_state.sutra_agent)}:** {st.session_state.user_info.get('location', 'N/A')}")

        st.markdown("---")

        reset_text = translate_text("Reset Chat", selected_language, st.session_state.sutra_agent)
        if st.button(f"🔄 {reset_text}"):
            st.session_state.chat_history = []
            st.rerun()

        logout_text = translate_text("Logout", selected_language, st.session_state.sutra_agent)
        if st.button(f"🚪 {logout_text}"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # Chat history display
    chat_title = translate_text("Chat History", selected_language, st.session_state.sutra_agent)
    st.markdown(f"### {chat_title}")

    # Container for chat messages
    chat_container = st.container()

    with chat_container:
        if len(st.session_state.chat_history) == 0:
            start_msg = translate_text("Start a conversation by typing your question below!", selected_language, st.session_state.sutra_agent)
            st.info(start_msg)
        else:
            for i, message in enumerate(st.session_state.chat_history):
                if message["role"] == "user":
                    with st.chat_message("user"):
                        st.write(message["content"])
                else:
                    with st.chat_message("assistant"):
                        st.write(message["content"])

    # Chat input (always at bottom)
    st.markdown("---")

    # Input form
    with st.form("chat_form", clear_on_submit=True):
        placeholder_text = translate_text("Ask me anything about diabetes management...", selected_language, st.session_state.sutra_agent)
        user_input = st.text_area(
            "Your message:",
            placeholder=f"{placeholder_text} ({selected_language})",
            label_visibility="collapsed",
            height=100
        )

        col1, col2 = st.columns([4, 1])
        with col2:
            send_text = translate_text("Send", selected_language, st.session_state.sutra_agent)
            submit_chat = st.form_submit_button(f"{send_text} 📤", use_container_width=True)

        if submit_chat and user_input.strip():
            # Add user message to chat history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input.strip()
            })

            # Process the input and get response
            with st.spinner("Thinking..."):
                # Get AI response
                response = get_chat_response(
                    user_input.strip(),
                    st.session_state.user_id,
                    selected_language,
                    st.session_state.gemini,
                    st.session_state.client,
                    st.session_state.sutra_agent
                )

            # Add assistant response to chat history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })

            # Rerun to update the display
            st.rerun()

        elif submit_chat:
            error_msg = translate_text("Please enter a message before sending", selected_language, st.session_state.sutra_agent)
            st.error(error_msg)

# Footer
st.markdown("---")
footer_text = translate_text("Diabetes Health Assistant - Stay healthy!", selected_language, st.session_state.sutra_agent)
st.markdown(
    f"""
    <div style='text-align: center; color: #666;'>
        <small>{footer_text} 🌟</small>
    </div>
    """,
    unsafe_allow_html=True
)
