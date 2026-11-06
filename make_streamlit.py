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


st.header("ROBE predictions")

st.subheader("Inventory number 2000, scan 0011")

with open('comparison_data/predictions_robe/NL-HaNA_1.04.02_2000_0011.json') as f:
    data = f.readlines()

regions = []
annotations_per_region = []

for line in data:
    regions.append(convert_to_annotated_text(ast.literal_eval(line)))
    annotations_per_region.append(extract_annotations(ast.literal_eval(line)))

for region_idx, r in enumerate(regions):
    annotated_text(r)  # shows complete text with labels

st.header("EtE predictions")

st.subheader("Inventory number 2000, scan 0011")

with open('comparison_data/predictions_ete/NL-HaNA_1.04.02_2000_0011.json') as f:
    data = f.readlines()

regions = []
annotations_per_region = []

for line in data:
    regions.append(convert_to_annotated_text(ast.literal_eval(line)))
    annotations_per_region.append(extract_annotations(ast.literal_eval(line)))

for region_idx, r in enumerate(regions):
    annotated_text(r)  # shows complete text with labels



st.header("ROBE predictions")

st.subheader("Inventory number 2000, scan 1230")

with open('comparison_data/predictions_robe/NL-HaNA_1.04.02_2000_1230.json') as f:
    data = f.readlines()

regions = []
annotations_per_region = []

for line in data:
    regions.append(convert_to_annotated_text(ast.literal_eval(line)))
    annotations_per_region.append(extract_annotations(ast.literal_eval(line)))

for region_idx, r in enumerate(regions):
    annotated_text(r)  # shows complete text with labels



st.header("EtE predictions")

st.subheader("Inventory number 2000, scan 1230")

with open('comparison_data/predictions_ete/NL-HaNA_1.04.02_2000_1230.json') as f:
    data = f.readlines()

regions = []
annotations_per_region = []

for line in data:
    regions.append(convert_to_annotated_text(ast.literal_eval(line)))
    annotations_per_region.append(extract_annotations(ast.literal_eval(line)))

for region_idx, r in enumerate(regions):
    annotated_text(r)  # shows complete text with labels



st.header("ROBE predictions")

st.subheader("Inventory number 2083, scan 0271")

with open('comparison_data/predictions_robe/NL-HaNA_1.04.02_2083_0271.json') as f:
    data = f.readlines()

regions = []
annotations_per_region = []

for line in data:
    regions.append(convert_to_annotated_text(ast.literal_eval(line)))
    annotations_per_region.append(extract_annotations(ast.literal_eval(line)))

for region_idx, r in enumerate(regions):
    annotated_text(r)  # shows complete text with labels



st.header("EtE predictions")

st.subheader("Inventory number 2083, scan 0271")

with open('comparison_data/predictions_ete/NL-HaNA_1.04.02_2083_0271.json') as f:
    data = f.readlines()

regions = []
annotations_per_region = []

for line in data:
    regions.append(convert_to_annotated_text(ast.literal_eval(line)))
    annotations_per_region.append(extract_annotations(ast.literal_eval(line)))

for region_idx, r in enumerate(regions):
    annotated_text(r)  # shows complete text with labels



st.header("ROBE predictions")

st.subheader("Inventory number 2026, scan 0309")

with open('comparison_data/predictions_robe/NL-HaNA_1.04.02_2026_0309.json') as f:
    data = f.readlines()

regions = []
annotations_per_region = []

for line in data:
    regions.append(convert_to_annotated_text(ast.literal_eval(line)))
    annotations_per_region.append(extract_annotations(ast.literal_eval(line)))

for region_idx, r in enumerate(regions):
    annotated_text(r)  # shows complete text with labels



st.header("EtE predictions")

st.subheader("Inventory number 2026, scan 0309")

with open('comparison_data/predictions_ete/NL-HaNA_1.04.02_2026_0309.json') as f:
    data = f.readlines()

regions = []
annotations_per_region = []

for line in data:
    regions.append(convert_to_annotated_text(ast.literal_eval(line)))
    annotations_per_region.append(extract_annotations(ast.literal_eval(line)))

for region_idx, r in enumerate(regions):
    annotated_text(r)  # shows complete text with labels
