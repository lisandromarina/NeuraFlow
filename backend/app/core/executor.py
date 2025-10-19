import re
import copy
import threading
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
        # Track node completion status and results for multiple parent handling
        self.node_results = {}
        self.node_completion_lock = threading.Lock()

    def execute_workflow(self, workflow_id, context=None):
        context = context or {}
        
        # Reset node tracking for new workflow execution
        with self.node_completion_lock:
            self.node_results = {}

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
        parent_map = {}  # Track which nodes are parents of each node
        
        for conn in connections:
            connection_map.setdefault(conn.from_step_id, []).append(conn)
            parent_map.setdefault(conn.to_step_id, []).append(conn.from_step_id)

        self.logger.log("Connection map:")
        for node_id, conns in connection_map.items():
            self.logger.log(f"  Node {node_id} -> {[c.to_step_id for c in conns]}")
        
        self.logger.log("Parent map:")
        for node_id, parents in parent_map.items():
            self.logger.log(f"  Node {node_id} <- {parents}")

        # Identify start nodes (nodes with no parents)
        start_nodes = [node for node in nodes if node.id not in parent_map]

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
                parent_map,
                0
            )
            for node in start_nodes
        ]

        wait(futures)
        self.logger.log("=== Workflow Execution Completed ===")

    def _run_node(self, node, context, node_map, connection_map, parent_map, indent_level):
        self.logger.log(f"--- Running node {node.id} ({node.node.category}) ---", indent_level)
        self.logger.log(f"Node config: {node.custom_config}", indent_level)

        # Check if this node has multiple parents and wait for all to complete
        parents = parent_map.get(node.id, [])
        if len(parents) > 1:
            self.logger.log(f"Node {node.id} has {len(parents)} parents: {parents}. Waiting for all to complete.", indent_level)
            self._wait_for_parents(node.id, parents, indent_level)
        
        # Build enhanced context with parent results
        enhanced_context = self._build_enhanced_context(node.id, parents, context, indent_level)

        # Skip trigger nodes but mark them as completed
        if node.node.type.lower() in self.TRIGGER_TYPES:
            self.logger.log(f"Skipping trigger node {node.id} — passing context to downstream nodes.", indent_level)
            
            # Mark trigger node as completed with a special result FIRST
            with self.node_completion_lock:
                self.node_results[node.id] = {"trigger_completed": True, "context": enhanced_context}
                self.logger.log(f"Trigger node {node.id} marked as completed", indent_level)
            
            # Now submit downstream nodes (they will see the parent as completed)
            self._submit_downstream(node, enhanced_context, node_map, connection_map, parent_map, indent_level, parent_result={"trigger_completed": True})
            return

        # Resolve config and execute node
        self.logger.log(f"Original config: {node.custom_config}", indent_level)
        self.logger.log(f"Enhanced context keys: {list(enhanced_context.keys())}", indent_level)
        config = resolve_config(node.custom_config or {}, enhanced_context)
        self.logger.log(f"Resolved config: {config}", indent_level)
        self.logger.log("before")
        executor_cls = NodeFactory.get_executor(node.node.category)
        self.logger.log("GOT EXECUTOR", indent_level)
        try:
            result = executor_cls.run(config, enhanced_context)
            self.logger.log(f"RESULT: {result}", indent_level)
        except Exception as e:
            self.logger.log(f"ERROR executing node {node.id}: {e}", indent_level)
            return

        # Store result and mark node as completed
        with self.node_completion_lock:
            self.node_results[node.id] = result
            self.logger.log(f"Node {node.id} completed and result stored", indent_level)

        enhanced_context[f"node_{node.id}_output"] = result
        self._submit_downstream(node, enhanced_context, node_map, connection_map, parent_map, indent_level, parent_result=result)

    def _submit_downstream(self, node, context, node_map, connection_map, parent_map, indent_level, parent_result=None):
        children = connection_map.get(node.id, [])
        if not children:
            self.logger.log(f"Node {node.id} has no downstream nodes.", indent_level)
            return

        self.logger.log(f"Node {node.id} has downstream nodes: {[c.to_step_id for c in children]}", indent_level)
        
        # For each child, check if it's ready and start it if so
        for conn in children:
            next_node = node_map[conn.to_step_id]
            
            # Check if the child node is ready to run (all parents completed)
            if self._is_node_ready_to_run(next_node.id, parent_map, indent_level + 1):
                # Build enhanced context for the child node with all parent results
                child_parents = parent_map.get(next_node.id, [])
                child_context = self._build_enhanced_context(next_node.id, child_parents, context, indent_level + 1)

                self.logger.log(f"Starting downstream node {next_node.id} from node {node.id} (condition: {conn.condition})", indent_level + 1)
                
                # Start the child node in a new thread
                self.executor_pool.submit(
                    self._run_node,
                    next_node,
                    child_context,
                    node_map,
                    connection_map,
                    parent_map,
                    indent_level + 1
                )
            else:
                self.logger.log(f"Node {next_node.id} not ready yet - waiting for other parents", indent_level + 1)

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

    def _wait_for_parents(self, node_id, parents, indent_level):
        """Wait for all parent nodes to complete"""
        while True:
            with self.node_completion_lock:
                completed_parents = [p for p in parents if p in self.node_results]
                if len(completed_parents) == len(parents):
                    self.logger.log(f"All parents {parents} completed for node {node_id}", indent_level)
                    break
            
            self.logger.log(f"Waiting for parents {parents} to complete for node {node_id}. Completed: {completed_parents}", indent_level)
            import time
            time.sleep(0.1)  # Small delay to avoid busy waiting

    def _build_enhanced_context(self, node_id, parents, base_context, indent_level):
        """Build enhanced context with parent results"""
        enhanced_context = self._safe_copy_context(base_context)
        
        # Add individual parent results
        with self.node_completion_lock:
            for parent_id in parents:
                if parent_id in self.node_results:
                    enhanced_context[f"parent_{parent_id}_result"] = self.node_results[parent_id]
                    self.logger.log(f"Added parent_{parent_id}_result to context for node {node_id}", indent_level)
        
        # Add generic parent_result for single parent case (for backward compatibility)
        if len(parents) == 1:
            parent_id = parents[0]
            with self.node_completion_lock:
                if parent_id in self.node_results:
                    enhanced_context["parent_result"] = self.node_results[parent_id]
                    self.logger.log(f"Added parent_result to context for node {node_id} (single parent)", indent_level)
        
        # Add aggregated parent results for convenience
        if len(parents) > 1:
            parent_results = []
            with self.node_completion_lock:
                for parent_id in parents:
                    if parent_id in self.node_results:
                        parent_results.append({
                            "parent_id": parent_id,
                            "result": self.node_results[parent_id]
                        })
            enhanced_context["all_parent_results"] = parent_results
            self.logger.log(f"Added all_parent_results with {len(parent_results)} entries for node {node_id}", indent_level)
        
        return enhanced_context

    def _is_node_ready_to_run(self, node_id, parent_map, indent_level):
        """Check if a node is ready to run (all parents completed)"""
        parents = parent_map.get(node_id, [])
        if not parents:
            self.logger.log(f"Node {node_id} has no parents - ready to run", indent_level)
            return True  # No parents, ready to run
        
        with self.node_completion_lock:
            completed_parents = [p for p in parents if p in self.node_results]
            is_ready = len(completed_parents) == len(parents)
            
        self.logger.log(f"Node {node_id} readiness check: {len(completed_parents)}/{len(parents)} parents completed. Ready: {is_ready}", indent_level)
        if completed_parents:
            self.logger.log(f"Completed parents for node {node_id}: {completed_parents}", indent_level)
        else:
            self.logger.log(f"No completed parents yet for node {node_id}. All parents: {parents}", indent_level)
            with self.node_completion_lock:
                self.logger.log(f"Current node_results keys: {list(self.node_results.keys())}", indent_level)
        
        return is_ready

def resolve_config(config, context):
    """Recursively resolve template variables in config"""
    if isinstance(config, dict):
        resolved = {}
        for key, value in config.items():
            resolved[key] = resolve_config(value, context)
        return resolved
    elif isinstance(config, list):
        return [resolve_config(item, context) for item in config]
    elif isinstance(config, str):
        match = re.fullmatch(r"\{\{\s*(.*?)\s*\}\}", config)
        if match:
            expr = match.group(1)
            parts = expr.split(".")
            current = context
            try:
                for part in parts:
                    current = current[part] if isinstance(current, dict) else getattr(current, part)
                print(f"[resolve_config] Resolved '{config}' to: {current}")
                return current
            except Exception as e:
                print(f"[resolve_config] Failed to resolve '{config}': {e}")
                return None
        else:
            return config
    else:
        return config
