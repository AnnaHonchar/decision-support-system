import React, { useState, useEffect } from "react";
import axios from "axios";

const ProfilePage = () => {
  const userId = localStorage.getItem("userId");
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: ""
  });
  const [message, setMessage] = useState("");

  useEffect(() => {
    const fetchUser = async () => {
      const res = await axios.get(`http://localhost:5000/api/profile/${userId}`);
      setFormData({
        username: res.data.username,
        email: res.data.email,
        password: "",
        confirmPassword: ""
      });
    };

    fetchUser();
  }, [userId]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSave = async () => {
    if (formData.password && formData.password !== formData.confirmPassword) {
      alert("Паролі не співпадають");
      return;
    }

    try {
      const res = await axios.put(`http://localhost:5000/api/profile/${userId}`, {
        username: formData.username,
        email: formData.email,
        password: formData.password || undefined,
      });
      setMessage(res.data.message);
    } catch (err) {
      alert(err.response?.data?.error || "Помилка оновлення профілю");
    }
  };

  return (
    <div className="max-w-md mx-auto px-4 py-10">
      <h2 className="text-2xl font-semibold mb-6 text-center">Редагування профілю</h2>

      <div className="space-y-4">
        <input
          name="username"
          placeholder="Ім’я користувача"
          value={formData.username}
          onChange={handleChange}
          className="w-full border px-4 py-2 rounded"
        />
        <input
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleChange}
          className="w-full border px-4 py-2 rounded"
        />
        <input
          name="password"
          placeholder="Новий пароль"
          type="password"
          value={formData.password}
          onChange={handleChange}
          className="w-full border px-4 py-2 rounded"
        />
        <input
          name="confirmPassword"
          placeholder="Підтвердіть пароль"
          type="password"
          value={formData.confirmPassword}
          onChange={handleChange}
          className="w-full border px-4 py-2 rounded"
        />
        <button
          onClick={handleSave}
          className="bg-blue-600 text-white w-full py-2 rounded shadow"
        >
          Зберегти зміни
        </button>
      </div>

      {message && (
        <p className="mt-4 text-center text-green-600">{message}</p>
      )}
    </div>
  );
};

export default ProfilePage;
