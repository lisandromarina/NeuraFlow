from sqlalchemy.orm import Session
from .node_factory import NodeFactory
from models.db_models.workflow_nodes import WorkflowNode
from models.db_models.workflow_connections_db import WorkflowConnection
from concurrent.futures import ThreadPoolExecutor, wait
from . import executors_examples
import datetime
import threading

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
        context = context or {}

        nodes = self.db.query(WorkflowNode).filter_by(workflow_id=workflow_id).all()
        connections = self.db.query(WorkflowConnection).filter_by(workflow_id=workflow_id).all()

        log("=== Workflow Execution Started ===")
        log(f"Workflow ID: {workflow_id}")
        log(f"Loaded nodes: {[node.id for node in nodes]}")
        log(f"Loaded connections: [{', '.join(f'{c.from_step_id}->{c.to_step_id}' for c in connections)}]")

        node_map = {node.id: node for node in nodes}
        connection_map = {}
        for conn in connections:
            connection_map.setdefault(conn.from_step_id, []).append(conn)

        log("Connection map:")
        for node_id, conns in connection_map.items():
            log(f"Node {node_id} -> {[c.to_step_id for c in conns]}")

        # Identify start nodes
        target_node_ids = {conn.to_step_id for conn in connections}
        start_nodes = [node for node in nodes if node.id not in target_node_ids]

        if not start_nodes:
            raise ValueError("No starting node found (all nodes are targeted)")

        log(f"Start nodes: {[node.id for node in start_nodes]}")

        # Submit start nodes
        futures = [self.executor_pool.submit(
            self.run_node_recursive_safe, node, context, node_map, connection_map, 0
        ) for node in start_nodes]

        wait(futures)
        self.executor_pool.shutdown(wait=True)
        log("=== Workflow Execution Completed ===")

    def run_node_recursive_safe(self, node, context, node_map, connection_map, indent_level):
        # Track indentation per thread
        if not hasattr(self.thread_local, "indent"):
            self.thread_local.indent = indent_level

        log(f"--- Running node {node.id} of type {node.node.type} ---", self.thread_local.indent)
        log(f"Node config: global={node.node.global_config}, custom={node.custom_config}", self.thread_local.indent)

        executor_cls = NodeFactory.get_executor(node.node.type)
        try:
            result = executor_cls.run(
                {**(node.node.global_config or {}), **(node.custom_config or {})}, 
                context
            )
        except Exception as e:
            log(f"ERROR executing node {node.id}: {e}", self.thread_local.indent)
            return

        log(f"Node {node.id} finished, result: {result}", self.thread_local.indent)

        downstream_futures = []
        children = connection_map.get(node.id, [])

        if children:
            log(f"Node {node.id} has downstream nodes: {[c.to_step_id for c in children]}", self.thread_local.indent)

        for conn in children:
            next_node = node_map[conn.to_step_id]
            log(f"Submitting downstream node {next_node.id} from node {node.id} (condition: {conn.condition})", self.thread_local.indent + 1)
            # Submit child with increased indentation
            fut = self.executor_pool.submit(
                self.run_node_recursive_safe, next_node, context, node_map, connection_map, self.thread_local.indent + 1
            )
            downstream_futures.append(fut)

        if downstream_futures:
            wait(downstream_futures)
            log(f"All downstream nodes for node {node.id} completed.", self.thread_local.indent)
        else:
            log(f"Node {node.id} has no downstream nodes.", self.thread_local.indent)
