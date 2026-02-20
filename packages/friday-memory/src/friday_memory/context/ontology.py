"""
Ontology configuration for memory extraction.

Defines the allowed node types, edge relation types, and label constraints
that govern what gets stored in the knowledge graph. Serves double duty:
1. Injected into the extraction prompt to constrain LLM output
2. Used by ExtractionFilter for post-processing validation

The ontology is config-driven via YAML for easy tuning without code changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class NodeTypeConfig:
    """Configuration for an allowed node type in the ontology.

    Attributes:
        description: Human-readable description of what this type represents.
        examples: Example entity labels of this type, used in prompt injection.
    """

    description: str
    examples: list[str] = field(default_factory=list)


@dataclass
class OntologyConfig:
    """Configuration defining the allowed ontology for knowledge graph extraction.

    Controls which node types, edge relations, and label patterns are valid.
    Loaded from YAML config or created with sensible defaults.

    Attributes:
        node_types: Mapping of allowed type names to their configs.
        edge_relations: Mapping of category names to lists of canonical relation names.
        label_blocklist: Words that disqualify a node label (case-insensitive).
        max_label_length: Maximum allowed label length in characters.
        min_label_length: Minimum allowed label length in characters.
    """

    node_types: dict[str, NodeTypeConfig]
    edge_relations: dict[str, list[str]]
    label_blocklist: list[str] = field(default_factory=list)
    max_label_length: int = 60
    min_label_length: int = 2

    @property
    def allowed_node_types(self) -> set[str]:
        """Return the set of allowed node type names."""
        return set(self.node_types.keys())

    @property
    def all_edge_relations(self) -> set[str]:
        """Return flat set of all canonical edge relation names across categories."""
        relations: set[str] = set()
        for category_relations in self.edge_relations.values():
            relations.update(category_relations)
        return relations

    @property
    def edge_relations_upper(self) -> set[str]:
        """Return all canonical edge relations normalized to uppercase."""
        return {r.upper() for r in self.all_edge_relations}

    def format_for_prompt(self) -> str:
        """Render the ontology as human-readable text for injection into extraction prompts.

        Returns:
            Formatted string listing allowed entity types and relations with examples.
        """  # noqa: E501
        lines: list[str] = []

        # Node types section
        lines.append("ALLOWED ENTITY TYPES:")
        for type_name, config in self.node_types.items():
            examples_str = ""
            if config.examples:
                examples_str = f" (e.g., {', '.join(config.examples)})"
            lines.append(f"- {type_name}: {config.description}{examples_str}")

        lines.append("")

        # Edge relations section
        lines.append("ALLOWED RELATIONS (use ONLY these):")
        for category, relations in self.edge_relations.items():
            category_display = category.replace("_", " ").title()
            lines.append(f"{category_display}: {', '.join(relations)}")

        return "\n".join(lines)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OntologyConfig:
        """Create an OntologyConfig from a parsed YAML/dict structure.

        Args:
            data: Dictionary with keys matching the ontology config schema.
                  Expected structure:
                  {
                      "node_types": {"person": {"description": "...", "examples": [...]}},
                      "edge_relations": {"ownership": ["OWNS", "CREATED"]},
                      "label_blocklist": ["morning", "afternoon"],
                      "max_label_length": 60,
                      "min_label_length": 2,
                  }

        Returns:
            Configured OntologyConfig instance.
        """  # noqa: E501
        node_types: dict[str, NodeTypeConfig] = {}
        for type_name, type_data in data.get("node_types", {}).items():
            if isinstance(type_data, dict):
                node_types[type_name] = NodeTypeConfig(
                    description=type_data.get("description", ""),
                    examples=type_data.get("examples", []),
                )
            elif isinstance(type_data, str):
                # Simple format: just a description string
                node_types[type_name] = NodeTypeConfig(description=type_data)

        edge_relations: dict[str, list[str]] = {}
        for category, relations in data.get("edge_relations", {}).items():
            if isinstance(relations, list):
                edge_relations[category] = relations

        return cls(
            node_types=node_types,
            edge_relations=edge_relations,
            label_blocklist=data.get("label_blocklist", []),
            max_label_length=data.get("max_label_length", 60),
            min_label_length=data.get("min_label_length", 2),
        )

    @classmethod
    def default(cls) -> OntologyConfig:
        """Create a default ontology with sensible built-in types and relations.

        Returns:
            OntologyConfig with standard entity types and ~30 canonical relations.
        """
        return cls(
            node_types={
                "person": NodeTypeConfig(
                    description="A human individual",
                    examples=["Chuck", "Elon Musk", "Dr. Smith"],
                ),
                "organization": NodeTypeConfig(
                    description="A company, institution, or group",
                    examples=["Google", "MIT", "United Nations"],
                ),
                "technology": NodeTypeConfig(
                    description="A software tool, language, framework, or hardware",
                    examples=["Python", "React", "ChromaDB", "GPU"],
                ),
                "location": NodeTypeConfig(
                    description="A physical or virtual place",
                    examples=["San Francisco", "GitHub", "AWS us-east-1"],
                ),
                "product": NodeTypeConfig(
                    description="A named product, service, or system",
                    examples=["Friday", "ChatGPT", "iPhone"],
                ),
                "document": NodeTypeConfig(
                    description="A named document, spec, or reference",
                    examples=["README", "RFC 7231", "build plan"],
                ),
            },
            edge_relations={
                "ownership": ["OWNS", "CREATED", "AUTHORED", "FOUNDED"],
                "association": [
                    "WORKS_AT",
                    "MEMBER_OF",
                    "AFFILIATED_WITH",
                    "PART_OF",
                ],
                "usage": ["USES", "DEPENDS_ON", "BUILT_WITH", "INTEGRATES"],
                "action": [
                    "MANAGES",
                    "MAINTAINS",
                    "CONTRIBUTES_TO",
                    "DEVELOPS",
                ],
                "knowledge": ["KNOWS", "EXPERT_IN", "STUDIES", "TEACHES"],
                "relationship": [
                    "RELATES_TO",
                    "SIMILAR_TO",
                    "DERIVES_FROM",
                    "REPLACES",
                ],
                "spatial": ["LOCATED_IN", "DEPLOYED_ON", "HOSTED_BY"],
                "preference": ["PREFERS", "DISLIKES", "RECOMMENDS"],
            },
            label_blocklist=[
                "morning",
                "afternoon",
                "evening",
                "today",
                "yesterday",
                "data",
                "thing",
                "stuff",
                "something",
            ],
            max_label_length=60,
            min_label_length=2,
        )
