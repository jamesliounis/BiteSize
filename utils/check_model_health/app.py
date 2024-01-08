import streamlit as st
from MCQGenerator import MCQGenerator

def main():
    st.title("MCQ Generator")

    # 1. Upload Files
    uploaded_file = st.file_uploader("Choose a document file", type=["pdf", "docx"])
    
    if uploaded_file:
        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
        st.write(file_details)
        
        generator = MCQGenerator()

        # 2. Display Text
        if uploaded_file.type == "application/pdf":
            extracted_text = generator.extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            extracted_text = generator.extract_text_from_docx(uploaded_file)
        else:
            st.warning("Unsupported file type!")
            return

        st.subheader("Extracted Text")
        st.write(extracted_text)

        # 3. Generate Questions
        if st.button("Generate MCQs"):
            questions = generator.generate_questions(extracted_text)

            # 4. Display MCQs
            st.subheader("Generated MCQs")
            for idx, q in enumerate(questions, 1):
                st.markdown(f"**Question {idx}**")
                st.write(q)
                st.write("---")

if __name__ == "__main__":
    main()
