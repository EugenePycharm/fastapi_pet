import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import apiClient from '../api/client';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth должен использоваться внутри AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const userData = await apiClient.getMe();
          setUser(userData);
        } catch (err) {
          apiClient.clearToken();
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const register = useCallback(async (email, password) => {
    setError(null);
    try {
      await apiClient.register(email, password);
      // После регистрации сразу логинимся
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      await apiClient.login(email, password);
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    }
  }, []);

  const login = useCallback(async (email, password) => {
    setError(null);
    try {
      await apiClient.login(email, password);
      const userData = await apiClient.getMe();
      setUser(userData);
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    }
  }, []);

  const logout = useCallback(async () => {
    await apiClient.logout();
    setUser(null);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const value = {
    user,
    loading,
    error,
    isAuthenticated: !!user,
    register,
    login,
    logout,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
