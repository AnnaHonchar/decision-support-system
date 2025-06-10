import React, { useState } from "react";
import axios from "axios";
import Papa from "papaparse";

const UploadPage = () => {
  if (!localStorage.getItem("userId")) {
    window.location.href = "/login";
  }

  const [file, setFile] = useState(null);
  const [userId, setUserId] = useState(localStorage.getItem("userId") || "");
  const [response, setResponse] = useState(null);
  const [previewData, setPreviewData] = useState([]);
  const [topsisFile, setTopsisFile] = useState(null);
  const [topsisResult, setTopsisResult] = useState("");
  const [classificationFile, setClassificationFile] = useState(null);
  const [classificationResult, setClassificationResult] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);

    Papa.parse(selectedFile, {
      header: true,
      skipEmptyLines: true,
      complete: function (results) {
        setPreviewData(results.data);
      },
    });
  };

  const handleClean = async () => {
    if (!userId) return;

    const res = await axios.get("http://localhost:5000/api/results", {
      params: { user_id: userId },
    });

    const latestDataset = res.data[res.data.length - 1];
    if (!latestDataset) return;

    await axios.post(
      `http://localhost:5000/api/clean/${latestDataset.dataset_id}`
    );
    alert("Дані очищено перед аналізом");
  };

  const handleUpload = async () => {
    if (!file || !userId) {
      alert("Оберіть файл і введіть user_id");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", userId);

    try {
      const uploadRes = await axios.post(
        "http://localhost:5000/api/upload",
        formData
      );
      const datasetId = uploadRes.data.dataset_id;

      const analyzeRes = await axios.post(
        "http://localhost:5000/api/analyze",
        { dataset_id: datasetId }
      );

      setResponse(analyzeRes.data);
    } catch (err) {
      console.error("Помилка від сервера:", err.response?.data || err.message);
      alert("Помилка під час завантаження або аналізу");
    }
  };

  const handleTopsisFileChange = (e) => {
    setTopsisFile(e.target.files[0]);
  };

  const handleTopsisUpload = async () => {
    if (!topsisFile || !userId) {
      alert("Оберіть файл для TOPSIS і введіть user_id");
      return;
    }

    const formData = new FormData();
    formData.append("file", topsisFile);
    formData.append("user_id", userId);

    try {
      const res = await axios.post("http://localhost:5000/api/topsis", formData);
      setTopsisResult(res.data.result);
      alert("Аналіз TOPSIS завершено!");
    } catch (err) {
      console.error("Помилка TOPSIS:", err.response?.data || err.message);
      alert("Не вдалося виконати аналіз TOPSIS");
    }
  };

  const handleClassificationChange = (e) => {
    const file = e.target.files[0];
    setClassificationFile(file);
  };

  const handleClassificationUpload = async () => {
    if (!classificationFile) return alert("Виберіть файл для класифікації");

    const formData = new FormData();
    formData.append("file", classificationFile);
    formData.append("user_id", userId);

    try {
      const res = await axios.post("http://localhost:5000/api/classify", formData);
      setClassificationResult(res.data);
      alert("Класифікація завершена");
    } catch (error) {
      console.error("Помилка класифікації:", error);
      alert("Не вдалося провести класифікацію");
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-6">
      <h2 className="text-2xl font-semibold mb-6">Завантаження файлу та аналіз</h2>

      <input
        type="text"
        placeholder="Введіть ваш user_id"
        value={userId}
        onChange={(e) => setUserId(e.target.value)}
        className="border rounded px-3 py-2 w-full mb-4"
      />

      <div className="space-y-3">
        <input type="file" accept=".csv" onChange={handleFileChange} className="w-full" />

        <div className="flex gap-3">
          <button onClick={handleUpload} className="bg-blue-600 text-white px-4 py-2 rounded shadow">
            Завантажити та проаналізувати
          </button>
          <button onClick={handleClean} className="bg-gray-600 text-white px-4 py-2 rounded shadow">
            Очистити дані
          </button>
        </div>
      </div>

      {previewData.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-medium mb-2">Попередній перегляд даних:</h3>
          <div className="overflow-auto">
            <table className="min-w-full text-sm border">
              <thead>
                <tr>
                  {Object.keys(previewData[0]).map((key, idx) => (
                    <th key={idx} className="border px-2 py-1 bg-gray-100">{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {previewData.map((row, idx) => (
                  <tr key={idx}>
                    {Object.values(row).map((val, i) => (
                      <td key={i} className="border px-2 py-1">{val}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {response && (
        <div className="mt-6">
          <h3 className="text-lg font-medium mb-2">Результат аналізу:</h3>
          <p><strong>Точність:</strong> {response.accuracy}</p>
          <p><strong>Рекомендація:</strong> {response.recommendation}</p>

          {response.chart_base64 && (
            <div className="mt-4">
              <h4 className="text-md font-medium mb-2">Візуалізація точності:</h4>
              <img
                src={`data:image/png;base64,${response.chart_base64}`}
                alt="Графік точності"
                className="border rounded max-w-full"
              />
            </div>
          )}
        </div>
      )}

      <hr className="my-8" />
      <h3 className="text-xl font-semibold mb-4">Аналіз асортименту (TOPSIS)</h3>

      <div className="space-y-3">
        <input type="file" accept=".csv" onChange={handleTopsisFileChange} className="w-full" />
        <button onClick={handleTopsisUpload} className="bg-blue-600 text-white px-4 py-2 rounded shadow">
          Завантажити та проаналізувати
        </button>
        {topsisResult && (
          <div className="bg-blue-100 p-4 rounded shadow">
            <strong>Результат TOPSIS:</strong>
            <p>{topsisResult}</p>
          </div>
        )}
      </div>

      <hr className="my-8" />
      <h3 className="text-xl font-semibold mb-4">Класифікація товарів за прибутковістю</h3>

      <div className="space-y-3">
        <input type="file" accept=".csv" onChange={handleClassificationChange} className="w-full" />
        <button onClick={handleClassificationUpload} className="bg-blue-600 text-white px-4 py-2 rounded shadow">
          Завантажити та класифікувати
        </button>

        {classificationResult && (
          <div className="bg-green-100 p-4 rounded shadow">
            <h4 className="text-lg font-medium mb-2">Результати класифікації:</h4>
            <table className="w-full border text-sm mb-4">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border px-2 py-1">Товар</th>
                  <th className="border px-2 py-1">Результат</th>
                </tr>
              </thead>
              <tbody>
                {classificationResult.results.map((item, idx) => (
                  <tr key={idx}>
                    <td className="border px-2 py-1">{item.product}</td>
                    <td
                      className={`border px-2 py-1 font-medium ${item.predicted === 1 ? "text-green-600" : "text-red-600"}`}
                    >
                      {item.predicted === 1 ? "Вигідний" : "Невигідний"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <h4 className="text-md font-medium mb-1">Метрики моделі:</h4>
            <ul className="list-disc pl-5">
              <li><strong>Accuracy:</strong> {classificationResult.metrics.accuracy}</li>
              <li><strong>Precision:</strong> {classificationResult.metrics.precision}</li>
              <li><strong>Recall:</strong> {classificationResult.metrics.recall}</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadPage;