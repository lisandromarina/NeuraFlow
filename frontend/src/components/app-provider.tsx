import { createContext, useState, type ReactNode } from "react";

interface User {
  id: string;
  name: string;
}

interface AppContextType {
  user: User | null;
  setUser: (user: User) => void;
}

export const AppContext = createContext<AppContextType>({
  user: null,
  setUser: () => {},
});

interface AppProviderProps {
  children: ReactNode;
  initialUser?: User; // optional initial user
}

export const AppProvider: React.FC<AppProviderProps> = ({ children, initialUser }) => {
  const [user, setUser] = useState<User | null>(initialUser || null);

  return (
    <AppContext.Provider value={{ user, setUser }}>
      {children}
    </AppContext.Provider>
  );
};
