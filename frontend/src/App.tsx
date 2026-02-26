import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import AppLayout from "@/components/AppLayout";

import Login from "./pages/Login";
import Register from "./pages/Register";
import RoleSelection from "./pages/RoleSelection";
import Dashboard from "./pages/Dashboard";
import Premium from "./pages/Premium";
import ProfileSettings from "./pages/ProfileSettings";
import TrainerClients from "./pages/trainer/TrainerClients";
import TrainerProgress from "./pages/trainer/TrainerProgress";
import AssignWorkouts from "./pages/trainer/AssignWorkouts";
import AssignMeals from "./pages/trainer/AssignMeals";
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminUsers from "./pages/admin/AdminUsers";
import AdminTrainers from "./pages/admin/AdminTrainers";
import AdminAnalytics from "./pages/admin/AdminAnalytics";
import AdminRevenue from "./pages/admin/AdminRevenue";
import NotFound from "./pages/NotFound";
import LiveWorkout from "@/pages/live-workout/LiveWorkout";
import Exercises from "@/pages/exercises/Exercises";
import Progress from "@/pages/progress/Progress";
import MealPlanner from "@/pages/meal-planner/MealPlanner";
import AICoach from "@/pages/ai-coach/AICoach";
import Achievements from "@/pages/achievements/Achievements";

const queryClient = new QueryClient();

const WithLayout = ({ children }: { children: React.ReactNode }) => (
  <AppLayout>{children}</AppLayout>
);

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          {/* Auth */}
          <Route path="/" element={<Login />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/role-select" element={<RoleSelection />} />

          {/* User */}
          <Route path="/dashboard" element={<WithLayout><Dashboard /></WithLayout>} />
          <Route path="/live-workout" element={<WithLayout><LiveWorkout /></WithLayout>} />
          <Route path="/exercises" element={<WithLayout><Exercises /></WithLayout>} />
          <Route path="/progress" element={<WithLayout><Progress /></WithLayout>} />
          <Route path="/meal-planner" element={<WithLayout><MealPlanner /></WithLayout>} />
          <Route path="/ai-coach" element={<WithLayout><AICoach /></WithLayout>} />
          <Route path="/achievements" element={<WithLayout><Achievements /></WithLayout>} />
          <Route path="/premium" element={<WithLayout><Premium /></WithLayout>} />
          <Route path="/settings" element={<WithLayout><ProfileSettings /></WithLayout>} />

          {/* Trainer */}
          <Route path="/trainer/clients" element={<WithLayout><TrainerClients /></WithLayout>} />
          <Route path="/trainer/progress" element={<WithLayout><TrainerProgress /></WithLayout>} />
          <Route path="/trainer/assign-workouts" element={<WithLayout><AssignWorkouts /></WithLayout>} />
          <Route path="/trainer/assign-meals" element={<WithLayout><AssignMeals /></WithLayout>} />

          {/* Admin */}
          <Route path="/admin/dashboard" element={<WithLayout><AdminDashboard /></WithLayout>} />
          <Route path="/admin/users" element={<WithLayout><AdminUsers /></WithLayout>} />
          <Route path="/admin/trainers" element={<WithLayout><AdminTrainers /></WithLayout>} />
          <Route path="/admin/analytics" element={<WithLayout><AdminAnalytics /></WithLayout>} />
          <Route path="/admin/revenue" element={<WithLayout><AdminRevenue /></WithLayout>} />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
