import streamlit as st
import google.generativeai as genai
import PyPDF2
import io


genai.configure(api_key="")  
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_pdf_text(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_topics(text):
    prompt = f"""
    Analyze this document and extract the main topics/chapters covered. 
    List them as simple topic names, one per line.
    
    Text: {text[:3000]}
    
    Format: Just list the topics, nothing else.
    """
    response = model.generate_content(prompt)
    topics = [topic.strip() for topic in response.text.split('\n') if topic.strip()]
    return topics

def generate_question(text, topic=None):
    if topic:
        prompt = f"Create one educational question specifically about '{topic}' based on this text:\n\n{text[:2000]}"
    else:
        prompt = f"Create one educational question based on this text:\n\n{text[:2000]}"
    response = model.generate_content(prompt)
    return response.text

def evaluate_answer(question, answer, text):
    prompt = f"""
    Text: {text[:2000]}
    Question: {question}
    Student Answer: {answer}
    
    Evaluate the answer. Provide:
    1. Correct/Incorrect
    2. Reason why
    3.  Question type: fact-based OR memory-based OR reasoning-based (choose only one)
    4. Topic covered (just give the name of the topic, no more details)
    """
    response = model.generate_content(prompt)
    return response.text

# Streamlit UI
st.title("Document Based Learning Assistant")

# File upload
uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    # Extract text
    course_content = extract_pdf_text(uploaded_file)
    st.success("PDF uploaded successfully!")
    
    # Extract topics
    if "topics" not in st.session_state:
        with st.spinner("Extracting topics..."):
            topics = extract_topics(course_content)
            st.session_state.topics = topics
            st.session_state.course_content = course_content
    
    # Topic selection
    st.write("**Select a topic:**")
    selected_topic = st.selectbox("Choose topic", st.session_state.topics)
    
    # Generate question
    if st.button("Generate Question"):
        question = generate_question(st.session_state.course_content, selected_topic)
        st.session_state.generated_question = question
        st.session_state.selected_topic = selected_topic
    
    # Show question
    if "generated_question" in st.session_state:
        st.write("**Question:**")
        st.write(st.session_state.generated_question)
        
        # User answer
        user_answer = st.text_input("Your answer:")
        
        # Evaluate answer
        if st.button("Evaluate Answer") and user_answer:
            evaluation = evaluate_answer(
                st.session_state.generated_question, 
                user_answer, 
                st.session_state.course_content
            )
            st.write("**Evaluation:**")
            st.write(evaluation)