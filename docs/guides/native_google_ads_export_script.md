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

## Способ 2: Google Ads Scripts (Для PRO-аудита / Все галочки)
Этот способ выгружает не только клики, но и **настройки** (стратегии ставок, бюджеты, типы сетей), что критично для анализа ИИ.

1.  Зайдите в `Инструменты` -> `Массовые действия` -> `Скрипты`.
2.  Используйте этот **"Deep Audit"** код:

```javascript
function main() {
  var SPREADSHEET_URL = 'ВАША_ССЫЛКА_НА_ТАБЛИЦУ_ТУТ';
  var spreadsheet = SpreadsheetApp.openByUrl(SPREADSHEET_URL);
  var sheet = spreadsheet.getActiveSheet();
  sheet.clear(); 
  
  // Заголовки (теперь тут есть настройки!)
  sheet.appendRow([
    'Кампания', 'Статус', 'Тип', 'Бюджет', 
    'Стратегия ставок', 'Целевой CPA', 'Поиск Google', 'Партнеры', 'КМС',
    'Показы', 'CTR', 'Расход', 'Конверсии'
  ]);
  
  var report = AdsApp.report(
    'SELECT campaign.name, campaign.status, campaign.advertising_channel_type, ' +
    'campaign_budget.amount_micros, campaign.bidding_strategy_type, ' +
    'campaign.target_cpa.target_cpa_micros, ' +
    'campaign.network_settings.target_google_search, ' +
    'campaign.network_settings.target_search_network, ' +
    'campaign.network_settings.target_content_network, ' +
    'metrics.impressions, metrics.ctr, metrics.cost_micros, metrics.conversions ' +
    'FROM campaign ' +
    'WHERE segments.date DURING LAST_30_DAYS'
  );
  
  var rows = report.rows();
  while (rows.hasNext()) {
    var row = rows.next();
    sheet.appendRow([
      row['campaign.name'],
      row['campaign.status'],
      row['campaign.advertising_channel_type'],
      (row['campaign_budget.amount_micros'] / 1000000), 
      row['campaign.bidding_strategy_type'],
      (row['campaign.target_cpa.target_cpa_micros'] / 1000000 || 0),
      row['campaign.network_settings.target_google_search'],
      row['campaign.network_settings.target_search_network'],
      row['campaign.network_settings.target_content_network'],
      row['metrics.impressions'],
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
