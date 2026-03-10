# Прямая автоматизация Google Ads -> Google Sheets

Есть два "чистых" способа сделать так, чтобы данные прилетали в таблицу сами каждый день, без n8n и Make.

---

## Способ 1: Официальное дополнение (Самый простой / No-code)
Google выпустил специальный аддон для Таблиц. Вы просто выбираете параметры в меню, и таблица сама обновляется по расписанию.

1.  Откройте вашу Google Таблицу.
2.  В меню: `Расширения` (Extensions) -> `Дополнения` -> `Установить дополнения`.
3.  Найдите **"Google Ads"** (официальный от Google) и установите.
4.  В меню: `Расширения` -> `Google Ads` -> `Create new report`.
5.  Выберите нужные поля (Campaign, Clicks, Cost и т.д.).
6.  **Главное**: В настройках отчета поставьте галочку **"Schedule reports"** и выберите `Daily` (Ежедневно).

**Плюс:** Вообще не нужно писать код.
**Минус:** Меньше гибкости, чем у скриптов.

---

## Способ 2: Google Ads Scripts (Для профи / Гибкий)
Этот способ позволяет выгружать данные, которые аддон может не потянуть (например, сложные связки с объектами объявлений).

1.  Зайдите в `Инструменты` -> `Массовые действия` -> `Скрипты`.
2.  Используйте код ниже:

```javascript
function main() {
  var SPREADSHEET_URL = 'ВАША_ССЫЛКА_НА_ТАБЛИЦУ_ТУТ';
  var spreadsheet = SpreadsheetApp.openByUrl(SPREADSHEET_URL);
  var sheet = spreadsheet.getActiveSheet();
  sheet.clear(); 
  
  sheet.appendRow(['Кампания', 'Показы', 'Клики', 'CTR', 'Расход', 'Конверсии']);
  
  var report = AdsApp.report(
    'SELECT campaign.name, metrics.impressions, metrics.clicks, metrics.ctr, metrics.cost_micros, metrics.conversions ' +
    'FROM campaign ' +
    'WHERE segments.date DURING LAST_30_DAYS'
  );
  
  var rows = report.rows();
  while (rows.hasNext()) {
    var row = rows.next();
    sheet.appendRow([
      row['campaign.name'],
      row['metrics.impressions'],
      row['metrics.clicks'],
      row['metrics.ctr'],
      (row['metrics.cost_micros'] / 1000000).toFixed(2),
      row['metrics.conversions']
    ]);
  }
}
```
3.  Поставьте расписание в кабинете Google Ads: **«Выполнять ежедневно»**.

---

## 📈 Сравнение:
| Параметр | Дополнение (Add-on) | Скрипт (Script) |
| :--- | :--- | :--- |
| **Сложность** | ⭐️ (Очень легко) | ⭐️⭐️⭐️ (Нужен копипаст кода) |
| **Автоматизация** | Да (по расписанию) | Да (по расписанию) |
| **Гибкость** | Ограничена меню | Безгранична |

**Рекомендация:** Начните с **Дополнения**. Если его возможностей перестанет хватать — перейдем на Скрипт.
