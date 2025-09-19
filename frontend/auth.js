const API_BASE = "https://scuba-dives.onrender.com"; 

const tabLogin = document.getElementById("tab-login");
const tabRegister = document.getElementById("tab-register");
const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const loginMsg = document.getElementById("login-msg");
const registerMsg = document.getElementById("register-msg");

tabLogin.addEventListener("click", () => {
  tabLogin.classList.add("active");
  tabRegister.classList.remove("active");
  loginForm.classList.add("active");
  registerForm.classList.remove("active");
  loginMsg.textContent = "";
  registerMsg.textContent = "";
});

tabRegister.addEventListener("click", () => {
  tabRegister.classList.add("active");
  tabLogin.classList.remove("active");
  registerForm.classList.add("active");
  loginForm.classList.remove("active");
  loginMsg.textContent = "";
  registerMsg.textContent = "";
});

(async function checkAlreadyLogin() {
  try {
    const me = await fetch(API_BASE + "/auth/me", { credentials: "include" });
    if (me.ok) {
      window.location.href = "./index.html";
    }
  } catch {}
})();

registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  registerMsg.textContent = "";
  registerMsg.className = "msg";
  const email = document.getElementById("register-email").value.trim();
  const password = document.getElementById("register-password").value.trim();
  if (!email || !password) {
    registerMsg.textContent = "Please enter email and password";
    registerMsg.classList.add("err");
    return;
  }
  try {
    const res = await fetch(API_BASE + "/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
      credentials: "include",
    });
    const data = await res.json();
    if (!res.ok) {
      registerMsg.textContent = data?.detail || "Registration failed";
      registerMsg.classList.add("err");
      return;
    }
    registerMsg.textContent = "Registration successful, please switch to login";
    registerMsg.classList.add("ok");
  } catch (err) {
    registerMsg.textContent = "Network error";
    registerMsg.classList.add("err");
  }
});

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  loginMsg.textContent = "";
  loginMsg.className = "msg";
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value.trim();
  if (!email || !password) {
    loginMsg.textContent = "Please enter email and password";
    loginMsg.classList.add("err");
    return;
  }
  try {
    const res = await fetch(API_BASE + "/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
      credentials: "include",
    });
    const data = await res.json();
    if (!res.ok) {
      loginMsg.textContent = data?.detail || "Login failed";
      loginMsg.classList.add("err");
      return;
    }
    window.location.href = "./index.html";
  } catch (err) {
    loginMsg.textContent = "Network error";
    loginMsg.classList.add("err");
  }
});
