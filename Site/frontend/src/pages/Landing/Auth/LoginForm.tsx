import React, { useState } from 'react';
import { Mail, Lock, User, ShieldCheck, ArrowRight } from 'lucide-react';
import { Button } from '@/components/Button';
import { useLanguage } from '@/contexts/LanguageContext';
interface LoginFormProps {
  onSuccess: () => void;
  onSwitchToRegister: () => void;
}
export const LoginForm: React.FC<LoginFormProps> = ({ onSuccess, onSwitchToRegister }) => {
  const { t } = useLanguage();
  const [loginMethod, setLoginMethod] = useState<'password' | 'code'>('password');
  const [isCodeSent, setIsCodeSent] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  // Form states
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [verifyCode, setVerifyCode] = useState('');
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // Mocking API delays
    await new Promise(resolve => setTimeout(resolve, 1000));
    if (loginMethod === 'code' && !isCodeSent) {
      setIsCodeSent(true);
      setIsLoading(false);
      return;
    }
    
    onSuccess();
    setIsLoading(false);
  };
  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
      <div className="flex bg-slate-800/50 p-1 rounded-lg border border-slate-700">
        <button
          onClick={() => { setLoginMethod('password'); setIsCodeSent(false); }}
          className={`flex-1 py-2 text-xs font-bold rounded-md transition-all ${loginMethod === 'password' ? 'bg-brand-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
        >
          {t('auth.usePassword')}
        </button>
        <button
          onClick={() => setLoginMethod('code')}
          className={`flex-1 py-2 text-xs font-bold rounded-md transition-all ${loginMethod === 'code' ? 'bg-brand-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
        >
          {t('auth.useEmailCode')}
        </button>
      </div>
      <form onSubmit={handleLogin} className="space-y-4">
        {loginMethod === 'password' ? (
          <>
            <div className="relative">
              <User className="absolute left-3 top-3.5 text-slate-500" size={18} />
              <input
                required
                type="text"
                placeholder={t('auth.username')}
                value={username}
                onChange={e => setUsername(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl py-3 pl-10 pr-4 text-sm text-white focus:ring-2 focus:ring-brand-500 outline-none transition-all"
              />
            </div>
            <div className="relative">
              <Lock className="absolute left-3 top-3.5 text-slate-500" size={18} />
              <input
                required
                type="password"
                placeholder={t('auth.password')}
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl py-3 pl-10 pr-4 text-sm text-white focus:ring-2 focus:ring-brand-500 outline-none transition-all"
              />
            </div>
          </>
        ) : (
          <>
            <div className="relative">
              <Mail className="absolute left-3 top-3.5 text-slate-500" size={18} />
              <input
                required
                type="email"
                placeholder={t('auth.email')}
                value={email}
                onChange={e => setEmail(e.target.value)}
                disabled={isCodeSent}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl py-3 pl-10 pr-4 text-sm text-white focus:ring-2 focus:ring-brand-500 outline-none transition-all disabled:opacity-50"
              />
            </div>
            {isCodeSent && (
              <div className="relative animate-in slide-in-from-top-2 duration-300">
                <ShieldCheck className="absolute left-3 top-3.5 text-brand-400" size={18} />
                <input
                  required
                  type="text"
                  maxLength={6}
                  placeholder={t('auth.code')}
                  value={verifyCode}
                  onChange={e => setVerifyCode(e.target.value)}
                  className="w-full bg-slate-950 border border-brand-500/50 rounded-xl py-3 pl-10 pr-4 text-sm text-white focus:ring-2 focus:ring-brand-500 outline-none transition-all"
                />
              </div>
            )}
          </>
        )}
        <Button
          type="submit"
          className="w-full py-4 text-sm font-bold shadow-xl shadow-brand-500/10"
          disabled={isLoading}
          icon={isLoading ? <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" /> : <ArrowRight size={18}/>}
        >
          {loginMethod === 'code' && !isCodeSent ? t('auth.sendCode') : t('auth.signIn')}
        </Button>
      </form>
      <div className="text-center">
        <p className="text-xs text-slate-500">
          {t('auth.noAccount')}{' '}
          <button onClick={onSwitchToRegister} className="text-brand-400 font-bold hover:underline transition-all">
            {t('auth.signUp')}
          </button>
        </p>
      </div>
    </div>
  );
};
