import { useEffect, useState } from "react";
import { motion, animate } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import API from "@/lib/apis";
import {
  Flame,
  Dumbbell,
  TrendingUp,
  Zap,
  Target,
} from "lucide-react";
import XPBar from "@/components/XPBar";

const Dashboard = () => {
  const { data, isLoading } = useQuery({
    queryKey: ["me"],
    queryFn: async () => {
      const res = await API.get("me/");
      return res.data;
    },
  });

  const [animatedXP, setAnimatedXP] = useState(0);

  useEffect(() => {
    if (data?.xp !== undefined) {
      const controls = animate(0, data.xp, {
        duration: 1.2,
        onUpdate(value) {
          setAnimatedXP(Math.floor(value));
        },
      });
      return () => controls.stop();
    }
  }, [data]);

  if (isLoading) {
    return <div className="text-white p-8">Loading...</div>;
  }

  const stats = [
    { label: "Total XP", value: animatedXP, icon: Flame },
    { label: "Workouts Done", value: data.total_workouts, icon: Dumbbell },
    { label: "Current Level", value: data.level, icon: TrendingUp },
    { label: "Goal", value: data.goal, icon: Zap },
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6 max-w-6xl"
    >
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">
          Welcome back, {data.username} 👋
        </h1>

        <div className="w-72">
          <XPBar
            current={data.xp}
            max={data.level * 500}
            level={data.level}
          />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s) => (
          <motion.div
            whileHover={{ scale: 1.04 }}
            key={s.label}
            className="glass-card-strong p-4 text-center"
          >
            <s.icon className="w-5 h-5 mx-auto mb-2 text-primary" />
            <motion.p
              key={s.value}
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              className="text-2xl font-bold"
            >
              {s.value}
            </motion.p>
            <p className="text-xs text-muted-foreground">
              {s.label}
            </p>
          </motion.div>
        ))}
      </div>

      {/* Daily Goals */}
      <div className="glass-card-strong p-5">
        <h2 className="font-semibold mb-4 flex items-center gap-2">
          <Target className="w-4 h-4" /> Daily Goals
        </h2>

        <div className="grid sm:grid-cols-3 gap-4">
          {[7200, 5, 95].map((value, i) => (
            <div key={i} className="space-y-2">
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <motion.div
                  className="xp-bar h-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${(value / 10000) * 100}%` }}
                  transition={{ duration: 1 }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
};

export default Dashboard;