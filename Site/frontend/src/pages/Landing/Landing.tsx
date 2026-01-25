import React from "react";
import {
  Shield,
  Zap,
  Bot,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Globe,
  Heart,
  DollarSign,
  UserPlus,
} from "lucide-react";
import { Button } from "@/components/Button";
import { useLanguage } from "@/contexts/LanguageContext";
import { AuthModal } from "./Auth/AuthModal";
import { isLoggedIn } from "@/services/auth";

export const LandingPage: React.FC = () => {
  const { t, language, setLanguage } = useLanguage();

  const [isAuthModalOpen, setIsAuthModalOpen] = React.useState(false);
  const [authMode, setAuthMode] = React.useState<'login' | 'register'>('login');
  const [isAuthenticated, setIsAuthenticated] = React.useState(false);
  const [channelCount, setChannelCount] = React.useState<number | null>(null);

  React.useEffect(() => {
    async function fetchStats() {
      try {
        const response = await fetch(`${import.meta.env.VITE_BACKEND_PATH}/landing/channels`);
        const data = await response.json();
        setChannelCount(data.channels);
      } catch (err) {
        console.error("Failed to fetch channel count:", err);
      }
    }
    async function checkAuth() {
      const authStatus = await isLoggedIn();
      setIsAuthenticated(authStatus);
    }
    fetchStats();
    checkAuth();
  }, []);

  function openAuth(mode: 'login' | 'register') {
    setAuthMode(mode);
    setIsAuthModalOpen(true);
  }

  return (
    <>
      <div className="min-h-screen bg-slate-950 text-slate-50 flex flex-col">
        {/* Header */}
        <header className="container mx-auto px-6 py-6 flex items-center justify-between sticky top-0 z-50 bg-slate-950/80 backdrop-blur-md border-b border-transparent hover:border-slate-800 transition-colors">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-400 to-cyan-500 flex items-center justify-center shadow-lg shadow-brand-500/20">
              <Bot className="text-white" size={24} />
            </div>
            <span className="text-xl font-bold">Holy-bot</span>
          </div>
          <div className="flex items-center gap-8">
            <nav className="hidden md:flex items-center space-x-8 text-sm font-medium text-slate-400">
              <a href="#features" className="hover:text-white transition-colors">
                {t("landing.features")}
              </a>
              <a href="#pricing" className="hover:text-white transition-colors">
                {t("landing.pricing")}
              </a>
              <a href="#about" className="hover:text-white transition-colors">
                {t("landing.about")}
              </a>
            </nav>

            <div className="flex items-center gap-4">
              {/* Language Switcher */}
              <button
                onClick={() => setLanguage(language === "en" ? "ru" : "en")}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-white bg-slate-900 border border-slate-800 rounded-md transition-colors"
              >
                <Globe size={14} />
                {language.toUpperCase()}
              </button>

              {isAuthenticated ? (
                <Button size="sm" variant="secondary" className="hidden md:flex" onClick={() => window.location.href = '/dashboard'}>
                  {t('landing.goToProfile')}
                </Button>
              ) : (
                <Button size="sm" variant="secondary" className="hidden md:flex" onClick={() => openAuth('login')}>
                  {t('landing.signIn')}
                </Button>
              )}
            </div>
          </div>
        </header>

        {/* Hero */}
        <main className="flex-1 flex flex-col">
          <div className="container mx-auto px-6 py-20 lg:py-32 flex flex-col lg:flex-row items-center gap-12">
            <div className="lg:w-1/2 space-y-8">
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-400 text-xs font-medium">
                <span className="w-2 h-2 rounded-full bg-brand-500 animate-pulse"></span>
                <span>{t("landing.heroBadge")}</span>
              </div>

              <h1 className="text-5xl lg:text-7xl font-bold tracking-tight text-white leading-tight">
                {t("landing.heroTitle")}
              </h1>

              <p className="text-lg text-slate-400 max-w-xl leading-relaxed">
                {t("landing.heroDesc")}
              </p>

              <div className="flex flex-col sm:flex-row gap-4">
                {isAuthenticated ? (
                  <Button size="lg" className="w-full sm:w-auto group" onClick={() => window.location.href = '/dashboard'}>
                    {t('landing.goToProfile')}
                    <ArrowRight size={16} className="ml-2 opacity-0 -translate-x-2 group-hover:translate-x-0 group-hover:opacity-100 transition-all" />
                  </Button>
                ) : (
                  <>
                    <Button size="lg" className="w-full sm:w-auto group" onClick={() => openAuth('register')}>
                      {t('landing.getStartedFree')}
                      <ArrowRight size={16} className="ml-2 opacity-0 -translate-x-2 group-hover:translate-x-0 group-hover:opacity-100 transition-all" />
                    </Button>
                  </>
                )}
                <Button
                  variant="secondary"
                  size="lg"
                  className="w-full sm:w-auto"
                >
                  {t("landing.viewDocs")}
                </Button>
              </div>

              <div className="pt-8 flex items-center gap-6 text-sm text-slate-500">
                <div className="flex items-center gap-2">
                  <CheckCircle2 size={16} className="text-brand-500" />
                  <span>{t("landing.noCard")}</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 size={16} className="text-brand-500" />
                  <span>{t("landing.activeUsers", { channels: channelCount ?? "..." })}</span>
                </div>
              </div>
            </div>

            <div className="lg:w-1/2 relative">
              <div className="absolute -inset-1 bg-gradient-to-r from-brand-400 to-cyan-500 rounded-2xl blur opacity-30 animate-pulse"></div>
              <div className="relative bg-slate-900 border border-slate-800 rounded-xl shadow-2xl overflow-hidden aspect-video group">
                {/* Mock Dashboard UI preview */}
                <div className="absolute inset-0 bg-slate-900 flex flex-col">
                  <div className="h-10 border-b border-slate-800 bg-slate-950/50 flex items-center px-4 gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500/20"></div>
                    <div className="w-3 h-3 rounded-full bg-amber-500/20"></div>
                    <div className="w-3 h-3 rounded-full bg-emerald-500/20"></div>
                  </div>
                  <div className="flex-1 p-6 grid grid-cols-2 gap-4 opacity-50 group-hover:opacity-100 transition-opacity duration-700">
                    <div className="bg-slate-800/50 rounded-lg h-32 animate-pulse"></div>
                    <div className="bg-slate-800/50 rounded-lg h-32 animate-pulse delay-75"></div>
                    <div className="col-span-2 bg-slate-800/50 rounded-lg h-40 animate-pulse delay-150"></div>
                  </div>

                  {/* Live Activity Mock Feed - Replaces Placeholder */}
                  <div className="absolute bottom-6 right-6 flex flex-col gap-2 w-64 transform translate-y-2 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-500">
                    <div className="bg-slate-800/90 backdrop-blur border border-slate-700 p-3 rounded-lg shadow-lg flex items-center gap-3 animate-in slide-in-from-right fade-in duration-300">
                      <div className="p-1.5 bg-emerald-500/20 rounded text-emerald-400">
                        <DollarSign size={14} />
                      </div>
                      <div className="text-xs">
                        <p className="text-slate-200 font-medium">
                          Donation{" "}
                          <span className="text-emerald-400">$20.00</span>
                        </p>
                        <p className="text-slate-500">HolyFan: keep it up!</p>
                      </div>
                    </div>
                    <div className="bg-slate-800/90 backdrop-blur border border-slate-700 p-3 rounded-lg shadow-lg flex items-center gap-3 animate-in slide-in-from-right fade-in duration-500 delay-100">
                      <div className="p-1.5 bg-brand-500/20 rounded text-brand-400">
                        <Heart size={14} />
                      </div>
                      <div className="text-xs">
                        <p className="text-slate-200 font-medium">New Follower</p>
                        <p className="text-slate-500">DivineGamer joined!</p>
                      </div>
                    </div>
                    <div className="bg-slate-800/90 backdrop-blur border border-slate-700 p-3 rounded-lg shadow-lg flex items-center gap-3 animate-in slide-in-from-right fade-in duration-700 delay-200">
                      <div className="p-1.5 bg-red-500/20 rounded text-red-400">
                        <Shield size={14} />
                      </div>
                      <div className="text-xs">
                        <p className="text-slate-200 font-medium">
                          AutoMod Action
                        </p>
                        <p className="text-slate-500">Blocked spam link</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>

        {/* Features Grid */}
        <section
          id="features"
          className="py-24 bg-slate-900/50 border-t border-slate-800"
        >
          <div className="container mx-auto px-6">
            <div className="text-center max-w-2xl mx-auto mb-16">
              <h2 className="text-3xl font-bold text-white mb-4">
                {t("landing.featuresTitle")}
              </h2>
              <p className="text-slate-400">{t("landing.featuresDesc")}</p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              <FeatureCard
                icon={<Shield size={32} className="text-emerald-400" />}
                title={t("landing.autoModTitle")}
                description={t("landing.autoModDesc")}
              />
              <FeatureCard
                icon={<BarChart3 size={32} className="text-brand-400" />}
                title={t("landing.analyticsTitle")}
                description={t("landing.analyticsDesc")}
              />
              <FeatureCard
                icon={<Bot size={32} className="text-purple-400" />}
                title={t("landing.aiTitle")}
                description={t("landing.aiDesc")}
              />
            </div>
          </div>
        </section>

        {/* About Section (Added for navigation) */}
        <section
          id="about"
          className="py-24 bg-slate-900/50 border-t border-slate-800"
        >
          <div className="container mx-auto px-6 text-center">
            <h2 className="text-3xl font-bold text-white mb-4">
              {t("landing.aboutTitle")}
            </h2>
            <p className="text-slate-400 max-w-2xl mx-auto mb-8">
              {t("landing.aboutDesc")}
            </p>
            <div className="flex justify-center gap-4">
              <div className="w-12 h-12 bg-slate-800 rounded-full flex items-center justify-center">
                🎮
              </div>
              <div className="w-12 h-12 bg-slate-800 rounded-full flex items-center justify-center">
                💻
              </div>
              <div className="w-12 h-12 bg-slate-800 rounded-full flex items-center justify-center">
                🚀
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-8 border-t border-slate-800 bg-slate-950 text-center text-slate-500 text-sm">
          <div className="container mx-auto px-6">
            <p>{t("landing.footerRights")}</p>
            <div className="mt-2 space-x-4"></div>
          </div>
        </footer>
      </div>

      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onSuccess={() => { window.location.href = '/dashboard' }}
        initialMode={authMode}
      />
    </>
  );
};


const FeatureCard: React.FC<{
  icon: React.ReactNode;
  title: string;
  description: string;
}> = ({ icon, title, description }) => (
  <div className="bg-slate-950 border border-slate-800 p-8 rounded-2xl hover:border-slate-700 transition-colors">
    <div className="mb-4 inline-block p-3 bg-slate-900 rounded-xl">{icon}</div>
    <h3 className="text-xl font-bold text-white mb-2">{title}</h3>
    <p className="text-slate-400 leading-relaxed">{description}</p>
  </div>
);
