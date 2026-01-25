import React, { useState } from 'react';
import { ShieldCheck } from 'lucide-react';
import { Button } from '@/components/Button';
import { useLanguage } from '@/contexts/LanguageContext';
import { verifyEmail } from '@/services/auth';
import { toast } from 'sonner';
interface VerifyFormProps {
  onSuccess: () => void;
}
export const VerifyForm: React.FC<VerifyFormProps> = ({ onSuccess }) => {
  const { t } = useLanguage();
  const [isLoading, setIsLoading] = useState(false);
  const [verifyCode, setVerifyCode] = useState('');
  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();

    setIsLoading(true);
    try {
      await verifyEmail(verifyCode);
      onSuccess();
    } catch (error: any) {
      console.error('Verification failed:', error);
      const status = error.response?.status;

      if (status === 401 || status === 400) {
        toast.error(t('auth.invalidCode'));
      } else if (status === 429) {
        toast.error(t('auth.errorTooManyRequests'));
      } else if (status >= 500) {
        toast.error(t('auth.errorServerError'));
      } else {
        toast.error(t('auth.errorGeneric'));
      }
    }
    setIsLoading(false);
  };
  return (
    <div className="space-y-6 animate-in zoom-in-95 duration-300">
      <div className="flex justify-center mb-4">
        <div className="w-16 h-16 rounded-full bg-brand-500/10 border border-brand-500/20 flex items-center justify-center">
          <ShieldCheck className="text-brand-500" size={32} />
        </div>
      </div>
      <form onSubmit={handleVerify} className="space-y-6">
        <div className="flex flex-col gap-4">
          <input
            required
            type="text"
            value={verifyCode}
            placeholder="abcdefghijklmnop"
            onChange={e => setVerifyCode(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl py-4 text-center text-xl font-mono tracking-wider text-white focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500/50 outline-none transition-all uppercase placeholder:text-slate-800"
          />
          <p className="text-[10px] text-center text-slate-500 uppercase font-bold tracking-widest">{t('auth.resend')}</p>
        </div>
        <Button
          type="submit"
          className="w-full py-4 text-sm font-bold"
          disabled={isLoading}
          icon={isLoading ? <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" /> : <ShieldCheck size={18} />}
        >
          {t('auth.verify')}
        </Button>
      </form>
    </div>
  );
};
