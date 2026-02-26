import { motion } from "framer-motion";

interface XPBarProps {
  current: number;
  max: number;
  level: number;
}

const XPBar = ({ current, max, level }: XPBarProps) => {
  const percent = (current / max) * 100;

  return (
    <div className="flex items-center gap-3 w-full">
      <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary text-primary-foreground font-display font-bold text-sm shrink-0">
        {level}
      </div>
      <div className="flex-1">
        <div className="flex justify-between text-xs font-medium mb-1">
          <span className="text-muted-foreground">Level {level}</span>
          <span className="text-muted-foreground">{current}/{max} XP</span>
        </div>
        <div className="h-2.5 rounded-full bg-muted overflow-hidden">
          <motion.div
            className="xp-bar h-full"
            initial={{ width: 0 }}
            animate={{ width: `${percent}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
          />
        </div>
      </div>
    </div>
  );
};

export default XPBar;
