import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('smartcart_user');
    return saved ? JSON.parse(saved) : null;
  });

  const login = async (email, password) => {
    const res = await api.post('auth/login/', { email, password });
    const data = res.data.data || res.data;
    localStorage.setItem('smartcart_access', data.access);
    localStorage.setItem('smartcart_refresh', data.refresh);
    localStorage.setItem('smartcart_user', JSON.stringify(data.user));
    setUser(data.user);
    return data.user;
  };

  const register = async (userData) => {
    const res = await api.post('auth/register/', userData);
    const data = res.data.data || res.data;
    localStorage.setItem('smartcart_access', data.access);
    localStorage.setItem('smartcart_refresh', data.refresh);
    localStorage.setItem('smartcart_user', JSON.stringify(data.user));
    setUser(data.user);
    return data.user;
  };

  const logout = async () => {
    try {
      const refresh = localStorage.getItem('smartcart_refresh');
      if (refresh) {
        await api.post('auth/logout/', { refresh });
      }
    } catch (e) {
      // Ignore network errors on logout
    } finally {
      localStorage.removeItem('smartcart_access');
      localStorage.removeItem('smartcart_refresh');
      localStorage.removeItem('smartcart_user');
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{ user, setUser, login, register, logout, isAdmin: user?.is_admin }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
