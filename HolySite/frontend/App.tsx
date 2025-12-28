import React, { useState } from 'react';
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { LandingPage } from './components/LandingPage';
import { Sidebar } from './components/Sidebar';
import { DashboardOverview } from './components/DashboardOverview';
import { Timers } from './components/Timers';
import { Moderators } from './components/Moderators';
import { AskAi } from './components/AskAi';
import { Commands } from './components/Commands';
import { Menu, Bell, User as UserIcon, Search, Globe } from 'lucide-react';
import { BotStatus } from './types';
import { LanguageProvider, useLanguage } from './contexts/LanguageContext';

const AppContent: React.FC = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [activePage, setActivePage] = useState('overview');
  const { language, setLanguage } = useLanguage();

  const handleLogin = () => {
    // Immediate redirect as per request
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setActivePage('overview');
  };

  // Main Dashboard Layout Wrapper
  const DashboardLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    return (
      <div className="flex h-screen bg-slate-950 text-slate-50 overflow-hidden">
        {/* Sidebar */}
        <Sidebar 
          activePage={activePage} 
          onNavigate={(page) => {
            setActivePage(page);
            setIsMobileMenuOpen(false);
          }}
          onLogout={handleLogout}
          isOpen={isMobileMenuOpen}
        />
        
        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          {/* Top Bar */}
          <header className="h-16 flex items-center justify-between px-6 border-b border-slate-800 bg-slate-950/50 backdrop-blur-sm z-40">
            <div className="flex items-center">
              <button 
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="lg:hidden mr-4 text-slate-400 hover:text-white"
              >
                <Menu size={24} />
              </button>
              
              {/* Search Bar - Visual only */}
              <div className="hidden md:flex items-center relative">
                <Search size={16} className="absolute left-3 text-slate-500" />
                <input 
                  type="text" 
                  placeholder="Search settings..." 
                  className="bg-slate-900 border border-slate-800 text-sm rounded-full py-1.5 pl-9 pr-4 text-slate-300 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-brand-500 w-64 transition-all"
                />
              </div>
            </div>

            <div className="flex items-center gap-4">
               {/* Language Switcher */}
              <button 
                onClick={() => setLanguage(language === 'en' ? 'ru' : 'en')}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-white bg-slate-900 border border-slate-800 rounded-md transition-colors"
              >
                <Globe size={14} />
                {language.toUpperCase()}
              </button>

              <div className="hidden md:flex items-center gap-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                <span className="text-xs font-medium text-emerald-400">{BotStatus.ONLINE}</span>
              </div>
              
              <button className="relative p-2 text-slate-400 hover:text-white transition-colors">
                <Bell size={20} />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-brand-500 rounded-full border border-slate-950"></span>
              </button>
              
              <div className="flex items-center gap-3 pl-4 border-l border-slate-800">
                <div className="text-right hidden sm:block">
                  <p className="text-sm font-medium text-white">StreamerName</p>
                  <p className="text-xs text-slate-500">Broadcaster</p>
                </div>
                <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center overflow-hidden">
                  <UserIcon size={16} className="text-slate-400" />
                </div>
              </div>
            </div>
          </header>

          {/* Page Content */}
          <main className="flex-1 overflow-y-auto p-6 scroll-smooth">
            <div className="max-w-7xl mx-auto">
             {children}
            </div>
          </main>
        </div>

        {/* Mobile Overlay */}
        {isMobileMenuOpen && (
          <div 
            className="fixed inset-0 bg-black/50 z-40 lg:hidden backdrop-blur-sm"
            onClick={() => setIsMobileMenuOpen(false)}
          />
        )}
      </div>
    );
  };

  // Render specific content based on activePage state (Client-side simple routing for demo)
  const renderContent = () => {
    switch(activePage) {
      case 'overview': return <DashboardOverview />;
      case 'commands': return <Commands />;
      case 'timers': return <Timers />;
      case 'moderators': return <Moderators />;
      case 'ai-chat': return <AskAi />;
      default: return <div className="text-center text-slate-500 mt-20">Page not found or under construction.</div>;
    }
  };

  return (
    <Router>
      <Routes>
        <Route path="/" element={
          !isLoggedIn ? <LandingPage onLogin={handleLogin} /> : <Navigate to="/dashboard" />
        } />
        <Route path="/dashboard" element={
          isLoggedIn ? (
            <DashboardLayout>
              {renderContent()}
            </DashboardLayout>
          ) : (
            <Navigate to="/" />
          )
        } />
      </Routes>
    </Router>
  );
};

const App: React.FC = () => (
  <LanguageProvider>
    <AppContent />
  </LanguageProvider>
);

export default App;