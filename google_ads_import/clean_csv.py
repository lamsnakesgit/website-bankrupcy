import csv
import os

def clean_csv(input_file, output_file, replace_map=None, base_url="https://koktem.kz/"):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        return

    # Try different encodings
    rows = []
    for encoding in ['utf-8-sig', 'cp1251', 'utf-8']:
        try:
            with open(input_file, mode='r', encoding=encoding) as f:
                content = f.read()
                if not content.strip(): continue
                # Determine delimiter from content
                try:
                    dialect = csv.Sniffer().sniff(content[:10000], delimiters=',;')
                except:
                    dialect = csv.excel # fallback
                
                f.seek(0)
                reader = csv.reader(f, dialect=dialect)
                rows = list(reader)
                if rows:
                    break
        except Exception:
            continue
    
    if not rows:
        print(f"Could not read {input_file} or file is empty")
        return

    # Headers mapping to standard Google Ads Editor format
    mapping = {
        "Campaign": "Campaign",
        "Adgoup": "Ad group",
        "Фраза (с минус-словами)": "Keyword",
        "Headline 1": "Headline 1",
        "Headline 2": "Headline 2",
        "Headline 3": "Headline 3",
        "Description 1": "Description 1",
        "Description 2": "Description 2",
        "MAX CPC": "Max CPC",
        "Ссылка": "Final URL"
    }

    # Find header row and indices
    header_row_idx = -1
    mapping_indices = {}
    
    for i, row in enumerate(rows):
        row_str = " ".join(row).lower()
        if "campaign" in row_str or "headline 1" in row_str or "adgoup" in row_str:
            header_row_idx = i
            for target_key, standard_name in mapping.items():
                for col_idx, col_name in enumerate(row):
                    if target_key.lower() in col_name.lower():
                        mapping_indices[standard_name] = col_idx
            break
            
    if header_row_idx == -1:
        print("Header row not found")
        return

    data_rows = rows[header_row_idx + 1:]
    new_fieldnames = ["Campaign", "Ad group", "Keyword", "Headline 1", "Headline 2", "Headline 3", "Description 1", "Description 2", "Max CPC", "Final URL"]
    utm_string = "?utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_content={adgroupid}&utm_term={keyword}"

    with open(output_file, mode='w', encoding='utf-8-sig', newline='') as fout:
        # Using semicolon for local Excel/Editor compatibility
        writer = csv.DictWriter(fout, fieldnames=new_fieldnames, delimiter=';')
        writer.writeheader()
        
        for row in data_rows:
            if not any(row): continue
            
            new_row = {}
            for field in new_fieldnames:
                idx = mapping_indices.get(field)
                val = row[idx].strip() if idx is not None and idx < len(row) else ""
                
                # Apply replacements
                if replace_map:
                    for old, new in replace_map.items():
                        val = val.replace(old, new)
                
                # Data cleanup
                if field == "Keyword":
                    val = val.strip('"')
                
                if field == "Max CPC":
                    val = val.replace(',', '.')
                
                if field == "Final URL":
                    if not val or val.lower() == "nan":
                        current_url = base_url
                    else:
                        # If user provided a URL, we keep it but ensure it has UTM
                        current_url = val
                    
                    if not current_url.startswith("http"):
                        current_url = "https://" + current_url if "." in current_url else base_url
                    
                    if "?" not in current_url:
                        current_url += utm_string
                
                new_row[field] = val if field != "Final URL" else current_url
            
            writer.writerow(new_row)

if __name__ == "__main__":
    input_f = "без пред  2 upd Copy koktem шаблон Города АП - Объявления Гугл.csv"
    if not os.path.exists(input_f):
        input_f = "без пред  2 upd Copy koktem шаблон Города АП - Объявления Гугл (1).csv"

    # 1. Almaty
    print(f"Generating Almaty campaign...")
    clean_csv(input_f, "google_ads_almaty.csv", base_url="https://kz.henrybonnar.com/")
    
    # 2. Tashkent
    print(f"Generating Tashkent campaign...")
    tashkent_replacements = {
        "Алматы": "Ташкент",
        "Алматыда": "Ташкентте",
        "almaty": "tashkent",
        "Almaty": "Tashkent"
    }
    clean_csv(input_f, "google_ads_tashkent.csv", replace_map=tashkent_replacements, base_url="https://uz.henrybonnar.com/")
    
    print("Done. Generated google_ads_almaty.csv and google_ads_tashkent.csv with updated URLs.")
