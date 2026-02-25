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
                try:
                    dialect = csv.Sniffer().sniff(content[:10000], delimiters=',;')
                except:
                    dialect = csv.excel # fallback
                
                f.seek(0)
                reader = csv.reader(f, dialect=dialect)
                rows = list(reader)
                if rows: break
        except Exception:
            continue
    
    if not rows:
        print(f"Could not read {input_file}")
        return

    # Headers mapping
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
    
    # Headers for Google Ads Bulk Upload (Web UI & Editor)
    new_fieldnames = [
        "Action", "Campaign", "Campaign status", "Budget", "Budget type", "Campaign type",
        "Networks", "Languages", "Locations", "Bidding strategy type",
        "Ad group", "Ad group status", "Ad type", "Keyword", 
        "Headline 1", "Headline 2", "Headline 3", 
        "Description 1", "Description 2", "Max CPC", "Final URL"
    ]
    utm_string = "?utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_content={adgroupid}&utm_term={keyword}"

    campaigns_created = set()
    ad_groups_created = set()
    ads_created = set()

    # Determine default location based on replace_map or base_url
    default_location = "Almaty"
    if replace_map and "Ташкент" in replace_map.values():
        default_location = "Tashkent"

    with open(output_file, mode='w', encoding='utf-8', newline='') as fout:
        writer = csv.DictWriter(fout, fieldnames=new_fieldnames, delimiter=',')
        writer.writeheader()
        
        for row in data_rows:
            if not any(row): continue
            
            # Extract basic info
            orig_campaign = row[mapping_indices["Campaign"]].strip() if "Campaign" in mapping_indices else ""
            orig_ad_group = row[mapping_indices["Ad group"]].strip() if "Ad group" in mapping_indices else ""
            
            campaign = orig_campaign
            ad_group = orig_ad_group
            
            if replace_map:
                for old, new in replace_map.items():
                    campaign = campaign.replace(old, new)
                    ad_group = ad_group.replace(old, new)

            if not campaign: continue

            # 1. CAMPAIGN CREATION ROW
            if campaign not in campaigns_created:
                camp_row = {
                    "Action": "Add",
                    "Campaign": campaign,
                    "Campaign status": "Enabled",
                    "Budget": "500",
                    "Budget type": "Daily",
                    "Campaign type": "Search",
                    "Networks": "Google search;Search partners",
                    "Languages": "ru;kk;en",
                    "Locations": default_location,
                    "Bidding strategy type": "Manual CPC",
                    "Ad group": "", "Ad group status": "", "Ad type": "", "Keyword": "",
                    "Headline 1": "", "Headline 2": "", "Headline 3": "",
                    "Description 1": "", "Description 2": "", "Max CPC": "", "Final URL": ""
                }
                writer.writerow(camp_row)
                campaigns_created.add(campaign)

            # 2. AD GROUP CREATION ROW
            ad_group_key = (campaign, ad_group)
            if ad_group and ad_group_key not in ad_groups_created:
                # Try to get a default bid from the current row
                row_max_cpc = row[mapping_indices["Max CPC"]].strip().replace(',', '.') if "Max CPC" in mapping_indices else "0.50"
                if not row_max_cpc: row_max_cpc = "0.50"

                ag_row = {
                    "Action": "Add",
                    "Campaign": campaign,
                    "Ad group": ad_group,
                    "Ad group status": "Enabled",
                    "Max CPC": row_max_cpc, # Crucial for Editor
                    "Campaign status": "", "Budget": "", "Budget type": "", "Campaign type": "",
                    "Networks": "", "Languages": "", "Locations": "", "Bidding strategy type": "",
                    "Ad type": "", "Keyword": "", "Headline 1": "", "Headline 2": "", "Headline 3": "",
                    "Description 1": "", "Description 2": "", "Final URL": ""
                }
                writer.writerow(ag_row)
                ad_groups_created.add(ad_group_key)

            # 3. KEYWORD ROW
            keyword = row[mapping_indices["Keyword"]].strip().strip('"') if "Keyword" in mapping_indices else ""
            max_cpc = row[mapping_indices["Max CPC"]].strip().replace(',', '.') if "Max CPC" in mapping_indices else ""
            
            if keyword:
                kw_row = {
                    "Action": "Add",
                    "Campaign": campaign,
                    "Ad group": ad_group,
                    "Keyword": keyword,
                    "Max CPC": max_cpc,
                    "Campaign status": "", "Budget": "", "Budget type": "", "Campaign type": "",
                    "Networks": "", "Languages": "", "Locations": "", "Bidding strategy type": "",
                    "Ad group status": "", "Ad type": "",
                    "Headline 1": "", "Headline 2": "", "Headline 3": "",
                    "Description 1": "", "Description 2": "", "Final URL": ""
                }
                writer.writerow(kw_row)

            # 4. AD ROW (only once per Ad Group)
            ad_row_key = (campaign, ad_group)
            if ad_row_key not in ads_created:
                h1 = row[mapping_indices["Headline 1"]].strip() if "Headline 1" in mapping_indices else ""
                h2 = row[mapping_indices["Headline 2"]].strip() if "Headline 2" in mapping_indices else ""
                h3 = row[mapping_indices["Headline 3"]].strip() if "Headline 3" in mapping_indices else ""
                d1 = row[mapping_indices["Description 1"]].strip() if "Description 1" in mapping_indices else ""
                d2 = row[mapping_indices["Description 2"]].strip() if "Description 2" in mapping_indices else ""
                url_val = row[mapping_indices["Final URL"]].strip() if "Final URL" in mapping_indices else ""

                if replace_map:
                    for old, new in replace_map.items():
                        h1, h2, h3, d1, d2 = [s.replace(old, new) for s in [h1, h2, h3, d1, d2]]

                if not url_val or url_val.lower() == "nan":
                    current_url = base_url
                else:
                    current_url = url_val
                
                if not current_url.startswith("http"):
                    current_url = "https://" + current_url if "." in current_url else base_url
                
                if "?" not in current_url:
                    current_url += utm_string

                ad_row = {
                    "Action": "Add",
                    "Campaign": campaign,
                    "Ad group": ad_group,
                    "Ad type": "Responsive search ad",
                    "Campaign status": "", "Budget": "", "Budget type": "", "Campaign type": "",
                    "Ad group status": "", "Keyword": "", "Max CPC": "",
                    "Headline 1": h1, "Headline 2": h2, "Headline 3": h3,
                    "Description 1": d1, "Description 2": d2, "Final URL": current_url
                }
                writer.writerow(ad_row)
                ads_created.add(ad_row_key)

if __name__ == "__main__":
    input_f = "без пред  2 upd Copy koktem шаблон Города АП - Объявления Гугл.csv"
    if not os.path.exists(input_f):
        input_f = "без пред  2 upd Copy koktem шаблон Города АП - Объявления Гугл (1).csv"

    print(f"Generating Almaty campaign (Creation + Split format)...")
    clean_csv(input_f, "google_ads_almaty.csv", base_url="https://kz.henrybonnar.com/", replace_map={"koktem almaty 1.0 АП": "Search-344 Almaty-2-26"})
    
    print(f"Generating Tashkent campaign (Creation + Split format)...")
    tash_repl = {
        "Алматы": "Ташкент", 
        "Алматыда": "Ташкентте", 
        "almaty": "tashkent", 
        "Almaty": "Tashkent",
        "koktem almaty 1.0 АП": "Search-344 Tashkent Uzb ru"
    }
    clean_csv(input_f, "google_ads_tashkent.csv", replace_map=tash_repl, base_url="https://uz.henrybonnar.com/")
    
    print("Done. Campaigns and Ad Groups creation rows included.")
