import React, { useState } from "react";
import axios from "axios";

const RegisterPage = () => {
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [message, setMessage] = useState("");

  const handleRegister = async () => {
    try {
      await axios.post("http://localhost:5000/api/register", form);
      setMessage("Успішно зареєстровано!");
    } catch (err) {
      setMessage("Помилка реєстрації");
    }
  };

  return (
    <div className="max-w-md mx-auto px-4 py-10">
      <h2 className="text-2xl font-semibold mb-6 text-center">Реєстрація</h2>

      <div className="space-y-4">
        <input
          type="text"
          placeholder="Ім'я"
          value={form.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })}
          className="w-full border px-4 py-2 rounded"
        />
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
          onClick={handleRegister}
          className="bg-green-600 text-white w-full py-2 rounded shadow"
        >
          Зареєструватися
        </button>
      </div>

      {message && (
        <p className="mt-4 text-center text-blue-700 font-medium">{message}</p>
      )}
    </div>
  );
};

export default RegisterPage;
