import React from 'react';
import { Search, Bell, UserCircle } from 'lucide-react';

export function TopBar() {
  return (
    <header className="bg-surface-dim/80 backdrop-blur-md fixed top-0 right-0 w-full md:w-[calc(100%-288px)] h-16 z-40 border-b border-white/5 shadow-sm flex justify-between items-center px-4 md:px-10">
      <div className="flex items-center gap-3 md:gap-4">
        <span className="font-display text-xl md:text-2xl font-black tracking-tighter text-on-surface truncate">
          BioBenchmark Console
        </span>
        <div className="hidden md:flex px-3 py-1 bg-red-500/10 border border-red-500/20 rounded-full items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse-slow"></div>
          <span className="text-[10px] font-bold uppercase tracking-widest text-red-500">LIVE BENCHMARK</span>
        </div>
        <div className="flex md:hidden w-2 h-2 rounded-full bg-red-500 animate-pulse-slow"></div>
      </div>

      <div className="flex items-center gap-4 md:gap-6">
        <div className="relative hidden lg:block w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant w-4 h-4" />
          <input
            type="text"
            className="w-full bg-surface-container-high border border-white/10 rounded-full py-1.5 pl-9 pr-4 text-sm text-on-surface focus:outline-none focus:border-primary-brand/50 transition-colors"
            placeholder="Search experiments..."
          />
        </div>
        <div className="flex gap-4">
          <button className="text-on-surface-variant hover:text-primary-brand transition-colors">
            <Bell className="w-5 h-5" />
          </button>
          <button className="hidden md:block text-on-surface-variant hover:text-primary-brand transition-colors">
            <UserCircle className="w-6 h-6" />
          </button>
        </div>
      </div>
    </header>
  );
}
