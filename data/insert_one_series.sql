-- Очищаем таблицу перед вставкой
TRUNCATE series RESTART IDENTITY CASCADE;

-- Добавляем один тестовый сериал
INSERT INTO series (name, photo, rating, status, review) VALUES (
    'Один сериал',
    'https://example.com/one.jpg',
    8,
    'watching',
    'Хороший сериал'
);