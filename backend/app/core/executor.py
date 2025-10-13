import re
import copy
import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, wait
from sqlalchemy.orm import Session
from .node_factory import NodeFactory
from models.db_models.workflow_nodes import WorkflowNode
from models.db_models.workflow_connections_db import WorkflowConnection
import nodes

# Thread-safe logger
def log(msg: str, indent_level=0):
    indent = "  " * indent_level
    thread_name = threading.current_thread().name
    print(f"{datetime.datetime.now().isoformat()} [{thread_name}] {indent}{msg}")


class WorkflowExecutor:
    def __init__(self, db: Session, max_workers=8):
        self.db = db
        self.executor_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.thread_local = threading.local()  # Optional: per-thread indentation

    def execute_workflow(self, workflow_id, context=None):
        context = context or {}

        # Load nodes and connections
        nodes = self.db.query(WorkflowNode).filter_by(workflow_id=workflow_id).all()
        connections = self.db.query(WorkflowConnection).filter_by(workflow_id=workflow_id).all()

        log("=== Workflow Execution Started ===")
        log(f"Workflow ID: {workflow_id}")
        log(f"Loaded nodes: {[node.id for node in nodes]}")
        log(f"Loaded connections: [{', '.join(f'{c.from_step_id}->{c.to_step_id}' for c in connections)}]")

        # Build node map
        node_map = {node.id: node for node in nodes}

        # Build connection map
        connection_map = {}
        for conn in connections:
            connection_map.setdefault(conn.from_step_id, []).append(conn)

        log("Connection map:")
        for node_id, conns in connection_map.items():
            log(f"  Node {node_id} -> {[c.to_step_id for c in conns]}")

        # Identify start nodes
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
                self._safe_copy_context(context),
                node_map,
                connection_map,
                0
            )
            for node in start_nodes
        ]

        # Wait for all start nodes to finish
        wait(futures)
        log("=== Workflow Execution Completed ===")

    def run_node_recursive_safe(self, node, context, node_map, connection_map, indent_level):
        indent = indent_level
        log(f"--- Running node {node.id} of category {node.node.category} ---", indent)
        log(f"Node config: custom={node.custom_config}", indent)

        # Detect trigger-type node
        TRIGGER_TYPES = {"trigger", "scheduler", "webhook"}
        if node.node.type.lower() in TRIGGER_TYPES:
            log(f"Skipping trigger node {node.id} execution — passing context to downstream nodes.", indent)
            
            # Schedule downstream nodes immediately
            children = connection_map.get(node.id, [])
            downstream_futures = []
            for conn in children:
                next_node = node_map[conn.to_step_id]

                # Build child context without node outputs
                child_context = {k: v for k, v in context.items() if not k.startswith("node_")}
                log(f"Submitting downstream node {next_node.id} from trigger node {node.id}", indent + 1)
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
                log(f"All downstream nodes for trigger node {node.id} completed.", indent)
            return  # Do not execute the trigger node itself

        # Resolve config for normal action nodes
        raw_config = node.custom_config or {}
        config = resolve_config(raw_config, context)
        log(f"Resolved config for node {node.id}: {config}", indent)

        # Fetch executor class
        executor_cls = NodeFactory.get_executor(node.node.category)
        log(f"GOT EXECUTOR")
        try:
            # Execute the node
            result = executor_cls.run(config, context)
            log(f"RESULT {result}")
        except Exception as e:
            log(f"ERROR executing node {node.id}: {e}", indent)
            return

        # Save node output
        context[f"node_{node.id}_output"] = result
        log(f"Node {node.id} finished, result: {result}", indent)

        # Handle downstream nodes
        children = connection_map.get(node.id, [])
        if children:
            log(f"Node {node.id} has downstream nodes: {[c.to_step_id for c in children]}", indent)
        
        downstream_futures = []
        for conn in children:
            next_node = node_map[conn.to_step_id]

            # Build child context (exclude node outputs)
            child_context = {k: v for k, v in context.items() if not k.startswith("node_")}
            child_context["parent_result"] = result

            log(f"Submitting downstream node {next_node.id} from node {node.id} (condition: {conn.condition})", indent + 1)
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


    def _safe_copy_context(self, context):
        """
        Make a safe copy of context without deep-copying unpicklable objects like DB sessions or service instances.
        """
        safe_context = {}

        for k, v in context.items():
            if k == "services":
                # keep the reference, do NOT deepcopy
                safe_context[k] = v
            else:
                try:
                    safe_context[k] = copy.deepcopy(v)
                except Exception:
                    # fallback if something else is not deepcopyable
                    safe_context[k] = v

        return safe_context

def resolve_config(config, context):
    """
    Replace placeholders in config like {{ parent_result.value }}
    """
    resolved = {}

    for key, value in config.items():
        if isinstance(value, str):
            match = re.fullmatch(r"\{\{\s*(.*?)\s*\}\}", value)
            if match:
                expr = match.group(1)  # e.g. "parent_result.value"
                parts = expr.split(".")
                current = context
                try:
                    for part in parts:
                        current = current[part] if isinstance(current, dict) else getattr(current, part)
                    resolved[key] = current
                except Exception:
                    resolved[key] = None
            else:
                resolved[key] = value
        else:
            resolved[key] = value

    return resolved