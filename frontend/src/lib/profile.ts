import API from "./apis";

export const fetchProfile = async () => {
  const response = await API.get("profile/");
  return response.data;
};

export const fetchLeaderboard = async () => {
  const response = await API.get("leaderboard/");
  return response.data;
};