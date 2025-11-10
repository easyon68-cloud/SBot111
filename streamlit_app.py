import streamlit as st
import requests
import json

def initialize_app():
    """Initialize the app configuration"""
    st.set_page_config(
        page_title="NCERT and CBSE Problem Solving Tutor",
        page_icon="📚",
        layout="wide"
    )
    
    return True

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
    
    if st.sidebar.button("Clear Chat History"):
        st.session_state.messages = [
            {
                "role": "assistant", 
                "content": "Chat history cleared! How can I help you with your NCERT or CBSE studies today?"
            }
        ]
        st.rerun()

def get_response_ollama(user_input, conversation_history):
    """
    Use Ollama with a free local model (fallback option)
    """
    try:
        # Prepare the prompt with NCERT context
        system_prompt = """You are an expert NCERT and CBSE problem solving tutor. 
        Provide clear, step-by-step explanations for problems.
        Focus on CBSE curriculum and NCERT textbook concepts."""
        
        # Format conversation history
        prompt = f"{system_prompt}\n\nConversation History:\n"
        for msg in conversation_history:
            prompt += f"{msg['role']}: {msg['content']}\n"
        
        prompt += f"user: {user_input}\nassistant:"
        
        # Call Ollama API (local installation required)
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama2',  # or 'mistral', 'codellama' etc.
                'prompt': prompt,
                'stream': False
            },
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()['response']
        else:
            return "I'm currently using a free model service. Please make sure Ollama is installed and running locally, or try the Hugging Face option below."
            
    except Exception as e:
        return f"I'm using alternative free services. Error: {str(e)}. Please try the demo responses below."

def get_response_huggingface(user_input, conversation_history):
    """
    Alternative: Use Hugging Face Inference API (free tier available)
    """
    try:
        # This is a simplified version - you'd need to set up HF token
        API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
        headers = {"Authorization": f"Bearer {st.secrets.get('HF_TOKEN', '')}"}
        
        # Format the conversation
        formatted_conversation = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in conversation_history[-4:]]  # Last 4 messages
        ) + f"\nuser: {user_input}\nassistant:"
        
        payload = {
            "inputs": formatted_conversation,
            "parameters": {"max_length": 500, "temperature": 0.7}
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0]['generated_text'].split('assistant:')[-1].strip()
        
        return "Using educational demo mode. In a full implementation, this would connect to Hugging Face models."
        
    except Exception as e:
        return get_fallback_response(user_input)

def get_fallback_response(user_input):
    """
    Simple rule-based fallback responses for demo
    """
    user_input_lower = user_input.lower()
    
    # Subject-specific responses
    if any(word in user_input_lower for word in ['math', 'algebra', 'calculus', 'geometry']):
        return """**Mathematics Solution Approach**:
        
1. **Understand the Problem**: Identify what's being asked
2. **Recall Formulas**: Apply relevant mathematical formulas
3. **Step-by-Step Calculation**: Show each calculation step
4. **Verify Answer**: Check if the solution makes sense

*For actual calculation, please provide the specific problem.*"""

    elif any(word in user_input_lower for word in ['science', 'physics', 'chemistry', 'biology']):
        return """**Science Problem Approach**:
        
1. **Concept Identification**: Which scientific principle applies?
2. **Theory Application**: How does the theory explain this?
3. **Experimental/Logical Reasoning**: Step-by-step reasoning
4. **Conclusion**: Summarize the findings

*Please share the specific science problem for detailed help.*"""

    elif any(word in user_input_lower for word in ['history', 'geography', 'civics']):
        return """**Social Studies Approach**:
        
1. **Context Setting**: Historical/Geographical context
2. **Key Concepts**: Important terms and ideas
3. **Analysis**: Cause-effect relationships
4. **Significance**: Why this matters

*Share the specific topic or question for detailed explanation.*"""

    else:
        return """I'd be happy to help you with your NCERT/CBSE problem! 

To provide the best assistance, please:
1. **Specify the subject** (Math, Science, Social Studies, etc.)
2. **Share the exact problem** from your textbook
3. **Mention your grade/class**

For example: "Can you help me with 10th grade Algebra problem about quadratic equations?""""

def get_response(user_input, conversation_history):
    """
    Main response function with multiple fallbacks
    """
    # Try Ollama first (local)
    response = get_response_ollama(user_input, conversation_history)
    
    # If Ollama fails, try fallback responses
    if "Error" in response or "error" in response.lower():
        response = get_fallback_response(user_input)
    
    return response

def display_chat_history():
    """Display the entire chat history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def handle_user_input():
    """Handle user input and generate responses"""
    user_input = st.chat_input("Type your NCERT/CBSE question here...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("🔍 Analyzing your question..."):
                assistant_response = get_response(user_input, st.session_state.messages)
                st.markdown(assistant_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

def main():
    """Main function to run the Streamlit app"""
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
    
    # Sidebar with setup instructions
    with st.sidebar:
        st.header("🛠️ Setup Options")
        
        st.subheader("Option 1: Local AI (Free)")
        st.markdown("""
        Install Ollama locally:
        ```bash
        # Install Ollama
        curl -fsSL https://ollama.ai/install.sh | sh
        
        # Pull a model
        ollama pull llama2
        ```
        """)
        
        st.subheader("Option 2: Demo Mode")
        st.markdown("""
        Currently running in **demo mode** with:
        - Rule-based responses
        - Subject-specific templates
        - Educational guidance
        """)
        
        st.header("🎯 Subjects Covered")
        st.markdown("""
        - **Mathematics**
        - **Science** 
        - **Social Studies**
        - **Languages**
        - **Computer Science**
        """)
    
    # Initialize app
    initialize_app()
    initialize_chat_history()
    
    # Display chat
    display_chat_history()
    handle_user_input()

if __name__ == "__main__":
    main()
