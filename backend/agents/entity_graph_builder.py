import spacy
import networkx as nx
from typing import Dict, List, Tuple, Any
import re
from datetime import datetime
import json

class EntityGraphBuilder:
    def __init__(self):
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback to basic NER if spaCy model not available
            self.nlp = None
            print("Warning: spaCy model not found. Using basic NER fallback.")
        
        self.graph = nx.DiGraph()
        self.entity_types = {
            'PERSON': 'person',
            'ORG': 'organization', 
            'GPE': 'location',
            'DATE': 'date',
            'EVENT': 'event',
            'PROJECT': 'project',
            'COMPANY': 'company'
        }
    
    def build_entity_graph(self, content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build a knowledge graph from public content updates.
        
        Args:
            content: List of content updates with 'title', 'snippet', 'source', 'date'
            
        Returns:
            Dict with nodes, edges, and raw triples
        """
        self.graph.clear()
        
        # Extract entities and relationships from each content piece
        all_triples = []
        
        for item in content:
            text = f"{item.get('title', '')} {item.get('snippet', '')}"
            source = item.get('source', 'Unknown')
            date = item.get('date', '')
            
            # Extract entities and relationships
            entities = self._extract_entities(text)
            relationships = self._extract_relationships(text, source, date)
            
            # Add to graph
            self._add_to_graph(entities, relationships)
            all_triples.extend(relationships)
        
        return {
            "nodes": self._get_nodes(),
            "edges": self._get_edges(),
            "raw_triples": all_triples,
            "graph_stats": {
                "node_count": self.graph.number_of_nodes(),
                "edge_count": self.graph.number_of_edges(),
                "density": nx.density(self.graph) if self.graph.number_of_nodes() > 1 else 0
            }
        }
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text using spaCy or fallback."""
        entities = []
        
        if self.nlp:
            # Use spaCy for advanced NER
            doc = self.nlp(text)
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "type": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                })
        else:
            # Basic fallback NER using regex patterns
            entities = self._basic_ner(text)
        
        return entities
    
    def _basic_ner(self, text: str) -> List[Dict[str, Any]]:
        """Basic NER fallback using regex patterns."""
        entities = []
        
        # Company/Organization patterns
        company_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|LLC|Ltd|Company|Co)\b',
            r'\b[A-Z][A-Z]+\b',  # Acronyms like IBM, NASA
        ]
        
        # Person patterns (simple)
        person_patterns = [
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # First Last
        ]
        
        # Date patterns
        date_patterns = [
            r'\b\d{4}\b',  # Year
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',
        ]
        
        # Extract matches
        for pattern in company_patterns:
            for match in re.finditer(pattern, text):
                entities.append({
                    "text": match.group(),
                    "type": "ORG",
                    "start": match.start(),
                    "end": match.end()
                })
        
        for pattern in person_patterns:
            for match in re.finditer(pattern, text):
                entities.append({
                    "text": match.group(),
                    "type": "PERSON", 
                    "start": match.start(),
                    "end": match.end()
                })
        
        for pattern in date_patterns:
            for match in re.finditer(pattern, text):
                entities.append({
                    "text": match.group(),
                    "type": "DATE",
                    "start": match.start(),
                    "end": match.end()
                })
        
        return entities
    
    def _extract_relationships(self, text: str, source: str, date: str) -> List[Tuple[str, str, str]]:
        """Extract relationships between entities."""
        relationships = []
        
        # Common relationship patterns
        relationship_patterns = [
            (r'(\w+)\s+(?:spoke at|presented at|attended)\s+(\w+)', 'spoke_at'),
            (r'(\w+)\s+(?:joined|works at|employed by)\s+(\w+)', 'works_at'),
            (r'(\w+)\s+(?:invested in|funded|backed)\s+(\w+)', 'invested_in'),
            (r'(\w+)\s+(?:wrote|published|authored)\s+(?:about|on)\s+(\w+)', 'wrote_about'),
            (r'(\w+)\s+(?:launched|started|founded)\s+(\w+)', 'founded'),
            (r'(\w+)\s+(?:acquired|bought|purchased)\s+(\w+)', 'acquired'),
        ]
        
        for pattern, relation_type in relationship_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entity1, entity2 = match.groups()
                relationships.append((entity1.strip(), relation_type, entity2.strip()))
        
        return relationships
    
    def _add_to_graph(self, entities: List[Dict], relationships: List[Tuple[str, str, str]]):
        """Add entities and relationships to the graph."""
        # Add entities as nodes
        for entity in entities:
            node_id = entity["text"]
            if not self.graph.has_node(node_id):
                self.graph.add_node(node_id, 
                                  type=entity["type"],
                                  label=entity["text"])
        
        # Add relationships as edges
        for subject, relation, object_ in relationships:
            if subject and object_:
                self.graph.add_edge(subject, object_, 
                                  relation=relation,
                                  weight=1.0)
    
    def _get_nodes(self) -> List[Dict[str, Any]]:
        """Get all nodes from the graph."""
        nodes = []
        for node, data in self.graph.nodes(data=True):
            nodes.append({
                "id": node,
                "label": data.get("label", node),
                "type": data.get("type", "unknown"),
                "degree": self.graph.degree(node)
            })
        return nodes
    
    def _get_edges(self) -> List[Dict[str, Any]]:
        """Get all edges from the graph."""
        edges = []
        for source, target, data in self.graph.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                "relation": data.get("relation", "related_to"),
                "weight": data.get("weight", 1.0)
            })
        return edges
    
    def get_relevant_subgraph(self, query_entities: List[str], max_depth: int = 2) -> Dict[str, Any]:
        """
        Get a subgraph containing relevant entities and their neighbors.
        
        Args:
            query_entities: List of entity names to search for
            max_depth: Maximum distance from query entities
            
        Returns:
            Subgraph with relevant nodes and edges
        """
        relevant_nodes = set()
        
        for entity in query_entities:
            if self.graph.has_node(entity):
                # Get nodes within max_depth distance
                for node in nx.single_source_shortest_path_length(self.graph, entity, cutoff=max_depth):
                    relevant_nodes.add(node)
        
        # Create subgraph
        subgraph = self.graph.subgraph(relevant_nodes)
        
        return {
            "nodes": [{"id": n, "label": self.graph.nodes[n].get("label", n), 
                      "type": self.graph.nodes[n].get("type", "unknown")} 
                     for n in subgraph.nodes()],
            "edges": [{"source": u, "target": v, "relation": d.get("relation", "related_to")} 
                     for u, v, d in subgraph.edges(data=True)]
        }

# Convenience function for easy import
async def build_entity_graph(content: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build entity graph from content updates."""
    builder = EntityGraphBuilder()
    return builder.build_entity_graph(content) 