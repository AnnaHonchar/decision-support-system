import React, { useState } from "react";
import axios from "axios";

const ResultPage = () => {
  if (!localStorage.getItem("userId")) {
    window.location.href = "/login";
  }

  const [userId, setUserId] = useState("");
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");

  const fetchResults = async () => {
    try {
      const res = await axios.get("http://localhost:5000/api/history", {
        params: { user_id: userId },
      });
      setResults(res.data);
      setError("");
    } catch (err) {
      setError("Не вдалося отримати результати.");
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-6">
      <h2 className="text-2xl font-semibold mb-4">Результати аналізу</h2>
      <div className="flex gap-4 mb-4">
        <input
          type="text"
          placeholder="User ID"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          className="border px-3 py-2 rounded w-full"
        />
        <button
          onClick={fetchResults}
          className="bg-blue-600 text-white px-4 py-2 rounded shadow"
        >
          Отримати результати
        </button>
      </div>

      {error && <p className="text-red-600 mb-4">{error}</p>}

      <ul className="space-y-4">
        {results.map((res, index) => (
          <li
            key={index}
            className="border rounded p-4 shadow-sm bg-white"
          >
            <p><strong>Файл:</strong> {res.filename}</p>
            <p><strong>Метод:</strong> {res.method === "topsis" ? "TOPSIS" : res.method === "classification" ? "Класифікація" : "Прогноз"}</p>
            <p><strong>Дата аналізу:</strong> {res.uploaded_at}</p>
            <p><strong>Рекомендація:</strong> {res.recommendation}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ResultPage;
