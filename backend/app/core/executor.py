from sqlalchemy.orm import Session
from .node_factory import NodeFactory
from models.db_models.workflow_nodes import WorkflowNode
from models.db_models.workflow_connections_db import WorkflowConnection
from concurrent.futures import ThreadPoolExecutor
from . import executors_examples
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

class WorkflowExecutor:
    def __init__(self, db: Session, max_workers=8):
        self.db = db
        self.executor_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.futures = set()  # Track all submitted futures

    def execute_workflow(self, workflow_id, context=None):
        context = context or {}

        # Load nodes and connections
        nodes = self.db.query(WorkflowNode).filter_by(workflow_id=workflow_id).all()
        connections = self.db.query(WorkflowConnection).filter_by(workflow_id=workflow_id).all()

        node_map = {node.id: node for node in nodes}
        connection_map = {}
        for conn in connections:
            connection_map.setdefault(conn.from_step_id, []).append(conn)

        target_node_ids = {conn.to_step_id for conn in connections}
        start_nodes = [node for node in nodes if node.id not in target_node_ids]

        if not start_nodes:
            raise ValueError("No starting node found (all nodes are targeted)")

        # Submit starting nodes
        for node in start_nodes:
            fut = self.executor_pool.submit(self.run_node_recursive, node, context, node_map, connection_map)
            self.futures.add(fut)

        # Wait for all submitted tasks to finish
        while self.futures:
            done, not_done = wait(self.futures, return_when=ALL_COMPLETED)
            self.futures = not_done

        self.executor_pool.shutdown(wait=True)

    def run_node_recursive(self, node, context, node_map, connection_map):
        config = {**(node.node.global_config or {}), **(node.custom_config or {})}
        executor = NodeFactory.get_executor(node.node.type)

        # Run the node
        result = executor.run(config, context)
        print(f"Node {node.id} finished, result: {result}")

        # Submit downstream nodes
        for conn in connection_map.get(node.id, []):
            if conn.condition is None or conn.condition == result.get("status"):
                next_node = node_map[conn.to_step_id]
                fut = self.executor_pool.submit(self.run_node_recursive, next_node, context, node_map, connection_map)
                self.futures.add(fut)