import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ResponsiveContainer
} from "recharts";

const ForecastChart = ({ datasetId }) => {
  const [dataByCategory, setDataByCategory] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const res = await axios.get(`http://localhost:5000/api/combined_forecast/${datasetId}`);
      const transformed = res.data.map(group => {
        const allDates = [...group.actual, ...group.forecast];
        const merged = {};

        allDates.forEach(entry => {
          if (!merged[entry.date]) {
            merged[entry.date] = { date: entry.date };
          }
          if (group.actual.some(d => d.date === entry.date)) {
            merged[entry.date].actual = entry.sales;
          }
          if (group.forecast.some(d => d.date === entry.date)) {
            merged[entry.date].forecast = entry.sales;
          }
        });

        return {
          category: group.category,
          data: Object.values(merged).sort((a, b) => new Date(a.date) - new Date(b.date))
        };
      });

      setDataByCategory(transformed);
    };
    fetchData();
  }, [datasetId]);

  return (
    <div style={{ marginTop: "2rem" }}>
      <h3>Графік прогнозу продажів</h3>

      {dataByCategory.map((entry, idx) => (
        <div key={idx} style={{ marginBottom: "2rem" }}>
          <h4>Категорія: {entry.category}</h4>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={entry.data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="actual" name="Факт" stroke="#8884d8" dot={false} />
              <Line
                type="monotone"
                dataKey="forecast"
                name="Прогноз"
                stroke="#82ca9d"
                dot={false}
                strokeDasharray="5 5"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ))}
    </div>
  );
};

export default ForecastChart;
