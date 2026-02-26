import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";

interface StubPageProps {
  title: string;
  description: string;
  icon: LucideIcon;
}

const StubPage = ({ title, description, icon: Icon }: StubPageProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center min-h-[60vh] text-center"
    >
      <div className="w-20 h-20 rounded-2xl bg-primary/10 flex items-center justify-center mb-6">
        <Icon className="w-10 h-10 text-primary" />
      </div>
      <h1 className="text-2xl font-display font-bold text-foreground mb-2">{title}</h1>
      <p className="text-muted-foreground text-sm max-w-md">{description}</p>
      <div className="mt-6 glass-card px-4 py-2 text-xs text-muted-foreground">
        🚧 Coming soon
      </div>
    </motion.div>
  );
};

export default StubPage;
