import re
import copy
from concurrent.futures import ThreadPoolExecutor, wait
from core.logger import Logger
from .node_factory import NodeFactory
from models.db_models.workflow_nodes import WorkflowNode
from models.db_models.workflow_connections_db import WorkflowConnection

class WorkflowExecutor:
    TRIGGER_TYPES = {"trigger", "scheduler", "webhook"}

    def __init__(self, db, max_workers=8, logger=None):
        self.db = db
        self.executor_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.logger = logger or Logger("[Executor]")

    def execute_workflow(self, workflow_id, context=None):
        context = context or {}

        # Load nodes and connections
        nodes = self.db.query(WorkflowNode).filter_by(workflow_id=workflow_id).all()
        connections = self.db.query(WorkflowConnection).filter_by(workflow_id=workflow_id).all()

        self.logger.log("=== Workflow Execution Started ===")
        self.logger.log(f"Workflow ID: {workflow_id}")
        self.logger.log(f"Loaded nodes: {[node.id for node in nodes]}")
        self.logger.log(f"Loaded connections: [{', '.join(f'{c.from_step_id}->{c.to_step_id}' for c in connections)}]")

        # Build node and connection maps
        node_map = {node.id: node for node in nodes}
        connection_map = {}
        for conn in connections:
            connection_map.setdefault(conn.from_step_id, []).append(conn)

        self.logger.log("Connection map:")
        for node_id, conns in connection_map.items():
            self.logger.log(f"  Node {node_id} -> {[c.to_step_id for c in conns]}")

        # Identify start nodes
        target_ids = {conn.to_step_id for conn in connections}
        start_nodes = [node for node in nodes if node.id not in target_ids]

        if not start_nodes:
            raise ValueError("No starting node found (all nodes are targeted)")

        self.logger.log(f"Start nodes: {[node.id for node in start_nodes]}")

        # Submit start nodes
        futures = [
            self.executor_pool.submit(
                self._run_node,
                node,
                self._safe_copy_context(context),
                node_map,
                connection_map,
                0
            )
            for node in start_nodes
        ]

        wait(futures)
        self.logger.log("=== Workflow Execution Completed ===")

    def _run_node(self, node, context, node_map, connection_map, indent_level):
        self.logger.log(f"--- Running node {node.id} ({node.node.category}) ---", indent_level)
        self.logger.log(f"Node config: {node.custom_config}", indent_level)

        # Skip trigger nodes
        if node.node.type.lower() in self.TRIGGER_TYPES:
            self.logger.log(f"Skipping trigger node {node.id} — passing context to downstream nodes.", indent_level)
            self._submit_downstream(node, context, node_map, connection_map, indent_level)
            return

        # Resolve config and execute node
        config = resolve_config(node.custom_config or {}, context)
        self.logger.log(f"Resolved config: {config}", indent_level)
        self.logger.log("before")
        executor_cls = NodeFactory.get_executor(node.node.category)
        self.logger.log("GOT EXECUTOR", indent_level)
        try:
            result = executor_cls.run(config, context)
            self.logger.log(f"RESULT: {result}", indent_level)
        except Exception as e:
            self.logger.log(f"ERROR executing node {node.id}: {e}", indent_level)
            return

        context[f"node_{node.id}_output"] = result
        self._submit_downstream(node, context, node_map, connection_map, indent_level, parent_result=result)

    def _submit_downstream(self, node, context, node_map, connection_map, indent_level, parent_result=None):
        children = connection_map.get(node.id, [])
        if not children:
            self.logger.log(f"Node {node.id} has no downstream nodes.", indent_level)
            return

        self.logger.log(f"Node {node.id} has downstream nodes: {[c.to_step_id for c in children]}", indent_level)
        futures = []
        for conn in children:
            next_node = node_map[conn.to_step_id]
            child_context = {k: v for k, v in context.items() if not k.startswith("node_")}
            if parent_result is not None:
                child_context["parent_result"] = parent_result

            self.logger.log(f"Submitting downstream node {next_node.id} from node {node.id} (condition: {conn.condition})", indent_level + 1)
            fut = self.executor_pool.submit(
                self._run_node,
                next_node,
                child_context,
                node_map,
                connection_map,
                indent_level + 1
            )
            futures.append(fut)

        if futures:
            wait(futures)
            self.logger.log(f"All downstream nodes for node {node.id} completed.", indent_level)

    def _safe_copy_context(self, context):
        safe_context = {}
        for k, v in context.items():
            if k == "services":
                safe_context[k] = v  # do not deepcopy services
            else:
                try:
                    safe_context[k] = copy.deepcopy(v)
                except Exception:
                    safe_context[k] = v
        return safe_context


def resolve_config(config, context):
    resolved = {}
    for key, value in config.items():
        if isinstance(value, str):
            match = re.fullmatch(r"\{\{\s*(.*?)\s*\}\}", value)
            if match:
                expr = match.group(1)
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
