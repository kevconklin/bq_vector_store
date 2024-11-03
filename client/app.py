import streamlit as st
import requests

chat_url = "http://server:8000/ask_question" 
backend_url = "http://server:8000/upload_pdf"

# Set up sidebar for PDF URL input
st.sidebar.title("Input URL to PDF")
pdf_url = st.sidebar.text_input("PDF URL:", "")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Button to upload PDF to backend
if st.sidebar.button("Upload PDF"):
    if pdf_url:
        # Send PDF URL to backend API
        response = requests.post(backend_url, 
            payload={
                "pdf_url": pdf_url
                }
            )
        if response.status_code == 200:
            st.sidebar.success("PDF uploaded successfully!")
        else:
            st.sidebar.error("Failed to upload PDF. Please try again.")
    else:
        st.sidebar.warning("Please enter a PDF URL.")

# Set up main page chatbot interface
st.title("Chat about your PDF")
st.write("Upload a PDF URL on the sidebar to begin.")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask a question"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = requests.post(chat_url, json={"question": prompt})
    answer = response.json()
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(answer)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": answer})

# # Button to submit question
# if st.button("Submit"):
#     if question:
#         # Send question to backend API and get response
#         chat_url = "http://server:8000/ask_question"  # Update with your backend API endpoint for asking questions
#         response = requests.post(chat_url, json={"question": question})
        
#         if response.status_code == 200:
#             answer = response.json().get("answer", "No answer found.")
#             st.session_state.chat_history.append({"question": question, "answer": answer})
#         else:
#             st.error("Failed to get a response. Please try again.")

# # Display chat history
# for entry in st.session_state.chat_history:
#     st.write("**You:**", entry["question"])
#     st.write("**Bot:**", entry["answer"])
