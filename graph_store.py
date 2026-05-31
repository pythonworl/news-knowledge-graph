import json
import os
from typing import Dict, List, Optional
from models import Person, Relationship, ExtractionResult

GRAPH_FILE = "graph_data.json"

class GraphStore:
    def __init__(self):
        self.nodes: Dict[str, Person] = {}
        # edges are stored as a list of relationships
        self.edges: List[Relationship] = []
        self.load()

    def _canonicalize_id(self, name: str) -> str:
        """Simple entity resolution: lowercase and strip to form an ID."""
        # A more robust system would handle Aliases ("Sam Altman" vs "Altman")
        # For simplicity, we just use a normalized string. The LLM is instructed to use full names as IDs.
        return name.lower().strip().replace(" ", "_")

    def merge_extraction(self, extraction: ExtractionResult):
        # Merge people
        for person in extraction.people:
            # We trust the LLM to provide a canonical ID, or we force it here
            cid = self._canonicalize_id(person.id)
            if cid not in self.nodes:
                self.nodes[cid] = Person(id=cid, name=person.name)
            
        # Merge relationships
        for rel in extraction.relationships:
            src_cid = self._canonicalize_id(rel.source)
            tgt_cid = self._canonicalize_id(rel.target)
            
            # Ensure nodes exist (sometimes LLM might invent a node in edges but not in people list)
            if src_cid not in self.nodes:
                self.nodes[src_cid] = Person(id=src_cid, name=rel.source)
            if tgt_cid not in self.nodes:
                self.nodes[tgt_cid] = Person(id=tgt_cid, name=rel.target)

            # Check for duplicate edge
            is_dup = False
            for existing_rel in self.edges:
                if (existing_rel.source == src_cid and 
                    existing_rel.target == tgt_cid and 
                    existing_rel.type == rel.type):
                    is_dup = True
                    break
            
            if not is_dup:
                # Store with canonicalized IDs
                self.edges.append(Relationship(
                    source=src_cid,
                    target=tgt_cid,
                    type=rel.type,
                    explanation=rel.explanation,
                    provenance=rel.provenance
                ))
        
        self.save()

    def get_people(self, skip: int = 0, limit: int = 10) -> List[Person]:
        all_people = list(self.nodes.values())
        return all_people[skip : skip + limit]

    def get_person(self, person_id: str) -> Optional[Person]:
        return self.nodes.get(person_id)

    def get_direct_relationships(self, person_id: str) -> List[Relationship]:
        result = []
        for edge in self.edges:
            if edge.source == person_id or edge.target == person_id:
                result.append(edge)
        return result

    def save(self):
        data = {
            "nodes": [p.dict() for p in self.nodes.values()],
            "edges": [e.dict() for e in self.edges]
        }
        with open(GRAPH_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self):
        if os.path.exists(GRAPH_FILE):
            with open(GRAPH_FILE, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    for n in data.get("nodes", []):
                        self.nodes[n["id"]] = Person(**n)
                    for e in data.get("edges", []):
                        self.edges.append(Relationship(**e))
                except json.JSONDecodeError:
                    pass

graph_db = GraphStore()
