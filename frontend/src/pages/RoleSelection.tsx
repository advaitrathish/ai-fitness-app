import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { User, Dumbbell, Shield } from "lucide-react";
import GlassBackground from "@/components/GlassBackground";
import ThemeToggle from "@/components/ThemeToggle";

const roles = [
  {
    id: "user",
    label: "User",
    description: "Track workouts, meals & progress",
    icon: User,
    gradient: "from-[hsl(200,90%,55%)] to-[hsl(265,85%,60%)]",
  },
  {
    id: "trainer",
    label: "Trainer",
    description: "Manage clients & assign plans",
    icon: Dumbbell,
    gradient: "from-[hsl(25,100%,65%)] to-[hsl(340,90%,60%)]",
  },
  {
    id: "admin",
    label: "Admin",
    description: "Full system management",
    icon: Shield,
    gradient: "from-[hsl(160,85%,50%)] to-[hsl(200,90%,55%)]",
  },
];

const RoleSelection = () => {
  const navigate = useNavigate();

  const handleSelect = (role: string) => {
    navigate(role === "admin" ? "/admin/dashboard" : role === "trainer" ? "/trainer/clients" : "/dashboard");
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative">
      <GlassBackground />
      <div className="absolute top-4 right-4"><ThemeToggle /></div>

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-lg"
      >
        <div className="text-center mb-8">
          <h1 className="text-3xl font-display font-bold gradient-text mb-2">Choose Your Role</h1>
          <p className="text-muted-foreground text-sm">Select how you'll use FitQuest</p>
        </div>

        <div className="grid gap-4">
          {roles.map((role, i) => (
            <motion.button
              key={role.id}
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.4, delay: i * 0.1 }}
              onClick={() => handleSelect(role.id)}
              className="glass-card-strong p-5 flex items-center gap-4 text-left hover:scale-[1.02] transition-transform group"
            >
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${role.gradient} flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform`}>
                <role.icon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-display font-semibold text-foreground">{role.label}</h3>
                <p className="text-sm text-muted-foreground">{role.description}</p>
              </div>
            </motion.button>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default RoleSelection;
