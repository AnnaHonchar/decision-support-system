import React, { useEffect, useState } from "react";
import axios from "axios";
import ForecastChart from "./ForecastChart";

const HistoryPage = () => {
  const [history, setHistory] = useState([]);
  const [search, setSearch] = useState("");
  const [selectedDatasetId, setSelectedDatasetId] = useState(null);
  const [forecastMap, setForecastMap] = useState({});

  const fetchData = async (query = "") => {
    const userId = localStorage.getItem("userId");
    if (!userId) return;

    const res = await axios.get("http://localhost:5000/api/history", {
      params: { user_id: userId, q: query },
    });

    setHistory(res.data);
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSearchChange = (e) => {
    const q = e.target.value;
    setSearch(q);
    fetchData(q);
  };

  const handleDelete = async (datasetId) => {
    if (!window.confirm("Ви впевнені, що хочете видалити цей прогноз?")) return;

    try {
      await axios.delete(`http://localhost:5000/api/history/${datasetId}`);
      alert("Прогноз видалено!");
      fetchData(search);
    } catch (err) {
      console.error("Помилка при видаленні:", err);
      alert("Не вдалося видалити прогноз");
    }
  };

  const handleRealForecast = async (datasetId) => {
    try {
      if (selectedDatasetId === datasetId) {
        setSelectedDatasetId(null);
        return;
      }

      await axios.post(`http://localhost:5000/api/real_forecast/${datasetId}`);
      const forecastRes = await axios.get(
        `http://localhost:5000/api/forecast_results/${datasetId}`
      );

      setForecastMap((prev) => ({
        ...prev,
        [datasetId]: forecastRes.data
      }));

      setSelectedDatasetId(datasetId);
      alert("Реальний прогноз створено!");
    } catch (error) {
      console.error("Помилка при побудові прогнозу", error);
      alert("Не вдалося побудувати прогноз");
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      <h2 className="text-2xl font-semibold mb-4">Історія прогнозів</h2>

      <input
        type="text"
        value={search}
        onChange={handleSearchChange}
        placeholder="Пошук за назвою або рекомендацією..."
        className="border px-3 py-2 rounded w-full mb-6"
      />

      {history.length === 0 ? (
        <p>Нічого не знайдено</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="border px-2 py-1">Файл</th>
                <th className="border px-2 py-1">Дата</th>
                <th className="border px-2 py-1">Рекомендація</th>
                <th className="border px-2 py-1">Дії</th>
              </tr>
            </thead>
            <tbody>
              {history.map((entry, idx) => (
                <React.Fragment key={idx}>
                  <tr>
                    <td className="border px-2 py-1">{entry.filename}</td>
                    <td className="border px-2 py-1">
                      {entry.uploaded_at}
                      <br />
                      <small className="text-gray-500">
                        Метод: {
                          entry.method === "topsis"
                            ? "TOPSIS"
                            : entry.method === "classification"
                            ? "Класифікація"
                            : "Прогноз"
                        }
                      </small>
                    </td>
                    <td className="border px-2 py-1">{entry.recommendation || "—"}</td>
                    <td className="space-y-2 border px-2 py-1">
  <button
    onClick={() => handleDelete(entry.dataset_id)}
    className="bg-red-600 text-white px-4 py-1 rounded hover:bg-red-700 w-full"
  >
    Видалити
  </button>

  <div className="flex flex-wrap gap-2">
    <a
      href={`http://localhost:5000/api/export/${entry.dataset_id}?format=pdf`}
      target="_blank"
      rel="noopener noreferrer"
      className="text-blue-600 underline hover:text-blue-800"
    >
      PDF
    </a>

    {entry.method !== "topsis" && (
      <a
        href={`http://localhost:5000/api/export/${entry.dataset_id}?format=excel`}
        target="_blank"
        rel="noopener noreferrer"
        className="text-blue-600 underline hover:text-blue-800"
      >
        Excel
      </a>
    )}
  </div>

  {entry.method === "prophet" && (
    <button
      onClick={() => handleRealForecast(entry.dataset_id)}
      className="bg-indigo-600 text-white px-3 py-1 rounded hover:bg-indigo-700 w-full flex items-center justify-center gap-2"
    >
      Прогноз Prophet
    </button>
  )}
</td>
                  </tr>

                  {selectedDatasetId === entry.dataset_id &&
                    forecastMap[entry.dataset_id]?.length > 0 &&
                    entry.method === "prophet" && (
                      <tr>
                        <td colSpan="4" className="bg-gray-50 p-4">
                          <h4 className="font-semibold mb-2">Прогноз продажів</h4>
                          <table className="w-full border mb-4">
                            <thead className="bg-gray-100">
                              <tr>
                                <th className="border px-2 py-1">Дата</th>
                                <th className="border px-2 py-1">Категорія</th>
                                <th className="border px-2 py-1">Продажі</th>
                                <th className="border px-2 py-1">Рекомендація</th>
                              </tr>
                            </thead>
                            <tbody>
                              {forecastMap[entry.dataset_id].map((item, subIdx) => (
                                <tr key={subIdx}>
                                  <td className="border px-2 py-1">{item.date}</td>
                                  <td className="border px-2 py-1">{item.category}</td>
                                  <td className="border px-2 py-1">{item.sales}</td>
                                  <td className="border px-2 py-1">{item.recommendation}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>

                          <ForecastChart datasetId={entry.dataset_id} />
                        </td>
                      </tr>
                    )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default HistoryPage;
