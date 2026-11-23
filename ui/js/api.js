const REQUEST_TIMEOUT_MS = 8000;
const STARTING_MESSAGE = "El servicio está iniciando. Inténtalo de nuevo en unos minutos.";

function getToken() {
    return localStorage.getItem("token");
}

function saveSession(token, vendor) {
    localStorage.setItem("token", token);
    localStorage.setItem("vendor", JSON.stringify(vendor));
}

function getVendor() {
    return JSON.parse(localStorage.getItem("vendor") || "null");
}

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("vendor");
    sessionStorage.clear();
    window.location.href = "index.html";
}

function requireLogin() {
    if (!getToken()) {
        window.location.href = "index.html";
    }
}


async function apiRequest(baseUrl, path, options = {}) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    const headers = { "Content-Type": "application/json" };
    const token = getToken();
    if (token) {
        headers["Authorization"] = "Bearer " + token;
    }

    let response;
    try {
        response = await fetch(baseUrl + path, {
            method: options.method || "GET",
            headers: headers,
            body: options.body ? JSON.stringify(options.body) : undefined,
            signal: controller.signal,
        });
    } catch (error) {
        // Se acabó el tiempo: casi siempre es un cold start en Azure.
        if (error.name === "AbortError") {
            throw new Error(STARTING_MESSAGE);
        }
        // El servicio está apagado, o Azure respondió su propio 503 mientras arranca:
        // esa respuesta no trae cabeceras CORS, así que el navegador la bloquea y llega aquí.
        throw new Error(options.unavailableMessage || "El servicio no está disponible. Inténtalo de nuevo en unos minutos.");
    } finally {
        clearTimeout(timer);
    }

    if (response.status === 401 && path !== "/login") {
        logout();
        throw new Error("Tu sesión expiró. Vuelve a iniciar sesión.");
    }

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        if (data.error) {
            throw new Error(data.error);
        }
        // 502/503/504 sin JSON de mi app: es Azure respondiendo mientras el contenedor arranca.
        if ([502, 503, 504].includes(response.status)) {
            throw new Error(STARTING_MESSAGE);
        }
        throw new Error("Error inesperado (" + response.status + ").");
    }
    return data;
}

function salesApi(path, options = {}) {
    return apiRequest(window.APP_CONFIG.SALES_URL, path, {
        unavailableMessage: "El servicio de ventas no está disponible. Inténtalo de nuevo en unos minutos.",
        ...options,
    });
}

function catalogApi(path, options = {}) {
    return apiRequest(window.APP_CONFIG.CATALOG_URL, path, {
        unavailableMessage: "El catálogo no está disponible en este momento. Inténtalo de nuevo en unos minutos.",
        ...options,
    });
}


// ---------- Cliente elegido y carrito (viven en el navegador) ----------

function getClient() {
    return JSON.parse(sessionStorage.getItem("client") || "null");
}

function saveClient(client) {
    sessionStorage.setItem("client", JSON.stringify(client));
}

function getCart() {
    return JSON.parse(sessionStorage.getItem("cart") || "[]");
}

function saveCart(cart) {
    sessionStorage.setItem("cart", JSON.stringify(cart));
}


// ---------- Ayudas para la página ----------

function showError(message) {
    const box = document.getElementById("error");
    box.textContent = message;
    box.style.display = "block";
}

function hideError() {
    document.getElementById("error").style.display = "none";
}

function money(value) {
    return "$" + Number(value).toFixed(2);
}

function cell(text) {
    const td = document.createElement("td");
    td.textContent = text;
    return td;
}

// Botón "Cerrar sesión" del navbar (si la página lo tiene)
document.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("logoutBtn");
    if (button) {
        button.addEventListener("click", logout);
    }
});