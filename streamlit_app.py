import streamlit as st
from openai import OpenAI

def initialize_app():
    """Initialize the OpenAI client and app configuration"""
    # Set page configuration
    st.set_page_config(
        page_title="NCERT and CBSE Problem Solving Tutor",
        page_icon="📚",
        layout="wide"
    )
    
    # Initialize OpenAI client
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        return client
    except Exception as e:
        st.error(f"Error initializing OpenAI client: {str(e)}")
        st.stop()

def initialize_chat_history():
    """Initialize or reset chat history in session state"""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant", 
                "content": """👋 Hello! I'm your dedicated NCERT and CBSE problem solving tutor. 

I can help you with:
📖 Mathematics - Algebra, Geometry, Calculus
🔬 Science - Physics, Chemistry, Biology
🌍 Social Studies - History, Geography, Civics
📝 English - Literature, Grammar, Writing
💻 Computer Science - Programming, Algorithms

What subject or specific problem would you like help with today?"""
            }
        ]
    
    # Add clear chat functionality
    if st.sidebar.button("Clear Chat History"):
        st.session_state.messages = [
            {
                "role": "assistant", 
                "content": "Chat history cleared! How can I help you with your NCERT or CBSE studies today?"
            }
        ]
        st.rerun()

def get_response(client, user_input, conversation_history):
    """
    Send conversation history and user input to OpenAI GPT-3.5 turbo
    and return the assistant's response with NCERT/CBSE context
    """
    try:
        # Prepare system message for NCERT/CBSE context
        system_message = {
            "role": "system",
            "content": """You are an expert NCERT and CBSE problem solving tutor. Your role is to:
1. Provide clear, step-by-step explanations for problems
2. Focus on CBSE curriculum and NCERT textbook concepts
3. Use simple language appropriate for students
4. Break down complex problems into manageable steps
5. Provide examples and analogies when helpful
6. Encourage conceptual understanding over rote learning
7. Cover subjects: Mathematics, Science, Social Science, English, Hindi, Computer Science
8. Adapt explanations to different grade levels (1-12)"""
        }
        
        # Prepare messages for API call
        messages = [system_message] + conversation_history + [{"role": "user", "content": user_input}]
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"❌ I apologize, but I encountered an error while processing your request. Please try again. Error: {str(e)}"

def display_chat_history():
    """Display the entire chat history in conversational format"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def handle_user_input(client):
    """Handle user input and generate responses"""
    # User input box with placeholder
    user_input = st.chat_input("Type your NCERT/CBSE question here...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("🔍 Analyzing your question and preparing explanation..."):
                assistant_response = get_response(client, user_input, st.session_state.messages)
                st.markdown(assistant_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

def main():
    """Main function to run the Streamlit app"""
    # App title and description
    st.title("📚 NCERT and CBSE Problem Solving Tutor")
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sub-header">Get step-by-step solutions for NCERT and CBSE curriculum problems</div>', unsafe_allow_html=True)
    
    # Sidebar information
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This AI tutor helps you with:
        - **Mathematics**: Algebra, Geometry, Calculus
        - **Science**: Physics, Chemistry, Biology  
        - **Social Science**: History, Geography
        - **Languages**: English, Hindi
        - **Computer Science**
        
        **Grades**: 1st to 12th
        **Curriculum**: NCERT & CBSE
        """)
        
        st.header("🎯 How to Use")
        st.markdown("""
        1. Type your question in the chat box
        2. Get step-by-step explanations
        3. Ask follow-up questions
        4. Clear chat to start fresh
        """)
    
    # Initialize app components
    client = initialize_app()
    initialize_chat_history()
    
    # Display chat interface
    display_chat_history()
    handle_user_input(client)

if __name__ == "__main__":
    main()
