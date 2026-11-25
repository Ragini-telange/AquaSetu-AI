import React, { useEffect, useState } from 'react';
import { Waves, Activity, Droplets, MapPin, Navigation, LayoutDashboard, Map } from 'lucide-react';
import { checkBackendHealth } from '../services/api';

export type TabKey = 'dashboard' | 'map' | 'regression' | 'classification' | 'spatial' | 'routing';

interface NavbarProps {
  activeTab: TabKey;
  onTabChange: (tab: TabKey) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, onTabChange }) => {
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    const ping = async () => {
      try {
        const health = await checkBackendHealth();
        setIsBackendHealthy(health.status === 'healthy');
      } catch {
        setIsBackendHealthy(false);
      }
    };
    ping();
    const interval = setInterval(ping, 10000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { key: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { key: 'map', label: 'Geo Map', icon: Map, sub: 'Maharashtra' },
    { key: 'regression', label: 'Groundwater Level', icon: Droplets, sub: 'Regression' },
    { key: 'classification', label: 'Water Potability', icon: Activity, sub: 'Potability' },
    { key: 'spatial', label: 'Nearest Wells', icon: MapPin, sub: 'Statewide' },
    { key: 'routing', label: 'Pune Road Routing', icon: Navigation, sub: 'OSM Graph' },
  ];

  return (
    <header className="bg-slate-900 text-white shadow-lg sticky top-0 z-50 border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Branding */}
          <div
            onClick={() => onTabChange('dashboard')}
            className="flex items-center gap-3 cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-teal-400 flex items-center justify-center shadow-md shadow-cyan-500/20 group-hover:scale-105 transition-transform">
              <Waves className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-xl tracking-tight bg-gradient-to-r from-white via-slate-100 to-cyan-300 bg-clip-text text-transparent">
                  AquaGuard AI
                </span>
                <span className="text-[10px] font-semibold bg-cyan-900/60 text-cyan-300 border border-cyan-700/50 px-1.5 py-0.5 rounded">
                  v1.0
                </span>
              </div>
              <p className="text-xs text-slate-400">Groundwater Intelligence & Potability System</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.key;
              return (
                <button
                  key={item.key}
                  onClick={() => onTabChange(item.key as TabKey)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${isActive
                      ? 'bg-cyan-500 text-white shadow-md shadow-cyan-500/25'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                    }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                  {item.sub && (
                    <span className={`text-[10px] px-1.5 py-0.2 rounded font-normal ${isActive ? 'bg-cyan-700/60 text-cyan-100' : 'bg-slate-800 text-slate-400'
                      }`}>
                      {item.sub}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* Live Backend Status */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-xs font-medium px-2.5 py-1.5 rounded-full bg-slate-800/80 border border-slate-700">
              <span
                className={`w-2 h-2 rounded-full ${isBackendHealthy === null
                    ? 'bg-yellow-400 animate-pulse'
                    : isBackendHealthy
                      ? 'bg-emerald-400 shadow-sm shadow-emerald-400/50'
                      : 'bg-rose-500 animate-ping'
                  }`}
              />
              <span className="text-slate-300">
                {isBackendHealthy === null
                  ? 'Connecting...'
                  : isBackendHealthy
                    ? 'Backend Active'
                    : 'Backend Offline'}
              </span>
            </div>
          </div>
        </div>

        {/* Mobile Nav Bar */}
        <div className="md:hidden flex overflow-x-auto py-2 gap-2 border-t border-slate-800/80">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.key;
            return (
              <button
                key={item.key}
                onClick={() => onTabChange(item.key as TabKey)}
                className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium whitespace-nowrap ${isActive ? 'bg-cyan-500 text-white' : 'text-slate-300 hover:bg-slate-800'
                  }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
