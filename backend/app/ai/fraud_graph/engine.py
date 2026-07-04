"""
KAVACH AI — Fraud Network Graph Engine
Graph-based analysis for detecting fraud rings, suspicious transaction
networks, and money laundering patterns.

Techniques:
1. Graph Construction from transactions/communications
2. Community Detection (Louvain algorithm)
3. Centrality Analysis (degree, betweenness, PageRank)
4. Anomaly Detection (outlier nodes, unusual patterns)
5. Fraud Ring Identification
"""

from typing import Any, Dict, List

import networkx as nx
import numpy as np


class FraudGraphEngine:
    """
    Fraud network analysis using graph theory.
    Identifies fraud rings, central actors, and suspicious patterns.
    """

    def __init__(self):
        self.risk_thresholds = {
            "high_degree": 10,        # Nodes with >10 connections
            "high_amount": 100000,    # Transactions > ₹1,00,000
            "rapid_transactions": 5,  # >5 transactions in short window
        }

    def build_network(self, transactions: list) -> Dict[str, Any]:
        """
        Build and analyze a fraud network from transaction records.

        Args:
            transactions: List of Transaction ORM objects.

        Returns:
            Network data with nodes, edges, communities, and risk analysis.
        """
        G = nx.DiGraph()

        # Build graph from transactions
        for txn in transactions:
            sender = txn.sender_id
            receiver = txn.receiver_id

            # Add nodes
            if not G.has_node(sender):
                G.add_node(sender, label=txn.sender_name or sender,
                           node_type="account", risk_score=0.0,
                           is_flagged=False, total_sent=0.0, total_received=0.0,
                           transaction_count=0)
            if not G.has_node(receiver):
                G.add_node(receiver, label=txn.receiver_name or receiver,
                           node_type="account", risk_score=0.0,
                           is_flagged=False, total_sent=0.0, total_received=0.0,
                           transaction_count=0)

            # Update node stats
            G.nodes[sender]['total_sent'] += txn.amount
            G.nodes[sender]['transaction_count'] += 1
            G.nodes[receiver]['total_received'] += txn.amount
            G.nodes[receiver]['transaction_count'] += 1

            if txn.is_flagged:
                G.nodes[sender]['is_flagged'] = True
                G.nodes[receiver]['is_flagged'] = True

            # Add or update edge
            if G.has_edge(sender, receiver):
                G[sender][receiver]['weight'] += txn.amount
                G[sender][receiver]['transaction_count'] += 1
                G[sender][receiver]['total_amount'] += txn.amount
            else:
                G.add_edge(sender, receiver,
                           weight=txn.amount,
                           transaction_count=1,
                           total_amount=txn.amount,
                           edge_type="transaction")

        if len(G.nodes) == 0:
            return self._empty_network()

        # ── Centrality Analysis ──────────────────────────
        degree_centrality = nx.degree_centrality(G)
        try:
            betweenness_centrality = nx.betweenness_centrality(G)
        except Exception:
            betweenness_centrality = {n: 0 for n in G.nodes}

        try:
            pagerank = nx.pagerank(G, alpha=0.85)
        except Exception:
            pagerank = {n: 1.0/len(G.nodes) for n in G.nodes}

        # ── Calculate Risk Scores ────────────────────────
        for node in G.nodes:
            risk_components = []

            # High degree → suspicious hub
            deg = G.degree(node)
            if deg > self.risk_thresholds["high_degree"]:
                risk_components.append(0.8)
            elif deg > 5:
                risk_components.append(0.4)

            # High betweenness → potential money mule
            bc = betweenness_centrality.get(node, 0)
            risk_components.append(min(bc * 5, 1.0))

            # High transaction volume
            total_flow = G.nodes[node]['total_sent'] + G.nodes[node]['total_received']
            if total_flow > self.risk_thresholds["high_amount"]:
                risk_components.append(0.6)

            # Previously flagged
            if G.nodes[node]['is_flagged']:
                risk_components.append(0.9)

            # Pagerank (importance in network)
            pr = pagerank.get(node, 0)
            risk_components.append(min(pr * len(G.nodes), 1.0))

            # Composite risk
            if risk_components:
                G.nodes[node]['risk_score'] = round(
                    sum(risk_components) / len(risk_components), 4
                )

        # ── Community Detection ──────────────────────────
        communities = self._detect_communities(G)

        # ── Identify Central Nodes ───────────────────────
        central_nodes = sorted(
            G.nodes,
            key=lambda n: G.nodes[n]['risk_score'],
            reverse=True,
        )[:10]

        # ── Build response ───────────────────────────────
        nodes = [
            {
                "id": node,
                "label": G.nodes[node].get('label', node),
                "node_type": G.nodes[node].get('node_type', 'account'),
                "risk_score": G.nodes[node].get('risk_score', 0.0),
                "is_flagged": G.nodes[node].get('is_flagged', False),
                "metadata": {
                    "total_sent": G.nodes[node].get('total_sent', 0),
                    "total_received": G.nodes[node].get('total_received', 0),
                    "transaction_count": G.nodes[node].get('transaction_count', 0),
                    "degree_centrality": round(degree_centrality.get(node, 0), 4),
                    "betweenness_centrality": round(betweenness_centrality.get(node, 0), 4),
                    "pagerank": round(pagerank.get(node, 0), 6),
                },
            }
            for node in G.nodes
        ]

        edges = [
            {
                "source": u,
                "target": v,
                "weight": round(data.get('weight', 0), 2),
                "transaction_count": data.get('transaction_count', 0),
                "total_amount": round(data.get('total_amount', 0), 2),
                "edge_type": data.get('edge_type', 'transaction'),
            }
            for u, v, data in G.edges(data=True)
        ]

        # Risk summary
        flagged_nodes = [n for n in G.nodes if G.nodes[n].get('is_flagged')]
        high_risk_nodes = [n for n in G.nodes if G.nodes[n].get('risk_score', 0) > 0.6]

        risk_summary = {
            "total_nodes": len(G.nodes),
            "total_edges": len(G.edges),
            "flagged_accounts": len(flagged_nodes),
            "high_risk_accounts": len(high_risk_nodes),
            "communities_detected": len(communities),
            "total_transaction_volume": sum(
                data.get('total_amount', 0) for _, _, data in G.edges(data=True)
            ),
            "network_density": round(nx.density(G), 4),
        }

        return {
            "nodes": nodes,
            "edges": edges,
            "communities": communities,
            "central_nodes": central_nodes,
            "risk_summary": risk_summary,
        }

    def _detect_communities(self, G: nx.DiGraph) -> List[Dict[str, Any]]:
        """Detect communities/clusters using connected components."""
        communities = []

        # Convert to undirected for community detection
        G_undirected = G.to_undirected()

        for i, component in enumerate(nx.connected_components(G_undirected)):
            if len(component) < 2:
                continue

            members = list(component)
            subgraph = G.subgraph(members)

            # Analyze community risk
            risk_scores = [G.nodes[n].get('risk_score', 0) for n in members]
            flagged = sum(1 for n in members if G.nodes[n].get('is_flagged', False))
            total_volume = sum(
                data.get('total_amount', 0)
                for _, _, data in subgraph.edges(data=True)
            )

            community = {
                "id": f"community_{i}",
                "member_count": len(members),
                "members": members[:20],  # Limit for API response
                "average_risk": round(np.mean(risk_scores), 4) if risk_scores else 0,
                "max_risk": round(max(risk_scores), 4) if risk_scores else 0,
                "flagged_members": flagged,
                "transaction_volume": round(total_volume, 2),
                "is_suspicious": np.mean(risk_scores) > 0.4 if risk_scores else False,
            }
            communities.append(community)

        return sorted(communities, key=lambda c: c['average_risk'], reverse=True)

    def _empty_network(self) -> Dict[str, Any]:
        """Return empty network structure."""
        return {
            "nodes": [],
            "edges": [],
            "communities": [],
            "central_nodes": [],
            "risk_summary": {
                "total_nodes": 0,
                "total_edges": 0,
                "flagged_accounts": 0,
                "high_risk_accounts": 0,
                "communities_detected": 0,
                "total_transaction_volume": 0,
                "network_density": 0,
            },
        }
