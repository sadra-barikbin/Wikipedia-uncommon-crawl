import os
from scrapy.exporters import BaseItemExporter
from typing import Dict
from crawl.items import Document

class DocumentExporter(BaseItemExporter):
    def __init__(self, file, **kwargs):
        super().__init__(dont_fail=True, **kwargs)
        self.lang_to_number: Dict[str, int] = {}
    
    def start_exporting(self):
        os.makedirs("wikidata", exist_ok=True)

    def export_item(self, item: Document):
        lang_code = item["lang_code"]
        lang_name = item['lang_name'].replace(' ', '_')
        lang_folder = f"{lang_code}_{lang_name}"
        if lang_code not in self.lang_to_number:
            os.makedirs(f"wikidata/{lang_folder}", exist_ok=True)
            self.lang_to_number[lang_code] = 1
        
        with open(f"wikidata/{lang_folder}/{self.lang_to_number[lang_code]}.txt", 'w', encoding='utf-8') as file:
            file.write(item['text'])
        self.lang_to_number[lang_code] += 1