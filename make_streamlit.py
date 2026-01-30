import streamlit as st
from annotated_text import annotated_text
import ast
import pandas as pd

# Initialize session state
if 'annotation_choices' not in st.session_state:
    st.session_state.annotation_choices = {}

def display_text_with_inline_buttons(data, file_id, region_idx):
    """
    Display text with annotations and inline buttons in a natural flow.
    """
    words = data['words']
    events = data['events']
    
    current_text = []
    current_event = None
    current_event_words = []
    ann_counter = 0
    
    # Container for the entire region
    container = st.container()
    
    for word, event in zip(words, events):
        if event.startswith('B-'):
            # Display accumulated non-event text
            if current_text:
                container.markdown(' '.join(current_text) + ' ', unsafe_allow_html=True)
                current_text = []
            
            # Display previous event with buttons
            if current_event_words and current_event:
                text = ' '.join(current_event_words)
                display_inline_annotation(container, text, current_event, file_id, region_idx, ann_counter)
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
                display_inline_annotation(container, text, current_event, file_id, region_idx, ann_counter)
                ann_counter += 1
                current_event_words = []
                current_event = None
            
            current_text.append(word)
    
    # Display remaining elements
    if current_text:
        container.markdown(' '.join(current_text), unsafe_allow_html=True)
    if current_event_words and current_event:
        text = ' '.join(current_event_words)
        display_inline_annotation(container, text, current_event, file_id, region_idx, ann_counter)

def display_inline_annotation(container, text, label, file_id, region_idx, ann_idx):
    """
    Display annotation with buttons inline using columns.
    """
    key = f"{file_id}_{region_idx}_{ann_idx}"
    
    with container:
        cols = st.columns([0.2, 0.03, 0.03, 0.74])
        
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
        
        with cols[3]:
            if key in st.session_state.annotation_choices:
                choice = st.session_state.annotation_choices[key]['choice']
                st.markdown("✅" if choice == 'correct' else "❌")

# Main app
st.header("Gold data for Events")

# First file
with open('3604.json') as f:
    data = f.readlines()

for region_idx, line in enumerate(data):
    parsed_data = ast.literal_eval(line)
    display_text_with_inline_buttons(parsed_data, '3604', region_idx)
    st.write("")  # Extra newline between regions
    st.write("")  # Extra newline between regions

st.subheader("Inventory number 1812: Missive from 1711")

# Second file
with open('1812.json') as f:
    data = f.readlines()

for region_idx, line in enumerate(data):
    parsed_data = ast.literal_eval(line)
    display_text_with_inline_buttons(parsed_data, '1812', region_idx)
    st.write("")  # Extra newline between regions
    st.write("")  # Extra newline between regions

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