import React, { useState, useEffect } from 'react';
import { Search, Menu, Building2 } from 'lucide-react';
import { checkBackendHealth } from '../services/api';
import type { TabKey } from './Sidebar';

interface HeaderProps {
  onOpenMobileSidebar: () => void;
  collapsed: boolean;
  onSearchSubmit?: (query: string) => void;
  onNavigate: (tab: TabKey) => void;
}

export const Header: React.FC<HeaderProps> = ({
  onOpenMobileSidebar,
  collapsed,
  onSearchSubmit,
  onNavigate,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    let isMounted = true;
    const checkHealth = async () => {
      try {
        const res = await checkBackendHealth();
        if (isMounted) setIsHealthy(res.status === 'healthy');
      } catch {
        if (isMounted) setIsHealthy(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSearchSubmit && searchTerm.trim()) {
      onSearchSubmit(searchTerm.trim());
    } else if (searchTerm.trim()) {
      // Default to opening Geo Map with search
      onNavigate('map');
    }
  };

  return (
    <header
      className={`sticky top-0 z-30 bg-[#FFFFFF] border-b border-[#E3EBE5] transition-all duration-200 h-16 flex items-center px-4 sm:px-6 shadow-xs ${
        collapsed ? 'md:pl-24' : 'md:pl-68'
      }`}
    >
      <div className="w-full flex items-center justify-between gap-3 sm:gap-6">
        {/* Left: Mobile Hamburger & Search Input */}
        <div className="flex items-center gap-3 flex-1 max-w-xl">
          <button
            onClick={onOpenMobileSidebar}
            className="md:hidden p-2 text-[#182C25] hover:bg-[#EDF8F1] rounded-lg transition-colors"
            title="Open navigation menu"
          >
            <Menu className="w-5 h-5" />
          </button>

          {/* Global Search Bar */}
          <form onSubmit={handleSearch} className="relative w-full">
            <Search className="w-4 h-4 text-[#718078] absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by District, Village or Well ID (e.g. W153803073591301, Pune, Matne)..."
              className="w-full pl-9 pr-4 py-2 text-xs bg-[#F8FAF7] border border-[#E3EBE5] focus:border-[#119B72] focus:bg-white focus:outline-none rounded-xl text-[#182C25] placeholder-[#718078] transition-all shadow-2xs"
            />
          </form>
        </div>

        {/* Right Section: System Connection & Agency Profile */}
        <div className="flex items-center gap-2.5 sm:gap-4 shrink-0">
          {/* Live System Health Pill */}
          <div className="flex items-center gap-2 px-2.5 sm:px-3 py-1.5 rounded-full bg-[#EDF8F1] border border-[#D9F2E6] text-[11px] font-medium text-[#073B32]">
            <span
              className={`w-2 h-2 rounded-full ${
                isHealthy === null
                  ? 'bg-[#E9A23B] animate-pulse'
                  : isHealthy
                  ? 'bg-[#119B72] shadow-xs shadow-[#119B72]'
                  : 'bg-[#E45B55] animate-ping'
              }`}
            />
            <span className="hidden sm:inline">
              {isHealthy === null ? 'Connecting...' : isHealthy ? 'System Online (Live API)' : 'Backend Offline'}
            </span>
            <span className="sm:hidden">
              {isHealthy ? 'Online' : 'Offline'}
            </span>
          </div>

          {/* Government / Agency Badge */}
          <div className="flex items-center gap-2 pl-2 border-l border-[#E3EBE5]">
            <div className="w-8 h-8 rounded-full bg-[#D9F2E6] text-[#073B32] flex items-center justify-center font-bold text-xs shrink-0">
              <Building2 className="w-4 h-4 text-[#0B4F43]" />
            </div>
            <div className="hidden lg:block text-left">
              <p className="text-xs font-bold text-[#182C25] leading-tight">
                CGWB Maharashtra
              </p>
              <p className="text-[10px] text-[#718078] leading-tight">
                Water Resources Intelligence
              </p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
