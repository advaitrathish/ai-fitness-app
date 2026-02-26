import { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import {
  LayoutDashboard, Dumbbell, ListChecks, TrendingUp, UtensilsCrossed,
  Bot, Trophy, Crown, Settings, Users, BarChart3, CreditCard, ShieldCheck,
  Menu, X
} from "lucide-react";
import { useState } from "react";
import GlassBackground from "@/components/GlassBackground";
import ThemeToggle from "@/components/ThemeToggle";
import XPBar from "@/components/XPBar";

interface NavItem {
  label: string;
  to: string;
  icon: React.ElementType;
}

const userNav: NavItem[] = [
  { label: "Dashboard", to: "/dashboard", icon: LayoutDashboard },
  { label: "Live Workout", to: "/live-workout", icon: Dumbbell },
  { label: "Exercises", to: "/exercises", icon: ListChecks },
  { label: "Progress", to: "/progress", icon: TrendingUp },
  { label: "Meal Planner", to: "/meal-planner", icon: UtensilsCrossed },
  { label: "AI Coach", to: "/ai-coach", icon: Bot },
  { label: "Achievements", to: "/achievements", icon: Trophy },
  { label: "Premium", to: "/premium", icon: Crown },
  { label: "Settings", to: "/settings", icon: Settings },
];

const trainerNav: NavItem[] = [
  { label: "Clients", to: "/trainer/clients", icon: Users },
  { label: "Client Progress", to: "/trainer/progress", icon: BarChart3 },
  { label: "Assign Workouts", to: "/trainer/assign-workouts", icon: Dumbbell },
  { label: "Assign Meals", to: "/trainer/assign-meals", icon: UtensilsCrossed },
];

const adminNav: NavItem[] = [
  { label: "Dashboard", to: "/admin/dashboard", icon: LayoutDashboard },
  { label: "Users", to: "/admin/users", icon: Users },
  { label: "Trainers", to: "/admin/trainers", icon: ShieldCheck },
  { label: "Analytics", to: "/admin/analytics", icon: BarChart3 },
  { label: "Revenue", to: "/admin/revenue", icon: CreditCard },
];

const AppLayout = ({ children }: { children: ReactNode }) => {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const isTrainer = location.pathname.startsWith("/trainer");
  const isAdmin = location.pathname.startsWith("/admin");

  const nav = isAdmin ? adminNav : isTrainer ? trainerNav : userNav;
  const sectionLabel = isAdmin ? "Admin Panel" : isTrainer ? "Trainer Panel" : "FitQuest";

  return (
    <div className="min-h-screen flex relative">
      <GlassBackground />

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/30 z-40 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside className={`fixed lg:sticky top-0 left-0 h-screen w-64 z-50 glass-card-strong border-r border-border/30 flex flex-col transition-transform duration-300 ${sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}`}>
        <div className="p-5 flex items-center justify-between">
          <Link to="/dashboard" className="font-display font-bold text-xl gradient-text">{sectionLabel}</Link>
          <button className="lg:hidden text-foreground" onClick={() => setSidebarOpen(false)}>
            <X className="w-5 h-5" />
          </button>
        </div>

        {!isAdmin && !isTrainer && (
          <div className="px-5 mb-4">
            <XPBar current={2450} max={3000} level={12} />
          </div>
        )}

        <nav className="flex-1 px-3 space-y-1 overflow-y-auto">
          {nav.map((item) => {
            const active = location.pathname === item.to;
            return (
              <Link
                key={item.to}
                to={item.to}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  active
                    ? "bg-primary/15 text-primary"
                    : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                }`}
              >
                <item.icon className="w-4 h-4" />
                {item.label}
                {active && (
                  <motion.div
                    layoutId="sidebar-active"
                    className="absolute left-0 w-1 h-6 rounded-r-full bg-primary"
                  />
                )}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-border/30">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-primary/20 flex items-center justify-center text-primary font-display font-bold text-sm">
              JD
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-foreground truncate">John Doe</p>
              <p className="text-xs text-muted-foreground">{isAdmin ? "Admin" : isTrainer ? "Trainer" : "Pro Member"}</p>
            </div>
            <ThemeToggle />
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 min-h-screen lg:ml-0">
        <header className="sticky top-0 z-30 glass-card border-b border-border/30 px-4 py-3 flex items-center gap-3 lg:hidden">
          <button onClick={() => setSidebarOpen(true)} className="text-foreground">
            <Menu className="w-5 h-5" />
          </button>
          <span className="font-display font-bold gradient-text">{sectionLabel}</span>
        </header>

        <div className="p-4 md:p-6 lg:p-8">
          {children}
        </div>
      </main>
    </div>
  );
};

export default AppLayout;
