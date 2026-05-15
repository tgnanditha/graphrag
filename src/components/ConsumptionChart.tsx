import React from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from 'recharts';

const data = [
  { name: 'LLM ONLY', tokens: 4096, color: '#ffb4ab' },
  { name: 'BASIC RAG', tokens: 12500, color: '#ffb690' },
  { name: 'GRAPHRAG', tokens: 2104, color: '#4ae176' },
];

export function ConsumptionChart() {
  return (
    <div className="glass-card rounded-xl p-6 h-full flex flex-col">
      <h4 className="text-[11px] font-bold uppercase tracking-widest text-on-surface-variant mb-6 border-b border-white/5 pb-2">
        Resource Consumption Comparison
      </h4>
      <div className="flex-1 min-h-[200px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
            <XAxis 
              dataKey="name" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: 'var(--color-on-surface-variant)', fontSize: 10, fontWeight: 700 }}
              dy={10}
            />
            <YAxis hide />
            <Tooltip 
              cursor={{ fill: 'rgba(255,255,255,0.05)' }}
              contentStyle={{ 
                backgroundColor: 'rgba(20,20,20,0.9)', 
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '8px',
                fontSize: '12px'
              }}
            />
            <Bar dataKey="tokens" radius={[4, 4, 0, 0]} barSize={40}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} fillOpacity={0.8} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="flex justify-center gap-6 mt-4">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-white/20 rounded" />
          <span className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">Token Count</span>
        </div>
      </div>
    </div>
  );
}
