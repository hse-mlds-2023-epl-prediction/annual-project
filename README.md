# Предсказательные модели для игроков EPL
В этом проекте будут разрабатываться предсказательные модели для игроков и команд EPL(Английская Премьер-лига)

## Команда проекта
|| telegram | github |
| ------ | ------ | ------ |
| Чуприн Александр | [@Chew13](https://t.me/Chew13) | [Chewye](https://github.com/Chewye) |
| Лапшин Никита | [@GodSiemens](https://t.me/GodSiemens) | [Nikita-hub000](https://github.com/Nikita-hub000) |
| Дубов Владислав | [@dubov_vv](https://t.me/dubov_vv) | [hotspurs](https://github.com/hotspurs) |
| Горяной Егор (куратор)| [@nogaromo](https://t.me/nogaromo) | |

## Задачи

### Поиск и анализ данных
1. Сбор подходящего датасета
  - написание парсера для сбора статистики по игрокам и матчам с информационных сайтов 
2. Проведение EDA
  - По запросу выводить статистику по игроку / команде за выбранный период
  - Выводить топ-N игроков / команд по заданному параметру за выбранный период
  - Построение графиков в зависимости от времени

### ML-задачи
1. Прогноз на результат матча
2. Прогноз трансферной стоимости игрока
3. Поиск талантливых игроков из низших лиг и прогноз их трансферной стоимости
4. Кластеризация игроков / команд
5. Применение методов анализа временных рядов к задаче

### DL-задачи
1. Использование нейронных сетей для решения задач из блока ML
2. Для анализа временных рядов использование рекуррентных сетей, сравнение их результатов с ML-подходом