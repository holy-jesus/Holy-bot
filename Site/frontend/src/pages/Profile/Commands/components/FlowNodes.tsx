import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Play, MessageSquare, ShieldAlert, Split } from 'lucide-react';

const NodeWrapper = ({ children, title, colorClass, icon }: any) => (
  <div className={`min-w-[150px] rounded-lg shadow-lg border-2 bg-slate-900 ${colorClass}`}>
    <div className={`px-3 py-2 text-xs font-bold text-white uppercase flex items-center gap-2 border-b border-white/10`}>
      {icon}
      {title}
    </div>
    <div className="p-3">
      {children}
    </div>
  </div>
);

export const TriggerNode = memo(({ data, isConnectable }: any) => {
  return (
    <NodeWrapper 
      title="Trigger" 
      colorClass="border-emerald-500/50 shadow-emerald-500/10"
      icon={<Play size={12} className="text-emerald-400" />}
    >
      <div className="text-xs text-slate-300">{data.label}</div>
      <input 
        className="mt-2 w-full bg-slate-950 text-xs text-white p-1 rounded border border-slate-700 focus:border-emerald-500 outline-none" 
        placeholder="!command" 
        defaultValue={data.value}
        onChange={(evt) => data.onChange && data.onChange(evt.target.value)}
      />
      <Handle type="source" position={Position.Bottom} isConnectable={isConnectable} className="w-3 h-3 bg-emerald-500" />
    </NodeWrapper>
  );
});

export const ActionNode = memo(({ data, isConnectable }: any) => {
  return (
    <NodeWrapper 
      title="Action" 
      colorClass="border-brand-500/50 shadow-brand-500/10"
      icon={<MessageSquare size={12} className="text-brand-400" />}
    >
      <Handle type="target" position={Position.Top} isConnectable={isConnectable} className="w-3 h-3 bg-brand-500" />
      <div className="text-xs text-slate-300 mb-2">{data.label}</div>
      <textarea 
        className="w-full bg-slate-950 text-xs text-white p-1 rounded border border-slate-700 focus:border-brand-500 outline-none resize-none" 
        placeholder="Response text..." 
        rows={2}
        defaultValue={data.value}
        onChange={(evt) => data.onChange && data.onChange(evt.target.value)}
      />
      <Handle type="source" position={Position.Bottom} isConnectable={isConnectable} className="w-3 h-3 bg-brand-500" />
    </NodeWrapper>
  );
});

export const ConditionNode = memo(({ data, isConnectable }: any) => {
  return (
    <NodeWrapper 
      title="Condition" 
      colorClass="border-amber-500/50 shadow-amber-500/10"
      icon={<Split size={12} className="text-amber-400" />}
    >
      <Handle type="target" position={Position.Top} isConnectable={isConnectable} className="w-3 h-3 bg-amber-500" />
      <div className="text-xs text-slate-300 mb-2">Is Subscriber?</div>
      <div className="flex justify-between px-2 text-[10px] text-slate-400 font-bold uppercase">
        <span>True</span>
        <span>False</span>
      </div>
      <Handle type="source" position={Position.Bottom} id="true" style={{ left: '25%' }} isConnectable={isConnectable} className="w-3 h-3 bg-emerald-500" />
      <Handle type="source" position={Position.Bottom} id="false" style={{ left: '75%' }} isConnectable={isConnectable} className="w-3 h-3 bg-red-500" />
    </NodeWrapper>
  );
});