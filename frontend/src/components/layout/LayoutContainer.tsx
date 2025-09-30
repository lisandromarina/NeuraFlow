import React, { useEffect, useState } from 'react';
import LayoutComponent from './LayoutComponent';
import { useApi } from '../../api/useApi';

interface ApiNode {
  id: number;
  name: string;
  type: string;
}

interface SidebarNode {
  id: number;
  title: string;
  type: string;
}

const LayoutContainer: React.FC = () => {
  const [nodes, setNodes] = useState<SidebarNode[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [isRightSidebarOpen, setIsRightSidebarOpen] = useState(false);

  const { callApi } = useApi();

  const fetchNodes = async () => {
    try {
      const data: ApiNode[] = await callApi('/nodes', 'GET');
      if (!data) throw new Error('No data returned from API');

      // Map API nodes to SidebarNode expected by AppSidebar
      const mappedNodes: SidebarNode[] = data.map((node) => ({
        id: node.id,
        title: node.name,  // rename name -> title
        type: node.type,
      }));

      setNodes(mappedNodes);
    } catch (err: any) {
      console.error('Failed to fetch nodes:', err);
      setError(err.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNodes();
  }, []);

  if (loading) return <div>Loading nodes...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
  <LayoutComponent 
    selectedNode={selectedNode}
    setSelectedNode={setSelectedNode}
    isRightSidebarOpen={isRightSidebarOpen}
    setIsRightSidebarOpen={setIsRightSidebarOpen}
    nodes={nodes} />
  );
};

export default LayoutContainer;
