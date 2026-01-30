import streamlit as st
from annotated_text import annotated_text
import ast
import pandas as pd

# Initialize session state
if 'annotation_choices' not in st.session_state:
    st.session_state.annotation_choices = {}

def display_text_with_inline_buttons(data, file_id, region_idx):
    """
    Display text with annotations and inline buttons, all in one flowing line.
    """
    words = data['words']
    events = data['events']
    
    # Build a list of elements to display
    elements = []
    current_text = []
    current_event = None
    current_event_words = []
    ann_counter = 0
    
    for word, event in zip(words, events):
        if event.startswith('B-'):
            # Add accumulated non-event text
            if current_text:
                elements.append(' '.join(current_text) + ' ')
                current_text = []
            
            # Add previous event with buttons
            if current_event_words and current_event:
                text = ' '.join(current_event_words)
                elements.append((text, current_event, file_id, region_idx, ann_counter))
                ann_counter += 1
                current_event_words = []
            
            # Start new event
            current_event = event[2:]
            current_event_words = [word]
            
        elif event.startswith('I-'):
            current_event_words.append(word)
            
        else:  # O
            # Add previous event with buttons
            if current_event_words and current_event:
                text = ' '.join(current_event_words)
                elements.append((text, current_event, file_id, region_idx, ann_counter))
                ann_counter += 1
                current_event_words = []
                current_event = None
            
            current_text.append(word)
    
    # Add remaining elements
    if current_text:
        elements.append(' '.join(current_text))
    if current_event_words and current_event:
        text = ' '.join(current_event_words)
        elements.append((text, current_event, file_id, region_idx, ann_counter))
    
    # Display all elements in columns to keep them inline
    cols = st.columns(len(elements))
    
    for idx, element in enumerate(elements):
        with cols[idx]:
            if isinstance(element, tuple):
                # This is an annotation with buttons
                text, label, fid, rid, aid = element
                key = f"{fid}_{rid}_{aid}"
                
                # Display annotation
                annotated_text((text + " ", label))
                
                # Display buttons inline
                btn_cols = st.columns(2)
                with btn_cols[0]:
                    if st.button("✓", key=f"correct_{key}"):
                        st.session_state.annotation_choices[key] = {
                            'file': fid,
                            'region': rid,
                            'text': text,
                            'label': label,
                            'choice': 'correct'
                        }
                
                with btn_cols[1]:
                    if st.button("✗", key=f"wrong_{key}"):
                        st.session_state.annotation_choices[key] = {
                            'file': fid,
                            'region': rid,
                            'text': text,
                            'label': label,
                            'choice': 'wrong'
                        }
                
                # Show current choice
                if key in st.session_state.annotation_choices:
                    choice = st.session_state.annotation_choices[key]['choice']
                    st.markdown("✅" if choice == 'correct' else "❌")
            else:
                # This is regular text
                st.markdown(element)

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