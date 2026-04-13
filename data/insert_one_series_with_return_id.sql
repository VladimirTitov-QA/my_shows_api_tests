-- Добавляем один тестовый сериал с возвратом ID
INSERT INTO series (name, photo, rating, status, review)
VALUES (
    'Тестовый сериал для фикстуры create_single_series',
    'https://avatars.mds.yandex.net/get-kinopoisk-image/1773646/21324634-7afd-4443-8ac4-5c4097ac5b6c/600x900',
    5,
    'watched',
    'Отзыв для теста.'
)
RETURNING id;