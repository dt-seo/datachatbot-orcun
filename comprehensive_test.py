# -*- coding: utf-8 -*-
"""
Tum mecralar icin kapsamli test
"""
from chatbot import GA4Chatbot
import re

def extract_number(response):
    '''Cevaptan sayiyi cikar'''
    # "Sayfa Goruntuleme: 4,035,881" formatindan sayi cikart
    match = re.search(r'(?:Sayfa\s*G[oö]r[uü]nt[uü]leme|Views?):\s*([\d,\.]+)', response, re.IGNORECASE)
    if match:
        return match.group(1)
    # Scorecard formatindan sayi cikart
    match = re.search(r'^\s*([\d,\.]+)\s*$', response, re.MULTILINE)
    if match:
        return match.group(1)
    match = re.search(r'([\d,\.]+)\s*(?:g[oö]r[uü]nt[uü]lenme|views?)', response, re.IGNORECASE)
    if match:
        return match.group(1)
    return 'N/A'

def test_brand(brand_name):
    print(f'\n{"="*70}')
    print(f'  {brand_name.upper()} DETAYLI TEST')
    print(f'{"="*70}')

    results = {
        'brand': brand_name,
        'editors': [],
        'categories': [],
        'editor_name_search': None,
        'editor_views': None,
        'publish_date_views': None,
        'errors': []
    }

    try:
        bot = GA4Chatbot(brand=brand_name)
    except Exception as e:
        print(f'[HATA] Bot baslatilamadi: {e}')
        results['errors'].append(str(e))
        return results

    # 1. En populer editorleri cek
    print(f'\n[1] EN POPULER EDITORLER (1-7 Aralik)')
    print('-' * 50)
    try:
        response = bot.process_query('1-7 aralik en populer editor')

        # Editor kodlarini cikart
        lines = response.split('\n')
        editors = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('=') or line.startswith('-'):
                continue
            if 'Edit' in line or 'Sayfa' in line or 'customEvent' in line:
                continue
            if 'Populer' in line or 'Performans' in line:
                continue
            parts = line.split()
            if parts and len(parts[0]) > 2:
                code = parts[0]
                if not code.isdigit() and code not in ['(not', 'set)', 'Ana']:
                    editors.append(code)

        editors = editors[:3]
        results['editors'] = editors
        print(f'Top 3 Editor Kodu: {editors}')
    except Exception as e:
        print(f'[HATA] Editor listesi cekilemedi: {e}')
        results['errors'].append(f'Editor listesi: {e}')

    # 2. Kategori listesi
    print(f'\n[2] EN POPULER KATEGORILER (1-7 Aralik)')
    print('-' * 50)
    try:
        response = bot.process_query('1-7 aralik kategori performansi')

        # Kategorileri cikart
        lines = response.split('\n')
        categories = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('=') or line.startswith('-'):
                continue
            if 'Kategori' in line or 'Sayfa' in line or 'Performans' in line:
                continue
            parts = line.split()
            if parts and len(parts[0]) > 2:
                cat = parts[0]
                if cat not in ['(not', 'set)', 'Ana'] and not cat.isdigit():
                    categories.append(cat)

        categories = categories[:3]
        results['categories'] = categories
        print(f'Top 3 Kategori: {categories}')
    except Exception as e:
        print(f'[HATA] Kategori listesi cekilemedi: {e}')
        results['errors'].append(f'Kategori listesi: {e}')

    # 3. Editor isimle arama ve views
    print(f'\n[3] EDITOR ISIMLE ARAMA (1-7 Aralik Views)')
    print('-' * 50)

    if results['editors']:
        editor_code = results['editors'][0]
        real_name = bot.editor_matcher.get_real_name(editor_code)

        search_term = real_name if real_name else editor_code
        results['editor_name_search'] = {
            'code': editor_code,
            'real_name': real_name,
            'search_term': search_term
        }

        print(f'Editor kodu: {editor_code}')
        print(f'Gercek isim: {real_name if real_name else "(bulunamadi)"}')

        try:
            query = f'{search_term} 1-7 aralik views'
            print(f'Sorgu: "{query}"')
            response = bot.process_query(query)
            views = extract_number(response)
            results['editor_views'] = views
            print(f'Sonuc: {views} views')
        except Exception as e:
            print(f'[HATA] Editor views cekilemedi: {e}')
            results['errors'].append(f'Editor views: {e}')

    # 4. Yayinlanma tarihi 1-7 Aralik olan icerikler
    print(f'\n[4] 1-7 ARALIK YAYINLANAN ICERIKLERIN VIEWS\'I')
    print('-' * 50)

    if results['editors']:
        editor_code = results['editors'][0]
        real_name = bot.editor_matcher.get_real_name(editor_code) or editor_code

        try:
            query = f'{real_name} 1-7 aralik yayinladigi icerikler ne kadar views aldi'
            print(f'Sorgu: "{query}"')
            response = bot.process_query(query)
            views = extract_number(response)
            results['publish_date_views'] = views
            print(f'Sonuc: {views} views')
        except Exception as e:
            print(f'[HATA] Yayin tarihi views cekilemedi: {e}')
            results['errors'].append(f'Yayin tarihi views: {e}')

    return results

def main():
    print('='*70)
    print('  TUM MECRALAR ICIN KAPSAMLI TEST')
    print('  1-7 Aralik 2024 Verileri')
    print('='*70)

    mecralar = ['hurriyet', 'vatan', 'fanatik', 'milliyet', 'posta', 'cnnturk', 'kanald']
    all_results = []

    for mecra in mecralar:
        result = test_brand(mecra)
        all_results.append(result)

    # Ozet
    print('\n')
    print('='*70)
    print('  SONUC OZETI')
    print('='*70)

    print(f'\n{"Mecra":<12} {"Top Editor":<20} {"Isim":<20} {"Views":<15} {"Yayin Tarihi Views":<15}')
    print('-'*82)

    for r in all_results:
        brand = r['brand'].upper()
        editor = r['editors'][0] if r['editors'] else 'N/A'
        name = r.get('editor_name_search', {}).get('real_name', '') or '-'
        views = r.get('editor_views', 'N/A')
        pub_views = r.get('publish_date_views', 'N/A')

        if len(name) > 18:
            name = name[:15] + '...'
        if len(editor) > 18:
            editor = editor[:15] + '...'

        print(f'{brand:<12} {editor:<20} {name:<20} {views:<15} {pub_views:<15}')

    print('\n--- Kategoriler ---')
    for r in all_results:
        print(f'{r["brand"].upper():<12}: {", ".join(r["categories"][:3]) if r["categories"] else "N/A"}')

    print('\n--- Hatalar ---')
    has_errors = False
    for r in all_results:
        if r['errors']:
            has_errors = True
            print(f'{r["brand"].upper()}: {"; ".join(r["errors"])}')
    if not has_errors:
        print('Hata yok!')

if __name__ == '__main__':
    main()
