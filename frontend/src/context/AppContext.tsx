"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";

export interface Restaurant {
  name: string;
  cuisine: string;
  rating: number | null;
  approx_cost: number;
  location: string;
  ai_explanation: string;
}

export interface Preferences {
  location: string;
  min_budget: number;
  max_budget: number;
  cuisine: string;
  min_rating: number;
  additional_preferences: string;
}

interface AppContextType {
  preferences: Preferences;
  setPreferences: React.Dispatch<React.SetStateAction<Preferences>>;
  recommendations: Restaurant[];
  setRecommendations: (recs: Restaurant[]) => void;
  loading: boolean;
  setLoading: (l: boolean) => void;
  error: string;
  setError: (e: string) => void;
}

const defaultPreferences: Preferences = {
  location: "Whitefield",
  min_budget: 200,
  max_budget: 1000,
  cuisine: "",
  min_rating: 3.5,
  additional_preferences: "",
};

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [preferences, setPreferences] = useState<Preferences>(defaultPreferences);
  const [recommendations, setRecommendationsState] = useState<Restaurant[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");

  const setRecommendations = (recs: Restaurant[]) => {
    setRecommendationsState(recs);
  };

  return (
    <AppContext.Provider
      value={{
        preferences,
        setPreferences,
        recommendations,
        setRecommendations,
        loading,
        setLoading,
        error,
        setError,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error("useApp must be used within an AppProvider");
  }
  return context;
}
