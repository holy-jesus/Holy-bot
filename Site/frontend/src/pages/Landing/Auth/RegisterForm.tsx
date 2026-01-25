import React, { useState } from 'react';
import { Mail, Lock, User } from 'lucide-react';
import { Button } from '@/components/Button';
import { useLanguage } from '@/contexts/LanguageContext';
import { register } from '@/services/auth';
import { toast } from 'sonner';

interface RegisterFormProps {
  onSuccess: () => void;
  onSwitchToLogin: () => void;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onSuccess, onSwitchToLogin }) => {
  const { t } = useLanguage();
  const [isLoading, setIsLoading] = useState(false);

  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const validateEmail = (email: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const validatePassword = (password: string) => {
    const hasLetter = /[a-zA-Z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    return {
      isEmpty: password.length === 0,
      isValid: password.length >= 8 && hasLetter && hasNumber,
      isLongEnough: password.length >= 8,
      hasLetterAndNumber: hasLetter && hasNumber
    };
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateEmail(email)) {
      toast.error(t('auth.errorEmail'));
      return;
    }

    const passwordValidation = validatePassword(password);
    if (!passwordValidation.isEmpty) {
      if (!passwordValidation.isLongEnough) {
        toast.error(t('auth.errorPasswordShort'));
        return;
      }
      if (!passwordValidation.hasLetterAndNumber) {
        toast.error(t('auth.errorPasswordWeak'));
        return;
      }
    }

    setIsLoading(true);

    try {
      const [status_code, data] = await register(email, username, password);
      if (status_code === 202) {
        onSuccess();
      } else if (status_code === 409) {
        toast.error(t('auth.errorUserExists'));
      } else if (status_code === 429) {
        toast.error(t('auth.errorTooManyRequests'));
      } else {
        toast.error(t('auth.errorGeneric'));
      }
    } catch (error: any) {
      console.error('Registration failed:', error);
      if (error.response?.status === 429) {
        toast.error(t('auth.errorTooManyRequests'));
      } else if (error.response?.status >= 500) {
        toast.error(t('auth.errorServerError'));
      } else {
        toast.error(t('auth.errorGeneric'));
      }
    }

    setIsLoading(false);
  };
  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
      <form onSubmit={handleRegister} className="space-y-4">
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
          <Mail className="absolute left-3 top-3.5 text-slate-500" size={18} />
          <input
            required
            type="email"
            placeholder={t('auth.email')}
            value={email}
            onChange={e => setEmail(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl py-3 pl-10 pr-4 text-sm text-white focus:ring-2 focus:ring-brand-500 outline-none transition-all"
          />
        </div>
        <div className="relative">
          <Lock className="absolute left-3 top-3.5 text-slate-500" size={18} />
          <input
            type="password"
            placeholder={t('auth.passwordOptional')}
            value={password}
            onChange={e => setPassword(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl py-3 pl-10 pr-4 text-sm text-white focus:ring-2 focus:ring-brand-500 outline-none transition-all"
          />
        </div>
        <Button
          type="submit"
          className="w-full py-4 text-sm font-bold"
          disabled={isLoading}
          icon={isLoading ? <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" /> : null}
        >
          {t('auth.signUp')}
        </Button>
      </form>
      <div className="text-center">
        <p className="text-xs text-slate-500">
          {t('auth.hasAccount')}{' '}
          <button onClick={onSwitchToLogin} className="text-brand-400 font-bold hover:underline transition-all">
            {t('auth.signIn')}
          </button>
        </p>
      </div>
    </div>
  );
};
