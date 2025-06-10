import React from "react";

const HelpPage = () => {
  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      <h2 className="text-3xl font-bold mb-8 text-center">Довідка та навчальні матеріали</h2>

      <section className="mb-6">
        <h3 className="text-xl font-semibold mb-2">📁 Як завантажити файл?</h3>
        <p className="text-gray-700">
          Перейдіть на сторінку "Завантаження", оберіть CSV-файл, введіть свій
          user ID та натисніть "Завантажити та проаналізувати".
        </p>
      </section>

      <section className="mb-6">
        <h3 className="text-xl font-semibold mb-2">🧹 Як працює очищення даних?</h3>
        <p className="text-gray-700">
          Система автоматично видаляє дублікати та порожні значення зі
          завантаженого файлу перед аналізом.
        </p>
      </section>

      <section className="mb-6">
        <h3 className="text-xl font-semibold mb-2">📊 Що означає "Точність"?</h3>
        <p className="text-gray-700">
          Точність — це частка правильних передбачень моделі. Висока точність
          (0.85+) вказує на якісну структуру та підготовку даних.
        </p>
      </section>

      <section className="mb-6">
        <h3 className="text-xl font-semibold mb-2">📈 Як читати графік?</h3>
        <p className="text-gray-700">
          Графік показує точність передбачення по класах. Чим вище стовпчик —
          тим точніше модель передбачає певний клас.
        </p>
      </section>

      <section className="mb-6">
        <h3 className="text-xl font-semibold mb-2">❗ Часті помилки</h3>
        <ul className="list-disc list-inside text-gray-700 space-y-1">
          <li>Неправильний формат CSV (немає заголовків колонок)</li>
          <li>Порожні або дубліковані рядки</li>
          <li>Завантаження нечислових даних без підготовки</li>
        </ul>
      </section>

      <section className="mb-6">
        <h3 className="text-xl font-semibold mb-2">📌 Корисні поради</h3>
        <ul className="list-disc list-inside text-gray-700 space-y-1">
          <li>Перед аналізом завжди очищайте дані</li>
          <li>Використовуйте однакові типи даних у колонках</li>
          <li>Використовуйте англійські заголовки для кращої сумісності</li>
        </ul>
      </section>
    </div>
  );
};

export default HelpPage;
