# Tutorial - Руководство пользователя

Это руководство проведет вас через все возможности FastHTTP - от базовых до продвинутых.

## Структура

Руководство разделено на несколько секций:

### Начало работы
- [Первые шаги](first-steps.md) - Установка и основные понятия
- [HTTP методы](http-methods.md) - GET, POST, PUT, PATCH, DELETE
- [Параметры запроса](request-parameters.md) - Query, JSON, заголовки
- [Обработка ответа](response-handling.md) - Работа с ответами

### Основные функции
- [Параллельное выполнение](parallel-execution.md) - Параллельные запросы
- [Теги](tags.md) - Группировка и фильтрация
- [Зависимости](dependencies.md) - Модификация запросов
- [Lifespan](lifespan.md) - Запуск и завершение

### Валидация данных
- [Pydantic валидация](validation/pydantic-validation.md) - Валидация ответов
- [Валидация запроса](validation/request-validation.md) - Валидация перед отправкой
- [Валидация ошибок](validation/error-validation.md) - Обработка ошибок API

### Конфигурация
- [Настройки](configuration/settings.md) - Конфигурация приложения
- [Заголовки](configuration/headers.md) - HTTP заголовки
- [Таймауты](configuration/timeouts.md) - Таймауты запросов
- [Логирование](configuration/logging.md) - Режим отладки
- [Переменные окружения](configuration/environment.md) - Конфигурация через env
- [HTTP/2](configuration/http2.md) - Поддержка HTTP/2
- [Прокси](configuration/proxy.md) - Конфигурация прокси

### Продвинутые темы
- [Middleware](middleware/index.md) - Глобальная логика запросов
- [Безопасность](security/index.md) - Встроенная защита
- [GraphQL](graphql/index.md) - Поддержка GraphQL
- [OpenAPI](openapi/index.md) - Swagger UI

## Как использовать

Каждый раздел основывается на предыдущем. Рекомендуем читать по порядку, если вы новичок в FastHTTP.

## Примеры

Все разделы содержат практические примеры кода, которые можно скопировать и запустить.
