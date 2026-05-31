# UNEFA — Sistema de deteccion de uniforme 
## Frontend Login (XD borren java)
---
##  Estructura del Proyecto
```
unefa-login/
│
├── index.html              ← Página principal (Login / Registro / Recuperar)
│
├── css/
│   ├── style.css           ← Estilos principales, variables, layout
│   └── animations.css      ← Keyframes y efectos de animación
│
├── js/
│   ├── utils.js            ← Funciones reutilizables (toast, loading, etc.)
│   ├── validation.js       ← Reglas de validación de formularios
│   ├── ui.js               ← Navegación entre vistas, comportamiento UI
│   └── app.js              ← Punto de entrada principal, event bindings
│
└── assets/
    └── images/
        └── escudo.png   
```
##  Integración con Backend - Pa los de backend ps XD

En `js/app.js` cada acción usa `fakeDelay()` para simular la red.
Reemplaza esas llamadas con `fetch()` a tu API real:

```js
// Ejemplo login real:
const res  = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ cedula, password }),
});
const data = await res.json();

if (data.token) {
  localStorage.setItem('token', data.token);
  window.location.href = '/dashboard';
} else {
  showToast(data.message || 'Credenciales incorrectas.', 'error');
}

