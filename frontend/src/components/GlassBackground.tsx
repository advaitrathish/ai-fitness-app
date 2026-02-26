import { motion } from "framer-motion";

const GlassBackground = () => {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
      <motion.div
        className="orb orb-1 w-[500px] h-[500px] -top-40 -right-40 animate-float"
        animate={{ x: [0, 30, -20, 0], y: [0, -20, 15, 0] }}
        transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="orb orb-2 w-[400px] h-[400px] top-1/3 -left-32 animate-float-slow"
        animate={{ x: [0, -25, 20, 0], y: [0, 25, -10, 0] }}
        transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="orb orb-3 w-[350px] h-[350px] bottom-20 right-1/4 animate-float-delay"
        animate={{ x: [0, 20, -15, 0], y: [0, -30, 10, 0] }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="orb orb-4 w-[250px] h-[250px] top-1/2 right-10 animate-pulse-glow"
        animate={{ scale: [1, 1.1, 0.95, 1] }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
      />
    </div>
  );
};

export default GlassBackground;
