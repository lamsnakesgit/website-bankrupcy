# Прямой экспорт из Google Ads в Google Таблицы (Без n8n/Make)

Если вы хотите полную автоматизацию без лишних прокладок и оплат за подписки (у Make есть лимиты), используйте **Google Ads Scripts**. Это мини-код на JavaScript, который живет прямо внутри вашего аккаунта.

---

## 🛠 Инструкция по настройке:

1.  Зайдите в аккаунт **Google Ads**.
2.  `Инструменты и настройки` -> `Массовые действия` -> `Скрипты`.
3.  Нажмите `+` и выберите «Новый скрипт».
4.  Сотрите всё, что там есть, и вставьте код ниже.
5.  Нажмите `Авторизовать` (дайте доступ к рекламному аккаунту и вашим таблицам).
6.  Нажмите `Сохранить` и поставьте расписание (например, «Раз в день»).

---

## 📄 Готовый код для копирования:

```javascript
function main() {
  // 1. Укажите ссылку на вашу пустую таблицу
  var SPREADSHEET_URL = 'ВАША_ССЫЛКА_НА_ТАБЛИЦУ_ТУТ';
  
  // 2. Выбираем лист (по умолчанию первый)
  var spreadsheet = SpreadsheetApp.openByUrl(SPREADSHEET_URL);
  var sheet = spreadsheet.getActiveSheet();
  sheet.clear(); // Очищаем всё перед новой записью
  
  // 3. Пишем заголовки
  sheet.appendRow(['Кампания', 'Показы', 'Клики', 'CTR', 'Расход', 'Конверсии']);
  
  // 4. Запрос к базе данных Google Ads (GAQL)
  var report = AdsApp.report(
    'SELECT campaign.name, metrics.impressions, metrics.clicks, metrics.ctr, metrics.cost_micros, metrics.conversions ' +
    'FROM campaign ' +
    'WHERE segments.date DURING LAST_30_DAYS'
  );
  
  // 5. Записываем данные в таблицу
  var rows = report.rows();
  while (rows.hasNext()) {
    var row = rows.next();
    sheet.appendRow([
      row['campaign.name'],
      row['metrics.impressions'],
      row['metrics.clicks'],
      row['metrics.ctr'],
      (row['metrics.cost_micros'] / 1000000).toFixed(2), // Перевод в валюту
      row['metrics.conversions']
    ]);
  }
  
  Logger.log('Отчет готов! Проверьте вашу таблицу по ссылке: ' + SPREADSHEET_URL);
}
```

---

## 💡 Почему это круто?
*   **0 рублей**: Вам не нужно платить за Make или n8n.
*   **Прямая связь**: Данные летят из сервера Google в сервер Google Таблиц.
*   **Гибкость**: Мы можем добавить любые поля (устройства, время, поисковые запросы) просто добавив их в строку `SELECT`.

**Важно**: Обязательно замените `ВАША_ССЫЛКА_НА_ТАБЛИЦУ_ТУТ` на реальную ссылку. Таблица должна быть открыта для вашей почты.
