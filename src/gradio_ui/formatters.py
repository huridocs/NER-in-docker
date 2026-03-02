from typing import Dict, Any
from .constants import ENTITY_COLORS


def format_entity_display(entity: Dict[str, Any]) -> str:
    """Format a single entity for display."""
    entity_type = entity.get("type", "UNKNOWN")
    text = entity.get("text", "")
    color = ENTITY_COLORS.get(entity_type, "#95A5A6")

    return f'<span style="background-color: {color}; padding: 2px 6px; border-radius: 3px; color: white; margin: 2px; display: inline-block;">{text} ({entity_type})</span>'


def format_entities_html(entities: list) -> str:
    """Format entities list as HTML."""
    if not entities:
        return "<p>No entities found.</p>"

    html = "<div style='line-height: 2.5;'>"

    # Group by entity type
    entities_by_type = {}
    for entity in entities:
        entity_type = entity.get("type", "UNKNOWN")
        if entity_type not in entities_by_type:
            entities_by_type[entity_type] = []
        entities_by_type[entity_type].append(entity)

    # Display grouped entities
    for entity_type, type_entities in entities_by_type.items():
        color = ENTITY_COLORS.get(entity_type, "#95A5A6")
        html += f'<h4 style="color: {color}; margin-top: 15px;">{entity_type} ({len(type_entities)})</h4>'
        html += '<div style="margin-bottom: 10px;">'
        for entity in type_entities:
            html += format_entity_display(entity)
        html += "</div>"

    html += "</div>"
    return html


def create_legend() -> str:
    """Create a legend showing entity types and their colors."""
    legend_html = "<div style='padding: 10px; background-color: #f5f5f5; border-radius: 5px; margin-bottom: 10px;'>"
    legend_html += "<h4 style='margin-top: 0;'>Entity Types Legend:</h4>"
    legend_html += "<div style='display: flex; flex-wrap: wrap; gap: 10px;'>"

    entity_labels = {
        "PERSON": "Person (PER)",
        "ORGANIZATION": "Organization (ORG)",
        "LOCATION": "Location (LOC)",
        "DATE": "Date (DAT)",
        "LAW": "Law (LAW)",
        "DOCUMENT_CODE": "Document Code (DOC)",
        "REFERENCE": "Reference (REF)",
    }

    for entity_type, label in entity_labels.items():
        color = ENTITY_COLORS.get(entity_type, "#95A5A6")
        legend_html += f'<span style="background-color: {color}; padding: 5px 10px; border-radius: 3px; color: white; font-weight: bold;">{label}</span>'

    legend_html += "</div></div>"
    return legend_html
