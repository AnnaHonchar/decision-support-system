import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import UploadPage from "./pages/UploadPage";
import ResultPage from "./pages/ResultPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import HistoryPage from "./pages/HistoryPage";
import ProfilePage from "./pages/ProfilePage";
import HelpPage from "./pages/HelpPage";


function App() {
  return (
    <Router>
      <div className="bg-gray-100 shadow-md px-6 py-4 flex justify-between items-center">
  <div className="flex gap-6 text-sm font-medium text-gray-800">
    <a href="/" className="hover:text-blue-600 transition">Завантажити</a>
    <a href="/results" className="hover:text-blue-600 transition">Результати</a>
    <a href="/login" className="hover:text-blue-600 transition">Вхід</a>
    <a href="/register" className="hover:text-blue-600 transition">Реєстрація</a>
    <a href="/history" className="hover:text-blue-600 transition">Історія</a>
    <a href="/profile" className="hover:text-blue-600 transition">Профіль</a>
    <a href="/help" className="hover:text-blue-600 transition">Допомога</a>
    <button
          onClick={() => {
            localStorage.removeItem("userId");
            window.location.href = "/login";
          }}
          style={{ marginLeft: "1rem" }}
        >
          Вийти
        </button>
  </div>
</div>

      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/results" element={<ResultPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/help" element={<HelpPage />} />
      </Routes>
    </Router>
  );
}

export default App;