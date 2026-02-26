import { create } from "zustand";

interface FitnessState {
  totalXP: number;
  level: number;
  streak: number;
  sessionsCompleted: number;
  lastLoginDate: string | null;

  addGoodRep: () => void;
  addBadRep: () => void;
  completeWorkout: () => void;
  addDailyLoginBonus: () => void;
  calculateLevel: () => void;
}

const calculateLevelFromXP = (xp: number) => {
  return Math.floor(Math.sqrt(xp / 100)) + 1;
};

export const useFitnessStore = create<FitnessState>((set, get) => ({
  totalXP: 0,
  level: 1,
  streak: 0,
  sessionsCompleted: 0,
  lastLoginDate: null,

  addGoodRep: () => {
    const newXP = get().totalXP + 10;
    set({ totalXP: newXP });
    get().calculateLevel();
  },

  addBadRep: () => {
    const newXP = get().totalXP + 3;
    set({ totalXP: newXP });
    get().calculateLevel();
  },

  completeWorkout: () => {
    const newXP = get().totalXP + 50;
    set({
      totalXP: newXP,
      sessionsCompleted: get().sessionsCompleted + 1,
    });
    get().calculateLevel();
  },

  addDailyLoginBonus: () => {
    const today = new Date().toDateString();

    if (get().lastLoginDate !== today) {
      set({
        totalXP: get().totalXP + 20,
        streak: get().streak + 1,
        lastLoginDate: today,
      });
      get().calculateLevel();
    }
  },

  calculateLevel: () => {
    const level = calculateLevelFromXP(get().totalXP);
    set({ level });
  },
}));