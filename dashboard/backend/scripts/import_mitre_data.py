import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.neo4j.neo4j_db import neo4j_conn

def import_mitre_data():
    print("Loading ICS ATT&CK data...")
    with open('data/ics-attack.json', 'r') as f:
        data = json.load(f)
    
    print(f"Found {len(data['objects'])} objects")
    
    # Clear existing data
    print("Clearing existing data...")
    neo4j_conn.query("MATCH (n) DETACH DELETE n")
    
    # Import techniques
    technique_count = 0
    for obj in data['objects']:
        if obj['type'] == 'attack-pattern':
            # Get external ID (e.g., T0800)
            external_id = None
            for ref in obj.get('external_references', []):
                if ref.get('source_name') in ['mitre-attack', 'mitre-ics-attack']:
                    external_id = ref.get('external_id')
                    break
            
            if not external_id:
                continue
            
            # Get tactics (kill chain phases)
            tactics = [phase['phase_name'] for phase in obj.get('kill_chain_phases', [])]
            
            query = """
            MERGE (t:Technique {id: $id})
            SET t.name = $name,
                t.description = $description,
                t.platforms = $platforms,
                t.tactics = $tactics,
                t.detected = false
            """
            neo4j_conn.query(query, {
                'id': external_id,
                'name': obj.get('name'),
                'description': obj.get('description', ''),
                'platforms': obj.get('x_mitre_platforms', []),
                'tactics': tactics
            })
            technique_count += 1
    
    print(f"Imported {technique_count} techniques")
    
    # Create relationships based on common tactics
    print("Creating technique relationships...")
    relationship_query = """
    MATCH (t1:Technique), (t2:Technique)
    WHERE t1.id <> t2.id
    AND size([tactic IN t1.tactics WHERE tactic IN t2.tactics]) > 0
    MERGE (t1)-[:LEADS_TO {probability: 0.7}]->(t2)
    """
    neo4j_conn.query(relationship_query)
    
    # Mark one technique as detected (for demo purposes)
    print("Marking sample technique as detected...")
    detected_query = """
    MATCH (t:Technique)
    WHERE t.id = 'T0800'
    SET t.detected = true
    """
    neo4j_conn.query(detected_query)
    
    print("ICS ATT&CK data imported successfully!")
    
    # Verify import
    count_query = "MATCH (t:Technique) RETURN count(t) as count"
    result = neo4j_conn.query(count_query)
    print(f"Total techniques in database: {result[0]['count']}")
    
    detected_count_query = "MATCH (t:Technique {detected: true}) RETURN count(t) as count"
    result = neo4j_conn.query(detected_count_query)
    print(f"Detected techniques: {result[0]['count']}")

if __name__ == "__main__":
    import_mitre_data()
