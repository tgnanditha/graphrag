import React from 'react';
import { cn } from '@/src/lib/utils';

const executions = [
  { id: 'Q-7829', pipeline: 'GraphRAG', tokens: '2,104', latency: '4.1', status: 'Complete', color: 'text-tertiary-brand' },
  { id: 'Q-7829', pipeline: 'Basic RAG', tokens: '12,500', latency: '8.4', status: 'Complete', color: 'text-secondary-brand' },
  { id: 'Q-7829', pipeline: 'LLM Only', tokens: '4,096', latency: '3.2', status: 'Complete', color: 'text-error-brand' },
];

export function ExecutionsTable() {
  return (
    <div className="glass-card rounded-xl overflow-hidden mt-6">
      <div className="p-4 border-b border-white/5 bg-white/5">
        <h4 className="text-[11px] font-bold uppercase tracking-widest text-on-surface-variant">
          Recent Executions
        </h4>
      </div>
      <div className="w-full overflow-x-auto">
        <table className="w-full text-left border-collapse min-w-[600px]">
          <thead>
            <tr className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/70 border-b border-white/5 bg-surface-container-lowest/50">
              <th className="p-4">Query ID</th>
              <th className="p-4">Pipeline</th>
              <th className="p-4">Tokens</th>
              <th className="p-4">Latency (s)</th>
              <th className="p-4">Status</th>
            </tr>
          </thead>
          <tbody className="font-mono text-[13px]">
            {executions.map((exec, idx) => (
              <tr key={idx} className="border-b border-white/5 hover:bg-white/5 transition-colors group">
                <td className="p-4 text-on-surface-variant">{exec.id}</td>
                <td className={cn("p-4 font-bold", exec.color)}>{exec.pipeline}</td>
                <td className="p-4 text-on-surface">{exec.tokens}</td>
                <td className="p-4 text-on-surface">{exec.latency}</td>
                <td className="p-4">
                  <span className="px-2 py-1 rounded bg-tertiary-brand/10 text-tertiary-brand text-[9px] font-bold uppercase tracking-widest">
                    {exec.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
