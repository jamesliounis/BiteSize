import streamlit as st
from generate_mcq import LlamaTextGenerator  # Enhanced Llama-based MCQ Generator
import re
import json

# Path to the configuration details
CONFIG_PATH = "../../../secrets/config.json"

# Read and load the configuration file
with open(CONFIG_PATH, "r") as file:
    config = json.load(file)

# Initialize the LlamaTextGenerator with the endpoint and project details
generator = LlamaTextGenerator(
    endpoint_id=config["endpoint_id"], project_id=config["project_id"]
)


def format_question(question_str):
    """
    Format the provided question string for better presentation.

    Args:
    - question_str (str): Raw question string from the model.

    Returns:
    - formatted (str): Formatted question string for display.
    """

    # Check for option 'a)' to determine if formatting is required
    if "a)" not in question_str:
        return question_str

    # Splitting the main question from its options and difficulty
    main_question, rest = question_str.split("a)", 1)
    options_parts = re.split(r"(?=[b-d]\))", "a)" + rest)

    difficulty_str = ""
    if "Difficulty:" in options_parts[-1]:
        difficulty_str = options_parts[-1].split("Difficulty:")[1].strip()
        options_parts[-1] = options_parts[-1].split("Difficulty:")[0].strip()

    # Compose the formatted string
    formatted = main_question.strip() + "\n\n" + "\n\n".join(options_parts)
    if difficulty_str:
        formatted += f"\n\n**Difficulty:** {difficulty_str}"
    return formatted


# Display logo at the top of the app
st.image("BiteSize_logo.png", use_column_width=True)

# Add custom CSS for styling Streamlit app
st.markdown(
    """
    <style>
        .stApp {
            background-color: rgb(113, 169, 214);
        }
        
        .sidebar .sidebar-content {
            background-color: rgb(113, 169, 214);
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def main():
    """Main function to run the Streamlit app."""

    st.title("BiteSize")
    st.markdown("## Learn in chunks!")

    # File uploader widget
    uploaded_file = st.file_uploader("Upload a document file", type=["pdf", "docx"])

    if uploaded_file:
        # Determine file type and extract text accordingly
        if uploaded_file.type == "application/pdf":
            extracted_text = generator.extract_text_from_pdf(uploaded_file)
        elif (
            uploaded_file.type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            extracted_text = generator.extract_text_from_docx(uploaded_file)
        else:
            st.warning("Unsupported file type!")
            return

        # Display the extracted text in an expandable section
        with st.expander("Extracted Text"):
            st.write(extracted_text)

        # Question type options
        st.subheader("Today's specials:")

        # Generate and display MCQs
        if st.button("Appetizer: MCQs"):
            questions = generator.generate_questions(extracted_text)
            display_questions(questions)

        # Additional buttons for future features or other question types
        # [Keep the logic for other buttons if needed]


def display_questions(questions):
    """
    Display the generated questions in a formatted manner.

    Args:
    - questions (list): List of generated questions.
    """

    if questions:
        st.subheader("Bon appétit!")
        question_number = 1

        for q in questions:
            formatted_question = format_question(q)

            # Present the difficulty separately for emphasis
            if "Difficulty:" in formatted_question:
                st.markdown(
                    f"<span style='color: black; font-size: 16px;'>{formatted_question}</span>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(f"**Question {question_number}**:")
                st.markdown(
                    f"<span style='color: black; font-size: 16px;'>{formatted_question}</span>",
                    unsafe_allow_html=True,
                )

            # Increment to update the question count
            question_number += 1


# Run the main function for the Streamlit app
if __name__ == "__main__":
    main()
