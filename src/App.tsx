import React from 'react';
import { Sidebar } from './components/Sidebar';
import { TopBar } from './components/TopBar';
import { MetricCard } from './components/MetricCard';
import { ConsumptionChart } from './components/ConsumptionChart';
import { EfficiencyRing } from './components/EfficiencyRing';
import { ExecutionsTable } from './components/ExecutionsTable';
import { 
  Cpu, 
  Network, 
  Share2, 
  Search, 
  Mic, 
  Info,
  Database,
  Menu,
  Plus
} from 'lucide-react';
import { motion } from 'motion/react';

const suggestedQueries = [
  "Does aspirin reduce...",
  "Side effects of metformin...",
  "Pathway for EGFR..."
];

export default function App() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      
      <div className="md:ml-72 flex-1 flex flex-col min-h-screen relative pb-20 md:pb-0">
        <TopBar />
        
        <main className="flex-1 pt-20 md:pt-24 pb-8 md:pb-32 px-4 md:px-10 flex flex-col gap-8 md:gap-10 max-w-7xl mx-auto w-full">
          {/* Hero Section */}
          <section className="flex flex-col items-center text-center gap-4 md:gap-6 mt-4 md:mt-8">
            <div className="space-y-2">
              <motion.h2 
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="font-display text-3xl md:text-5xl font-bold text-on-surface drop-shadow-[0_0_15px_rgba(255,179,173,0.3)]"
              >
                🧬 GraphRAG vs RAG vs LLM
              </motion.h2>
              <p className="text-sm md:text-base text-on-surface-variant max-w-2xl mx-auto">
                Biomedical QA Benchmark — Token Reduction at Scale
              </p>
            </div>

            <div className="w-full max-w-3xl mt-2 md:mt-4 space-y-4">
              <div className="relative glass-card rounded-2xl md:rounded-full p-2 flex flex-col md:flex-row items-center focus-within:border-primary-brand/50 transition-all gap-2 md:gap-0">
                <div className="flex items-center w-full px-2">
                  <Search className="text-on-surface-variant ml-2 mr-2 w-5 h-5" />
                  <input 
                    type="text" 
                    className="flex-1 bg-transparent border-none focus:ring-0 text-on-surface placeholder-on-surface-variant/50 h-12 text-sm md:text-base"
                    placeholder="Enter biomedical query..."
                    defaultValue="What is the effect of aspirin on platelet aggregation?"
                  />
                  <button className="w-10 h-10 rounded-full hover:bg-white/5 flex items-center justify-center text-on-surface-variant transition-colors">
                    <Mic className="w-5 h-5" />
                  </button>
                </div>
                <button className="w-full md:w-auto bg-primary-brand text-on-primary-brand text-[11px] font-bold uppercase tracking-widest px-8 py-4 rounded-xl md:rounded-full hover:bg-primary-container transition-all shadow-[0_0_20px_rgba(255,179,173,0.4)] active:scale-95 shrink-0">
                  Run All 3 Pipelines
                </button>
              </div>

              <div className="flex flex-wrap justify-center gap-2 pb-2">
                <span className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/50 mr-2 py-1">Suggested:</span>
                {suggestedQueries.map(query => (
                  <button 
                    key={query}
                    className="glass-card px-3 py-1 rounded-full font-mono text-[11px] text-on-surface-variant hover:text-on-surface hover:border-white/20 transition-colors whitespace-nowrap"
                  >
                    {query}
                  </button>
                ))}
              </div>
            </div>
          </section>

          {/* Results Grid */}
          <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <MetricCard 
              title="LLM Only"
              icon={Cpu}
              colorClass="text-error-brand"
              tokens="4,096"
              latency="3.2s"
              cost="$0.04"
              content="Aspirin irreversibly inhibits cyclooxygenase-1 (COX-1) in platelets, preventing the synthesis of thromboxane A2. This effect persists for the life of the platelet (approx. 7-10 days)..."
            />
            <MetricCard 
              title="Basic RAG"
              icon={Network}
              colorClass="text-secondary-brand"
              tokens="12,500"
              latency="8.4s"
              cost="$0.12"
              content="Based on retrieved documents (Doc1, Doc4, Doc12): Aspirin blocks platelet aggregation by inhibiting COX-1 and thus TxA2 production. Clinical studies indicate a reduction in myocardial infarction risk..."
            />
            <MetricCard 
              title="GraphRAG"
              isBest
              icon={Share2}
              colorClass="text-tertiary-brand"
              tokens="2,104"
              latency="4.1s"
              cost="$0.02"
              content="> Path extracted: [Aspirin] -(inhibits)-> [COX-1] -(prevents)-> [TxA2 synthesis] -(stops)-> [Platelet Aggregation]. Directly answers query with high precision using sub-graph traversal of the biomedical relationship map."
            />
          </section>

          {/* Data Module */}
          <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-8">
              <ConsumptionChart />
            </div>
            <div className="lg:col-span-4">
              <EfficiencyRing />
            </div>
          </section>

          {/* Executions Table */}
          <ExecutionsTable />
        </main>

        {/* Footer */}
        <footer className="hidden md:flex bg-surface-dim fixed bottom-0 right-0 w-[calc(100%-288px)] py-4 border-t border-white/5 justify-between items-center px-10 z-40">
          <div className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
            © 2024 NeuralBio Research Labs. System Status: Optimal.
          </div>
          <div className="flex gap-6 font-mono text-[11px]">
            <a className="text-on-surface-variant/60 hover:text-tertiary-brand transition-colors" href="#">Documentation</a>
            <a className="text-on-surface-variant/60 hover:text-tertiary-brand transition-colors" href="#">API Access</a>
            <a className="text-on-surface-variant/60 hover:text-tertiary-brand transition-colors" href="#">Privacy Docs</a>
          </div>
        </footer>

        {/* Mobile Bottom Nav */}
        <nav className="md:hidden bg-surface-dim/90 backdrop-blur-xl fixed bottom-0 left-0 w-full h-16 border-t border-white/10 flex justify-around items-center px-2 z-50">
          <a className="flex flex-col items-center gap-1 text-primary-brand" href="#">
            <Share2 className="w-5 h-5" />
            <span className="text-[9px] font-bold uppercase tracking-widest">GraphRAG</span>
          </a>
          <a className="flex flex-col items-center gap-1 text-on-surface-variant" href="#">
            <Database className="w-5 h-5" />
            <span className="text-[9px] font-bold uppercase tracking-widest">Data</span>
          </a>
          <a className="flex flex-col justify-center items-center relative -top-4" href="#">
            <div className="w-12 h-12 bg-primary-brand rounded-full flex items-center justify-center text-on-primary-brand shadow-[0_0_15px_rgba(255,179,173,0.3)]">
              <Plus className="w-6 h-6" />
            </div>
          </a>
          <a className="flex flex-col items-center gap-1 text-on-surface-variant" href="#">
            <Cpu className="w-5 h-5" />
            <span className="text-[9px] font-bold uppercase tracking-widest">Models</span>
          </a>
          <a className="flex flex-col items-center gap-1 text-on-surface-variant" href="#">
            <Menu className="w-5 h-5" />
            <span className="text-[9px] font-bold uppercase tracking-widest">Menu</span>
          </a>
        </nav>
      </div>
    </div>
  );
}
