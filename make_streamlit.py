import streamlit as st
import json
import ast
from annotated_text import annotated_text
import pandas as pd
import io


def convert_to_annotated_text(data):
    """
    Written by Claude

    Convert words and events data to annotated_text format.
    
    Args:
        data: dict with 'words' and 'events' keys
    
    Returns:
        list of tuples and strings for annotated_text
    """
    words = data['words']
    events = data['events']
    
    result = []
    current_text = []
    current_event = None
    current_event_words = []
    
    for word, event in zip(words, events):
        # Check if this is a B- (Begin) tag or different event
        if event.startswith('B-'):
            # Save any accumulated non-event text
            if current_text:
                result.append(' '.join(current_text))
                current_text = []
            
            # Save any previous event
            if current_event_words and current_event:
                result.append((' '.join(current_event_words) + ' ', current_event))
                current_event_words = []
            
            # Start new event
            current_event = event[2:]  # Remove 'B-' prefix
            current_event_words = [word]
            
        elif event.startswith('I-'):
            # Continue current event
            current_event_words.append(word)
            
        else:  # event == 'O' (no event)
            # Save any previous event first
            if current_event_words and current_event:
                result.append((' '.join(current_event_words) + ' ', current_event))
                current_event_words = []
                current_event = None
            
            # Add to regular text
            current_text.append(word)
    
    # Don't forget remaining text/events
    if current_text:
        result.append(' '.join(current_text))
    if current_event_words and current_event:
        result.append((' '.join(current_event_words) + ' ', current_event))
    
    return result

def extract_annotations(data):
    """
    Extract all annotated spans from the data.
    
    Args:
        data: dict with 'words' and 'events' keys
    
    Returns:
        list of tuples: [(text, label), ...]
    """
    words = data['words']
    events = data['events']
    
    annotations = []
    current_event = None
    current_words = []
    
    for word, event in zip(words, events):
        if event.startswith('B-'):
            # Save previous annotation if exists
            if current_words and current_event:
                annotations.append((' '.join(current_words), current_event))
            
            # Start new annotation
            current_event = event[2:]  # Remove 'B-' prefix
            current_words = [word]
            
        elif event.startswith('I-'):
            # Continue current annotation
            current_words.append(word)
            
        else:  # event == 'O'
            # Save previous annotation if exists
            if current_words and current_event:
                annotations.append((' '.join(current_words), current_event))
                current_words = []
                current_event = None
    
    # Don't forget the last annotation
    if current_words and current_event:
        annotations.append((' '.join(current_words), current_event))
    
    return annotations

st.header("Gold data for events")

st.subheader("Inventory number 3604: Missive sent from Batavia, 1782")

# First file (3604.json)
with open('3604.json') as f:
    data = f.readlines()

regions = []
annotations_per_region = []

for line in data:   
    regions.append(convert_to_annotated_text(ast.literal_eval(line)))
    annotations_per_region.append(extract_annotations(ast.literal_eval(line)))

for region_idx, r in enumerate(regions):
    annotated_text(r)  # shows complete text with labels
    
    for ann_idx, (text, label) in enumerate(annotations_per_region[region_idx]):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        key = f"file1_{region_idx}_{ann_idx}"
        
        with col1:
            annotated_text((text, label))
        
        with col2:
            if st.button("✓", key=f"correct_{key}"):
                st.session_state.annotation_choices[key] = {
                    'file': '3604.json',
                    'region': region_idx,
                    'text': text,
                    'label': label,
                    'choice': 'correct'
                }
                st.success("Marked as correct!")
        
        with col3:
            if st.button("✗", key=f"wrong_{key}"):
                st.session_state.annotation_choices[key] = {
                    'file': '3604.json',
                    'region': region_idx,
                    'text': text,
                    'label': label,
                    'choice': 'wrong'
                }
                st.error("Marked as wrong!")
        
        # Show current choice if exists
        if key in st.session_state.annotation_choices:
            choice = st.session_state.annotation_choices[key]['choice']
            st.caption(f"Current: {choice}")

st.subheader("Inventory number 1812: Missive from 1711")

# Second file (1812.json)
with open('1812.json') as f:
    data = f.readlines()

regions = []
annotations_per_region = []

for line in data:   
    regions.append(convert_to_annotated_text(ast.literal_eval(line)))
    annotations_per_region.append(extract_annotations(ast.literal_eval(line)))

for region_idx, r in enumerate(regions):
    annotated_text(r)
    
    for ann_idx, (text, label) in enumerate(annotations_per_region[region_idx]):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        key = f"file2_{region_idx}_{ann_idx}"
        
        with col1:
            annotated_text((text, label))
        
        with col2:
            if st.button("✓", key=f"correct_{key}"):
                st.session_state.annotation_choices[key] = {
                    'file': '1812.json',
                    'region': region_idx,
                    'text': text,
                    'label': label,
                    'choice': 'correct'
                }
                st.success("Marked as correct!")
        
        with col3:
            if st.button("✗", key=f"wrong_{key}"):
                st.session_state.annotation_choices[key] = {
                    'file': '1812.json',
                    'region': region_idx,
                    'text': text,
                    'label': label,
                    'choice': 'wrong'
                }
                st.error("Marked as wrong!")
        
        # Show current choice if exists
        if key in st.session_state.annotation_choices:
            choice = st.session_state.annotation_choices[key]['choice']
            st.caption(f"Current: {choice}")

# Download section at the bottom
st.divider()
st.subheader("Download Your Choices")

if st.session_state.annotation_choices:
    # Convert choices to DataFrame
    df = pd.DataFrame.from_dict(st.session_state.annotation_choices, orient='index')
    
    # Show preview
    st.write(f"Total annotations reviewed: {len(df)}")
    st.dataframe(df)
    
    # Convert to CSV
    csv = df.to_csv(index=False)
    
    # Download button
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="annotation_choices.csv",
        mime="text/csv"
    )
    
    # Optional: Reset button
    if st.button("Reset All Choices"):
        st.session_state.annotation_choices = {}
        st.rerun()
else:
    st.info("No annotations have been marked yet. Click ✓ or ✗ on annotations above.")