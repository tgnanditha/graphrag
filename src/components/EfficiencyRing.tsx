import React from 'react';
import { Target } from 'lucide-react';

export function EfficiencyRing() {
  const percentage = 42;
  const strokeWidth = 8;
  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <div className="glass-card rounded-xl p-6 flex flex-col justify-center items-center text-center gap-6 relative overflow-hidden h-full">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(74,225,118,0.1)_0%,transparent_70%)] pointer-events-none" />
      
      <div className="relative w-32 h-32 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          <circle 
            cx="50" 
            cy="50" 
            r={radius} 
            fill="none" 
            stroke="rgba(255,255,255,0.05)" 
            strokeWidth={strokeWidth} 
          />
          <circle 
            cx="50" 
            cy="50" 
            r={radius} 
            fill="none" 
            stroke="#4ae176" 
            strokeWidth={strokeWidth} 
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
            style={{ filter: 'drop-shadow(0 0 4px rgba(74,225,118,0.5))' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-display text-3xl font-bold text-tertiary-brand -mt-1">-{percentage}%</span>
        </div>
      </div>

      <div>
        <div className="flex items-center justify-center gap-2 mb-2">
          <Target className="w-5 h-5 text-tertiary-brand" />
          <h4 className="font-display text-lg font-bold text-on-surface">GraphRAG Efficiency</h4>
        </div>
        <p className="text-sm text-on-surface-variant leading-relaxed">
          GraphRAG used 42% fewer tokens compared to baseline RAG while maintaining 98% factual accuracy.
        </p>
      </div>
    </div>
  );
}
