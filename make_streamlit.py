import streamlit as st
from annotated_text import annotated_text
import ast
import pandas as pd

# Initialize session state
if 'annotation_choices' not in st.session_state:
    st.session_state.annotation_choices = {}

def convert_to_annotated_text(data):
    """Convert data to annotated_text format."""
    words = data['words']
    events = data['events']
    
    result = []
    current_text = []
    current_event = None
    current_event_words = []
    
    for word, event in zip(words, events):
        if event.startswith('B-'):
            if current_text:
                result.append(' '.join(current_text) + ' ')
                current_text = []
            
            if current_event_words and current_event:
                result.append((' '.join(current_event_words) + ' ', current_event))
                current_event_words = []
            
            current_event = event[2:]
            current_event_words = [word]
            
        elif event.startswith('I-'):
            current_event_words.append(word)
            
        else:
            if current_event_words and current_event:
                result.append((' '.join(current_event_words) + ' ', current_event))
                current_event_words = []
                current_event = None
            
            current_text.append(word)
    
    if current_text:
        result.append(' '.join(current_text))
    if current_event_words and current_event:
        result.append((' '.join(current_event_words) + ' ', current_event))
    
    return result

def extract_annotations(data):
    """Extract all annotations."""
    words = data['words']
    events = data['events']
    
    annotations = []
    current_event = None
    current_words = []
    
    for word, event in zip(words, events):
        if event.startswith('B-'):
            if current_words and current_event:
                annotations.append((' '.join(current_words), current_event))
            
            current_event = event[2:]
            current_words = [word]
            
        elif event.startswith('I-'):
            current_words.append(word)
            
        else:
            if current_words and current_event:
                annotations.append((' '.join(current_words), current_event))
                current_words = []
                current_event = None
    
    if current_words and current_event:
        annotations.append((' '.join(current_words), current_event))
    
    return annotations

def display_region_with_buttons(data, file_id, region_idx):
    """Display annotated text and buttons for each annotation."""
    # Display the full annotated text
    annotated_version = convert_to_annotated_text(data)
    annotated_text(*annotated_version)
    
    # Get all annotations
    annotations = extract_annotations(data)
    
    # Display compact buttons for each annotation
    if annotations:
        st.markdown("---")
        for ann_idx, (text, label) in enumerate(annotations):
            key = f"{file_id}_{region_idx}_{ann_idx}"
            
            cols = st.columns([0.6, 0.1, 0.1, 0.2])
            
            with cols[0]:
                st.markdown(f"**{text}** `({label})`")
            
            with cols[1]:
                if st.button("✓", key=f"correct_{key}"):
                    st.session_state.annotation_choices[key] = {
                        'file': file_id,
                        'region': region_idx,
                        'text': text,
                        'label': label,
                        'choice': 'correct'
                    }
            
            with cols[2]:
                if st.button("✗", key=f"wrong_{key}"):
                    st.session_state.annotation_choices[key] = {
                        'file': file_id,
                        'region': region_idx,
                        'text': text,
                        'label': label,
                        'choice': 'wrong'
                    }
            
            with cols[3]:
                if key in st.session_state.annotation_choices:
                    choice = st.session_state.annotation_choices[key]['choice']
                    st.markdown("✅ Correct" if choice == 'correct' else "❌ Wrong")

# Main app
st.header("Gold data for Events")

# First file
with open('3604.json') as f:
    data = f.readlines()

for region_idx, line in enumerate(data):
    parsed_data = ast.literal_eval(line)
    display_region_with_buttons(parsed_data, '3604', region_idx)
    st.write("")
    st.write("")

st.subheader("Inventory number 1812: Missive from 1711")

# Second file
with open('1812.json') as f:
    data = f.readlines()

for region_idx, line in enumerate(data):
    parsed_data = ast.literal_eval(line)
    display_region_with_buttons(parsed_data, '1812', region_idx)
    st.write("")
    st.write("")

# Download section
st.divider()
st.subheader("Download Your Choices")

if st.session_state.annotation_choices:
    df = pd.DataFrame.from_dict(st.session_state.annotation_choices, orient='index')
    st.write(f"Total annotations reviewed: {len(df)}")
    st.dataframe(df)
    
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="annotation_choices.csv",
        mime="text/csv"
    )
    
    if st.button("Reset All Choices"):
        st.session_state.annotation_choices = {}
        st.rerun()
else:
    st.info("No annotations have been marked yet.")