# Тестирование производительности СХД OCFS2 и ВМ

## Описание

Тестирование производительности СХД OCFS2 и ВМ — это проект нацеленный на тестирование выполнения базового функционала СХД OCFS2, а так же тест на производительность дисковых устройств ВМ, размещенных в данном хранилище.

## Функциональность

- **Тестирование выполнения базового функционала СХД OCFS2**:
  - способность записи, чтения, создания файлов (pytest).
- **Создание дисковых устройств для ВМ**:
  - гибкое создание дисковых устройств.
- **Подключение дисковых устройств для ВМ**:
  - подключение и параметризация подключаемых дисковых устройств (pytest).
- **Тестирование на производительность дисковых устройств ВМ**:
  - тестирование на производительность дисковых устройств ВМ со снятием основных метрик.
- **Визуализация метрик**:
  - визуализация метрик c помощью seaborn и matplotlib.
