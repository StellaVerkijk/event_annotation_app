import streamlit as st
from annotated_text import annotated_text
import ast
import pandas as pd

# Initialize session state
if 'annotation_choices' not in st.session_state:
    st.session_state.annotation_choices = {}

def display_text_with_inline_buttons(data, file_id, region_idx):
    """
    Display text with annotations and inline buttons after each annotation.
    """
    words = data['words']
    events = data['events']
    
    current_text = []
    current_event = None
    current_event_words = []
    ann_counter = 0
    
    for word_idx, (word, event) in enumerate(zip(words, events)):
        if event.startswith('B-'):
            # Display accumulated non-event text
            if current_text:
                st.markdown(' '.join(current_text), unsafe_allow_html=True)
                current_text = []
            
            # Display previous event with buttons
            if current_event_words and current_event:
                text = ' '.join(current_event_words)
                display_annotation_with_buttons(text, current_event, file_id, region_idx, ann_counter)
                ann_counter += 1
                current_event_words = []
            
            # Start new event
            current_event = event[2:]
            current_event_words = [word]
            
        elif event.startswith('I-'):
            current_event_words.append(word)
            
        else:  # O
            # Display previous event with buttons
            if current_event_words and current_event:
                text = ' '.join(current_event_words)
                display_annotation_with_buttons(text, current_event, file_id, region_idx, ann_counter)
                ann_counter += 1
                current_event_words = []
                current_event = None
            
            current_text.append(word)
    
    # Display remaining text/events
    if current_text:
        st.markdown(' '.join(current_text), unsafe_allow_html=True)
    if current_event_words and current_event:
        text = ' '.join(current_event_words)
        display_annotation_with_buttons(text, current_event, file_id, region_idx, ann_counter)

def display_annotation_with_buttons(text, label, file_id, region_idx, ann_idx):
    """
    Display an annotation inline with V and X buttons.
    """
    key = f"{file_id}_{region_idx}_{ann_idx}"
    
    # Create inline columns for annotation and buttons
    cols = st.columns([0.3, 0.05, 0.05, 0.6])
    
    with cols[0]:
        annotated_text((text + " ", label))
    
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
    
    # Show current choice in the remaining space
    with cols[3]:
        if key in st.session_state.annotation_choices:
            choice = st.session_state.annotation_choices[key]['choice']
            if choice == 'correct':
                st.markdown("✅", unsafe_allow_html=True)
            else:
                st.markdown("❌", unsafe_allow_html=True)

# Main app
st.header("Gold data for Events")

# First file
with open('3604.json') as f:
    data = f.readlines()

for region_idx, line in enumerate(data):
    parsed_data = ast.literal_eval(line)
    display_text_with_inline_buttons(parsed_data, '3604', region_idx)
    st.divider()

st.subheader("Inventory number 1812: Missive from 1711")

# Second file
with open('1812.json') as f:
    data = f.readlines()

for region_idx, line in enumerate(data):
    parsed_data = ast.literal_eval(line)
    display_text_with_inline_buttons(parsed_data, '1812', region_idx)
    st.divider()

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
