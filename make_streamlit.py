import streamlit as st
from annotated_text import annotated_text
import ast
import pandas as pd
import random

# Initialize session state
if 'annotation_choices' not in st.session_state:
    st.session_state.annotation_choices = {}

if 'region_sources' not in st.session_state:
    st.session_state.region_sources = {}

# Define color schemes with lighter blues
ENTITY_COLORS = {
    'LOC_NAME': '#4A90E2',  # Medium blue
    'LOC_ADJ': '#7FB3D5',  # Light blue
    'PER_NAME': '#9FCDFF',  # Powder blue
    'PER_ATTR': '#5B9BD5',  # Sky blue
    'PRF': '#89CFF0',  # Baby blue
    'CMTY_QUANT': '#6BB6FF',  # Bright blue
    'CMTY_NAME': '#A8D5FF',  # Soft blue
    'DOC': '#1E90FF',  # Dodger blue
    'DATE': '#87CEEB',  # Sky blue light
    'SHIP_TYPE': '#C2DFFF',  # Alice blue
    'ORG': '#B0D7FF'  # Baby blue
     }

# #'LOC_NAME': '#B3D9FF',  # Light blue #'LOC_ADJ': '#CCE5FF',  # Very light blue #'PER_NAME': '#99CCFF',  # Sky blue #'PER_ATTR': '#B8D4FF',  # Pale blue #'PRF': '#D0E8FF',  # Ice blue #'CMTY_QUANT': '#A8D5FF',  # Soft blue #'CMTY_NAME': '#9FCDFF',  # Powder blue #'DOC': '#C2DFFF',  # Alice blue #'DATE': '#BFE3FF',  # Light sky blue #'SHIP_TYPE': '#B0D7FF',  # Baby blue  EVENT_COLORS = {

# Add your event types here with orange shades
EVENT_COLORS = {
    'event1': '#FF8C00',  # Dark orange
    'event2': '#FFA500',  # Orange
    'event3': '#FFB347',  # Light orange
    'event4': '#FF7F50',  # Coral
    'event5': '#FF6347',  # Tomato
}
# Add more event types as needed


def get_color_for_label(label):
    """Get the appropriate color for a label."""
    if label in ENTITY_COLORS:
        return ENTITY_COLORS[label]
    elif label in EVENT_COLORS:
        return EVENT_COLORS[label]
    else:
        # Default colors if not found
        if is_entity_label(label):
            return '#B3D9FF'  # Default light blue
        else:
            return '#FFD699'  # Default light orange


def is_entity_label(label):
    """Check if a label is an entity type."""
    entity_labels = ['LOC_NAME', 'PER_NAME', 'PER_ATTR', 'PRF', 'CMTY_QUANT',
                     'CMTY_NAME', 'DOC', 'DATE', 'SHIP_TYPE', 'LOC_ADJ', 'ORG']
    return any(entity in label for entity in entity_labels)


def merge_annotations(event_data, entity_data):
    """Merge event and entity annotations into a single data structure."""
    words = event_data['words']
    events = event_data['events']
    entities = entity_data['events']

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
    """Convert data to annotated_text format with color coding."""
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
                label = current_event
                color = get_color_for_label(label)
                result.append((' '.join(current_event_words) + ' ', label, color))
                current_event_words = []

            current_event = event[2:]
            current_event_words = [word]

        elif event.startswith('I-'):
            current_event_words.append(word)

        else:
            if current_event_words and current_event:
                label = current_event
                color = get_color_for_label(label)
                result.append((' '.join(current_event_words) + ' ', label, color))
                current_event_words = []
                current_event = None

            current_text.append(word)

    if current_text:
        result.append(' '.join(current_text))
    if current_event_words and current_event:
        label = current_event
        color = get_color_for_label(label)
        result.append((' '.join(current_event_words) + ' ', label, color))

    return result


def extract_annotations(data, annotation_type='event'):
    """Extract annotations. Can filter by type (event vs entity)."""
    words = data['words']
    events = data['events']

    annotations = []
    current_event = None
    current_words = []

    for word, event in zip(words, events):
        if event.startswith('B-'):
            if current_words and current_event:
                label_type = current_event
                is_entity = is_entity_label(label_type)
                is_event = not is_entity

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
                is_entity = is_entity_label(label_type)
                is_event = not is_entity

                if (annotation_type == 'entity' and is_entity) or \
                        (annotation_type == 'event' and is_event) or \
                        (annotation_type == 'all'):
                    annotations.append((' '.join(current_words), current_event, 'entity' if is_entity else 'event'))
                current_words = []
                current_event = None

    if current_words and current_event:
        label_type = current_event
        is_entity = is_entity_label(label_type)
        is_event = not is_entity

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

    num_chunks = (total_words + max_words - 1) // max_words
    chunk_size = total_words // num_chunks
    remainder = total_words % num_chunks

    chunks = []
    start_idx = 0

    for i in range(num_chunks):
        extra = 1 if i < remainder else 0
        end_idx = start_idx + chunk_size + extra

        chunk = {
            'words': words[start_idx:end_idx],
            'events': events[start_idx:end_idx]
        }
        chunks.append(chunk)
        start_idx = end_idx

    return chunks


def display_region_with_buttons(data, file_id, region_idx, data_source):
    """Display annotated text and buttons for each annotation."""
    chunks = split_data_into_chunks(data, max_words=150)

    # Store the data source for this region
    st.session_state.region_sources[f"{file_id}_{region_idx}"] = data_source

    for chunk_idx, chunk in enumerate(chunks):
        annotated_version = convert_to_annotated_text(chunk)
        annotated_text(*annotated_version)

        annotations = extract_annotations(chunk, annotation_type='event')

        if annotations:
            st.markdown("---")
            for ann_idx, (text, label, ann_type) in enumerate(annotations):
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
                            'choice': 'useful',
                            'data_source': data_source  # Track whether this was gold or prediction
                        }

                with cols[2]:
                    if st.button("✗", key=f"wrong_{key}"):
                        st.session_state.annotation_choices[key] = {
                            'file': file_id,
                            'region': region_idx,
                            'chunk': chunk_idx,
                            'text': text,
                            'label': label,
                            'choice': 'misleading',
                            'data_source': data_source  # Track whether this was gold or prediction
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

# Load both prediction and gold data
with open('predictions/3604_mixed_experts.json') as f:
    pred_event_data = f.readlines()

with open('gold/3604.json') as f:
    gold_event_data = f.readlines()

with open('gold/curated_entities_3604/p_80-ner-event-preanno_NL-HaNA_1.04.02_3604_0270-0276 - 1782 -.json') as f:
    entity_data = f.readlines()

# Determine which regions to show as gold (40%)
total_regions = len(pred_event_data)
num_gold_regions = int(total_regions * 0.4)

# Use a fixed seed for consistency across reruns in the same session
if 'gold_region_indices' not in st.session_state:
    random.seed(29)  # You can change this seed or make it random
    st.session_state.gold_region_indices = set(random.sample(range(total_regions), num_gold_regions))

gold_region_indices = st.session_state.gold_region_indices

# Display regions (mix of predictions and gold)
for region_idx in range(total_regions):
    if region_idx in gold_region_indices:
        # Show gold data
        event_parsed = ast.literal_eval(gold_event_data[region_idx])
        entity_parsed = ast.literal_eval(entity_data[region_idx])
        data_source = 'gold'
    else:
        # Show prediction data
        event_parsed = ast.literal_eval(pred_event_data[region_idx])
        entity_parsed = ast.literal_eval(entity_data[region_idx])
        data_source = 'prediction'

    merged_data = merge_annotations(event_parsed, entity_parsed)

    display_region_with_buttons(merged_data, '3604_mixed_experts', region_idx, data_source)
    st.write("")
    st.write("")

# Download section
st.divider()
st.subheader("Download Your Choices")

if st.session_state.annotation_choices:
    df = pd.DataFrame.from_dict(st.session_state.annotation_choices, orient='index')
    st.write(f"Total annotations reviewed: {len(df)}")

    # Show breakdown of gold vs prediction annotations
    if 'data_source' in df.columns:
        gold_count = (df['data_source'] == 'gold').sum()
        pred_count = (df['data_source'] == 'prediction').sum()
        st.write(f"Gold annotations: {gold_count} | Prediction annotations: {pred_count}")

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
        st.session_state.region_sources = {}
        st.session_state.gold_region_indices = None
        st.rerun()
else:
    st.info("No annotations have been marked yet.")