import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import AppLayout from "@/components/AppLayout";
import ProtectedRoute from "@/components/ProtectedRoute";

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

const ProtectedWithLayout = ({ children }: { children: React.ReactNode }) => (
  <ProtectedRoute>
    <WithLayout>{children}</WithLayout>
  </ProtectedRoute>
);

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Login />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/role-select" element={<RoleSelection />} />

          {/* User Routes (Protected) */}
          <Route path="/dashboard" element={<ProtectedWithLayout><Dashboard /></ProtectedWithLayout>} />
          <Route path="/live-workout" element={<ProtectedWithLayout><LiveWorkout /></ProtectedWithLayout>} />
          <Route path="/exercises" element={<ProtectedWithLayout><Exercises /></ProtectedWithLayout>} />
          <Route path="/progress" element={<ProtectedWithLayout><Progress /></ProtectedWithLayout>} />
          <Route path="/meal-planner" element={<ProtectedWithLayout><MealPlanner /></ProtectedWithLayout>} />
          <Route path="/ai-coach" element={<ProtectedWithLayout><AICoach /></ProtectedWithLayout>} />
          <Route path="/achievements" element={<ProtectedWithLayout><Achievements /></ProtectedWithLayout>} />
          <Route path="/premium" element={<ProtectedWithLayout><Premium /></ProtectedWithLayout>} />
          <Route path="/settings" element={<ProtectedWithLayout><ProfileSettings /></ProtectedWithLayout>} />

          {/* Trainer Routes (Protected) */}
          <Route path="/trainer/clients" element={<ProtectedWithLayout><TrainerClients /></ProtectedWithLayout>} />
          <Route path="/trainer/progress" element={<ProtectedWithLayout><TrainerProgress /></ProtectedWithLayout>} />
          <Route path="/trainer/assign-workouts" element={<ProtectedWithLayout><AssignWorkouts /></ProtectedWithLayout>} />
          <Route path="/trainer/assign-meals" element={<ProtectedWithLayout><AssignMeals /></ProtectedWithLayout>} />

          {/* Admin Routes (Protected) */}
          <Route path="/admin/dashboard" element={<ProtectedWithLayout><AdminDashboard /></ProtectedWithLayout>} />
          <Route path="/admin/users" element={<ProtectedWithLayout><AdminUsers /></ProtectedWithLayout>} />
          <Route path="/admin/trainers" element={<ProtectedWithLayout><AdminTrainers /></ProtectedWithLayout>} />
          <Route path="/admin/analytics" element={<ProtectedWithLayout><AdminAnalytics /></ProtectedWithLayout>} />
          <Route path="/admin/revenue" element={<ProtectedWithLayout><AdminRevenue /></ProtectedWithLayout>} />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;