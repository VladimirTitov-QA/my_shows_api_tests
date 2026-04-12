-- Очищаем таблицу перед вставкой
TRUNCATE series RESTART IDENTITY CASCADE;

-- Добавляем тестовые сериалы
INSERT INTO series (name, photo, rating, status, review) VALUES
    ('Пацаны',
     'https://avatars.mds.yandex.net/get-kinopoisk-image/1773646/21324634-7afd-4443-8ac4-5c4097ac5b6c/600x900',
     9,
     'watched',
     'Мне понравился. Современный и с юмором'),
    ('Игра престолов',
     'https://avatars.mds.yandex.net/get-kinopoisk-image/1777765/dd78edfd-6a1f-486c-9a86-6acbca940418/600x900',
     9,
     'watching',
     'Мне нравится.');