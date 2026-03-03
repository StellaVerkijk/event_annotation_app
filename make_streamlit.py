import streamlit as st
from annotated_text import annotated_text
import ast
import pandas as pd
import random

# Initialize session state
if 'annotation_choices' not in st.session_state:
    st.session_state.annotation_choices = {}

if 'chunk_sources' not in st.session_state:
    st.session_state.chunk_sources = {}

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
    'ORG': '#B0D7FF',  # Baby blue
    'STATUS': '#AFEEEE'  # Pale Turquoise
}

EVENT_COLORS = {
    'event1': '#FF8C00',  # Dark orange
    'event2': '#FFA500',  # Orange
    'event3': '#FFB347',  # Light orange
    'event4': '#FF7F50',  # Coral
    'event5': '#FF6347',  # Tomato
}


def hex_to_rgba(hex_color, opacity=1.0):
    """Convert hex color to rgba with specified opacity."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f'rgba({r}, {g}, {b}, {opacity})'


def get_color_for_label(label, transparent_entities=False):
    """Get the appropriate color for a label."""
    if label in ENTITY_COLORS:
        color = ENTITY_COLORS[label]
        if transparent_entities:
            return hex_to_rgba(color, 0.25)  # 75% transparent = 25% opacity
        return color
    elif label in EVENT_COLORS:
        return EVENT_COLORS[label]
    else:
        # Default colors if not found
        if is_entity_label(label):
            color = '#B3D9FF'  # Default light blue
            if transparent_entities:
                return hex_to_rgba(color, 0.25)
            return color
        else:
            return '#FFD699'  # Default light orange


def is_entity_label(label):
    """Check if a label is an entity type."""
    entity_labels = ['LOC_NAME', 'PER_NAME', 'PER_ATTR', 'PRF', 'CMTY_QUANT',
                     'CMTY_NAME', 'DOC', 'DATE', 'SHIP_TYPE', 'LOC_ADJ', 'ORG', 'STATUS', 'SHIP']
    return any(entity in label for entity in entity_labels)


def count_event_annotations(data):
    """Count the number of event annotations in a data structure."""
    events = data['events']
    count = 0
    for event in events:
        if event.startswith('B-') and not is_entity_label(event[2:]):
            count += 1
    return count


def merge_annotations(event_data, entity_data):
    """Merge event and entity annotations into a single data structure."""
    words = event_data['words']
    events = event_data['events']
    entities = entity_data['entities']

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


def convert_to_annotated_text(data, transparent_entities=False):
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
                color = get_color_for_label(label, transparent_entities)
                result.append((' '.join(current_event_words) + ' ', label, color))
                current_event_words = []

            current_event = event[2:]
            current_event_words = [word]

        elif event.startswith('I-'):
            current_event_words.append(word)

        else:
            if current_event_words and current_event:
                label = current_event
                color = get_color_for_label(label, transparent_entities)
                result.append((' '.join(current_event_words) + ' ', label, color))
                current_event_words = []
                current_event = None

            current_text.append(word)

    if current_text:
        result.append(' '.join(current_text))
    if current_event_words and current_event:
        label = current_event
        color = get_color_for_label(label, transparent_entities)
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


def display_region_with_buttons(pred_data, gold_data, file_id, region_idx, gold_chunk_ids, transparent_entities=False):
    """Display annotated text and buttons for each annotation.
    
    Args:
        pred_data: Prediction annotation data
        gold_data: Gold annotation data
        file_id: Identifier for the file
        region_idx: Index of the current region
        gold_chunk_ids: Set of chunk IDs that should display gold data
        transparent_entities: Whether to make entity labels transparent
    """
    pred_chunks = split_data_into_chunks(pred_data, max_words=150)
    gold_chunks = split_data_into_chunks(gold_data, max_words=150)

    for chunk_idx in range(len(pred_chunks)):
        chunk_id = f"{region_idx}_{chunk_idx}"
        
        # Determine if this chunk should use gold or prediction data
        if chunk_id in gold_chunk_ids:
            chunk = gold_chunks[chunk_idx]
            data_source = 'gold'
        else:
            chunk = pred_chunks[chunk_idx]
            data_source = 'prediction'
        
        # Store the data source for this chunk
        st.session_state.chunk_sources[chunk_id] = data_source
        
        annotated_version = convert_to_annotated_text(chunk, transparent_entities)
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
                            'data_source': data_source
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
                            'data_source': data_source
                        }

                with cols[3]:
                    if key in st.session_state.annotation_choices:
                        choice = st.session_state.annotation_choices[key]['choice']
                        st.markdown("✅ Useful" if choice == 'useful' else "❌ Misleading")

        if chunk_idx < len(pred_chunks) - 1:
            st.markdown("---")


# Main app

st.header("Missive sent from Batavia in 1782 (inv. nr. 3604)")

# Add toggle for transparent entities
transparent_entities = st.toggle("Make entity labels transparent", value=False)

st.subheader("Predictions of Mixed Experts model")

# Load both prediction and gold data
with open('predictions/3604_mixed_experts.json') as f:
    pred_event_data = f.readlines()

with open('gold/3604.json') as f:
    gold_event_data = f.readlines()

with open('gold/curated_entities_3604/p_80-ner-event-preanno_NL-HaNA_1.04.02_3604_0270-0276 - 1782 -.json') as f:
    entity_data = f.readlines()

# Calculate annotation counts per chunk and select chunks to get ~25% gold annotations
if 'gold_chunk_ids' not in st.session_state:
    total_regions = len(pred_event_data)

    # Build a list of all chunks with their annotation counts
    chunk_annotation_counts = []

    for region_idx in range(total_regions):
        pred_event_parsed = ast.literal_eval(pred_event_data[region_idx])
        entity_parsed = ast.literal_eval(entity_data[region_idx])
        merged_pred = merge_annotations(pred_event_parsed, entity_parsed)

        # Split into chunks
        chunks = split_data_into_chunks(merged_pred, max_words=150)

        for chunk_idx, chunk in enumerate(chunks):
            chunk_id = f"{region_idx}_{chunk_idx}"
            annotation_count = count_event_annotations(chunk)
            chunk_annotation_counts.append((chunk_id, annotation_count))

    # Calculate total annotations
    total_annotations = sum(count for _, count in chunk_annotation_counts)
    target_gold_annotations = int(total_annotations * 0.25)

    # Sort chunks by annotation count (smallest first for better control)
    sorted_chunks = sorted(chunk_annotation_counts, key=lambda x: x[1])
    
    # Shuffle to avoid bias but keep small chunks at beginning for better precision
    random.seed(29)
    random.shuffle(sorted_chunks)

    gold_chunk_ids = set()
    current_gold_count = 0

    # Only add chunks that don't exceed the target
    for chunk_id, count in sorted_chunks:
        if current_gold_count + count <= target_gold_annotations:
            gold_chunk_ids.add(chunk_id)
            current_gold_count += count

    st.session_state.gold_chunk_ids = gold_chunk_ids
    st.session_state.total_annotations = total_annotations
    st.session_state.gold_annotations_count = current_gold_count

gold_chunk_ids = st.session_state.gold_chunk_ids

# Display regions with mixed gold/prediction chunks
for region_idx in range(len(pred_event_data)):
    pred_event_parsed = ast.literal_eval(pred_event_data[region_idx])
    gold_event_parsed = ast.literal_eval(gold_event_data[region_idx])
    entity_parsed = ast.literal_eval(entity_data[region_idx])

    merged_pred = merge_annotations(pred_event_parsed, entity_parsed)
    merged_gold = merge_annotations(gold_event_parsed, entity_parsed)

    display_region_with_buttons(merged_pred, merged_gold, '3604_mixed_experts', region_idx, gold_chunk_ids, transparent_entities)
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
        total = gold_count + pred_count
        gold_percentage = (gold_count / total * 100) if total > 0 else 0
        st.write(
            f"Gold annotations: {gold_count} ({gold_percentage:.1f}%) | Prediction annotations: {pred_count} ({100 - gold_percentage:.1f}%)")

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
        st.session_state.chunk_sources = {}
        st.session_state.gold_chunk_ids = None
        st.rerun()
else:
    st.info("No annotations have been marked yet.")
