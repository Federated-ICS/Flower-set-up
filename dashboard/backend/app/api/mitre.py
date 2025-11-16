from typing import List

from fastapi import APIRouter, HTTPException

from app.models.mitre import AttackGraph, TechniqueDetails, TechniqueLink, TechniqueNode
from app.neo4j.neo4j_db import neo4j_conn

router = APIRouter(prefix="/api/mitre", tags=["mitre"])


@router.get("/graph", response_model=AttackGraph)
async def get_attack_graph():
    """Get the current attack graph with predictions"""
    try:
        # Get current attacks (from alerts)
        current_query = """
        MATCH (t:Technique)
        WHERE t.detected = true
        RETURN t.id as id, t.name as name, 1.0 as probability
        """
        current = neo4j_conn.query(current_query)

        # Get predicted attacks (techniques that current attacks lead to)
        predicted_query = """
        MATCH (current:Technique)-[:LEADS_TO]->(predicted:Technique)
        WHERE current.detected = true AND predicted.detected = false
        RETURN DISTINCT predicted.id as id, predicted.name as name, 0.85 as probability
        LIMIT 20
        """
        predicted = neo4j_conn.query(predicted_query)

        # Build nodes
        nodes = [
            TechniqueNode(id=n["id"], name=n["name"], type="current", probability=n["probability"])
            for n in current
        ] + [
            TechniqueNode(
                id=n["id"], name=n["name"], type="predicted", probability=n["probability"]
            )
            for n in predicted
        ]

        # Create a set of node IDs for quick lookup
        node_ids = {node.id for node in nodes}

        # Build links (only between nodes that exist in our graph)
        links_query = """
        MATCH (source:Technique)-[r:LEADS_TO]->(target:Technique)
        WHERE source.detected = true AND target.detected = false
        RETURN DISTINCT source.id as source, target.id as target, r.probability as probability
        LIMIT 50
        """
        links_data = neo4j_conn.query(links_query)

        # Filter links to only include those between existing nodes
        links = [
            TechniqueLink(
                source=link["source"], target=link["target"], probability=link["probability"]
            )
            for link in links_data
            if link["source"] in node_ids and link["target"] in node_ids
        ]

        return AttackGraph(nodes=nodes, links=links)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/techniques", response_model=List[TechniqueDetails])
async def get_all_techniques():
    """Get all MITRE ATT&CK techniques"""
    try:
        query = """
        MATCH (t:Technique)
        RETURN t.id as id, t.name as name, t.description as description,
               t.platforms as platforms, t.tactics as tactics
        ORDER BY t.id
        LIMIT 100
        """
        results = neo4j_conn.query(query)
        return [
            TechniqueDetails(
                id=r["id"],
                name=r["name"],
                description=r["description"],
                detection=None,
                mitigation=None,
                platforms=r["platforms"] or [],
                tactics=r["tactics"] or [],
            )
            for r in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/technique/{technique_id}", response_model=TechniqueDetails)
async def get_technique_details(technique_id: str):
    """Get details for a specific technique"""
    try:
        query = """
        MATCH (t:Technique {id: $id})
        RETURN t.id as id, t.name as name, t.description as description,
               t.platforms as platforms, t.tactics as tactics
        """
        results = neo4j_conn.query(query, {"id": technique_id})

        if not results:
            raise HTTPException(status_code=404, detail="Technique not found")

        r = results[0]
        return TechniqueDetails(
            id=r["id"],
            name=r["name"],
            description=r["description"],
            detection=(
                "Monitor for unusual patterns in ICS network traffic " "and device behavior..."
            ),
            mitigation=(
                "Implement network segmentation "
                ", access controls,"
                "and regular security audits..."
            ),
            platforms=r["platforms"] or [],
            tactics=r["tactics"] or [],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
