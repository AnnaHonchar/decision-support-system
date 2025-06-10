import React, { useState } from "react";
import axios from "axios";

const LoginPage = () => {
  const [form, setForm] = useState({ email: "", password: "" });
  const [message, setMessage] = useState("");

  const handleLogin = async () => {
    try {
      const res = await axios.post("http://localhost:5000/api/login", form);
      localStorage.setItem("userId", res.data.user_id);
      setMessage("Успішний вхід");
      window.location.href = "/"; // Перенаправлення після входу
    } catch (err) {
      setMessage("Помилка входу");
    }
  };

  return (
    <div className="max-w-md mx-auto px-4 py-10">
      <h2 className="text-2xl font-semibold mb-6 text-center">Вхід до системи</h2>

      <div className="space-y-4">
        <input
          type="email"
          placeholder="Email"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
          className="w-full border px-4 py-2 rounded"
        />
        <input
          type="password"
          placeholder="Пароль"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
          className="w-full border px-4 py-2 rounded"
        />
        <button
          onClick={handleLogin}
          className="bg-blue-600 text-white w-full py-2 rounded shadow"
        >
          Увійти
        </button>
      </div>

      {message && (
        <p className="mt-4 text-center text-sm text-gray-700">{message}</p>
      )}
    </div>
  );
};

export default LoginPage;
