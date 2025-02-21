import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_URL } from '@/constants';
import authService from './authService';
import { Category } from '../types/category';

// Interfaces
export interface ApiResponse<T> {
    success: boolean;
    data: T | null;
    error: string | null;
}

export interface UserProfile {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    profile: {
        profile_image: string | null;
        phone: string | null;
        birth_date: string | null;
        role: string;
        first_name: string;
        last_name: string;
        email: string;
        username: string;
    };
}

// API Client Class
class ApiClient {
    private baseUrl: string;
    private prevcadPrefix: string;
    private lastTokenValidation: number = 0;
    private tokenValidationInterval: number = 300000; // 5 minutos
    private tokenRefreshThreshold: number = 60000; // 1 minuto antes de expirar

    constructor() {
        this.baseUrl = API_URL;
        this.prevcadPrefix = '/prevcad';
        this.initializeTokenRefresh();
    }

    private async initializeTokenRefresh() {
        // Verificar token al iniciar
        await this.validateAndRefreshToken();

        // Configurar intervalo de verificación
        setInterval(async () => {
            await this.validateAndRefreshToken();
        }, this.tokenValidationInterval);
    }

    private async validateAndRefreshToken(): Promise<boolean> {
        try {
            const token = await AsyncStorage.getItem('auth_token');
            if (!token) return false;

            const tokenData = this.parseJwt(token);
            if (!tokenData) return false;

            // Verificar si el token expirará pronto
            const expirationTime = tokenData.exp * 1000; // Convertir a milisegundos
            const currentTime = Date.now();

            if (expirationTime - currentTime < this.tokenRefreshThreshold) {
                const refreshToken = await AsyncStorage.getItem('refresh_token');
                if (!refreshToken) return false;

                const newToken = await authService.refreshToken(refreshToken);
                return !!newToken;
            }

            return true;
        } catch (error) {
            console.error('Error validating token:', error);
            return false;
        }
    }

    private parseJwt(token: string) {
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(atob(base64).split('').map(c =>
                '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
            ).join(''));
            return JSON.parse(jsonPayload);
        } catch (error) {
            console.error('Error parsing JWT:', error);
            return null;
        }
    }

    public async getHeaders(includeAuth: boolean = true): Promise<HeadersInit> {
        const headers: HeadersInit = {
            'Content-Type': 'application/json',
        };

        if (includeAuth) {
            const token = await AsyncStorage.getItem('auth_token');
            if (!token) {
                throw new Error('No auth token found');
            }

            // Solo validar si es necesario
            if (Date.now() - this.lastTokenValidation > this.tokenValidationInterval) {
                const isValid = await this.validateAndRefreshToken();
                if (!isValid) {
                    await authService.logout();
                    throw new Error('Session expired');
                }
                this.lastTokenValidation = Date.now();
            }

            headers['Authorization'] = `Bearer ${token}`;
        }

        return headers;
    }

    private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
        if (response.status === 401) {
            const token = await AsyncStorage.getItem('auth_token');
            const refreshToken = await AsyncStorage.getItem('refresh_token');

            if (token && refreshToken) {
                // Intentar validar el token actual primero
                const isValid = await authService.validateToken(token);
                if (!isValid) {
                    // Si no es válido, intentar refrescar
                    const newToken = await authService.refreshToken(refreshToken);
                    if (newToken) {
                        // Reintentar la petición original con el nuevo token
                        const newResponse = await fetch(
                            response.url,
                            {
                                ...response,
                                headers: {
                                    ...response.headers,
                                    'Authorization': `Bearer ${newToken}`
                                }
                            }
                        );
                        return this.handleResponse(newResponse);
                    }
                }
            }

            // Si no se pudo recuperar la sesión, hacer logout
            await authService.logout();
            throw new Error('Session expired');
        }

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        return {
            success: true,
            data,
            error: data.message,
        };
    }

    private getUrl(endpoint: string, usePrevcadPrefix: boolean = true): string {
        return `${this.baseUrl}${usePrevcadPrefix ? this.prevcadPrefix : ''}${endpoint}`;
    }

    // Health Categories
    public categories = {
        create: async (templateId: number): Promise<ApiResponse<Category>> => {
            const response = await fetch(
                this.getUrl('/health-categories/create'),
                {
                    method: 'POST',
                    headers: await this.getHeaders(true),
                    body: JSON.stringify({ template_id: templateId }),
                }
            );
            return this.handleResponse<Category>(response);
        },

        saveResponses: async (categoryId: number, formData: FormData): Promise<ApiResponse<any>> => {
            try {
                const response = await fetch(
                    this.getUrl(`/health-categories/${categoryId}/responses/`),
                    {
                        method: 'POST',
                        body: formData,
                        headers: await this.getHeaders(true),
                    });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                return await response.json();
            } catch (error) {
                console.error('Error in saveResponses:', error);
                throw error;
            }
        },

        getAll: async (): Promise<ApiResponse<Category[]>> => {
            try {
                const token = await AsyncStorage.getItem('auth_token');
                if (!token) {
                    throw new Error('No auth token found');
                }

                const response = await fetch(
                    this.getUrl('/health_categories/'),
                    {
                        headers: await this.getHeaders(true),
                    }
                );
                return this.handleResponse<Category[]>(response);
            } catch (error) {
                console.error('Error fetching categories:', error);
                throw error;
            }
        },

        getById: async (id: number): Promise<ApiResponse<Category>> => {
            const response = await fetch(
                this.getUrl(`/health_categories/${id}`),
                {
                    headers: await this.getHeaders(true),
                }
            );
            return this.handleResponse<Category>(response);
        },
    };

    // User Management
    public user = {
        getProfile: async (): Promise<ApiResponse<UserProfile>> => {
            try {
                const token = await AsyncStorage.getItem('auth_token');
                const url = this.getUrl('/api/prevcad/user/profile/');
                
                const headers = {
                    'Accept': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                };
                
                const response = await fetch(url, { headers });
                const data = await response.json();
                
                if (response.ok) {
                    return {
                        success: true,
                        data: data as UserProfile,
                        error: null
                    };
                } else {
                    return {
                        success: false,
                        data: null,
                        error: data.detail || 'Error desconocido'
                    };
                }
            } catch (error) {
                console.error('Error en getProfile:', error);
                return {
                    success: false,
                    data: null,
                    error: error instanceof Error ? error.message : 'Error desconocido'
                };
            }
        },

        updateProfile: async (data: Partial<UserProfile>): Promise<ApiResponse<UserProfile>> => {
            const response = await fetch(
                this.getUrl('/user/profile'),
                {
                    method: 'PUT',
                    headers: await this.getHeaders(),
                    body: JSON.stringify(data),
                }
            );
            return this.handleResponse<UserProfile>(response);
        },

        uploadProfileImage: async (imageUri: string): Promise<ApiResponse<UserProfile>> => {
            try {
                console.log("Starting image upload...");

                const formData = new FormData();

                // Obtener el nombre del archivo y su extensión
                const filename = imageUri.split('/').pop() || 'profile-image.jpg';
                const match = /\.(\w+)$/.exec(filename);
                const type = match ? `image/${match[1]}` : 'image/jpeg';

                // Agregar la imagen al FormData con la estructura correcta
                formData.append('profile_image', {
                    uri: imageUri,
                    type,
                    name: filename,
                } as any);

                const token = await AsyncStorage.getItem('auth_token');
                if (!token) {
                    throw new Error('No auth token found');
                }

                // Usar la ruta específica para subir imágenes
                const response = await fetch(
                    this.getUrl('/user/profile/upload_image/'),  // Ruta actualizada
                    {
                        method: 'POST',  // Cambiado a POST para coincidir con el backend
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Accept': 'application/json',
                        },
                        body: formData,
                    }
                );

                console.log('Upload response status:', response.status);

                if (!response.ok) {
                    const errorData = await response.json();
                    console.error('Upload error:', errorData);
                    throw new Error(errorData.detail || 'Error uploading image');
                }

                return this.handleResponse<UserProfile>(response);
            } catch (error) {
                console.error("Error uploading image:", error);
                throw error;
            }
        },

        deleteProfileImage: async (): Promise<ApiResponse<UserProfile>> => {
            const response = await fetch(
                this.getUrl('/user/profile/delete_image/'),
                {
                    method: 'DELETE',
                    headers: await this.getHeaders(),
                }
            );
            return this.handleResponse<UserProfile>(response);
        },
    };

    public recommendations = {
        getAll: async (): Promise<ApiResponse<any>> => {
            try {
                const token = await AsyncStorage.getItem('auth_token');
                if (!token) {
                    throw new Error('No auth token found');
                }

                const response = await fetch(
                    this.getUrl('/text_recommendations/'),
                    {
                        headers: await this.getHeaders(),
                    }
                );
                return this.handleResponse(response);
            } catch (error) {
                console.error('Error fetching recommendations:', error);
                throw error;
            }
        },
        registerClick: async (recommendationId: number): Promise<ApiResponse<any>> => {
            const response = await fetch(
                this.getUrl(`/text_recommendations/${recommendationId}/register_click`),
                {
                    method: 'POST',
                    headers: {
                        ...(await this.getHeaders()),
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                    },
                }
            );

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Error Response:', {
                    status: response.status,
                    statusText: response.statusText,
                    body: errorText
                });
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        }
    };

    public events = {
        getAll: async (): Promise<ApiResponse<any>> => {
            const response = await fetch(
                this.getUrl('/appointments/'),
                {
                    headers: await this.getHeaders(),
                }
            );
            return this.handleResponse(response);
        }
    }
}

export const apiService = new ApiClient();
export default apiService; 