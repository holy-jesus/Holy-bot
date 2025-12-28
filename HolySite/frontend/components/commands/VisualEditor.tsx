import React, { useCallback, useState, useEffect } from 'react';
import { 
  ReactFlow, 
  Controls, 
  Background, 
  addEdge, 
  Connection, 
  Edge, 
  Node, 
  useNodesState, 
  useEdgesState,
  BackgroundVariant
} from '@xyflow/react';
import { TriggerNode, ActionNode, ConditionNode } from './FlowNodes';
import { useLanguage } from '../../contexts/LanguageContext';

const nodeTypes = {
  triggerNode: TriggerNode,
  actionNode: ActionNode,
  conditionNode: ConditionNode,
};

interface VisualEditorProps {
  initialNodes?: Node[];
  initialEdges?: Edge[];
  onChange: (nodes: Node[], edges: Edge[]) => void;
}

// Wrapped in React.memo to prevent re-renders from parent unless props strictly change
export const VisualEditor: React.FC<VisualEditorProps> = React.memo(({ initialNodes, initialEdges, onChange }) => {
  const { t } = useLanguage();
  
  const defaultNodes: Node[] = [
    { 
      id: '1', 
      type: 'triggerNode', 
      position: { x: 250, y: 0 }, 
      data: { label: t('commands.nodeTrigger'), value: '!hello' } 
    },
  ];

  // Initialize state only once using initial props or defaults
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes && initialNodes.length > 0 ? initialNodes : defaultNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges || []);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const type = event.dataTransfer.getData('application/reactflow');
      if (typeof type === 'undefined' || !type) return;

      const position = {
        x: event.clientX - event.currentTarget.getBoundingClientRect().left - 100,
        y: event.clientY - event.currentTarget.getBoundingClientRect().top,
      };

      const newNode: Node = {
        id: Date.now().toString(),
        type,
        position,
        data: { 
            label: type === 'triggerNode' ? t('commands.nodeTrigger') : 
                   type === 'actionNode' ? t('commands.nodeAction') : 
                   t('commands.nodeCondition'),
            value: '' 
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [setNodes, t],
  );

  // DEBOUNCE LOGIC: Only call onChange (updating parent state) after 500ms of no changes.
  // This prevents the parent from re-rendering on every mouse move (node drag),
  // which causes the "laggy" 10fps feel.
  useEffect(() => {
    const handler = setTimeout(() => {
      onChange(nodes, edges);
    }, 500);

    return () => {
      clearTimeout(handler);
    };
  }, [nodes, edges, onChange]);

  return (
    <div className="flex h-[600px] border border-slate-800 rounded-lg overflow-hidden bg-slate-950">
      {/* Sidebar / Toolbox */}
      <div className="w-48 bg-slate-900 border-r border-slate-800 p-4 flex flex-col gap-3">
        <h3 className="text-sm font-semibold text-white mb-2">{t('commands.nodes')}</h3>
        
        <div 
          className="bg-slate-800 p-3 rounded cursor-move border border-emerald-500/30 text-emerald-400 text-xs font-medium hover:bg-slate-700 transition"
          onDragStart={(event) => event.dataTransfer.setData('application/reactflow', 'triggerNode')}
          draggable
        >
          {t('commands.nodeTrigger')}
        </div>
        
        <div 
          className="bg-slate-800 p-3 rounded cursor-move border border-brand-500/30 text-brand-400 text-xs font-medium hover:bg-slate-700 transition"
          onDragStart={(event) => event.dataTransfer.setData('application/reactflow', 'actionNode')}
          draggable
        >
          {t('commands.nodeAction')}
        </div>

        <div 
          className="bg-slate-800 p-3 rounded cursor-move border border-amber-500/30 text-amber-400 text-xs font-medium hover:bg-slate-700 transition"
          onDragStart={(event) => event.dataTransfer.setData('application/reactflow', 'conditionNode')}
          draggable
        >
          {t('commands.nodeCondition')}
        </div>

        <div className="mt-auto text-[10px] text-slate-500">
            Drag nodes to canvas
        </div>
      </div>

      {/* Canvas */}
      <div className="flex-1 h-full" onDrop={onDrop} onDragOver={onDragOver}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
          className="bg-slate-950"
        >
          <Background color="#334155" gap={20} variant={BackgroundVariant.Dots} />
          <Controls className="bg-slate-800 border-slate-700 fill-slate-300 text-slate-300" />
        </ReactFlow>
      </div>
    </div>
  );
});