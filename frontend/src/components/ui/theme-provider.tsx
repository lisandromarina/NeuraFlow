import { createContext, useContext, useState, useEffect } from 'react';

const initialState: ThemeProviderState = {
  theme: { mode: 'dark', color: 'yellow' },
  setTheme: () => null
};

const ThemeProviderContext = createContext<ThemeProviderState>(initialState);

export function ThemeProvider({
  children,
  defaultTheme = { mode: 'dark', color: 'yellow' },
  storageKey = 'distort-ui-theme',
  ...props
}: ThemeProviderProps) {
  const [storedTheme, setStoredTheme] = useState<Theme>(() => {
    // Try to load from localStorage
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        try {
          return JSON.parse(saved);
        } catch {
          console.warn('Invalid theme data in localStorage, using default');
        }
      }
    }
    // Fallback to default
    return defaultTheme;
  });

  // Save theme to localStorage whenever it changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(storageKey, JSON.stringify(storedTheme));
    }
  }, [storedTheme, storageKey]);

  useEffect(() => {
    const root = document.documentElement;

    if (storedTheme.mode === 'system') {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.classList.toggle('dark', isDark);
    } else {
      root.classList.toggle('dark', storedTheme.mode === 'dark');
    }
  }, [storedTheme.mode]);

  const value = {
    theme: storedTheme,
    setTheme: (theme: Theme) => {
      setStoredTheme(theme);
    }
  };

  const resolvedMode =
    storedTheme.mode === 'system'
      ? window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light'
      : storedTheme.mode;

  return (
    <ThemeProviderContext.Provider {...props} value={value}>
      <div
        className={resolvedMode}
        data-theme={`${storedTheme.color}-${resolvedMode}`}
      >
        {children}
      </div>
    </ThemeProviderContext.Provider>
  );
}

/**
 * Hook to get and set new theme throughout application
 */
export const useTheme = () => {
  const context = useContext(ThemeProviderContext);

  if (context === undefined)
    throw new Error('useTheme must be used within a ThemeProvider');

  return context;
};
