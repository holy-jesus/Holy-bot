import React, { useState, useEffect } from 'react';
import { X, Bot, Sparkles } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { LoginForm } from './LoginForm';
import { RegisterForm } from './RegisterForm';
import { VerifyForm } from './VerifyForm';
import { getCSRFToken } from "@/services/auth";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  initialMode?: 'login' | 'register';
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, onSuccess, initialMode = 'login' }) => {
  const { t } = useLanguage();
  const [mode, setMode] = useState<'login' | 'register' | 'verify'>(initialMode);

  useEffect(() => {
    if (isOpen) {
      getCSRFToken();
    }
  }, [isOpen]);

  if (!isOpen) return null;


  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-xl animate-in fade-in duration-300" onClick={onClose} />
      {/* Modal Card */}
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-slate-500 hover:text-white transition-colors"
        >
          <X size={20} />
        </button>
        <div className="p-8">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-400 to-purple-600 flex items-center justify-center shadow-lg shadow-brand-500/20">
              <Bot className="text-white" size={24} />
            </div>
            <div>
              <h2 className="text-2xl font-black text-white tracking-tight">
                {mode === 'login' ? t('auth.loginTitle') : mode === 'register' ? t('auth.registerTitle') : t('auth.verifyTitle')}
              </h2>
              <p className="text-xs text-slate-400">
                {mode === 'login' ? t('auth.loginSubtitle') : mode === 'register' ? t('auth.registerSubtitle') : t('auth.verifySubtitle')}
              </p>
            </div>
          </div>
          {mode === 'login' ? (
            <LoginForm
              onSuccess={onSuccess}
              onSwitchToRegister={() => setMode('register')}
            />
          ) : mode === 'register' ? (
            <RegisterForm
              onSuccess={() => setMode('verify')}
              onSwitchToLogin={() => setMode('login')}
            />
          ) : (
            <VerifyForm onSuccess={onSuccess} />
          )}
          <div className="mt-8 pt-6 border-t border-slate-800 flex items-center justify-center gap-2">
            <Sparkles size={14} className="text-brand-500" />
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Divine Security Guaranteed</span>
          </div>
        </div>
      </div>
    </div>
  );
};
