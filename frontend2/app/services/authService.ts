import { API_URL } from '@/constants';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiService } from './apiService';

export interface AuthResponse {
  user: {
    id: number;
    username: string;
    email: string;
  };
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      console.log('Environment:', __DEV__ ? 'Development' : 'Production');
      console.log('Login attempt to:', `${API_URL}/token/`);
      
      const response = await fetch(`${API_URL}/token/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      console.log('Response status:', response.status);
      const data = await response.json();
      console.log("Datos de autenticación:", data);

      if (!response.ok) {
        console.error("Error de autenticación:", data);
        throw new Error(data.detail || 'Error en la autenticación');
      }

      if (!data.access) {
        throw new Error('Token de acceso no recibido');
      }

      return data;
    } catch (error) {
      console.error('Error en login:', error);
      throw error;
    }
  },

  async getUserInfo(token: string) {
    try {
      const response = await apiService.user.getProfile();
      return response.data;
    } catch (error) {
      console.error('Error getting user info:', error);
      throw error;
    }
  },

  async validateToken(token: string): Promise<boolean> {
    try {
      const response = await fetch(`${API_URL}/token/verify/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });

      if (!response.ok) {
        // Si el token no es válido, intentar refrescarlo automáticamente
        const refreshToken = await AsyncStorage.getItem('refresh_token');
        if (refreshToken) {
          const newToken = await authService.refreshToken(refreshToken);
          return newToken !== null;
        }
        return false;
      }

      return true;
    } catch {
      return false;
    }
  },

  async refreshToken(refreshToken: string): Promise<string | null> {
    try {
        console.log('Intentando refrescar token con:', refreshToken.substring(0, 20) + '...');
        
        const response = await fetch(`${API_URL}/token/refresh/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken }),
        });

        console.log('Refresh response status:', response.status);
        const data = await response.json();
        console.log('Refresh response data:', data);

        if (!response.ok) {
            console.error('Error refreshing token:', data);
            await this.logout();
            return null;
        }

        // Guardar tanto el nuevo access token como el refresh token
        await AsyncStorage.setItem('auth_token', data.access);
        if (data.refresh) {
            await AsyncStorage.setItem('refresh_token', data.refresh);
        }

        return data.access;
    } catch (error) {
        console.error('Error en refreshToken:', error);
        await this.logout();
        return null;
    }
  },

  async logout(): Promise<void> {
    try {
      await AsyncStorage.removeItem('auth_token');
      await AsyncStorage.removeItem('refresh_token');
    } catch (error) {
      console.error('Error during logout:', error);
      throw error;
    }
  },
};

export default authService; 