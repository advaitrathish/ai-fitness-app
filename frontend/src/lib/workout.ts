import API from "./apis";

export const logWorkout = async (data: {
  exercise_name: string;
  reps: number;
  duration_minutes: number;
}) => {
  const response = await API.post("log-workout/", data);
  return response.data;
};