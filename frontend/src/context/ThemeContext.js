import React, { createContext, useState, useContext, useEffect, useMemo } from 'react';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import { lightTheme, darkTheme } from '../theme/theme';

const ThemeContext = createContext(null);

export const useThemeMode = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useThemeMode должен использоваться внутри ThemeContextProvider');
  }
  return context;
};

export const ThemeContextProvider = ({ children }) => {
  // Проверяем сохранённую тему или используем тёмную по умолчанию
  const [mode, setMode] = useState(() => {
    const savedTheme = localStorage.getItem('theme');
    return savedTheme || 'dark'; // Тёмная тема по умолчанию
  });

  // Сохраняем тему при изменении
  useEffect(() => {
    localStorage.setItem('theme', mode);
  }, [mode]);

  const toggleTheme = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  // Выбираем тему на основе режима
  const theme = useMemo(() => (mode === 'light' ? lightTheme : darkTheme), [mode]);

  const value = {
    mode,
    isDark: mode === 'dark',
    toggleTheme,
    setMode,
  };

  return (
    <ThemeContext.Provider value={value}>
      <MuiThemeProvider theme={theme}>{children}</MuiThemeProvider>
    </ThemeContext.Provider>
  );
};
