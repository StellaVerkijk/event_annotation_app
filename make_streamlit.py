import streamlit as st
from annotated_text import annotated_text
import ast
import pandas as pd

# Initialize session state
if 'annotation_choices' not in st.session_state:
    st.session_state.annotation_choices = {}


def merge_annotations(event_data, entity_data):
    """Merge event and entity annotations into a single data structure."""
    # Assuming both have the same words in the same order
    words = event_data['words']
    events = event_data['events']
    entities = entity_data['events']  # Entity labels are in the 'events' field

    # Combine events and entities - prioritize events, add entities where events are 'O'
    combined = []
    for event, entity in zip(events, entities):
        if event != 'O':
            combined.append(event)
        else:
            combined.append(entity)

    return {
        'words': words,
        'events': combined
    }


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


def extract_annotations(data, annotation_type='event'):
    """Extract annotations. Can filter by type (event vs entity)."""
    words = data['words']
    events = data['events']

    # Define which labels are events vs entities
    event_labels = ['event1', 'event2']  # Add your event label types here
    entity_labels = ['LOC_NAME', 'PER_NAME', 'PER_ATTR', 'PRF', 'CMTY_QUANT',
                     'CMTY_NAME', 'DOC', 'DATE', 'SHIP_TYPE', 'LOC_ADJ']  # Your entity types

    annotations = []
    current_event = None
    current_words = []

    for word, event in zip(words, events):
        if event.startswith('B-'):
            if current_words and current_event:
                label_type = current_event
                # Determine if this is an event or entity
                is_entity = any(entity in label_type for entity in entity_labels)
                is_event = any(evt in label_type for evt in event_labels) or not is_entity

                if (annotation_type == 'entity' and is_entity) or \
                        (annotation_type == 'event' and is_event) or \
                        (annotation_type == 'all'):
                    annotations.append((' '.join(current_words), current_event, 'entity' if is_entity else 'event'))

            current_event = event[2:]
            current_words = [word]

        elif event.startswith('I-'):
            current_words.append(word)

        else:
            if current_words and current_event:
                label_type = current_event
                is_entity = any(entity in label_type for entity in entity_labels)
                is_event = any(evt in label_type for evt in event_labels) or not is_entity

                if (annotation_type == 'entity' and is_entity) or \
                        (annotation_type == 'event' and is_event) or \
                        (annotation_type == 'all'):
                    annotations.append((' '.join(current_words), current_event, 'entity' if is_entity else 'event'))
                current_words = []
                current_event = None

    if current_words and current_event:
        label_type = current_event
        is_entity = any(entity in label_type for entity in entity_labels)
        is_event = any(evt in label_type for evt in event_labels) or not is_entity

        if (annotation_type == 'entity' and is_entity) or \
                (annotation_type == 'event' and is_event) or \
                (annotation_type == 'all'):
            annotations.append((' '.join(current_words), current_event, 'entity' if is_entity else 'event'))

    return annotations


def split_data_into_chunks(data, max_words=150):
    """Split data into roughly equal chunks, each up to max_words."""
    words = data['words']
    events = data['events']

    total_words = len(words)

    if total_words <= max_words:
        return [data]

    # Calculate optimal number of chunks
    num_chunks = (total_words + max_words - 1) // max_words  # Ceiling division
    chunk_size = total_words // num_chunks
    remainder = total_words % num_chunks

    chunks = []
    start_idx = 0

    for i in range(num_chunks):
        # Distribute remainder words across first chunks
        extra = 1 if i < remainder else 0
        end_idx = start_idx + chunk_size + extra

        chunk = {
            'words': words[start_idx:end_idx],
            'events': events[start_idx:end_idx]
        }
        chunks.append(chunk)
        start_idx = end_idx

    return chunks


def display_region_with_buttons(data, file_id, region_idx):
    """Display annotated text and buttons for each annotation."""
    # Check if we need to split the region
    chunks = split_data_into_chunks(data, max_words=150)

    for chunk_idx, chunk in enumerate(chunks):
        # Display the full annotated text
        annotated_version = convert_to_annotated_text(chunk)
        annotated_text(*annotated_version)

        # Get all annotations - only events get buttons
        annotations = extract_annotations(chunk, annotation_type='event')

        # Display compact buttons for each event annotation
        if annotations:
            st.markdown("---")
            for ann_idx, (text, label, ann_type) in enumerate(annotations):
                # Use chunk_idx in the key to make it unique across chunks
                key = f"{file_id}_{region_idx}_{chunk_idx}_{ann_idx}"

                cols = st.columns([0.6, 0.1, 0.1, 0.2])

                with cols[0]:
                    st.markdown(f"**{text}** `({label})`")

                with cols[1]:
                    if st.button("✓", key=f"correct_{key}"):
                        st.session_state.annotation_choices[key] = {
                            'file': file_id,
                            'region': region_idx,
                            'chunk': chunk_idx,
                            'text': text,
                            'label': label,
                            'choice': 'useful'
                        }

                with cols[2]:
                    if st.button("✗", key=f"wrong_{key}"):
                        st.session_state.annotation_choices[key] = {
                            'file': file_id,
                            'region': region_idx,
                            'chunk': chunk_idx,
                            'text': text,
                            'label': label,
                            'choice': 'misleading'
                        }

                with cols[3]:
                    if key in st.session_state.annotation_choices:
                        choice = st.session_state.annotation_choices[key]['choice']
                        st.markdown("✅ Useful" if choice == 'useful' else "❌ Misleading")

        if len(chunks) > 1 and chunk_idx < len(chunks) - 1:
            st.markdown("---")


# Main app

st.header("Missive sent from Batavia in 1782 (inv. nr. 3604)")

st.subheader("Predictions of Mixed Experts model")

# Load both event and entity predictions
with open('predictions/3604_mixed_experts.json') as f:
    event_data = f.readlines()

with open('gold/curated_entities_3604/p_80-ner-event-preanno_NL-HaNA_1.04.02_3604_0270-0276 - 1782 -.json') as f:
    entity_data = f.readlines()

# Merge and display
for region_idx in range(len(event_data)):
    event_parsed = ast.literal_eval(event_data[region_idx])
    entity_parsed = ast.literal_eval(entity_data[region_idx])

    # Merge the annotations
    merged_data = merge_annotations(event_parsed, entity_parsed)

    display_region_with_buttons(merged_data, '3604_mixed_experts', region_idx)
    st.write("")
    st.write("")

st.subheader("Gold annotations")

# Load both gold event and entity annotations
with open('gold/3604.json') as f:
    gold_event_data = f.readlines()

with open('gold/curated_entities_3604/p_80-ner-event-preanno_NL-HaNA_1.04.02_3604_0270-0276 - 1782 -.json') as f:
    gold_entity_data = f.readlines()

# Merge and display
for region_idx in range(len(gold_event_data)):
    event_parsed = ast.literal_eval(gold_event_data[region_idx])
    entity_parsed = ast.literal_eval(gold_entity_data[region_idx])

    # Merge the annotations
    merged_data = merge_annotations(event_parsed, entity_parsed)

    display_region_with_buttons(merged_data, '3604', region_idx)
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