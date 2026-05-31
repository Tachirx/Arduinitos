const API_URL = "http://localhost:8000/auth";

export const authService = {
  login: async (cedula, password) => {
    try {
      const formData = new URLSearchParams();
      formData.append("username", cedula);
      formData.append("password", password);

      const response = await fetch(`${API_URL}/iniciar_sesion`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Error al iniciar sesión");
      }
      return data; // { access_token, token_type }
    } catch (error) {
      throw error;
    }
  },

  register: async (userData) => {
    try {
      const response = await fetch(`${API_URL}/registrar`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(userData),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Error al registrar usuario");
      }
      return data;
    } catch (error) {
      throw error;
    }
  },

  getPreguntas: async (cedula) => {
    try {
      const response = await fetch(`${API_URL}/preguntas/${cedula}`, {
        method: "GET",
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Error al obtener preguntas");
      }
      return data;
    } catch (error) {
      throw error;
    }
  },

  recuperarClave: async (cedula, respuestas, nueva_clave) => {
    try {
      const response = await fetch(`${API_URL}/recuperar_clave`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ cedula, respuestas, nueva_clave }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Error al recuperar clave");
      }
      return data;
    } catch (error) {
      throw error;
    }
  },
};
