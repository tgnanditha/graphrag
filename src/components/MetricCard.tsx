import React from 'react';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/src/lib/utils';
import { motion } from 'motion/react';

interface MetricCardProps {
  title: string;
  icon: LucideIcon;
  content: string;
  tokens: string;
  latency: string;
  cost: string;
  colorClass: string;
  isBest?: boolean;
}

export function MetricCard({ 
  title, 
  icon: Icon, 
  content, 
  tokens, 
  latency, 
  cost, 
  colorClass,
  isBest 
}: MetricCardProps) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        "glass-card rounded-xl p-6 flex flex-col gap-4 relative overflow-hidden",
        isBest ? "border-tertiary-brand/30 shadow-[0_0_20px_rgba(74,225,118,0.1)]" : "border-t-2"
      )}
      style={!isBest ? { borderTopColor: colorClass === 'text-error-brand' ? 'var(--color-error-brand)' : 'var(--color-secondary-brand)' } : {}}
    >
      {isBest && (
        <div className="absolute top-0 right-0 bg-tertiary-brand text-on-tertiary-brand text-[9px] px-2 py-1 rounded-bl-lg font-bold uppercase tracking-widest">
          Best System
        </div>
      )}
      
      <div className="flex justify-between items-center">
        <h3 className={cn("text-base font-bold", colorClass)}>{title}</h3>
        <Icon className={cn("w-5 h-5 opacity-50", colorClass)} />
      </div>

      <div className="bg-surface-container-lowest border border-white/5 rounded-lg p-4 font-mono text-[13px] text-on-surface-variant terminal-scanline min-h-[140px] relative">
        {content}
        <div className="absolute bottom-2 right-2">
          <div className={cn("w-1.5 h-1.5 rounded-full animate-pulse-slow", 
            isBest ? "bg-tertiary-brand" : colorClass === 'text-error-brand' ? "bg-error-brand" : "bg-secondary-brand"
          )} />
        </div>
      </div>

      <div className={cn("grid grid-cols-3 gap-2 mt-auto pt-4 border-t", isBest ? "border-tertiary-brand/20" : "border-white/5")}>
        <div className="flex flex-col">
          <span className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/50">Tokens</span>
          <span className={cn("text-sm font-mono", isBest && "text-tertiary-brand font-bold")}>{tokens}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/50">Latency</span>
          <span className={cn("text-sm font-mono", isBest && "text-tertiary-brand font-bold")}>{latency}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/50">Cost</span>
          <span className={cn("text-sm font-mono font-bold", isBest ? "text-tertiary-brand" : colorClass)}>
            {cost}
          </span>
        </div>
      </div>
    </motion.div>
  );
}
