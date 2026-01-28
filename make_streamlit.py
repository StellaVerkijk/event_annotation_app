import streamlit as st
import json
import ast
from annotated_text import annotated_text


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

with open('3604.json') as f:
    data = f.readlines()

#for line in data:
    #annotated = convert_to_annotated_text(line)

print("EXAMPLE OF DATA")
print(data[3])
print(type(ast.literal_eval(data[3])))

regions = []

for line in data:   
    regions.append(convert_to_annotated_text(ast.literal_eval(line)))
    
st.header("Gold data for Events")

for r in regions:
    annotated_text(r) #shows complete text with labels

    annotations = extract_annotations(r)

    for i, (text, label) in enumerate(annotations):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            annotated_text((text, label))
        
        with col2:
            if st.button("✓", key=f"correct_{i}"):
                st.session_state[f"status_{i}"] = "correct"
        
        with col3:
            if st.button("✗", key=f"wrong_{i}"):
                st.session_state[f"status_{i}"] = "wrong"

