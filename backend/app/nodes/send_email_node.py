from .node_executor import NodeExecutor

class SendEmailNodeExecutor(NodeExecutor):
    def execute(self):
        config = self.node['config']
        print(f"Sending email to {config['to']} with subject '{config['subject']}'")
        # Call actual email service here
        return {"status": "email_sent"}
