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
    registerMsg.textContent = "请输入邮箱与密码";
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
      registerMsg.textContent = data?.detail || "注册失败";
      registerMsg.classList.add("err");
      return;
    }
    registerMsg.textContent = "注册成功，请切换到登录";
    registerMsg.classList.add("ok");
  } catch (err) {
    registerMsg.textContent = "网络错误";
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
    loginMsg.textContent = "请输入邮箱与密码";
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
      loginMsg.textContent = data?.detail || "登录失败";
      loginMsg.classList.add("err");
      return;
    }
    window.location.href = "./index.html";
  } catch (err) {
    loginMsg.textContent = "网络错误";
    loginMsg.classList.add("err");
  }
});
