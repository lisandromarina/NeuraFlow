# engine/executor.py
from sqlalchemy.orm import Session
from .node_factory import NodeFactory
from models.db_models.workflow_nodes import WorkflowNode
from models.db_models.workflow_connections_db import WorkflowConnection
from concurrent.futures import ThreadPoolExecutor, wait
from . import executors_examples
import datetime
import threading
import copy

def log(msg: str, indent_level=0):
    """Thread-safe logging with timestamps and indentation."""
    indent = "  " * indent_level
    print(f"{datetime.datetime.now().isoformat()} | {indent}{msg}")


class WorkflowExecutor:
    def __init__(self, db: Session, max_workers=8):
        self.db = db
        self.executor_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.thread_local = threading.local()  # Keep track of log indentation per thread

    def execute_workflow(self, workflow_id, context=None):
        """
        Execute the entire workflow starting from the initial nodes.
        initial_context is a dict that is passed to the first node(s).
        """
        context = context or {}

        # Load workflow nodes and connections
        nodes = self.db.query(WorkflowNode).filter_by(workflow_id=workflow_id).all()
        connections = self.db.query(WorkflowConnection).filter_by(workflow_id=workflow_id).all()

        log("=== Workflow Execution Started ===")
        log(f"Workflow ID: {workflow_id}")
        log(f"Loaded nodes: {[node.id for node in nodes]}")
        log(f"Loaded connections: [{', '.join(f'{c.from_step_id}->{c.to_step_id}' for c in connections)}]")

        # Build node lookup map
        node_map = {node.id: node for node in nodes}

        # Build connection map: from_step_id -> list of connections
        connection_map = {}
        for conn in connections:
            connection_map.setdefault(conn.from_step_id, []).append(conn)

        log("Connection map:")
        for node_id, conns in connection_map.items():
            log(f"  Node {node_id} -> {[c.to_step_id for c in conns]}")

        # Identify start nodes (nodes not targeted by any other node)
        target_node_ids = {conn.to_step_id for conn in connections}
        start_nodes = [node for node in nodes if node.id not in target_node_ids]

        if not start_nodes:
            raise ValueError("No starting node found (all nodes are targeted)")

        log(f"Start nodes: {[node.id for node in start_nodes]}")

        # Submit start nodes
        futures = [
            self.executor_pool.submit(
                self.run_node_recursive_safe,
                node,
                copy.deepcopy(context),  # Pass a fresh context per start node
                node_map,
                connection_map,
                0
            )
            for node in start_nodes
        ]

        # Wait for all parallel start nodes to finish
        wait(futures)
        self.executor_pool.shutdown(wait=True)

        log("=== Workflow Execution Completed ===")

    def run_node_recursive_safe(self, node, context, node_map, connection_map, indent_level):
        """Run a node and recursively run its children, passing only parent_result in context."""
        indent = indent_level  # Use local indent for logging

        log(f"--- Running node {node.id} of type {node.node.type} ---", indent)
        log(f"Node config: custom={node.custom_config}", indent)

        # Merge node global config and custom config
        config = {
            **(node.custom_config or {}),
        }

        # Fetch executor for this node type
        executor_cls = NodeFactory.get_executor(node.node.type)

        try:
            # Run executor and get output
            result = executor_cls.run(config, context)
        except Exception as e:
            log(f"ERROR executing node {node.id}: {e}", indent)
            return

        log(f"Node {node.id} finished, result: {result}", indent)

        # Update context with current node output (for logging or parent reference)
        context[f"node_{node.id}_output"] = result

        # Find downstream children
        children = connection_map.get(node.id, [])
        if children:
            log(f"Node {node.id} has downstream nodes: {[c.to_step_id for c in children]}", indent)

        downstream_futures = []

        for conn in children:
            next_node = node_map[conn.to_step_id]

            # Build child context: only initial context + current node result
            child_context = {k: v for k, v in context.items() if not k.startswith("node_")}
            child_context["parent_result"] = result

            log(f"Submitting downstream node {next_node.id} from node {node.id} (condition: {conn.condition})",
                indent + 1)

            fut = self.executor_pool.submit(
                self.run_node_recursive_safe,
                next_node,
                child_context,
                node_map,
                connection_map,
                indent + 1
            )
            downstream_futures.append(fut)

        if downstream_futures:
            wait(downstream_futures)
            log(f"All downstream nodes for node {node.id} completed.", indent)
        else:
            log(f"Node {node.id} has no downstream nodes.", indent)
