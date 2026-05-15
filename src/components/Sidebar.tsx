import React from 'react';
import { 
  Info, 
  Database, 
  Cpu, 
  Network, 
  Share2, 
  Settings, 
  HelpCircle, 
  Plus,
  UserCircle
} from 'lucide-react';
import { cn } from '@/src/lib/utils';

const navItems = [
  { icon: Info, label: 'About' },
  { icon: Database, label: 'Dataset' },
  { icon: Cpu, label: 'LLM Pipeline' },
  { icon: Network, label: 'RAG Pipeline' },
  { icon: Share2, label: 'GraphRAG Pipeline', active: true },
];

export function Sidebar() {
  return (
    <nav className="hidden md:flex bg-surface-dim/60 backdrop-blur-xl h-screen w-72 fixed left-0 top-0 border-r border-white/10 shadow-2xl flex-col py-6 px-4 z-50">
      {/* Header */}
      <div className="mb-8 flex flex-col gap-2">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-surface-container-high border border-white/10 overflow-hidden flex items-center justify-center">
            <UserCircle className="text-primary-brand w-8 h-8" />
          </div>
          <div>
            <h1 className="font-display text-xl font-bold tracking-tight text-on-surface">BioBenchmark AI</h1>
            <p className="text-[10px] uppercase font-bold tracking-widest text-on-surface-variant mt-1">V0.4.2-alpha</p>
          </div>
        </div>
        <button className="mt-4 w-full bg-black border border-white/20 text-on-surface py-2 px-4 rounded hover:bg-white/5 hover:text-on-surface transition-all duration-150 active:scale-95 text-[11px] font-bold uppercase tracking-widest flex items-center justify-center gap-2">
          <Plus className="w-4 h-4" />
          New Analysis
        </button>
      </div>

      {/* Main Tabs */}
      <div className="flex-1 flex flex-col gap-2">
        {navItems.map((item) => (
          <a
            key={item.label}
            href="#"
            className={cn(
              "flex items-center gap-3 px-4 py-3 transition-all duration-300 rounded-lg group",
              item.active 
                ? "bg-primary-brand/10 text-primary-brand border-r-2 border-primary-brand" 
                : "text-on-surface-variant hover:bg-white/5 hover:text-on-surface"
            )}
          >
            <item.icon className={cn("w-5 h-5", item.active && "drop-shadow-[0_0_8px_rgba(255,179,173,0.5)]")} />
            <span className="text-[11px] font-bold uppercase tracking-widest">{item.label}</span>
          </a>
        ))}
      </div>

      {/* Footer Tabs */}
      <div className="mt-auto flex flex-col gap-2 pt-4 border-t border-white/5">
        <a className="flex items-center gap-3 px-4 py-3 text-on-surface-variant hover:bg-white/5 hover:text-on-surface transition-colors rounded-lg" href="#">
          <Settings className="w-5 h-5" />
          <span className="text-[11px] font-bold uppercase tracking-widest">Settings</span>
        </a>
        <a className="flex items-center gap-3 px-4 py-3 text-on-surface-variant hover:bg-white/5 hover:text-on-surface transition-colors rounded-lg" href="#">
          <HelpCircle className="w-5 h-5" />
          <span className="text-[11px] font-bold uppercase tracking-widest">Support</span>
        </a>
      </div>
    </nav>
  );
}
