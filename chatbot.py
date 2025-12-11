# -*- coding: utf-8 -*-
"""
Google Analytics 4 - Chatbot
Keyword-based soru anlama ve GA4 sorgu calistirma

Kullanim:
    python chatbot.py
"""

import re
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from ga4_client import GA4Client
from ga4_mappings import QUICK_QUERIES, DIMENSIONS, METRICS, CUSTOM_DIMENSIONS, CUSTOM_METRICS
from fuzzy_matcher import EditorMatcher, AuthorMatcher, DimensionMetricMatcher

# Turkce gun isimleri
TURKISH_DAY_NAMES = {
    "0": "Pazar",
    "1": "Pazartesi",
    "2": "Sali",
    "3": "Carsamba",
    "4": "Persembe",
    "5": "Cuma",
    "6": "Cumartesi",
    # Ingilizce isimler icin de
    "Sunday": "Pazar",
    "Monday": "Pazartesi",
    "Tuesday": "Sali",
    "Wednesday": "Carsamba",
    "Thursday": "Persembe",
    "Friday": "Cuma",
    "Saturday": "Cumartesi",
}


class GA4Chatbot:
    """GA4 Chatbot - Keyword tabanli soru anlama"""

    def __init__(self, brand: str = None):
        """
        Chatbot'u baslat

        Args:
            brand: Marka adi ("hurriyet", "vatan", "cnnturk", "fanatik", "kanald", "milliyet", "posta")
                   None ise varsayilan olarak Hurriyet kullanilir
        """
        self.client = GA4Client(brand=brand)
        self.brand = brand or "hurriyet"
        self.editor_matcher = EditorMatcher(self.client)
        self.author_matcher = AuthorMatcher(self.client)
        self.dm_matcher = DimensionMetricMatcher()  # Dimension/Metric matcher
        self.last_dataframe = None  # Web arayuzu icin son DataFrame
        self.context = {
            "last_query": None,
            "last_result": None,
            "date_range": {"start": "yesterday", "end": "yesterday"},
            "pending_disambiguation": None  # Editor/yazar secimi bekliyor mu?
        }

        # Tarih pattern'leri - kapsamli Turkce tarih ifadeleri
        # NOT: Daha spesifik pattern'ler (hafta sonu gibi) once tanimlanmali
        self.date_patterns = {
            # === HAFTA SONU (ONCE TANIMLANMALI - daha spesifik) ===
            r"ge[cçcs]en\s*hafta\s*sonu": "last_weekend",
            r"ge[cçcs][cçct]i[gğ]imiz\s*hafta\s*sonu": "last_weekend",
            r"gecen\s*hafta\s*sonu": "last_weekend",
            r"[oö]nceki\s*hafta\s*sonu": "last_weekend",
            r"bu\s*hafta\s*sonu": "this_weekend",
            r"haftasonu": "last_weekend",

            # === BUGUN ===
            r"bug[uü]n": "today",
            r"bug[uü]nk[uü]": "today",
            r"g[uü]n[uü]m[uü]z": "today",
            r"bug[uü]ne\s*kadar": "today",
            r"bug[uü]n\s*i[cç]in": "today",
            r"bug[uü]n\s*itibariyle": "today",
            r"[sş]u\s*an": "today",
            r"[sş]imdi": "today",
            r"[sş]imdiye\s*kadar": "today",
            r"anlık": "today",
            r"anlik": "today",

            # === DUN ===
            r"d[uü]n": "yesterday",
            r"d[uü]nk[uü]": "yesterday",
            r"bir\s*g[uü]n\s*[oö]nce": "yesterday",
            r"1\s*g[uü]n\s*[oö]nce": "yesterday",
            r"bir\s*[oö]nceki\s*g[uü]n": "yesterday",
            r"ge[cç]en\s*g[uü]n": "yesterday",

            # === EVVELKI GUN (2 gun once) ===
            r"evvelki\s*g[uü]n": "2daysAgo",
            r"evvelsi\s*g[uü]n": "2daysAgo",
            r"iki\s*g[uü]n\s*[oö]nce": "2daysAgo",
            r"2\s*g[uü]n\s*[oö]nce": "2daysAgo",

            # === X GUN ONCE ===
            r"3\s*g[uü]n\s*[oö]nce": "3daysAgo",
            r"[uü][cç]\s*g[uü]n\s*[oö]nce": "3daysAgo",
            r"4\s*g[uü]n\s*[oö]nce": "4daysAgo",
            r"d[oö]rt\s*g[uü]n\s*[oö]nce": "4daysAgo",
            r"5\s*g[uü]n\s*[oö]nce": "5daysAgo",
            r"be[sş]\s*g[uü]n\s*[oö]nce": "5daysAgo",
            r"bir\s*hafta\s*[oö]nce": "7daysAgo",
            r"1\s*hafta\s*[oö]nce": "7daysAgo",
            r"iki\s*hafta\s*[oö]nce": "14daysAgo",
            r"2\s*hafta\s*[oö]nce": "14daysAgo",
            r"bir\s*ay\s*[oö]nce": "30daysAgo",
            r"1\s*ay\s*[oö]nce": "30daysAgo",
            r"iki\s*ay\s*[oö]nce": "60daysAgo",
            r"2\s*ay\s*[oö]nce": "60daysAgo",

            # === SON X GUN ===
            r"son\s*1\s*g[uü]n": "1daysAgo",
            r"son\s*bir\s*g[uü]n": "1daysAgo",
            r"son\s*2\s*g[uü]n": "2daysAgo",
            r"son\s*iki\s*g[uü]n": "2daysAgo",
            r"son\s*3\s*g[uü]n": "3daysAgo",
            r"son\s*[uü][cç]\s*g[uü]n": "3daysAgo",
            r"son\s*4\s*g[uü]n": "4daysAgo",
            r"son\s*d[oö]rt\s*g[uü]n": "4daysAgo",
            r"son\s*5\s*g[uü]n": "5daysAgo",
            r"son\s*be[sş]\s*g[uü]n": "5daysAgo",
            r"son\s*6\s*g[uü]n": "6daysAgo",
            r"son\s*alt[iı]\s*g[uü]n": "6daysAgo",
            r"son\s*7\s*g[uü]n": "7daysAgo",
            r"son\s*yedi\s*g[uü]n": "7daysAgo",
            r"son\s*10\s*g[uü]n": "10daysAgo",
            r"son\s*on\s*g[uü]n": "10daysAgo",
            r"son\s*14\s*g[uü]n": "14daysAgo",
            r"son\s*15\s*g[uü]n": "15daysAgo",
            r"son\s*on\s*be[sş]\s*g[uü]n": "15daysAgo",
            r"son\s*20\s*g[uü]n": "20daysAgo",
            r"son\s*yirmi\s*g[uü]n": "20daysAgo",
            r"son\s*30\s*g[uü]n": "30daysAgo",
            r"son\s*otuz\s*g[uü]n": "30daysAgo",
            r"son\s*45\s*g[uü]n": "45daysAgo",
            r"son\s*60\s*g[uü]n": "60daysAgo",
            r"son\s*altm[iı][sş]\s*g[uü]n": "60daysAgo",
            r"son\s*90\s*g[uü]n": "90daysAgo",
            r"son\s*doksan\s*g[uü]n": "90daysAgo",
            r"son\s*120\s*g[uü]n": "120daysAgo",
            r"son\s*180\s*g[uü]n": "180daysAgo",
            r"son\s*365\s*g[uü]n": "365daysAgo",

            # === SON X HAFTA ===
            # "son hafta" = gecen hafta (last_week), "son 1 hafta" = son 7 gun
            r"son\s*hafta\b": "last_week",
            r"son\s*bir\s*hafta": "7daysAgo",
            r"son\s*1\s*hafta": "7daysAgo",
            r"son\s*2\s*hafta": "14daysAgo",
            r"son\s*iki\s*hafta": "14daysAgo",
            r"son\s*3\s*hafta": "21daysAgo",
            r"son\s*[uü][cç]\s*hafta": "21daysAgo",
            r"son\s*4\s*hafta": "28daysAgo",
            r"son\s*d[oö]rt\s*hafta": "28daysAgo",
            r"son\s*5\s*hafta": "35daysAgo",
            r"son\s*be[sş]\s*hafta": "35daysAgo",
            r"son\s*6\s*hafta": "42daysAgo",
            r"son\s*alt[iı]\s*hafta": "42daysAgo",
            r"son\s*8\s*hafta": "56daysAgo",
            r"son\s*sekiz\s*hafta": "56daysAgo",

            # === SON X AY ===
            # "son ay" = gecen ay (last_month), "son 1 ay" = son 30 gun
            r"son\s*ay\b": "last_month",
            r"son\s*bir\s*ay": "30daysAgo",
            r"son\s*1\s*ay": "30daysAgo",
            r"son\s*2\s*ay": "60daysAgo",
            r"son\s*iki\s*ay": "60daysAgo",
            r"son\s*3\s*ay": "90daysAgo",
            r"son\s*[uü][cç]\s*ay": "90daysAgo",
            r"son\s*4\s*ay": "120daysAgo",
            r"son\s*d[oö]rt\s*ay": "120daysAgo",
            r"son\s*5\s*ay": "150daysAgo",
            r"son\s*be[sş]\s*ay": "150daysAgo",
            r"son\s*6\s*ay": "180daysAgo",
            r"son\s*alt[iı]\s*ay": "180daysAgo",
            r"son\s*yar[iı]m?\s*y[iı]l": "180daysAgo",
            r"son\s*9\s*ay": "270daysAgo",
            r"son\s*dokuz\s*ay": "270daysAgo",
            r"son\s*12\s*ay": "365daysAgo",
            r"son\s*on\s*iki\s*ay": "365daysAgo",

            # === SON X YIL ===
            # "son yil" = gecen yil (last_year), "son 1 yil" = son 365 gun
            r"son\s*y[iı]l\b": "last_year",
            r"son\s*bir\s*y[iı]l": "365daysAgo",
            r"son\s*1\s*y[iı]l": "365daysAgo",
            r"son\s*2\s*y[iı]l": "730daysAgo",
            r"son\s*iki\s*y[iı]l": "730daysAgo",

            # === GECEN/GECTIGIMIZ HAFTA ===
            r"ge[cçcs][cçct]i[gğ]imiz\s*hafta": "last_week",
            r"ge[cçcs]en\s*hafta": "last_week",
            r"[oö]nceki\s*hafta": "last_week",
            r"bir\s*[oö]nceki\s*hafta": "last_week",
            r"gecen\s*hafta": "last_week",
            r"gectigimiz\s*hafta": "last_week",
            r"evvelki\s*hafta": "last_week",

            # === GECEN/GECTIGIMIZ AY ===
            r"ge[cçcs][cçct]i[gğ]imiz\s*ay": "last_month",
            r"ge[cçcs]en\s*ay": "last_month",
            r"[oö]nceki\s*ay": "last_month",
            r"bir\s*[oö]nceki\s*ay": "last_month",
            r"gecen\s*ay": "last_month",
            r"gectigimiz\s*ay": "last_month",
            r"evvelki\s*ay": "last_month",

            # === BU HAFTA / BU AY ===
            r"bu\s*hafta": "this_week",
            r"bu\s*ay": "this_month",
            r"i[cç]inde\s*bulundu[gğ]umuz\s*hafta": "this_week",
            r"i[cç]inde\s*bulundu[gğ]umuz\s*ay": "this_month",
            r"icinde\s*bulundugumuz\s*hafta": "this_week",
            r"icinde\s*bulundugumuz\s*ay": "this_month",
            r"mevcut\s*hafta": "this_week",
            r"mevcut\s*ay": "this_month",
            r"haftanın\s*ba[sş][iı]ndan": "this_week",
            r"haftanin\s*basindan": "this_week",
            r"ay[iı]n\s*ba[sş][iı]ndan": "this_month",
            r"ayin\s*basindan": "this_month",

            # === BU YIL / GECEN YIL ===
            r"bu\s*y[iı]l": "this_year",
            r"bu\s*sene": "this_year",
            r"y[iı]l[iı]n\s*ba[sş][iı]ndan": "this_year",
            r"yilin\s*basindan": "this_year",
            r"ocaktan\s*beri": "this_year",
            r"ocaktan\s*itibaren": "this_year",
            r"ge[cçcs]en\s*y[iı]l": "last_year",
            r"ge[cçcs]en\s*sene": "last_year",
            r"ge[cçcs][cçct]i[gğ]imiz\s*y[iı]l": "last_year",
            r"ge[cçcs][cçct]i[gğ]imiz\s*sene": "last_year",
            r"[oö]nceki\s*y[iı]l": "last_year",
            r"[oö]nceki\s*sene": "last_year",
            r"gecen\s*yil": "last_year",
            r"gecen\s*sene": "last_year",
            r"gectigimiz\s*yil": "last_year",
            r"bir\s*y[iı]l\s*[oö]nceki": "last_year",

            # === CEYREKLER (QUARTERS) ===
            r"bu\s*[cç]eyrek": "this_quarter",
            r"ge[cç]en\s*[cç]eyrek": "last_quarter",
            r"[oö]nceki\s*[cç]eyrek": "last_quarter",
            r"ilk\s*[cç]eyrek": "q1",
            r"birinci\s*[cç]eyrek": "q1",
            r"1\.?\s*[cç]eyrek": "q1",
            r"ikinci\s*[cç]eyrek": "q2",
            r"2\.?\s*[cç]eyrek": "q2",
            r"[uü][cç][uü]nc[uü]\s*[cç]eyrek": "q3",
            r"3\.?\s*[cç]eyrek": "q3",
            r"d[oö]rd[uü]nc[uü]\s*[cç]eyrek": "q4",
            r"4\.?\s*[cç]eyrek": "q4",
            r"son\s*[cç]eyrek": "last_quarter",
            r"q1": "q1",
            r"q2": "q2",
            r"q3": "q3",
            r"q4": "q4",

            # === AY ISIMLERI (tek basina) ===
            r"\bocak\s*ay[iı]?\b": "january",
            r"\b[sş]ubat\s*ay[iı]?\b": "february",
            r"\bmart\s*ay[iı]?\b": "march",
            r"\bnisan\s*ay[iı]?\b": "april",
            r"\bmay[iı]s\s*ay[iı]?\b": "may",
            r"\bhaziran\s*ay[iı]?\b": "june",
            r"\btemmuz\s*ay[iı]?\b": "july",
            r"\ba[gğ]ustos\s*ay[iı]?\b": "august",
            r"\beyl[uü]l\s*ay[iı]?\b": "september",
            r"\bekim\s*ay[iı]?\b": "october",
            r"\bkas[iı]m\s*ay[iı]?\b": "november",
            r"\baral[iı]k\s*ay[iı]?\b": "december",

            # === OZEL GUNLER ===
            r"yeni\s*y[iı]l": "new_year",
            r"y[iı]lba[sş][iı]": "new_year",
        }

        # Sorgu intent'leri - DIKKAT: Daha spesifik intent'ler once tanimlanmali
        self.intents = {
            # person_stats EN ONCE - "muberra kac view aldi" gibi kisi bazli sorgular
            # simple_metric'ten once olmali ki "isim + kac view" sorgusu buraya gelsin
            "person_stats": {
                "patterns": [
                    r"(\w+)\s+\d+\s*[-–]?\s*\d*\s*(ocak|[sş]ubat|mart|nisan|may[i,ı]s|haziran|temmuz|a[gğ]ustos|eyl[uü]l|ekim|kas[i,ı]m|aral[i,ı]k).*ka[cç]",  # "muberra 1 aralıkta kaç"
                    r"(\w+)\s+ka[cç]\s*g[oö]r[uü]nt[uü]len",  # "muberra kaç görüntülenme"
                    r"(\w+)\s+ka[cç]\s*view",                  # "muberra kaç view"
                    r"(\w+)\s+ka[cç]\s*t[i,ı]klama",          # "muberra kaç tıklama"
                    r"(\w+)\s+ka[cç]\s*okuma",                # "muberra kaç okuma"
                    r"(\w+)\s+toplam\s*g[oö]r[uü]nt[uü]len",  # "muberra toplam görüntülenme"
                    r"(\w+)\s+d[uü]n\s*ka[cç]",               # "muberra dün kaç"
                    r"(\w+)\s+bug[uü]n\s*ka[cç]",             # "muberra bugün kaç"
                    r"(\w+)\s+istatisti[gğ]i",                # "muberra istatistiği"
                    r"(\w+)\s+(ald[i,ı]|aldi)",               # "muberra aldı"
                ],
                "handler": self._handle_person_stats
            },
            # simple_metric - "bugün kaç kullanıcı geldi" gibi genel metrik sorulari
            # Kisi ismi OLMAYAN sorgular icin
            "simple_metric": {
                "patterns": [
                    r"^ka[cç]\s*kullan[i,ı]c[i,ı]",              # "kaç kullanıcı" (basta)
                    r"^ka[cç]\s*ki[sş]i",                        # "kaç kişi" (basta)
                    r"^ka[cç]\s*ziyaret[cç]i",                   # "kaç ziyaretçi" (basta)
                    r"^ka[cç]\s*oturum",                         # "kaç oturum" (basta)
                    r"^ka[cç]\s*session",                        # "kaç session" (basta)
                    r"^ka[cç]\s*g[oö]r[uü]nt[uü]len",           # "kaç görüntülenme" (basta)
                    r"^ka[cç]\s*view",                           # "kaç view" (basta)
                    r"bug[uü]n\s*ka[cç]\s*kullan[i,ı]c[i,ı]",   # "bugün kaç kullanıcı"
                    r"d[uü]n\s*ka[cç]\s*kullan[i,ı]c[i,ı]",     # "dün kaç kullanıcı"
                    r"bug[uü]n\s*ka[cç]\s*ki[sş]i",             # "bugün kaç kişi"
                    r"d[uü]n\s*ka[cç]\s*ki[sş]i",               # "dün kaç kişi"
                    r"bug[uü]n\s*ka[cç]\s*oturum",              # "bugün kaç oturum"
                    r"d[uü]n\s*ka[cç]\s*oturum",                # "dün kaç oturum"
                    r"bug[uü]n\s*ka[cç]\s*g[oö]r[uü]nt[uü]",   # "bugün kaç görüntülenme"
                    r"d[uü]n\s*ka[cç]\s*g[oö]r[uü]nt[uü]",     # "dün kaç görüntülenme"
                    r"toplam\s*kullan[i,ı]c[i,ı]\s*ka[cç]",     # "toplam kullanıcı kaç"
                    r"toplam\s*oturum\s*ka[cç]",                # "toplam oturum kaç"
                ],
                "handler": self._handle_simple_metric
            },
            # popular_editors once tanimlanmali (top_pages'den once) - "en populer editor" icin
            "popular_editors": {
                "patterns": [
                    r"pop[uü]ler\s*edit[oö]r",
                    r"en\s*pop[uü]ler\s*edit[oö]r",
                    r"edit[oö]r\s*listesi",
                    r"edit[oö]r\s*s[i,ı]ralama",
                ],
                "handler": self._handle_popular_editors
            },
            "top_pages": {
                "patterns": [
                    r"en\s*[c,ç]ok\s*okunan",
                    r"en\s*pop[uü]ler\s*(sayfa|haber|i[c,ç]erik)?$",  # Sadece "en populer" + sayfa/haber veya bos
                    r"en\s*[c,ç]ok\s*g[oö]r[uü]nt[uü]lenen",
                    r"en\s*[c,ç]ok\s*t[i,ı]klanan",
                    r"top\s*sayfa",
                    r"hit\s*haber",
                ],
                "handler": self._handle_top_pages
            },
            "traffic_sources": {
                "patterns": [
                    r"trafik\s*kayna[gğ]",
                    r"nereden\s*gel",
                    r"kanal\s*da[gğ][i,ı]l[i,ı]m",
                    r"organic|direct|social|referral",
                    r"kaynak\s*da[gğ][i,ı]l[i,ı]m",
                ],
                "handler": self._handle_traffic_sources
            },
            "category_performance": {
                "patterns": [
                    r"kategori\s*performans",
                    r"kategori\s*da[gğ][i,ı]l[i,ı]m",
                    r"hangi\s*kategori",
                    r"kategori\s*[oö]zet",
                    r"d[uü]n[uü]n\s*kategori",
                ],
                "handler": self._handle_category_performance
            },
            "editor_performance": {
                "patterns": [
                    r"edit[oö]r\s*performans",
                    r"edit[oö]r\s*da[gğ][i,ı]l[i,ı]m",
                    r"hangi\s*edit[oö]r",
                    r"en\s*[c,ç]ok\s*yazan",
                    r"edit[oö]r[uü]?\s+\w+",  # "editor cansu", "editoru ahmet"
                    r"\w+\s+edit[oö]r[uü]",   # "cansu editoru"
                ],
                "handler": self._handle_editor_performance
            },
            "device_breakdown": {
                "patterns": [
                    r"cihaz\s*da[gğ][i,ı]l[i,ı]m",
                    r"mobil|desktop|tablet",
                    r"hangi\s*cihaz",
                    r"cihaz\s*t[uü]r",
                ],
                "handler": self._handle_device_breakdown
            },
            "city_breakdown": {
                "patterns": [
                    r"[sş]ehir\s*da[gğ][i,ı]l[i,ı]m",
                    r"hangi\s*[sş]ehir",
                    r"nereden\s*gir",
                    r"co[gğ]rafi",
                    r"lokasyon",
                ],
                "handler": self._handle_city_breakdown
            },
            "hourly_traffic": {
                "patterns": [
                    r"saat\s*da[gğ][i,ı]l[i,ı]m",
                    r"saatlik\s*trafik",
                    r"hangi\s*saat",
                    r"saat\s*ba[zs][i,ı]nda",
                ],
                "handler": self._handle_hourly_traffic
            },
            "daily_trend": {
                "patterns": [
                    r"g[uü]nl[uü]k\s*trend",
                    r"g[uü]nl[uü]k\s*de[gğ]i[sş]im",
                    r"son\s*\d+\s*g[uü]n.*trend",
                    r"trafik\s*trend",
                ],
                "handler": self._handle_daily_trend
            },
            "summary": {
                "patterns": [
                    r"genel\s*bak[i,ı][sş]",
                    r"[oö]zet",
                    r"genel\s*durum",
                    r"nas[i,ı]l\s*gidiyor",
                    r"performans\s*nas[i,ı]l",
                ],
                "handler": self._handle_summary
            },
            "compare": {
                "patterns": [
                    r"kar[sş][i,ı]la[sş]t[i,ı]r",
                    r"ge[c,ç]en\s*haftaya\s*g[oö]re",
                    r"[oö]nceki\s*g[uü]ne\s*g[oö]re",
                    r"de[gğ]i[sş]im\s*oran[i,ı]",
                    r"art[i,ı][sş]|azal[i,ı][sş]",
                ],
                "handler": self._handle_compare
            },
            "author_performance": {
                "patterns": [
                    r"yazar\s*performans",
                    r"yazar\s*da[gğ][i,ı]l[i,ı]m",
                    r"hangi\s*yazar",
                    r"en\s*[c,ç]ok\s*okunan\s*yazar",
                    r"k[oö][sş]e\s*yazar",
                    r"yazar\s*istatistik",
                ],
                "handler": self._handle_author_performance
            },
            "news_type": {
                "patterns": [
                    r"haber\s*tipi",
                    r"haber\s*t[uü]r[uü]",
                    r"video\s*haber",
                    r"galeri\s*haber",
                    r"i[c,ç]erik\s*tipi",
                    r"video|galeri|foto",
                ],
                "handler": self._handle_news_type
            },
            "tag_analysis": {
                "patterns": [
                    r"etiket\s*analiz",
                    r"tag\s*analiz",
                    r"hangi\s*etiket",
                    r"pop[uü]ler\s*etiket",
                    r"en\s*[c,ç]ok\s*etiket",
                ],
                "handler": self._handle_tag_analysis
            },
            "content_age": {
                "patterns": [
                    r"eski\s*haber",
                    r"yeni\s*haber",
                    r"bug[uü]n\s*yay[i,ı]nlanan",
                    r"ka[c,ç]\s*g[uü]nl[uü]k",
                    r"i[c,ç]erik\s*ya[sş]",
                ],
                "handler": self._handle_content_age
            },
            "browser_analysis": {
                "patterns": [
                    r"taray[i,ı]c[i,ı]\s*da[gğ][i,ı]l[i,ı]m",
                    r"browser",
                    r"chrome|safari|firefox|edge",
                    r"hangi\s*taray[i,ı]c[i,ı]",
                ],
                "handler": self._handle_browser_analysis
            },
            "os_analysis": {
                "patterns": [
                    r"i[sş]letim\s*sistemi",
                    r"operating\s*system",
                    r"windows|mac|ios|android",
                    r"hangi\s*i[sş]letim",
                ],
                "handler": self._handle_os_analysis
            },
            "landing_pages": {
                "patterns": [
                    r"giri[sş]\s*sayfa",
                    r"landing\s*page",
                    r"ilk\s*sayfa",
                    r"nereden\s*gir",
                ],
                "handler": self._handle_landing_pages
            },
            "exit_pages": {
                "patterns": [
                    r"[c,ç][i,ı]k[i,ı][sş]\s*sayfa",
                    r"exit\s*page",
                    r"terk\s*edilen",
                    r"son\s*sayfa",
                ],
                "handler": self._handle_exit_pages
            },
            "new_vs_returning": {
                "patterns": [
                    r"yeni\s*kullan[i,ı]c[i,ı]",
                    r"geri\s*d[oö]nen",
                    r"returning",
                    r"yeni\s*mi\s*eski\s*mi",
                ],
                "handler": self._handle_new_vs_returning
            },
            "real_time": {
                "patterns": [
                    r"[sş]u\s*an",
                    r"canl[i,ı]",
                    r"real\s*time",
                    r"anl[i,ı]k",
                    r"[sş]imdi",
                ],
                "handler": self._handle_real_time
            },
            "daily_users": {
                "patterns": [
                    r"ka[cç]\s*kullan[i,ı]c[i,ı]",
                    r"toplam\s*kullan[i,ı]c[i,ı]",
                    r"kullan[i,ı]c[i,ı]\s*say[i,ı]s[i,ı]",
                    r"ziyaret[cç]i\s*say[i,ı]s[i,ı]",
                    r"ka[cç]\s*ki[sş]i",
                ],
                "handler": self._handle_daily_users
            },
            "weekly_trend": {
                "patterns": [
                    r"haftal[i,ı]k\s*trend",
                    r"haftal[i,ı]k\s*rapor",
                    r"son\s*7\s*g[uü]n\s*trend",
                    r"haftan[i,ı]n\s*trend",
                ],
                "handler": self._handle_weekly_trend
            },
            "device_ratio": {
                "patterns": [
                    r"mobil\s*oran",
                    r"desktop\s*oran",
                    r"cihaz\s*oran",
                    r"mobil\s*y[uü]zde",
                ],
                "handler": self._handle_device_ratio
            },
        }

        # Hizli sorgu komutlari - Ana menu
        self.quick_commands = {
            "1": ("En cok okunan sayfalar (dun)", lambda: self._handle_top_pages("dun")),
            "2": ("Trafik kaynaklari (dun)", lambda: self._handle_traffic_sources("dun")),
            "3": ("Kategori performansi (son 7 gun)", lambda: self._handle_category_performance("son 7 gun")),
            "4": ("Editor performansi (son 7 gun)", lambda: self._handle_editor_performance("son 7 gun")),
            "5": ("Yazar performansi (son 7 gun)", lambda: self._handle_author_performance("son 7 gun")),
            "6": ("Cihaz dagilimi (dun)", lambda: self._handle_device_breakdown("dun")),
            "7": ("Sehir dagilimi (dun)", lambda: self._handle_city_breakdown("dun")),
            "8": ("Haber tipi dagilimi (son 7 gun)", lambda: self._handle_news_type("son 7 gun")),
            "9": ("Genel ozet (dun)", lambda: self._handle_summary("dun")),
            "0": ("Haftalik karsilastirma", lambda: self._handle_compare("")),
            # Ek komutlar
            "11": ("Saatlik trafik (dun)", lambda: self._handle_hourly_traffic("dun")),
            "12": ("Gunluk trend (son 30 gun)", lambda: self._handle_daily_trend("son 30 gun")),
            "13": ("Etiket analizi (son 7 gun)", lambda: self._handle_tag_analysis("son 7 gun")),
            "14": ("Tarayici dagilimi (dun)", lambda: self._handle_browser_analysis("dun")),
            "15": ("Isletim sistemi (dun)", lambda: self._handle_os_analysis("dun")),
            "16": ("Giris sayfalari (dun)", lambda: self._handle_landing_pages("dun")),
            "17": ("Cikis sayfalari (dun)", lambda: self._handle_exit_pages("dun")),
            "18": ("Yeni vs Geri donen (dun)", lambda: self._handle_new_vs_returning("dun")),
            "19": ("Anlik durum (bugun)", lambda: self._handle_real_time("bugun")),
        }

    def switch_brand(self, brand: str) -> bool:
        """
        Aktif markayi degistir

        Args:
            brand: Yeni marka adi

        Returns:
            Basarili ise True
        """
        if self.client.switch_brand(brand):
            self.brand = brand
            # Matcher'lari guncelle
            self.editor_matcher = EditorMatcher(self.client)
            self.author_matcher = AuthorMatcher(self.client)
            return True
        return False

    def get_current_brand(self) -> str:
        """Aktif markayi dondur"""
        return self.client.brand_name

    def _filter_not_set_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        DataFrame'den (not set) ve bos satirlari filtrele

        Args:
            df: DataFrame

        Returns:
            Filtrelenmis DataFrame
        """
        if df.empty:
            return df

        result_df = df.copy()

        # Tum sutunlarda (not set) ve bos degerleri kontrol et
        for col in result_df.columns:
            # Sadece object (string) sutunlarinda filtrele
            if result_df[col].dtype == 'object':
                # (not set), bos string, None degerleri filtrele
                mask = ~(
                    (result_df[col] == "(not set)") |
                    (result_df[col] == "") |
                    (result_df[col].isna()) |
                    (result_df[col].astype(str).str.strip() == "")
                )
                result_df = result_df[mask]

        return result_df.reset_index(drop=True)

    def _add_percentage_columns(self, df: pd.DataFrame, exclude_cols: List[str] = None) -> pd.DataFrame:
        """
        DataFrame'e oran sutunlari ekle
        Her numerik sutun icin toplama gore yuzde orani hesaplar
        Oran sutunlari ilgili sutunun hemen yanina eklenir

        Args:
            df: DataFrame
            exclude_cols: Oran hesaplanmayacak sutunlar (ornegin tarih, isim vb.)

        Returns:
            Oran sutunlari ekli DataFrame
        """
        if df.empty:
            return df

        if exclude_cols is None:
            exclude_cols = []

        # Sistem sutunlarini ve tarih sutunlarini da haric tut
        system_cols = ["_chart_type", "Tarih", "Gun", "Saat", "Hafta"]
        exclude_cols = exclude_cols + system_cols

        # Yeni sutun siralamasini olustur
        new_columns = []
        pct_data = {}

        for col in df.columns:
            new_columns.append(col)

            # Haric tutulan sutunlari atla
            if col in exclude_cols:
                continue

            # Sadece numerik sutunlarda oran hesapla
            if pd.api.types.is_numeric_dtype(df[col]):
                total = df[col].sum()
                if total > 0:
                    # Oran sutunu ekle (her deger/toplam * 100)
                    pct_col_name = f"{col} %"
                    pct_data[pct_col_name] = (df[col] / total * 100).round(1)
                    # Yuzde sutununu ilgili sutunun hemen arkasina ekle
                    new_columns.append(pct_col_name)

        # Yeni DataFrame olustur
        result_df = df.copy()
        for pct_col, pct_values in pct_data.items():
            result_df[pct_col] = pct_values

        # Sutunlari yeniden sirala (yuzde sutunlari ilgili sutunun yaninda)
        result_df = result_df[new_columns]

        return result_df

    def _extract_date_range(self, query: str) -> Tuple[str, str]:
        """Sorgudan tarih araligini cikar"""
        query_lower = query.lower()

        # Turkce ay isimleri
        months = {
            "ocak": 1, "şubat": 2, "subat": 2, "mart": 3, "nisan": 4,
            "mayıs": 5, "mayis": 5, "haziran": 6, "temmuz": 7, "ağustos": 8,
            "agustos": 8, "eylül": 9, "eylul": 9, "ekim": 10, "kasım": 11,
            "kasim": 11, "aralık": 12, "aralik": 12
        }

        # ONCE tarih araligi kontrol et (1-7 aralik gibi)
        # Tarih araligi pattern'i: "1-5 aralık", "10-15 kasım", "1-7 aralik"
        date_range_match = re.search(
            r"(\d{1,2})\s*[-–]\s*(\d{1,2})\s*(ocak|[sş]ubat|mart|nisan|may[i,ı]s|haziran|temmuz|a[gğ]ustos|eyl[uü]l|ekim|kas[i,ı]m|aral[i,ı]k)",
            query_lower
        )

        if date_range_match:
            start_day = int(date_range_match.group(1))
            end_day = int(date_range_match.group(2))
            month_str = date_range_match.group(3)

            month_normalized = month_str.replace("ş", "s").replace("ı", "i").replace("ğ", "g").replace("ü", "u")
            month = months.get(month_normalized) or months.get(month_str)

            if month:
                current_date = datetime.now()
                year = current_date.year
                if month > current_date.month:
                    year -= 1

                try:
                    start_date = datetime(year, month, start_day)
                    end_date = datetime(year, month, end_day)
                    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
                except ValueError:
                    pass

        # Spesifik tarih pattern'i: "1 aralık", "15 kasım", "3 ocak"
        specific_date_match = re.search(
            r"(\d{1,2})\s*(ocak|[sş]ubat|mart|nisan|may[i,ı]s|haziran|temmuz|a[gğ]ustos|eyl[uü]l|ekim|kas[i,ı]m|aral[i,ı]k)",
            query_lower
        )

        if specific_date_match:
            day = int(specific_date_match.group(1))
            month_str = specific_date_match.group(2)

            # Ay ismini normalize et
            month_normalized = month_str.replace("ş", "s").replace("ı", "i").replace("ğ", "g").replace("ü", "u")
            month = months.get(month_normalized) or months.get(month_str)

            if month and 1 <= day <= 31:
                # Yil: eger ay su anki aydan buyukse gecen yil, degilse bu yil
                current_date = datetime.now()
                year = current_date.year
                if month > current_date.month or (month == current_date.month and day > current_date.day):
                    year -= 1

                try:
                    specific_date = datetime(year, month, day)
                    date_str = specific_date.strftime("%Y-%m-%d")
                    return date_str, date_str
                except ValueError:
                    pass  # Gecersiz tarih, devam et

        # Standart pattern'ler
        for pattern, date_value in self.date_patterns.items():
            if re.search(pattern, query_lower):
                today = datetime.now()

                # === BUGUN / DUN ===
                if date_value == "today":
                    return "today", "today"
                elif date_value == "yesterday":
                    return "yesterday", "yesterday"

                # === SON X GUN (dinamik) ===
                elif date_value.endswith("daysAgo"):
                    days = int(date_value.replace("daysAgo", ""))
                    start_date = today - timedelta(days=days)
                    end_date = today - timedelta(days=1)  # dune kadar
                    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

                # === GECEN HAFTA (Pazartesi-Pazar) ===
                elif date_value == "last_week":
                    # Gecen haftanin Pazartesi gunu
                    days_since_monday = today.weekday()  # 0=Pazartesi
                    this_monday = today - timedelta(days=days_since_monday)
                    last_monday = this_monday - timedelta(days=7)
                    last_sunday = last_monday + timedelta(days=6)
                    return last_monday.strftime("%Y-%m-%d"), last_sunday.strftime("%Y-%m-%d")

                # === GECEN AY (1 - son gun) ===
                elif date_value == "last_month":
                    first_of_this_month = today.replace(day=1)
                    last_day_of_prev_month = first_of_this_month - timedelta(days=1)
                    first_of_prev_month = last_day_of_prev_month.replace(day=1)
                    return first_of_prev_month.strftime("%Y-%m-%d"), last_day_of_prev_month.strftime("%Y-%m-%d")

                # === BU HAFTA (Pazartesi - bugun) ===
                elif date_value == "this_week":
                    days_since_monday = today.weekday()
                    this_monday = today - timedelta(days=days_since_monday)
                    return this_monday.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")

                # === BU AY (1 - bugun) ===
                elif date_value == "this_month":
                    first_of_this_month = today.replace(day=1)
                    return first_of_this_month.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")

                # === BU YIL (1 Ocak - bugun) ===
                elif date_value == "this_year":
                    first_of_year = today.replace(month=1, day=1)
                    return first_of_year.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")

                # === GECEN YIL (1 Ocak - 31 Aralik) ===
                elif date_value == "last_year":
                    last_year = today.year - 1
                    first_of_last_year = datetime(last_year, 1, 1)
                    last_of_last_year = datetime(last_year, 12, 31)
                    return first_of_last_year.strftime("%Y-%m-%d"), last_of_last_year.strftime("%Y-%m-%d")

                # === GECEN HAFTA SONU (Cumartesi-Pazar) ===
                elif date_value == "last_weekend":
                    days_since_sunday = (today.weekday() + 1) % 7  # Pazar=0
                    last_sunday = today - timedelta(days=days_since_sunday)
                    if days_since_sunday == 0:  # Bugun Pazar ise gecen hafta sonunu al
                        last_sunday = today - timedelta(days=7)
                    last_saturday = last_sunday - timedelta(days=1)
                    return last_saturday.strftime("%Y-%m-%d"), last_sunday.strftime("%Y-%m-%d")

                # === BU HAFTA SONU ===
                elif date_value == "this_weekend":
                    days_until_saturday = (5 - today.weekday()) % 7
                    if days_until_saturday == 0 and today.weekday() != 5:
                        days_until_saturday = 7
                    this_saturday = today + timedelta(days=days_until_saturday)
                    this_sunday = this_saturday + timedelta(days=1)
                    # Eger zaten hafta sonu ise bugunun tarihini kullan
                    if today.weekday() >= 5:  # Cumartesi veya Pazar
                        this_saturday = today - timedelta(days=today.weekday()-5) if today.weekday() == 6 else today
                        this_sunday = this_saturday + timedelta(days=1)
                    return this_saturday.strftime("%Y-%m-%d"), this_sunday.strftime("%Y-%m-%d")

                # === BU CEYREK ===
                elif date_value == "this_quarter":
                    quarter = (today.month - 1) // 3 + 1
                    quarter_start_month = (quarter - 1) * 3 + 1
                    start = datetime(today.year, quarter_start_month, 1)
                    return start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")

                # === GECEN CEYREK ===
                elif date_value == "last_quarter":
                    quarter = (today.month - 1) // 3 + 1
                    if quarter == 1:
                        # Q1'de isek gecen ceyrek Q4 (gecen yil)
                        start = datetime(today.year - 1, 10, 1)
                        end = datetime(today.year - 1, 12, 31)
                    else:
                        prev_quarter = quarter - 1
                        start_month = (prev_quarter - 1) * 3 + 1
                        end_month = prev_quarter * 3
                        start = datetime(today.year, start_month, 1)
                        # Ayin son gunu
                        if end_month == 12:
                            end = datetime(today.year, 12, 31)
                        else:
                            end = datetime(today.year, end_month + 1, 1) - timedelta(days=1)
                    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

                # === SPESIFIK CEYREKLER (Q1, Q2, Q3, Q4) ===
                elif date_value in ["q1", "q2", "q3", "q4"]:
                    quarter_num = int(date_value[1])
                    start_month = (quarter_num - 1) * 3 + 1
                    end_month = quarter_num * 3
                    year = today.year
                    # Eger ceyrek henuz gelmemisse gecen yili kullan
                    if start_month > today.month:
                        year -= 1
                    start = datetime(year, start_month, 1)
                    if end_month == 12:
                        end = datetime(year, 12, 31)
                    else:
                        end = datetime(year, end_month + 1, 1) - timedelta(days=1)
                    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

                # === AY ISIMLERI ===
                elif date_value in ["january", "february", "march", "april", "may", "june",
                                    "july", "august", "september", "october", "november", "december"]:
                    month_map = {
                        "january": 1, "february": 2, "march": 3, "april": 4,
                        "may": 5, "june": 6, "july": 7, "august": 8,
                        "september": 9, "october": 10, "november": 11, "december": 12
                    }
                    month = month_map[date_value]
                    year = today.year
                    # Eger ay henuz gelmemisse veya su an o aydaysak bu yil, yoksa gecen yil
                    if month > today.month:
                        year -= 1
                    start = datetime(year, month, 1)
                    if month == 12:
                        end = datetime(year, 12, 31)
                    else:
                        end = datetime(year, month + 1, 1) - timedelta(days=1)
                    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

                # === YENI YIL / YILBASI ===
                elif date_value == "new_year":
                    # Son yilbasi gunu (1 Ocak)
                    year = today.year if today.month > 1 or (today.month == 1 and today.day > 1) else today.year - 1
                    new_year_date = datetime(year, 1, 1)
                    return new_year_date.strftime("%Y-%m-%d"), new_year_date.strftime("%Y-%m-%d")

        # Varsayilan: dun
        return "yesterday", "yesterday"

    def _extract_category(self, query: str) -> Optional[str]:
        """Sorgudan kategori cikar - kapsamli pattern destegi"""
        # Her kategori icin birden fazla pattern
        categories = {
            "Spor": [
                r"\bspor\b", r"futbol", r"basketbol", r"voleybol",
                r"fenerbah[cç]e", r"galatasaray", r"be[sş]ikta[sş]", r"trabzonspor",
                r"s[uü]per\s*lig", r"[sş]ampiyonlar\s*ligi", r"champions\s*league",
                r"ma[cç]\s*sonu[cç]", r"puan\s*durumu", r"transfer",
                r"milli\s*tak[iı]m", r"euro\s*\d+", r"olimpiyat",
                r"tenis", r"formula", r"f1", r"motorsport",
            ],
            "Ekonomi": [
                r"\bekonomi\b", r"ekonomik", r"finans", r"finansal",
                r"borsa", r"bist", r"dolar", r"euro\b", r"alt[iı]n",
                r"faiz", r"enflasyon", r"merkez\s*bankas[iı]",
                r"kur", r"d[oö]viz", r"yat[iı]r[iı]m", r"hisse",
                r"kripto", r"bitcoin", r"piyasa", r"ticaret",
                r"i[sş]\s*d[uü]nyas[iı]", r"[sş]irket", r"vergi",
            ],
            "Magazin": [
                r"\bmagazin\b", r"[uü]nl[uü]", r"[uü]nl[uü]ler",
                r"sosyete", r"celebrity", r"[sş][oö]hret",
                r"dizi", r"film", r"sinema", r"oyuncu",
                r"[sş]ark[iı]c[iı]", r"sanat[cç][iı]", r"pop[uü]ler",
                r"moda", r"fashion", r"g[uü]zellik", r"stil",
                r"d[uü][gğ][uü]n", r"evlilik", r"bo[sş]anma",
                r"dedikodu", r"scandal", r"olay",
            ],
            "Gundem": [
                r"g[uü]ndem", r"g[uü]ncel", r"son\s*dakika",
                r"breaking", r"fla[sş]", r"a[cç][iı]klama",
                r"haberleri?\b", r"geli[sş]me",
                r"olay", r"vaka", r"kaza", r"yang[iı]n",
                r"deprem", r"sel", r"afet", r"do[gğ]al\s*afet",
            ],
            "Siyaset": [
                r"siyaset", r"siyasi", r"politik", r"politika",
                r"se[cç]im", r"oy", r"sand[iı]k", r"milletvekili",
                r"cumhurba[sş]kan", r"ba[sş]bakan", r"bakan\b",
                r"meclis", r"tbmm", r"h[uü]k[uü]met", r"muhalefet",
                r"parti\b", r"akp", r"chp", r"mhp", r"iyi\s*parti",
                r"belediye", r"vali", r"kaymakam",
            ],
            "Teknoloji": [
                r"teknoloji", r"tech", r"bilim", r"bilimsel",
                r"iphone", r"android", r"samsung", r"apple",
                r"google", r"microsoft", r"facebook", r"meta",
                r"yapay\s*zeka", r"ai\b", r"robot", r"otonom",
                r"uzay", r"nasa", r"spacex", r"roket",
                r"siber", r"hack", r"g[uü]venlik",
                r"oyun", r"gaming", r"playstation", r"xbox",
                r"uygulama", r"app", r"yaz[iı]l[iı]m", r"software",
            ],
            "Saglik": [
                r"sa[gğ]l[iı]k", r"saglik", r"sağlık",
                r"hastane", r"doktor", r"hekim", r"t[iı]p",
                r"hastal[iı]k", r"tedavi", r"ila[cç]", r"a[sş][iı]",
                r"covid", r"korona", r"vir[uü]s", r"grip",
                r"kanser", r"diyabet", r"kalp", r"tansiyon",
                r"diyet", r"beslenme", r"zay[iı]flama", r"kilo",
                r"fitness", r"spor\s*sa[gğ]l[iı]k", r"psikoloji",
            ],
            "Kultur": [
                r"k[uü]lt[uü]r", r"kultur", r"kültür",
                r"sanat", r"sergi", r"m[uü]ze", r"tiyatro",
                r"konser", r"festival", r"etkinlik",
                r"kitap", r"yazar\b", r"edebiyat", r"roman",
                r"tarih", r"tarihi", r"arkeoloji", r"antik",
            ],
            "Yasam": [
                r"ya[sş]am", r"yasam", r"yaşam", r"lifestyle",
                r"seyahat", r"gezi", r"tatil", r"turizm",
                r"yemek", r"tarif", r"mutfak", r"restoran",
                r"dekorasyon", r"ev", r"bahçe", r"garden",
                r"aile", r"[cç]ocuk", r"e[gğ]itim", r"okul",
                r"ili[sş]ki", r"a[sş]k", r"evlilik",
                r"hobiler", r"el\s*i[sş]i", r"diy",
            ],
            "Otomobil": [
                r"otomobil", r"araba", r"ara[cç]", r"car",
                r"otomotiv", r"automotive", r"vas[iı]ta",
                r"bmw", r"mercedes", r"audi", r"volkswagen",
                r"toyota", r"honda", r"ford", r"renault",
                r"elektrikli\s*ara[cç]", r"tesla", r"ev\s*car",
                r"motor", r"yak[iı]t", r"benzin", r"dizel",
                r"trafik", r"ehliyet", r"sigorta",
            ],
            "Dunya": [
                r"d[uü]nya", r"dunya", r"dünya", r"world",
                r"uluslararas[iı]", r"international", r"global",
                r"abd", r"amerika", r"avrupa", r"rusya",
                r"[cç]in", r"japonya", r"almanya", r"fransa",
                r"ingiltere", r"[iİ]ngiltere", r"uk\b", r"eu\b",
                r"orta\s*do[gğ]u", r"suriye", r"irak", r"iran",
                r"sava[sş]", r"bar[iı][sş]", r"diplomasi",
                r"bm\b", r"nato", r"birle[sş]mi[sş]\s*milletler",
            ],
            "Egitim": [
                r"e[gğ]itim", r"egitim", r"eğitim", r"education",
                r"okul", r"[uü]niversite", r"lise", r"ilkokul",
                r"[oö][gğ]renci", r"[oö][gğ]retmen", r"hoca",
                r"s[iı]nav", r"y[kö]s", r"lgs", r"kpss", r"ales",
                r"burs", r"mezuniyet", r"diploma",
            ],
            "Astroloji": [
                r"astroloji", r"bur[cç]", r"hor[ao]skop",
                r"ko[cç]", r"bo[gğ]a", r"ikizler", r"yenge[cç]",
                r"aslan", r"ba[sş]ak", r"terazi", r"akrep",
                r"yay\b", r"o[gğ]lak", r"kova", r"bal[iı]k",
                r"gezegen", r"y[iı]ld[iı]z", r"ay\s*tutulmas[iı]",
            ],
        }

        query_lower = query.lower()
        for category, patterns in categories.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return category

        return None

    def _extract_newstype(self, query: str) -> Optional[str]:
        """
        Sorgudan icerik turu (newstype/pagetype) cikar.

        Ornek sorgular:
        - "video icerikleri kac view aldi"
        - "galeri haberleri performansi"
        - "foto galeri kac goruntulendi"

        Returns:
            GA4'te newstype degerine uygun string veya None
        """
        query_lower = query.lower()

        # Newstype pattern'leri - GA4'teki gercek degerlere eslesir
        # GA4 newstype degerleri: haber, newsgaleri, video, gazete-haberi, yazar,
        # plus, seo-content-haber, ozel-haber, derleme-haber, viral, vb.
        newstype_patterns = {
            # === VIDEO ICERIKLERI ===
            "video": [
                r"video\s*(icerik|içerik|haber|i[cç]erikler)?",
                r"videolar", r"video\s*haber",
                r"canl[iı]\s*yay[iı]n", r"live\s*stream",
                r"youtube", r"izle", r"izleme",
                r"klip", r"video\s*klip",
            ],

            # === GALERI ICERIKLERI (GA4: newsgaleri) ===
            "newsgaleri": [
                r"galeri\s*(icerik|içerik|haber|i[cç]erikler)?",
                r"galeriler", r"foto\s*galeri",
                r"resim\s*galeri", r"g[oö]rsel\s*galeri",
                r"foto[gğ]raf\s*(galeri)?", r"image\s*gallery",
                r"slide\s*show", r"slayt",
            ],

            # === OZEL HABER (spesifik - once kontrol edilmeli) ===
            "ozel-haber": [
                r"[oö]zel\s*haber", r"ozel\s*haber",
                r"exclusive", r"[oö]zel\s*dosya",
                r"ara[sş]t[iı]rma\s*haber", r"investigative",
                r"[oö]zel\s*r[oö]portaj",
            ],

            # === AJANS HABERI (spesifik - once kontrol edilmeli) ===
            "ajans-haberi": [
                r"ajans\s*haber", r"wire", r"agency",
                r"\baa\b", r"reuters", r"afp", r"\bdha\b",
                r"anadolu\s*ajans",
            ],

            # === BBC / DW HABERI (spesifik) ===
            "bbc-haberi": [
                r"bbc\s*haber", r"bbc\s*t[uü]rk[cç]e",
            ],
            "dw-haberi": [
                r"dw\s*haber", r"deutsche\s*welle",
            ],

            # === YAZAR / KOSE YAZISI ===
            "yazar": [
                r"k[oö][sş]e\s*yaz[iı]", r"kose\s*yazisi", r"köşe\s*yazısı",
                r"yorum\s*yaz[iı]", r"g[oö]r[uü][sş]", r"analiz",
                r"yazar\s*(yaz[iı]|icerik|içerik)?",
                r"opinion", r"editorial", r"k[oö][sş]e\s*yazar",
                r"yazar\s*k[oö][sş]e",
            ],

            # === HABER / MAKALE (genel - en son kontrol edilmeli) ===
            "haber": [
                r"(?<![oö]zel\s)(?<!ajans\s)\bhaber\b", # ozel haber ve ajans haber haric
                r"haberler(?!\s*i)",  # haberleri haric (ajans haberleri gibi)
                r"makale", r"makaleler",
                r"man[sş]et", r"ba[sş]l[iı]k",
                r"h[iı]k[aâ]ye", r"story",
            ],

            # === DERLEME HABER ===
            "derleme-haber": [
                r"derleme", r"compilation",
                r"[oö]zet", r"summary",
                r"toplu\s*haber", r"round\s*up",
            ],

            # === PLUS / PREMIUM ===
            "plus": [
                r"plus\s*(icerik|içerik)?", r"premium",
                r"[uü]yelik", r"membership",
                r"[oö]zel\s*i[cç]erik", r"exclusive\s*content",
                r"paral[iı]\s*i[cç]erik",
            ],

            # === VIRAL ===
            "viral": [
                r"viral", r"trending", r"pop[uü]ler",
                r"[cç]ok\s*payla[sş][iı]lan", r"most\s*shared",
                r"sosyal\s*medya\s*fenomen",
            ],

            # === INTERAKTIF ===
            "interactive": [
                r"interaktif", r"interactive",
                r"etkile[sş]imli", r"anket", r"quiz",
                r"test\b", r"oyun\s*haber",
            ],

            # === GAZETE HABERI ===
            "gazete-haberi": [
                r"gazete\s*haber", r"bas[iı]l[iı]\s*haber",
                r"print", r"gazete\s*man[sş]et",
                r"gazete\s*sayfas[iı]",
            ],

            # === SEO CONTENT ===
            "seo-content-haber": [
                r"seo\s*(content|i[cç]erik)?",
                r"evergreen", r"rehber",
                r"nas[iı]l\s*yap[iı]l[iı]r", r"how\s*to",
                r"en\s*iyi\s*\d+", r"top\s*\d+\s*list",
            ],
        }

        for newstype, patterns in newstype_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return newstype

        return None

    def _extract_limit(self, query: str) -> Optional[int]:
        """
        Sorgudan sonuc limitini cikar.

        Ornek sorgular:
        - "en cok 10 editor"
        - "top 5 kategori"
        - "ilk 20 haber"

        Returns:
            Limit sayisi veya None
        """
        query_lower = query.lower()

        # Limit pattern'leri
        limit_patterns = [
            # top X, en cok X
            (r"top\s*(\d+)", 1),
            (r"en\s*[cç]ok\s*(\d+)", 1),
            (r"en\s*fazla\s*(\d+)", 1),
            (r"en\s*y[uü]ksek\s*(\d+)", 1),
            (r"en\s*iyi\s*(\d+)", 1),

            # ilk X, ilk X tane
            (r"ilk\s*(\d+)", 1),
            (r"ba[sş]ta(ki)?\s*(\d+)", 2),

            # son X, son X tane
            (r"son\s*(\d+)\s*(tane|adet)?(?!\s*(g[uü]n|hafta|ay|y[iı]l))", 1),

            # X tane, X adet
            (r"(\d+)\s*tane", 1),
            (r"(\d+)\s*adet", 1),

            # en az X
            (r"en\s*az\s*(\d+)", 1),

            # limit X
            (r"limit\s*(\d+)", 1),
        ]

        for pattern, group in limit_patterns:
            match = re.search(pattern, query_lower)
            if match:
                try:
                    return int(match.group(group))
                except (ValueError, IndexError):
                    pass

        # Varsayilan limit pattern'leri (sayi olmadan)
        default_limits = {
            r"en\s*[cç]ok": 10,
            r"en\s*pop[uü]ler": 10,
            r"en\s*ba[sş]ar[iı]l[iı]": 10,
            r"en\s*y[uü]ksek": 10,
            r"en\s*d[uü][sş][uü]k": 10,
            r"en\s*az": 10,
        }

        for pattern, default in default_limits.items():
            if re.search(pattern, query_lower):
                return default

        return None

    def _extract_sort_order(self, query: str) -> Optional[str]:
        """
        Sorgudan siralama yonunu cikar.

        Returns:
            "desc" (buyukten kucuge) veya "asc" (kucukten buyuge) veya None
        """
        query_lower = query.lower()

        # Azalan siralama (desc)
        desc_patterns = [
            r"en\s*[cç]ok", r"en\s*fazla", r"en\s*y[uü]ksek",
            r"en\s*pop[uü]ler", r"en\s*ba[sş]ar[iı]l[iı]",
            r"b[uü]y[uü]kten\s*k[uü][cç][uü][gğ]e",
            r"azalan", r"descending", r"desc\b",
            r"top\s*\d*", r"en\s*iyi",
        ]

        # Artan siralama (asc)
        asc_patterns = [
            r"en\s*az", r"en\s*d[uü][sş][uü]k", r"en\s*k[oö]t[uü]",
            r"k[uü][cç][uü]kten\s*b[uü]y[uü][gğ]e",
            r"artan", r"ascending", r"asc\b",
            r"en\s*son", r"sondan",
        ]

        for pattern in desc_patterns:
            if re.search(pattern, query_lower):
                return "desc"

        for pattern in asc_patterns:
            if re.search(pattern, query_lower):
                return "asc"

        return None

    def _extract_comparison(self, query: str) -> Optional[Dict]:
        """
        Sorgudan karsilastirma bilgisi cikar.

        Ornek sorgular:
        - "ahmet hakan vs elif okutan"
        - "spor ile ekonomi karsilastir"
        - "bu hafta gecen haftaya gore"

        Returns:
            Karsilastirma dict veya None
        """
        query_lower = query.lower()

        comparison = None

        # VS pattern'i
        vs_match = re.search(r"(\w+(?:\s+\w+)?)\s+(?:vs|versus|kar[sş][iı])\s+(\w+(?:\s+\w+)?)", query_lower)
        if vs_match:
            comparison = {
                "type": "vs",
                "item1": vs_match.group(1).strip(),
                "item2": vs_match.group(2).strip(),
            }

        # Karsilastir pattern'i
        kar_match = re.search(r"(\w+(?:\s+\w+)?)\s+ile\s+(\w+(?:\s+\w+)?)\s*kar[sş][iı]la[sş]t[iı]r", query_lower)
        if kar_match:
            comparison = {
                "type": "compare",
                "item1": kar_match.group(1).strip(),
                "item2": kar_match.group(2).strip(),
            }

        # Gore pattern'i (donem karsilastirmasi)
        gore_match = re.search(r"(bu\s*(?:hafta|ay|y[iı]l))\s+(?:ge[cç]en|[oö]nceki)\s*(?:hafta|ay|y[iı]l)(?:a|ya)?\s*g[oö]re", query_lower)
        if gore_match:
            comparison = {
                "type": "period",
                "current": gore_match.group(1).strip(),
                "previous": "previous",
            }

        return comparison

    def _extract_publish_date_range(self, query: str) -> Optional[Tuple[str, str]]:
        """
        Sorgudan yayin tarihi araligini cikar.

        Ornek sorgular:
        - "gecen hafta yayinlanan icerikler"
        - "1-7 aralik yayinladigi haberler"
        - "dun yayinlanan"

        Returns:
            (start_date, end_date) tuple veya None
            Tarihler GA4 vpublisheddate formatinda: "20251210"
        """
        query_lower = query.lower()

        # Yayin tarihi ile ilgili ifadeler var mi kontrol et
        publish_keywords = [
            r"yayin(la|lad|lan)",      # yayinlanan, yayinladigi
            r"yay[i,ı]m(la|lad|lan)",  # yayimlanan, yayimladigi
            r"yazdigi",                 # yazdigi
            r"girdi[gğ]i",              # girdigi (haber girdigi)
            r"ekledigi",                # ekledigi
            r"payla[sş]t[i,ı][gğ][i,ı]", # paylastigi
        ]

        has_publish_context = any(re.search(p, query_lower) for p in publish_keywords)

        if not has_publish_context:
            return None

        # Turkce ay isimleri
        months = {
            "ocak": 1, "şubat": 2, "subat": 2, "mart": 3, "nisan": 4,
            "mayıs": 5, "mayis": 5, "haziran": 6, "temmuz": 7, "ağustos": 8,
            "agustos": 8, "eylül": 9, "eylul": 9, "ekim": 10, "kasım": 11,
            "kasim": 11, "aralık": 12, "aralik": 12
        }

        # Tarih araligi pattern'i: "1-7 aralik yayinlanan"
        date_range_match = re.search(
            r"(\d{1,2})\s*[-–]\s*(\d{1,2})\s*(ocak|[sş]ubat|mart|nisan|may[i,ı]s|haziran|temmuz|a[gğ]ustos|eyl[uü]l|ekim|kas[i,ı]m|aral[i,ı]k)",
            query_lower
        )

        if date_range_match:
            start_day = int(date_range_match.group(1))
            end_day = int(date_range_match.group(2))
            month_str = date_range_match.group(3)

            month_normalized = month_str.replace("ş", "s").replace("ı", "i").replace("ğ", "g").replace("ü", "u")
            month = months.get(month_normalized) or months.get(month_str)

            if month:
                current_date = datetime.now()
                year = current_date.year
                if month > current_date.month:
                    year -= 1

                try:
                    start_date = datetime(year, month, start_day)
                    end_date = datetime(year, month, end_day)
                    # GA4 vpublisheddate formati: "20251210"
                    return start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d")
                except ValueError:
                    pass

        # Spesifik tarih: "5 aralik yayinladigi"
        specific_date_match = re.search(
            r"(\d{1,2})\s*(ocak|[sş]ubat|mart|nisan|may[i,ı]s|haziran|temmuz|a[gğ]ustos|eyl[uü]l|ekim|kas[i,ı]m|aral[i,ı]k)",
            query_lower
        )

        if specific_date_match:
            day = int(specific_date_match.group(1))
            month_str = specific_date_match.group(2)
            month_normalized = month_str.replace("ş", "s").replace("ı", "i").replace("ğ", "g").replace("ü", "u")
            month = months.get(month_normalized) or months.get(month_str)

            if month and 1 <= day <= 31:
                current_date = datetime.now()
                year = current_date.year
                if month > current_date.month or (month == current_date.month and day > current_date.day):
                    year -= 1

                try:
                    specific_date = datetime(year, month, day)
                    date_str = specific_date.strftime("%Y%m%d")
                    return date_str, date_str
                except ValueError:
                    pass

        # Genel tarih pattern'leri: "gecen hafta yayinlanan", "dun yayinladigi"
        if re.search(r"bug[uü]n", query_lower):
            today = datetime.now()
            date_str = today.strftime("%Y%m%d")
            return date_str, date_str

        if re.search(r"d[uü]n", query_lower):
            yesterday = datetime.now() - timedelta(days=1)
            date_str = yesterday.strftime("%Y%m%d")
            return date_str, date_str

        if re.search(r"ge[cç]en\s*hafta|ge[cç]ti[gğ]imiz\s*hafta|son\s*7\s*g[uü]n|son\s*bir?\s*hafta", query_lower):
            end_date = datetime.now() - timedelta(days=1)
            start_date = end_date - timedelta(days=6)
            return start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d")

        if re.search(r"son\s*30\s*g[uü]n|son\s*bir?\s*ay|ge[cç]en\s*ay", query_lower):
            end_date = datetime.now() - timedelta(days=1)
            start_date = end_date - timedelta(days=29)
            return start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d")

        return None

    def _format_publish_date(self, ga4_date: str) -> str:
        """
        GA4 vpublisheddate formatini okunabilir formata cevir.

        Args:
            ga4_date: "20251210" formatinda tarih

        Returns:
            "10 Aralik 2025" formatinda tarih
        """
        if not ga4_date or ga4_date == "(not set)" or len(ga4_date) != 8:
            return ga4_date

        try:
            date_obj = datetime.strptime(ga4_date, "%Y%m%d")
            months_tr = {
                1: "Ocak", 2: "Subat", 3: "Mart", 4: "Nisan",
                5: "Mayis", 6: "Haziran", 7: "Temmuz", 8: "Agustos",
                9: "Eylul", 10: "Ekim", 11: "Kasim", 12: "Aralik"
            }
            return f"{date_obj.day} {months_tr[date_obj.month]} {date_obj.year}"
        except ValueError:
            return ga4_date

    def _extract_editor_name(self, query: str) -> Optional[str]:
        """
        Sorgudan editor/yazar ismini cikar

        Ornekler:
            "cemile gelgec editoru nasil" -> "cemile gelgec"
            "c.gelgec performansi" -> "c.gelgec"
            "editor ahmet kara son 7 gun" -> "ahmet kara"
        """
        query_lower = query.lower()

        # Anahtar kelimeleri cikar
        keywords_to_remove = [
            r"edit[oö]r\s*performans[i,ı]?",
            r"edit[oö]r[uü]n?[uü]?\s*",
            r"edit[oö]r\s*",
            r"performans[i,ı]?",
            r"nas[i,ı]l",
            r"son\s*\d+\s*g[uü]n",
            r"son\s*\d+\s*ay",
            r"bug[uü]n",
            r"d[uü]n",
            r"ge[cs]en\s*hafta",
            r"haberleri?",
            r"sayfa\s*g[oö]r[uü]nt[uü]leme",
            r"\d+\s*tane",
            r"ilk\s*\d+",
            r"top\s*\d+",
            r"gidiyor",
        ]

        cleaned = query_lower
        for pattern in keywords_to_remove:
            cleaned = re.sub(pattern, " ", cleaned)

        # Fazla bosluklari temizle
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        # En az 2 karakter olmali
        if len(cleaned) >= 2:
            return cleaned

        return None

    def _extract_author_name(self, query: str) -> Optional[str]:
        """
        Sorgudan yazar ismini cikar

        Ornekler:
            "yazar ahmet yilmaz haberleri" -> "ahmet yilmaz"
            "kose yazari mehmet bey" -> "mehmet bey"
        """
        query_lower = query.lower()

        keywords_to_remove = [
            r"yazar\s*performans[i,ı]?",
            r"yazar\s*",
            r"k[oö][sş]e\s*yazar[i,ı]?",
            r"performans[i,ı]?",
            r"nas[i,ı]l",
            r"son\s*\d+\s*g[uü]n",
            r"son\s*\d+\s*ay",
            r"bug[uü]n",
            r"d[uü]n",
            r"ge[cs]en\s*hafta",
            r"haberleri?",
            r"yaz[i,ı]lar[i,ı]?",
            r"sayfa\s*g[oö]r[uü]nt[uü]leme",
            r"\d+\s*tane",
            r"ilk\s*\d+",
            r"top\s*\d+",
        ]

        cleaned = query_lower
        for pattern in keywords_to_remove:
            cleaned = re.sub(pattern, " ", cleaned)

        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        if len(cleaned) >= 2:
            return cleaned

        return None

    def _extract_filters(self, query: str) -> Dict[str, str]:
        """
        Sorgudan filtreleri cikar

        Ornekler:
            "spor kategorisi" -> {"cat1": "spor"} (marka bazli: hcat1 veya vcat1)
            "turkiye'den gelen trafik" -> {"country": "Turkey"}
            "istanbul sehri" -> {"city": "Istanbul"}
            "mobil cihazlar" -> {"deviceCategory": "mobile"}
        """
        query_lower = query.lower()
        filters = {}

        # Kategori filtreleri - GA4'teki gercek degerler
        category_patterns = {
            r"\bekonomi\b": "ekonomi",
            r"\bmagazin\b": "magazin",
            r"\bg[uü]ndem\b": "gundem",
            r"\bsiyaset\b": "siyaset",
            r"\bsa[gğ]l[i,ı]k\b": "saglik",
            r"\bk[uü]lt[uü]r": "kultur-sanat",
            r"\bya[sş]am\b": "yasam",
            r"\botomobil\b": "otomobil",
            r"\bd[uü]nya\b": "dunya",
            r"\b[sş]ehir": "sehirler",
            r"\byerel[- ]?haber": "yerel-haberler",
            r"\bar[sş]iv\b": "arsiv",
            r"\bastroloji\b": "astroloji",
            r"\bramazan\b": "ramazan",
            r"\be[gğ]itim\b": "egitim",
        }

        for pattern, value in category_patterns.items():
            if re.search(pattern, query_lower):
                # Jenerik "cat1" kullan - GA4Client marka bazli cozecek
                filters["cat1"] = value
                break

        # Ulke filtreleri - GA4'teki gercek degerler (Turkiye Turkce karakterle)
        country_patterns = {
            r"t[uü]rkiye": "Türkiye",
            r"almanya": "Germany",
            r"amerika|abd|usa": "United States",
            r"ingiltere|birle[sş]ik\s*krall[i,ı]k": "United Kingdom",
            r"fransa": "France",
            r"hollanda": "Netherlands",
            r"bel[cç]ika": "Belgium",
            r"avusturya": "Austria",
            r"isvi[cç]re": "Switzerland",
            r"k[i,ı]br[i,ı]s": "Cyprus",
            r"azerbaycan": "Azerbaijan",
        }

        for pattern, value in country_patterns.items():
            if re.search(pattern, query_lower):
                filters["country"] = value
                break

        # Sehir filtreleri
        city_patterns = {
            r"\bistanbul\b": "Istanbul",
            r"\bankara\b": "Ankara",
            r"\bizmir\b": "Izmir",
            r"\bantalya\b": "Antalya",
            r"\bbursa\b": "Bursa",
            r"\badana\b": "Adana",
            r"\bkonya\b": "Konya",
            r"\bgaziantep\b": "Gaziantep",
            r"\bmersin\b": "Mersin",
            r"\bkayseri\b": "Kayseri",
        }

        for pattern, value in city_patterns.items():
            if re.search(pattern, query_lower):
                filters["city"] = value
                break

        # Cihaz filtreleri
        device_patterns = {
            r"\bmobil\b|\bcep\s*telefon": "mobile",
            r"\bdesktop\b|\bmasaustu\b|\bbilgisayar\b": "desktop",
            r"\btablet\b": "tablet",
        }

        for pattern, value in device_patterns.items():
            if re.search(pattern, query_lower):
                filters["deviceCategory"] = value
                break

        # Kanal filtreleri
        channel_patterns = {
            r"\borganic\s*search\b|\borganik\s*arama\b": "Organic Search",
            r"\bdirect\b|\bdirekt\b|\bdo[gğ]rudan\b": "Direct",
            r"\breferral\b|\byonlendirme\b": "Referral",
            r"\bsocial\b|\bsosyal\b": "Organic Social",
            r"\bpaid\s*search\b|\b[uü]cretli\s*arama\b": "Paid Search",
            r"\bemail\b|\be-?posta\b": "Email",
        }

        for pattern, value in channel_patterns.items():
            if re.search(pattern, query_lower):
                filters["sessionDefaultChannelGroup"] = value
                break

        # Tarayici filtreleri
        browser_patterns = {
            r"\bchrome\b": "Chrome",
            r"\bsafari\b": "Safari",
            r"\bfirefox\b": "Firefox",
            r"\bedge\b": "Edge",
            r"\bsamsung\s*internet\b": "Samsung Internet",
        }

        for pattern, value in browser_patterns.items():
            if re.search(pattern, query_lower):
                filters["browser"] = value
                break

        # Isletim sistemi filtreleri
        os_patterns = {
            r"\bandroid\b": "Android",
            r"\bios\b|\biphone\b|\bipad\b": "iOS",
            r"\bwindows\b": "Windows",
            r"\bmac\s*os\b|\bmacos\b": "Macintosh",
            r"\blinux\b": "Linux",
        }

        for pattern, value in os_patterns.items():
            if re.search(pattern, query_lower):
                filters["operatingSystem"] = value
                break

        return filters

    def _format_number(self, num) -> str:
        """Sayilari formatla"""
        if isinstance(num, float):
            if num < 1:
                return f"{num:.2%}"
            return f"{num:,.2f}"
        return f"{num:,}"

    def _format_dataframe(self, df, title: str = "", add_percentages: bool = True, filter_not_set: bool = True) -> str:
        """DataFrame'i okunabilir formata cevir"""
        if df.empty:
            self.last_dataframe = None
            return "Veri bulunamadi."

        # (not set) ve bos satirlari filtrele (opsiyonel)
        if filter_not_set:
            df = self._filter_not_set_rows(df)

        # Filtreleme sonrasi bos mu kontrol et
        if df.empty:
            self.last_dataframe = None
            return "Veri bulunamadi."

        # Oran sutunlari ekle (opsiyonel)
        if add_percentages:
            df = self._add_percentage_columns(df)

        # DataFrame'i web arayuzu icin sakla
        self.last_dataframe = df.copy()

        output = []
        if title:
            output.append(f"\n{'='*50}")
            output.append(f"  {title}")
            output.append(f"{'='*50}\n")

        # Sutun genisliklerini hesapla
        col_widths = {}
        for col in df.columns:
            max_width = max(
                len(str(col)),
                df[col].astype(str).str.len().max()
            )
            col_widths[col] = min(max_width + 2, 40)

        # Header
        header = ""
        for col in df.columns:
            header += str(col)[:col_widths[col]-1].ljust(col_widths[col])
        output.append(header)
        output.append("-" * len(header))

        # Rows
        for _, row in df.head(20).iterrows():  # Max 20 satir goster
            row_str = ""
            for col in df.columns:
                val = row[col]
                if isinstance(val, (int, float)):
                    val = self._format_number(val)
                row_str += str(val)[:col_widths[col]-1].ljust(col_widths[col])
            output.append(row_str)

        if len(df) > 20:
            output.append(f"\n... ve {len(df) - 20} satir daha")

        output.append(f"\nToplam: {len(df)} satir")

        return "\n".join(output)

    # =========================================================================
    # INTENT HANDLERS
    # =========================================================================

    def _handle_simple_metric(self, query: str) -> str:
        """
        Basit metrik sorgulari - sadece istenen metrigi dondur

        Ornekler:
            "bugün kaç kullanıcı geldi" -> Sadece kullanıcı sayısı
            "dün kaç oturum açıldı" -> Sadece oturum sayısı
            "kaç görüntülenme oldu" -> Sadece sayfa görüntülenme
        """
        start_date, end_date = self._extract_date_range(query)
        query_lower = query.lower()

        # Hangi metrik isteniyor?
        metric = None
        metric_name = None

        # Kullanıcı/kişi/ziyaretçi
        if re.search(r"kullan[i,ı]c[i,ı]|ki[sş]i|ziyaret[cç]i", query_lower):
            metric = "totalUsers"
            metric_name = "Kullanici"
        # Oturum/session
        elif re.search(r"oturum|session", query_lower):
            metric = "sessions"
            metric_name = "Oturum"
        # Görüntülenme/view/pageview
        elif re.search(r"g[oö]r[uü]nt[uü]len|view|pageview", query_lower):
            metric = "screenPageViews"
            metric_name = "Sayfa Goruntuleme"
        # Tıklama
        elif re.search(r"t[i,ı]klama|click", query_lower):
            metric = "screenPageViews"  # GA4'te tıklama için en yakın metrik
            metric_name = "Sayfa Goruntuleme"
        else:
            # Varsayılan olarak kullanıcı
            metric = "totalUsers"
            metric_name = "Kullanici"

        # GA4'ten sadece istenen metrigi al
        df = self.client.run_query(
            dimensions=[],  # Dimension yok - sadece toplam
            metrics=[metric],
            start_date=start_date,
            end_date=end_date,
            return_type="list"
        )

        if not df:
            return "Veri bulunamadi."

        data = df[0]

        # Tarih aciklamasi
        if start_date == "yesterday" and end_date == "yesterday":
            tarih_str = "Dun"
        elif start_date == "today" and end_date == "today":
            tarih_str = "Bugun"
        elif start_date == "7daysAgo":
            tarih_str = "Son 7 Gun"
        elif start_date == "30daysAgo":
            tarih_str = "Son 30 Gun"
        else:
            tarih_str = f"{start_date} - {end_date}"

        # Degeri al - kolon adi farkli olabilir
        value = 0
        for key, val in data.items():
            if isinstance(val, (int, float)):
                value = val
                break

        # Scorecard formatinda dondur
        output = []
        output.append("")
        output.append("=" * 40)
        output.append(f"  {metric_name.upper()}")
        output.append(f"  {tarih_str}")
        output.append("=" * 40)
        output.append("")
        output.append(f"  {self._format_number(value)}")
        output.append("")
        output.append("=" * 40)

        # Tablo gosterme
        self.last_dataframe = None

        return "\n".join(output)

    def _handle_top_pages(self, query: str) -> str:
        """En cok okunan sayfalar"""
        start_date, end_date = self._extract_date_range(query)
        category = self._extract_category(query)
        limit = self._extract_limit(query)

        df = self.client.get_top_pages(
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            category=category
        )

        title = "En Cok Okunan Sayfalar"
        if category:
            title += f" ({category})"

        return self._format_dataframe(df, title)

    def _handle_traffic_sources(self, query: str) -> str:
        """Trafik kaynaklari"""
        start_date, end_date = self._extract_date_range(query)

        df = self.client.get_traffic_sources(
            start_date=start_date,
            end_date=end_date
        )

        return self._format_dataframe(df, "Trafik Kaynaklari")

    def _handle_category_performance(self, query: str) -> str:
        """Kategori performansi"""
        start_date, end_date = self._extract_date_range(query)
        limit = self._extract_limit(query)

        df = self.client.get_category_performance(
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )

        return self._format_dataframe(df, "Kategori Performansi")

    def _handle_editor_performance(self, query: str) -> str:
        """Editor performansi"""
        start_date, end_date = self._extract_date_range(query)
        limit = self._extract_limit(query)

        # Belirli bir editor sorgusu mu?
        specific_editor = self._extract_editor_name(query)

        if specific_editor:
            # Fuzzy matching ile editor bul
            result = self.editor_matcher.find_editor(specific_editor)

            if result["status"] == "single":
                # Tek esleme - direkt sorgula
                editor_code = result["matches"][0]["code"]
                df = self.client.run_query(
                    dimensions=["veditor", "pagePath", "pageTitle"],
                    metrics=["screenPageViews", "totalUsers", "sessions"],
                    start_date=start_date,
                    end_date=end_date,
                    filters={"veditor": editor_code},
                    order_by="screenPageViews",
                    order_desc=True,
                    limit=limit
                )
                return self._format_dataframe(df, f"Editor: {editor_code}")

            elif result["status"] == "multiple":
                # Birden fazla esleme - kullaniciya sor
                self.context["pending_disambiguation"] = {
                    "type": "editor",
                    "matches": result["matches"],
                    "original_query": query
                }
                return result["message"]

            else:
                # Bulunamadi
                return result["message"] + "\n\nGenel editor performansini gormek icin tekrar deneyin."

        # Genel editor listesi
        df = self.client.get_editor_performance(
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )

        return self._format_dataframe(df, "Editor Performansi")

    def _handle_device_breakdown(self, query: str) -> str:
        """Cihaz dagilimi"""
        start_date, end_date = self._extract_date_range(query)

        df = self.client.get_device_breakdown(
            start_date=start_date,
            end_date=end_date
        )

        return self._format_dataframe(df, "Cihaz Dagilimi")

    def _handle_city_breakdown(self, query: str) -> str:
        """Sehir dagilimi"""
        start_date, end_date = self._extract_date_range(query)
        limit = self._extract_limit(query)

        df = self.client.get_city_breakdown(
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )

        return self._format_dataframe(df, "Sehir Dagilimi (Turkiye)")

    def _handle_hourly_traffic(self, query: str) -> str:
        """Saatlik trafik"""
        start_date, _ = self._extract_date_range(query)

        df = self.client.get_hourly_traffic(date=start_date)

        return self._format_dataframe(df, "Saatlik Trafik Dagilimi")

    def _handle_daily_trend(self, query: str) -> str:
        """Gunluk trend"""
        start_date, end_date = self._extract_date_range(query)

        # Trend icin en az 7 gun olmali
        if start_date == "yesterday":
            start_date = "7daysAgo"

        df = self.client.get_daily_trend(
            start_date=start_date,
            end_date=end_date
        )

        return self._format_dataframe(df, "Gunluk Trafik Trendi")

    def _handle_summary(self, query: str) -> str:
        """Genel ozet"""
        start_date, end_date = self._extract_date_range(query)

        # Temel metrikler
        df = self.client.run_query(
            dimensions=[],
            metrics=["totalUsers", "sessions", "screenPageViews", "bounceRate", "averageSessionDuration", "newUsers"],
            start_date=start_date,
            end_date=end_date,
            return_type="list"
        )

        if not df:
            return "Veri bulunamadi."

        data = df[0]

        output = []
        output.append("\n" + "="*50)
        output.append("  GENEL OZET")
        output.append("="*50 + "\n")

        output.append(f"  Toplam Kullanici:      {self._format_number(data.get('Toplam Kullanici', 0))}")
        output.append(f"  Yeni Kullanici:        {self._format_number(data.get('Yeni Kullanici', 0))}")
        output.append(f"  Oturum Sayisi:         {self._format_number(data.get('Oturum Sayisi', 0))}")
        output.append(f"  Sayfa Goruntuleme:     {self._format_number(data.get('Sayfa Goruntuleme', 0))}")
        output.append(f"  Hemen Cikma Orani:     {self._format_number(data.get('Hemen Cikma Orani', 0))}")
        output.append(f"  Ort. Oturum Suresi:    {data.get('Ortalama Oturum Suresi', 0):.0f} saniye")

        return "\n".join(output)

    def _handle_compare(self, query: str) -> str:
        """Donem karsilastirma"""
        comparison = self.client.compare_periods(
            metrics=["totalUsers", "sessions", "screenPageViews"],
            current_start="7daysAgo",
            current_end="yesterday",
            previous_start="14daysAgo",
            previous_end="8daysAgo"
        )

        output = []
        output.append("\n" + "="*50)
        output.append("  HAFTALIK KARSILASTIRMA")
        output.append("  (Bu hafta vs Gecen hafta)")
        output.append("="*50 + "\n")

        for metric_name, values in comparison.items():
            change_symbol = "+" if values["change_percent"] >= 0 else ""
            output.append(f"  {metric_name}:")
            output.append(f"    Bu hafta:    {self._format_number(values['current'])}")
            output.append(f"    Gecen hafta: {self._format_number(values['previous'])}")
            output.append(f"    Degisim:     {change_symbol}{values['change_percent']}%")
            output.append("")

        return "\n".join(output)

    def _handle_author_performance(self, query: str) -> str:
        """Yazar performansi"""
        start_date, end_date = self._extract_date_range(query)
        limit = self._extract_limit(query)

        # Belirli bir yazar sorgusu mu?
        specific_author = self._extract_author_name(query)

        if specific_author:
            # Fuzzy matching ile yazar bul
            result = self.author_matcher.find_editor(specific_author)

            if result["status"] == "single":
                # Tek esleme - direkt sorgula
                author_code = result["matches"][0]["code"]
                df = self.client.run_query(
                    dimensions=["vauthor", "pagePath", "pageTitle"],
                    metrics=["screenPageViews", "totalUsers", "sessions"],
                    start_date=start_date,
                    end_date=end_date,
                    filters={"vauthor": author_code},
                    order_by="screenPageViews",
                    order_desc=True,
                    limit=limit
                )
                return self._format_dataframe(df, f"Yazar: {author_code}")

            elif result["status"] == "multiple":
                # Birden fazla esleme - kullaniciya sor
                self.context["pending_disambiguation"] = {
                    "type": "author",
                    "matches": result["matches"],
                    "original_query": query
                }
                return result["message"]

            else:
                # Bulunamadi
                return result["message"] + "\n\nGenel yazar performansini gormek icin tekrar deneyin."

        # Genel yazar listesi
        df = self.client.run_query(
            dimensions=["vauthor"],
            metrics=["screenPageViews", "totalUsers", "sessions"],
            start_date=start_date,
            end_date=end_date,
            order_by="screenPageViews",
            order_desc=True,
            limit=limit
        )

        return self._format_dataframe(df, "Yazar Performansi")

    def _handle_news_type(self, query: str) -> str:
        """Haber tipi dagilimi"""
        start_date, end_date = self._extract_date_range(query)

        df = self.client.run_query(
            dimensions=["newstype"],
            metrics=["screenPageViews", "totalUsers", "sessions", "averageSessionDuration"],
            start_date=start_date,
            end_date=end_date,
            order_by="screenPageViews",
            order_desc=True
        )

        return self._format_dataframe(df, "Haber Tipi Dagilimi")

    def _handle_tag_analysis(self, query: str) -> str:
        """Etiket analizi"""
        start_date, end_date = self._extract_date_range(query)
        limit = self._extract_limit(query)

        df = self.client.run_query(
            dimensions=["tag"],
            metrics=["screenPageViews", "totalUsers", "sessions"],
            start_date=start_date,
            end_date=end_date,
            order_by="screenPageViews",
            order_desc=True,
            limit=limit
        )

        return self._format_dataframe(df, "Etiket (Tag) Analizi")

    def _handle_content_age(self, query: str) -> str:
        """Icerik yasi analizi"""
        start_date, end_date = self._extract_date_range(query)

        df = self.client.run_query(
            dimensions=["publisheddate"],
            metrics=["screenPageViews", "totalUsers"],
            start_date=start_date,
            end_date=end_date,
            order_by="screenPageViews",
            order_desc=True,
            limit=20
        )

        return self._format_dataframe(df, "Icerik Yayinlanma Tarihine Gore Performans")

    def _handle_browser_analysis(self, query: str) -> str:
        """Tarayici dagilimi"""
        start_date, end_date = self._extract_date_range(query)

        df = self.client.run_query(
            dimensions=["browser"],
            metrics=["totalUsers", "sessions", "screenPageViews", "bounceRate"],
            start_date=start_date,
            end_date=end_date,
            order_by="totalUsers",
            order_desc=True,
            limit=15
        )

        return self._format_dataframe(df, "Tarayici Dagilimi")

    def _handle_os_analysis(self, query: str) -> str:
        """Isletim sistemi dagilimi"""
        start_date, end_date = self._extract_date_range(query)

        df = self.client.run_query(
            dimensions=["operatingSystem"],
            metrics=["totalUsers", "sessions", "screenPageViews", "bounceRate"],
            start_date=start_date,
            end_date=end_date,
            order_by="totalUsers",
            order_desc=True,
            limit=15
        )

        return self._format_dataframe(df, "Isletim Sistemi Dagilimi")

    def _handle_landing_pages(self, query: str) -> str:
        """Giris sayfalari"""
        start_date, end_date = self._extract_date_range(query)
        limit = self._extract_limit(query)

        df = self.client.run_query(
            dimensions=["landingPage"],
            metrics=["sessions", "totalUsers", "bounceRate", "averageSessionDuration"],
            start_date=start_date,
            end_date=end_date,
            order_by="sessions",
            order_desc=True,
            limit=limit
        )

        return self._format_dataframe(df, "Giris Sayfalari (Landing Pages)")

    def _handle_exit_pages(self, query: str) -> str:
        """Cikis sayfalari"""
        start_date, end_date = self._extract_date_range(query)
        limit = self._extract_limit(query)

        df = self.client.run_query(
            dimensions=["pagePath"],
            metrics=["exits", "screenPageViews", "totalUsers"],
            start_date=start_date,
            end_date=end_date,
            order_by="exits",
            order_desc=True,
            limit=limit
        )

        return self._format_dataframe(df, "Cikis Sayfalari (Exit Pages)")

    def _handle_new_vs_returning(self, query: str) -> str:
        """Yeni vs Geri donen kullanicilar"""
        start_date, end_date = self._extract_date_range(query)

        df = self.client.run_query(
            dimensions=["newVsReturning"],
            metrics=["totalUsers", "sessions", "screenPageViews", "bounceRate", "averageSessionDuration"],
            start_date=start_date,
            end_date=end_date,
            order_by="totalUsers",
            order_desc=True
        )

        return self._format_dataframe(df, "Yeni vs Geri Donen Kullanicilar")

    def _handle_real_time(self, query: str) -> str:
        """Anlik durum (bugunun verisi)"""
        df = self.client.run_query(
            dimensions=[],
            metrics=["activeUsers", "sessions", "screenPageViews", "newUsers"],
            start_date="today",
            end_date="today",
            return_type="list"
        )

        if not df:
            return "Veri bulunamadi."

        data = df[0]

        output = []
        output.append("\n" + "="*50)
        output.append("  ANLIK DURUM (Bugun)")
        output.append("="*50 + "\n")

        output.append(f"  Aktif Kullanici:       {self._format_number(data.get('Aktif Kullanici', 0))}")
        output.append(f"  Oturum Sayisi:         {self._format_number(data.get('Oturum Sayisi', 0))}")
        output.append(f"  Sayfa Goruntuleme:     {self._format_number(data.get('Sayfa Goruntuleme', 0))}")
        output.append(f"  Yeni Kullanici:        {self._format_number(data.get('Yeni Kullanici', 0))}")

        return "\n".join(output)

    def _handle_daily_users(self, query: str) -> str:
        """Gunluk kullanici sayisi - Turkce gun ismi ile"""
        start_date, end_date = self._extract_date_range(query)

        # Eger "bugun" ise sadece bugunun verisi
        if "bug" in query.lower() or start_date == "today":
            df = self.client.run_query(
                dimensions=["dayOfWeek"],
                metrics=["totalUsers", "sessions", "screenPageViews"],
                start_date="today",
                end_date="today"
            )
            title = "Bugunun Kullanici Sayisi"
        else:
            df = self.client.run_query(
                dimensions=["dayOfWeek"],
                metrics=["totalUsers", "sessions", "screenPageViews"],
                start_date=start_date,
                end_date=end_date
            )
            title = "Kullanici Sayisi"

        # Haftanin gunu numarasini Turkce isme cevir
        # Sutun adi "Haftanın Günü" (Turkce karakterli) olarak donuyor
        day_col = None
        for col in df.columns:
            if "Hafta" in col and "Gün" in col:
                day_col = col
                break

        if day_col:
            df[day_col] = df[day_col].astype(str).map(
                lambda x: TURKISH_DAY_NAMES.get(x, x)
            )
            df = df.rename(columns={day_col: "Gun"})

        return self._format_dataframe(df, title)

    def _handle_weekly_trend(self, query: str) -> str:
        """Haftalik trend - son 7 gun grafik verisi"""
        df = self.client.run_query(
            dimensions=["date"],
            metrics=["screenPageViews", "sessions", "totalUsers"],
            start_date="7daysAgo",
            end_date="yesterday",
            order_by="date",
            order_desc=False
        )

        # Tarih formatini duzenle
        if "Tarih" in df.columns:
            df["Tarih"] = pd.to_datetime(df["Tarih"], format="%Y%m%d").dt.strftime("%d/%m")

        # DataFrame'i web arayuzu icin sakla (grafik icin)
        self.last_dataframe = df.copy()
        self.last_dataframe["_chart_type"] = "weekly_trend"

        return self._format_dataframe(df, "Haftalik Trend (Son 7 Gun)")

    def _handle_device_ratio(self, query: str) -> str:
        """Cihaz oranlari - yuzde ile"""
        start_date, end_date = self._extract_date_range(query)

        df = self.client.run_query(
            dimensions=["deviceCategory"],
            metrics=["totalUsers", "sessions", "screenPageViews"],
            start_date=start_date,
            end_date=end_date,
            order_by="totalUsers",
            order_desc=True
        )

        # Oran sutunlari otomatik olarak _format_dataframe icerisinde ekleniyor
        return self._format_dataframe(df, "Cihaz Oranlari")

    def _handle_popular_editors(self, query: str) -> str:
        """En populer editorler - duzgun calisan"""
        start_date, end_date = self._extract_date_range(query)
        limit = self._extract_limit(query)

        # Jenerik "editor" kullan - GA4Client marka bazli cozecek
        df = self.client.run_query(
            dimensions=["editor"],
            metrics=["screenPageViews", "totalUsers", "sessions"],
            start_date=start_date,
            end_date=end_date,
            order_by="screenPageViews",
            order_desc=True,
            limit=limit
        )

        return self._format_dataframe(df, "En Populer Editorler")

    def _handle_person_stats(self, query: str) -> str:
        """
        Belirli bir kisi (editor/yazar) icin toplam istatistik goster - scorecard formati

        Ornekler:
            "muberra dun kac goruntulenme aldi" -> mgoren'in toplam goruntulenme sayisi
            "ahmet bugun kac view" -> ahmet'in toplam view sayisi
        """
        start_date, end_date = self._extract_date_range(query)

        # Sorgudan ismi cikar
        query_lower = query.lower()

        # Atlanacak kelimeler (bunlar isim degil)
        skip_words = ["dun", "dün", "bugun", "bugün", "son", "kac", "kaç",
                      "yazar", "editor", "editör", "view", "views", "görüntülenme",
                      "goruntulenme", "tıklama", "tiklama", "okuma", "toplam",
                      "istatistik", "istatistiği", "istatistigi", "aldi", "aldı"]

        # "yazar xxx" veya "editor xxx" paterni - ozel durum
        person_name = None
        force_type = None  # "author" veya "editor" olarak zorla

        # Yazar/editor belirtilmis mi kontrol et
        yazar_match = re.search(r"yazar\s+(\w+)", query_lower)
        editor_match = re.search(r"edit[oö]r\s+(\w+)", query_lower)

        if yazar_match:
            person_name = yazar_match.group(1)
            force_type = "author"
        elif editor_match:
            person_name = editor_match.group(1)
            force_type = "editor"
        else:
            # Genel pattern ile ismi yakala
            patterns_to_try = [
                r"(\w+)\s+ka[cç]",                      # "xxx kaç" paterni
                r"(\w+)\s+d[uü]n",                      # "xxx dün" paterni
                r"(\w+)\s+bug[uü]n",                    # "xxx bugün" paterni
                r"(\w+)\s+toplam",                      # "xxx toplam" paterni
                r"(\w+)\s+istatisti[gğ]i",             # "xxx istatistiği" paterni
                r"^(\w+)\s+",                           # Baştaki ilk kelime (en son dene)
            ]

            for pattern in patterns_to_try:
                match = re.search(pattern, query_lower)
                if match:
                    candidate = match.group(1)
                    # Atlanacak kelime degilse kullan
                    if candidate not in skip_words:
                        person_name = candidate
                        break

        if not person_name:
            return "Kimin istatistiklerini gormek istediginizi anlayamadim. Ornek: 'muberra dun kac goruntulenme aldi'"

        # Tip zorlanmis mi?
        if force_type == "author":
            # Yazar icin CSV yok - dogrudan GA4'te vauthor dimension'inda ara
            # Once GA4'ten yazarlari cek ve icinde aranan ismi bul
            author_code = self._find_author_in_ga4(person_name, start_date, end_date)
            if author_code:
                return self._get_person_scorecard(author_code, "author", start_date, end_date)
            return f"'{person_name}' isimli yazar bulunamadi."

        elif force_type == "editor":
            # Direkt editor olarak ara
            editor_result = self.editor_matcher.find_editor(person_name)
            if editor_result["status"] in ["single", "multiple"]:
                editor_code = editor_result["matches"][0]["code"]
                return self._get_person_scorecard(editor_code, "editor", start_date, end_date)
            return f"'{person_name}' isimli editor bulunamadi."

        # Tip belirtilmemis - once editor, sonra yazar dene
        editor_result = self.editor_matcher.find_editor(person_name)

        if editor_result["status"] in ["single", "multiple"]:
            editor_code = editor_result["matches"][0]["code"]
            return self._get_person_scorecard(editor_code, "editor", start_date, end_date)

        # Editor bulunamadi - yazar olarak dene
        author_result = self.author_matcher.find_editor(person_name)

        if author_result["status"] in ["single", "multiple"]:
            author_code = author_result["matches"][0]["code"]
            return self._get_person_scorecard(author_code, "author", start_date, end_date)

        # Hic bulunamadi
        return f"'{person_name}' isimli editor veya yazar bulunamadi. Lutfen tam ismini kontrol edin."

    def _find_author_in_ga4(self, search_name: str, start_date: str, end_date: str) -> Optional[str]:
        """
        GA4'ten yazarlari cekip aranan ismi bul.
        CSV olmadigi icin dogrudan GA4'teki vauthor dimension'indan arama yapar.

        Args:
            search_name: Aranan yazar ismi (orn: "muberra", "ahmet")
            start_date: Baslangic tarihi
            end_date: Bitis tarihi

        Returns:
            Bulunan yazar kodu veya None
        """
        # Turkce karakter normalizasyonu
        turkish_map = {
            'ü': 'u', 'ö': 'o', 'ş': 's', 'ğ': 'g', 'ı': 'i', 'ç': 'c',
            'Ü': 'U', 'Ö': 'O', 'Ş': 'S', 'Ğ': 'G', 'İ': 'I', 'Ç': 'C'
        }

        def normalize(text: str) -> str:
            result = text.lower()
            for tr_char, en_char in turkish_map.items():
                result = result.replace(tr_char, en_char)
            return result

        search_normalized = normalize(search_name)

        # GA4'ten yazarlari cek
        df = self.client.run_query(
            dimensions=["author"],
            metrics=["screenPageViews"],
            start_date=start_date,
            end_date=end_date,
            order_by="screenPageViews",
            order_desc=True,
            limit=500  # En aktif 500 yazar
        )

        if df is None or df.empty:
            return None

        # Yazar kolonunun adini bul
        author_col = None
        for col in df.columns:
            if 'yazar' in col.lower() or 'author' in col.lower():
                author_col = col
                break

        if not author_col:
            # Ilk kolon yazar olabilir
            author_col = df.columns[0]

        # Yazarlar arasinda ara
        best_match = None
        best_score = 0

        for author in df[author_col].unique():
            if not author or author == "(not set)":
                continue

            author_normalized = normalize(str(author))

            # Tam eslesme
            if search_normalized == author_normalized:
                return str(author)

            # Icinde gecme (contains)
            if search_normalized in author_normalized:
                # Daha kisa yazar adi daha iyi eslesme
                score = len(search_normalized) / len(author_normalized)
                if score > best_score:
                    best_score = score
                    best_match = str(author)

            # Baslangic eslesmesi
            if author_normalized.startswith(search_normalized):
                score = 0.9  # Baslangic eslesmesi yuksek skor
                if score > best_score:
                    best_score = score
                    best_match = str(author)

        return best_match

    def _get_person_scorecard(self, person_code: str, person_type: str, start_date: str, end_date: str) -> str:
        """
        Belirli bir kisi icin scorecard formatinda ozet istatistik dondur

        Args:
            person_code: Kisi kodu (orn: "mgoren", "sdinc")
            person_type: "editor" veya "author"
            start_date: Baslangic tarihi
            end_date: Bitis tarihi

        Returns:
            Scorecard formatinda string
        """
        # Dimension adini belirle
        dimension = "editor" if person_type == "editor" else "author"

        # Sadece toplam degerleri al - dimension olmadan
        df = self.client.run_query(
            dimensions=[],  # Dimension yok - sadece toplam
            metrics=["screenPageViews", "totalUsers", "sessions"],
            start_date=start_date,
            end_date=end_date,
            filters={dimension: person_code},
            return_type="list"
        )

        if not df:
            return f"'{person_code}' icin veri bulunamadi."

        data = df[0]

        # Tarih aciklamasi
        if start_date == "yesterday" and end_date == "yesterday":
            tarih_str = "Dun"
        elif start_date == "today" and end_date == "today":
            tarih_str = "Bugun"
        elif start_date == "7daysAgo":
            tarih_str = "Son 7 Gun"
        elif start_date == "30daysAgo":
            tarih_str = "Son 30 Gun"
        else:
            tarih_str = f"{start_date} - {end_date}"

        # Ana metrik - Sayfa Goruntuleme (views)
        views = data.get("Sayfa Goruntuleme", data.get("Sayfa Görüntüleme", 0))

        # Gercek ismi bul
        if person_type == "editor":
            # Editor icin CSV'den bak
            real_name = self.editor_matcher.get_real_name(person_code) or person_code
        else:
            # Yazar icin CSV yok - dogrudan person_code kullan (GA4'ten gelen tam isim)
            real_name = person_code

        # Sade scorecard formati - sadece views
        output = []
        output.append("")
        output.append("=" * 50)
        output.append(f"  {real_name.upper()}")
        if person_type == "editor" and real_name != person_code:
            # Editor icin kod farkliysa goster
            output.append(f"  ({person_code}) - {tarih_str}")
        else:
            # Yazar icin veya kod ayni ise sadece tarih
            output.append(f"  {tarih_str}")
        output.append("=" * 50)
        output.append("")
        output.append(f"  Sayfa Goruntuleme: {self._format_number(views)}")
        output.append("")
        output.append("=" * 50)

        # Tablo gosterme - scorecard icin DataFrame set etme
        self.last_dataframe = None

        return "\n".join(output)

    def _handle_unknown(self, query: str) -> str:
        """Bilinmeyen sorgu - Dinamik sorgu denenir"""
        # Dimension/Metric matcher ile dinamik sorgu dene
        result = self._try_dynamic_query(query)
        if result:
            return result

        return """
Sorunuzu anlamadim. Asagidaki konularda yardimci olabilirim:

ICERIK & PERFORMANS:
- En cok okunan sayfalar/haberler
- Kategori performansi
- Editor performansi
- Yazar performansi
- Haber tipi dagilimi (video, galeri, vb.)
- Etiket (tag) analizi

TRAFIK & KULLANICI:
- Trafik kaynaklari
- Yeni vs geri donen kullanicilar
- Cihaz dagilimi (mobil/desktop)
- Tarayici ve isletim sistemi
- Sehir dagilimi

SAYFA ANALIZI:
- Giris sayfalari (landing pages)
- Cikis sayfalari (exit pages)
- Saatlik trafik
- Gunluk trend

GENEL:
- Genel ozet
- Haftalik karsilastirma
- Anlik durum

Ornek sorular:
  "Dunun en cok okunan 10 haberi"
  "Hangi yazarlar en cok okunuyor"
  "Video haberler nasil performans gosteriyor"
  "Mobil mi desktop mu daha cok"

Hizli erisim icin 'yardim' yazin veya numara girin.
"""

    def _try_dynamic_query(self, query: str) -> Optional[str]:
        """
        DimensionMetricMatcher kullanarak dinamik sorgu olustur ve calistir

        Args:
            query: Kullanici sorgusu

        Returns:
            Sonuc string'i veya None (esleme bulunamazsa)
        """
        # Sorgudan dimension ve metric cikar
        suggestions = self.dm_matcher.suggest_for_query(query)

        # Sorgudan filtreleri cikar
        filters = self._extract_filters(query)

        # Filtre varsa guven seviyesini yukselt
        has_filters = len(filters) > 0

        # Yeterli guven yoksa ve filtre de yoksa None don
        if suggestions["confidence"] == "low" and not has_filters:
            return None

        dims = suggestions.get("suggested_dimensions", [])
        mets = suggestions.get("suggested_metrics", [])

        # En az 1 dimension, metric veya filtre olmali
        if not dims and not mets and not has_filters:
            return None

        # Dimension API isimlerini al
        dimension_names = [d["api_name"] for d in dims]

        # Filtre varsa ve ilgili dimension yoksa, dimension'a ekleme
        # Ornegin: "spor kategorisi goruntulenmeleri" -> vcat1 filtre olarak kullanilacak, dimension olarak degil
        # Boylece sadece spor kategorisi verileri gelir

        # Metric API isimlerini al, yoksa varsayilan kullan
        if mets:
            metric_names = [m["api_name"] for m in mets]
        else:
            # Varsayilan metrikler
            metric_names = ["screenPageViews", "totalUsers", "sessions"]

        # Eger dimension yoksa, varsayilan belirle
        if not dimension_names:
            # Filtreye gore varsayilan dimension sec
            if "cat1" in filters:
                dimension_names = ["pagePath", "pageTitle"]  # Kategori filtreliyse sayfa bazli goster
            elif "country" in filters:
                dimension_names = ["sessionDefaultChannelGroup"]  # Ulke filtreliyse kanal bazli goster
            elif "city" in filters:
                dimension_names = ["sessionDefaultChannelGroup"]  # Sehir filtreliyse kanal bazli goster
            elif "deviceCategory" in filters:
                dimension_names = ["pagePath"]  # Cihaz filtreliyse sayfa bazli goster
            else:
                dimension_names = ["pagePath"]  # Varsayilan dimension

        # Tarih araligini cikar
        start_date, end_date = self._extract_date_range(query)
        limit = self._extract_limit(query)

        # Sorguyu calistir
        try:
            df = self.client.run_query(
                dimensions=dimension_names[:3],  # Max 3 dimension
                metrics=metric_names[:4],        # Max 4 metric
                start_date=start_date,
                end_date=end_date,
                filters=filters if filters else None,  # Filtreleri ekle
                order_by=metric_names[0] if metric_names else "screenPageViews",
                order_desc=True,
                limit=limit
            )

            # Baslik olustur
            dim_labels = ", ".join([d.get("matched_alias", d["api_name"]) for d in dims]) if dims else "Genel"
            met_labels = ", ".join([m.get("matched_alias", m["api_name"]) for m in mets]) if mets else ""

            # Filtre bilgisini basliga ekle
            filter_labels = []
            for key, value in filters.items():
                filter_labels.append(f"{value}")
            filter_str = " | ".join(filter_labels) if filter_labels else ""

            # Baslik olustur
            if filter_str:
                title = f"Filtre: {filter_str}"
            else:
                title = f"Sonuc: {dim_labels}"
            if met_labels:
                title += f" ({met_labels})"

            return self._format_dataframe(df, title)

        except Exception as e:
            print(f"[HATA] Dinamik sorgu hatasi: {str(e)}")
            return None

    def _analyze_query(self, query: str) -> Dict:
        """
        Sorguyu parcalara ayirip analiz et.

        Returns:
            Dict with keys: person, date_range, metric, dimension, category, filters
        """
        query_lower = query.lower()
        analysis = {
            "person": None,           # Kisi ismi (editor/yazar)
            "person_type": None,      # "editor" veya "author"
            "date_range": None,       # (start_date, end_date) - veri cekilecek tarih araligi
            "publish_date_range": None,  # (start_date, end_date) - icerigin yayinlandigi tarih araligi
            "metric": None,           # Istenen metrik
            "metric_name": None,      # Metrik gosterim adi
            "dimension": None,        # Istenen dimension
            "category": None,         # Kategori filtresi
            "newstype": None,         # Newstype/pagetype filtresi (video, galeri, haber, vb.)
            "filters": {},            # Diger filtreler
            "query_type": None,       # "person_metric", "simple_metric", "dimension_breakdown", "complex"
            "limit": None,            # Sonuc limiti (top 10, ilk 5, vb.)
            "sort_order": None,       # Siralama yonu ("desc" veya "asc")
            "sort_by": None,          # Siralama kriteri (metrik adi)
            "comparison": None,       # Karsilastirma turu ("vs", "kar", vb.)
        }

        # 1. Tarih analizi
        analysis["date_range"] = self._extract_date_range(query)

        # 1.5. Yayin tarihi analizi - "yayinlanan", "yayinladigi" gibi ifadeler icin
        analysis["publish_date_range"] = self._extract_publish_date_range(query)

        # 1.6. Eger yayin tarihi varsa ve veri tarihi belirtilmemisse,
        # veri tarihini yayin tarihi araligi ile ayni yap
        if analysis["publish_date_range"]:
            pub_start, pub_end = analysis["publish_date_range"]
            # GA4 formatindan (20251201) normal formata (2025-12-01) cevir
            try:
                start_dt = datetime.strptime(pub_start, "%Y%m%d")
                end_dt = datetime.strptime(pub_end, "%Y%m%d")
                # Veri araligi = yayin tarihi araligi
                # "1-7 aralik yayinladigi icerikler" -> 1-7 aralik verisi
                analysis["date_range"] = (start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d"))
            except ValueError:
                pass

        # 2. Kategori analizi
        analysis["category"] = self._extract_category(query)

        # 2.5. Newstype/pagetype analizi - icerik turu filtresi
        analysis["newstype"] = self._extract_newstype(query)

        # 2.6. Limit analizi - kac sonuc isteniyor?
        analysis["limit"] = self._extract_limit(query)

        # 2.7. Siralama analizi - nasil siralansin?
        analysis["sort_order"] = self._extract_sort_order(query)

        # 2.8. Karsilastirma analizi - karsilastirma var mi?
        analysis["comparison"] = self._extract_comparison(query)

        # 3. Metrik analizi - hangi metrik isteniyor?
        # Metrik pattern'leri - kapsamli
        # NOT: Daha spesifik pattern'ler (yeni kullanici, geri donen) ONCE kontrol edilmeli
        metric_patterns = [
            # === YENI KULLANICI (spesifik - once kontrol edilmeli) ===
            ("newUsers", {
                "patterns": [
                    r"yeni\s*kullan[iı]c[iı]", r"new\s*user",
                    r"ilk\s*kez\s*gelen", r"first\s*time",
                    r"yeni\s*ziyaret[cç]i", r"yeni\s*gelen",
                ],
                "name": "Yeni Kullanici"
            }),
            # === GERI DONEN KULLANICI (spesifik - once kontrol edilmeli) ===
            ("returningUsers", {
                "patterns": [
                    r"geri\s*d[oö]nen", r"returning",
                    r"tekrar\s*gelen", r"sad[iı]k\s*kullan[iı]c[iı]",
                    r"mevcut\s*kullan[iı]c[iı]", r"eski\s*kullan[iı]c[iı]",
                ],
                "name": "Geri Donen Kullanici"
            }),
            # === ETKILESIM / ENGAGEMENT ===
            ("engagementRate", {
                "patterns": [
                    r"etkile[sş]im\s*oran", r"etkilesim\s*oran", r"etkileşim\s*oran",
                    r"engagement\s*rate", r"engagement",
                    r"ba[gğ]l[iı]l[iı]k", r"baglilik", r"bağlılık",
                ],
                "name": "Etkilesim Orani"
            }),
            # === ORTALAMA SURE ===
            ("averageSessionDuration", {
                "patterns": [
                    r"ortalama\s*s[uü]re", r"ort\.?\s*s[uü]re",
                    r"oturum\s*s[uü]re", r"session\s*duration",
                    r"kalma\s*s[uü]re", r"sitede\s*kalma",
                    r"ge[cç]irilen\s*s[uü]re",
                ],
                "name": "Ortalama Sure"
            }),
            # === HEMEN CIKMA / BOUNCE ===
            ("bounceRate", {
                "patterns": [
                    r"hemen\s*[cç][iı]kma", r"bounce\s*rate", r"bounce",
                    r"tek\s*sayfa", r"single\s*page",
                    r"[cç][iı]kma\s*oran", r"cikma\s*oran", r"çıkma\s*oran",
                ],
                "name": "Hemen Cikma Orani"
            }),
            # === KULLANICI / USER (genel - sonra kontrol edilmeli) ===
            ("totalUsers", {
                "patterns": [
                    r"kullan[iı]c[iı]", r"kullanici", r"kullanıcı",
                    r"ki[sş]i", r"kisi", r"kişi",
                    r"ziyaret[cç]i", r"ziyaretci", r"ziyaretçi",
                    r"unique\s*user", r"tekil\s*kullan[iı]c[iı]",
                    r"user\s*say[iı]s[iı]", r"kac\s*kisi", r"kaç\s*kişi",
                    r"toplam\s*kullan[iı]c[iı]", r"aktif\s*kullan[iı]c[iı]",
                ],
                "name": "Kullanici"
            }),
            # === OTURUM / SESSION ===
            ("sessions", {
                "patterns": [
                    r"oturum", r"session",
                    r"ziyaret\b", r"visit",
                    r"giri[sş]\b", r"giris\b", r"giriş\b",
                    r"oturum\s*say[iı]s[iı]", r"session\s*count",
                    r"toplam\s*oturum", r"aktif\s*oturum",
                ],
                "name": "Oturum"
            }),
            # === SAYFA GORUNTULEME / PAGEVIEW ===
            ("screenPageViews", {
                "patterns": [
                    r"g[oö]r[uü]nt[uü]len", r"goruntuleme", r"görüntülenme",
                    r"goruntulenme", r"görüntüleme",
                    r"view", r"views", r"pageview", r"page\s*view",
                    r"sayfa\s*g[oö]r[uü]nt[uü]", r"sayfa\s*view",
                    r"t[iı]klama", r"tiklama", r"tıklama", r"click",
                    r"okuma", r"okunma", r"hit",
                    r"izlenme", r"eri[sş]im", r"erisim", r"erişim",
                    r"trafik", r"traffic",
                    r"ka[cç]\s*kez", r"kac\s*kez", r"kaç\s*kez",
                    r"ka[cç]\s*defa", r"kac\s*defa", r"kaç\s*defa",
                ],
                "name": "Sayfa Goruntuleme"
            }),
        ]

        # Metrik eslestirme (sirayla kontrol et)
        for metric_key, metric_data in metric_patterns:
            for pattern in metric_data["patterns"]:
                if re.search(pattern, query_lower):
                    analysis["metric"] = metric_key
                    analysis["metric_name"] = metric_data["name"]
                    break
            if analysis["metric"]:
                break

        # 4. Kisi analizi - yazar veya editor ismi var mi?
        # "yazar xxx yyy" veya "editor xxx yyy" pattern'i (iki kelimeli isim destegi)
        # Iki kelimeli yazar ismi dene
        yazar_match_2 = re.search(r"yazar\s+(\w+)\s+(\w+)", query_lower)
        # Tek kelimeli yazar ismi
        yazar_match_1 = re.search(r"yazar\s+(\w+)", query_lower)
        # Iki kelimeli editor ismi dene
        editor_match_2 = re.search(r"edit[oö]r\s+(\w+)\s+(\w+)", query_lower)
        # Tek kelimeli editor ismi
        editor_match_1 = re.search(r"edit[oö]r\s+(\w+)", query_lower)

        if yazar_match_2:
            # Iki kelimeli yazar ismi (ahmet hakan gibi)
            second_word = yazar_match_2.group(2)
            # Ikinci kelime tarih veya metrik degil mi kontrol et
            non_name_words = ["kac", "kaç", "views", "view", "goruntuleme", "görüntülenme",
                             "aralik", "aralık", "ocak", "subat", "şubat", "mart", "nisan",
                             "mayis", "mayıs", "haziran", "temmuz", "agustos", "ağustos",
                             "eylul", "eylül", "ekim", "kasim", "kasım"]
            if second_word not in non_name_words and not second_word.isdigit():
                analysis["person"] = f"{yazar_match_2.group(1)} {yazar_match_2.group(2)}"
                analysis["person_type"] = "author"
            else:
                analysis["person"] = yazar_match_1.group(1)
                analysis["person_type"] = "author"
        elif yazar_match_1:
            analysis["person"] = yazar_match_1.group(1)
            analysis["person_type"] = "author"
        elif editor_match_2:
            second_word = editor_match_2.group(2)
            non_name_words = ["kac", "kaç", "views", "view", "goruntuleme", "görüntülenme",
                             "aralik", "aralık", "ocak", "subat", "şubat", "mart", "nisan",
                             "mayis", "mayıs", "haziran", "temmuz", "agustos", "ağustos",
                             "eylul", "eylül", "ekim", "kasim", "kasım"]
            if second_word not in non_name_words and not second_word.isdigit():
                analysis["person"] = f"{editor_match_2.group(1)} {editor_match_2.group(2)}"
                analysis["person_type"] = "editor"
            else:
                analysis["person"] = editor_match_1.group(1)
                analysis["person_type"] = "editor"
        elif editor_match_1:
            analysis["person"] = editor_match_1.group(1)
            analysis["person_type"] = "editor"
        else:
            # Genel isim pattern'i - sorgunun basindaki kelime(ler) bir isim olabilir
            # Atlanacak kelimeler
            skip_words = ["dun", "dün", "bugun", "bugün", "son", "kac", "kaç",
                         "yazar", "editor", "editör", "view", "views", "görüntülenme",
                         "goruntulenme", "tıklama", "tiklama", "okuma", "toplam",
                         "istatistik", "istatistiği", "istatistigi", "aldi", "aldı",
                         "kullanıcı", "kullanici", "oturum", "session", "kisi", "kişi",
                         "ziyaretci", "ziyaretçi", "en", "cok", "çok", "populer", "popüler",
                         "spor", "ekonomi", "magazin", "gundem", "gündem", "siyaset",
                         "teknoloji", "saglik", "sağlık", "kultur", "kültür", "yasam", "yaşam",
                         "ocak", "subat", "şubat", "mart", "nisan", "mayis", "mayıs",
                         "haziran", "temmuz", "agustos", "ağustos", "eylul", "eylül",
                         "ekim", "kasim", "kasım", "aralik", "aralık", "geldi", "oldu",
                         "ne", "nasil", "nasıl", "hangi", "nerede", "kim", "kimin",
                         # Yayin tarihi ile ilgili kelimeler
                         "gecen", "geçen", "gectigimiz", "geçtiğimiz", "gectigi", "geçtiği",
                         "yayinladigi", "yayınladığı", "yayinlanan", "yayınlanan",
                         "yayimladigi", "yayımladığı", "yazdigi", "yazdığı",
                         "hafta", "ay", "gun", "gün", "icerik", "içerik", "icerikler", "içerikler",
                         "haber", "haberler", "kadar",
                         # Icerik turleri (newstype)
                         "video", "videolar", "galeri", "galeriler", "makale", "makaleler",
                         "canli", "canlı", "podcast", "interaktif"]

            # Once iki kelimeli isim dene (elif okutan, hakan alkan gibi)
            two_word_match = re.match(r"^(\w+)\s+(\w+)", query_lower)
            if two_word_match:
                first_word = two_word_match.group(1)
                second_word = two_word_match.group(2)
                # Iki kelime de skip_words'te degilse, birlikte dene
                if (first_word not in skip_words and second_word not in skip_words
                    and not first_word.isdigit() and not second_word.isdigit()):
                    two_word_candidate = f"{first_word} {second_word}"
                    editor_result = self.editor_matcher.find_editor(two_word_candidate)
                    if editor_result["status"] in ["single", "multiple"]:
                        analysis["person"] = two_word_candidate
                        analysis["person_type"] = "editor"

            # Iki kelimeli isim bulunamadiysa tek kelime dene
            if not analysis["person"]:
                first_word_match = re.match(r"^(\w+)", query_lower)
                if first_word_match:
                    candidate = first_word_match.group(1)
                    # Sayi degilse ve skip_words'te degilse
                    if not candidate.isdigit() and candidate not in skip_words and len(candidate) > 2:
                        # Bu bir isim olabilir - editor matcher ile kontrol et
                        editor_result = self.editor_matcher.find_editor(candidate)
                        if editor_result["status"] in ["single", "multiple"]:
                            analysis["person"] = candidate
                            analysis["person_type"] = "editor"

        # 5. Query type belirleme
        if analysis["person"]:
            analysis["query_type"] = "person_metric"
        elif analysis["metric"] and not analysis["category"]:
            analysis["query_type"] = "simple_metric"
        elif analysis["category"]:
            analysis["query_type"] = "category_metric"
        else:
            analysis["query_type"] = "complex"

        return analysis

    def _handle_analyzed_query(self, query: str, analysis: Dict) -> Optional[str]:
        """
        Analiz edilmis sorguyu isle.

        Returns:
            Sonuc string veya None (baska handler'a devretmek icin)
        """
        query_type = analysis["query_type"]

        # Kisi bazli metrik sorgusu (metric None olsa bile varsayilan screenPageViews kullanilir)
        if query_type == "person_metric" and analysis["person"]:
            return self._handle_person_metric(analysis)

        # Basit metrik sorgusu (kisi yok)
        if query_type == "simple_metric" and analysis["metric"]:
            return self._handle_simple_metric_analyzed(analysis)

        # Kategori bazli metrik sorgusu
        if query_type == "category_metric" and analysis["category"]:
            return self._handle_category_metric(analysis)

        return None  # Diger handler'lara devret

    def _handle_person_metric(self, analysis: Dict) -> str:
        """Kisi bazli metrik sorgusu - analiz edilmis"""
        person_name = analysis["person"]
        person_type = analysis["person_type"]
        start_date, end_date = analysis["date_range"]
        publish_date_range = analysis.get("publish_date_range")  # Yayin tarihi filtresi
        newstype_filter = analysis.get("newstype")  # Icerik turu filtresi (video, galeri, vb.)
        metric = analysis["metric"] or "screenPageViews"
        metric_name = analysis["metric_name"] or "Sayfa Goruntuleme"

        # Kisiyi bul
        if person_type == "author":
            # Yazar icin GA4'te ara
            person_code = self._find_author_in_ga4(person_name, start_date, end_date)
            if not person_code:
                return f"'{person_name}' isimli yazar bulunamadi."
            real_name = person_code  # Yazar icin kod = isim
            dimension = "author"
            codes_to_query = [person_code]  # Yazar icin tek kod
        else:
            # Editor icin CSV'den ara
            editor_result = self.editor_matcher.find_editor(person_name)
            if editor_result["status"] not in ["single", "multiple"]:
                return f"'{person_name}' isimli editor bulunamadi."
            person_code = editor_result["matches"][0]["code"]
            real_name = self.editor_matcher.get_real_name(person_code) or person_code
            dimension = "editor"

            # Dot variation'lari da ekle (oyenilmez ve o.yenilmez gibi)
            codes_to_query = [person_code]
            person_code_lower = person_code.lower()

            # Noktali versiyon varsa noktasiz da ekle
            if '.' in person_code_lower:
                without_dot = person_code_lower.replace('.', '')
                if without_dot not in [c.lower() for c in codes_to_query]:
                    codes_to_query.append(without_dot)
            else:
                # Noktasiz ise noktali versiyon da ekle (ilk harf + nokta + geri kalan)
                if len(person_code_lower) > 1:
                    dotted = person_code_lower[0] + '.' + person_code_lower[1:]
                    if dotted not in [c.lower() for c in codes_to_query]:
                        codes_to_query.append(dotted)

        # Tum kod varyasyonlari icin toplam deger hesapla
        total_value = 0
        found_any_data = False

        for code in codes_to_query:
            # Filtre olustur
            filters = {dimension: code}

            # Newstype filtresi varsa ekle (video, galeri, vb.)
            if newstype_filter:
                filters["newstype"] = newstype_filter

            # Yayin tarihi filtresi varsa ekle
            if publish_date_range:
                pub_start, pub_end = publish_date_range
                # publisheddate filtresi - tarih araliginda yayinlanan icerikler
                # GA4'te tarih araligi filtresi icin birden fazla deger gerekebilir
                # Simdilik tek tarih veya tarih araligi icin farkli sorgular yapacagiz

                if pub_start == pub_end:
                    # Tek gun
                    filters["publisheddate"] = pub_start
                else:
                    # Tarih araligi - publisheddate dimension'i ile birlikte sorgu yapacagiz
                    # ve sonuclari filtreleyecegiz
                    pass  # Asagida ozel islem yapilacak

            # Yayin tarihi araligi varsa ozel sorgu
            if publish_date_range and publish_date_range[0] != publish_date_range[1]:
                pub_start, pub_end = publish_date_range
                # publisheddate dimension'i ile sorgu yap ve filtreleme uygula
                pub_filters = {dimension: code}
                # Newstype filtresi varsa ekle
                if newstype_filter:
                    pub_filters["newstype"] = newstype_filter

                df = self.client.run_query(
                    dimensions=["publisheddate"],
                    metrics=[metric],
                    start_date=start_date,
                    end_date=end_date,
                    filters=pub_filters,
                    return_type="list"
                )

                if df:
                    for row in df:
                        # publisheddate sutununu bul - farkli formatlarda gelebilir
                        published_date = None
                        for key in row.keys():
                            key_lower = key.lower()
                            if 'publish' in key_lower or 'yayin' in key_lower or 'yayın' in key_lower:
                                published_date = row[key]
                                break

                        # Tarih araliginda mi kontrol et
                        if published_date and pub_start <= str(published_date) <= pub_end:
                            found_any_data = True
                            for key, val in row.items():
                                if isinstance(val, (int, float)):
                                    total_value += val
            else:
                # Normal sorgu veya tek gun yayin tarihi
                df = self.client.run_query(
                    dimensions=[],
                    metrics=[metric],
                    start_date=start_date,
                    end_date=end_date,
                    filters=filters,
                    return_type="list"
                )

                if df:
                    found_any_data = True
                    # Tum satirlardaki degerleri topla
                    for row in df:
                        for key, val in row.items():
                            if isinstance(val, (int, float)) and key != 'Tarih':
                                total_value += val

        if not found_any_data:
            return f"'{person_name}' icin veri bulunamadi."

        value = total_value

        # Tarih aciklamasi
        tarih_str = self._get_date_description(start_date, end_date)

        # Yayin tarihi aciklamasi
        publish_str = None
        if publish_date_range:
            pub_start, pub_end = publish_date_range
            if pub_start == pub_end:
                publish_str = f"Yayin Tarihi: {self._format_publish_date(pub_start)}"
            else:
                publish_str = f"Yayin Tarihi: {self._format_publish_date(pub_start)} - {self._format_publish_date(pub_end)}"

        # Newstype aciklamasi
        newstype_str = None
        if newstype_filter:
            newstype_display = {
                "video": "Video",
                "newsgaleri": "Galeri",
                "haber": "Haber",
                "yazar": "Kose Yazisi",
                "ozel-haber": "Ozel Haber",
                "derleme-haber": "Derleme Haber",
                "plus": "Plus Icerik",
                "viral": "Viral",
                "interactive": "Interaktif",
                "gazete-haberi": "Gazete Haberi"
            }
            newstype_str = f"Icerik Turu: {newstype_display.get(newstype_filter, newstype_filter.title())}"

        # Scorecard formatinda dondur
        output = []
        output.append("")
        output.append("=" * 50)
        output.append(f"  {real_name.upper()}")
        output.append(f"  Veri Tarihi: {tarih_str}")
        if publish_str:
            output.append(f"  {publish_str}")
        if newstype_str:
            output.append(f"  {newstype_str}")
        output.append("=" * 50)
        output.append("")
        output.append(f"  {metric_name}: {self._format_number(value)}")
        output.append("")
        output.append("=" * 50)

        self.last_dataframe = None
        return "\n".join(output)

    def _handle_simple_metric_analyzed(self, analysis: Dict) -> str:
        """Basit metrik sorgusu - analiz edilmis"""
        start_date, end_date = analysis["date_range"]
        metric = analysis["metric"]
        metric_name = analysis["metric_name"]

        # GA4'ten veri cek
        df = self.client.run_query(
            dimensions=[],
            metrics=[metric],
            start_date=start_date,
            end_date=end_date,
            return_type="list"
        )

        if not df:
            return "Veri bulunamadi."

        # Degeri al
        value = 0
        for key, val in df[0].items():
            if isinstance(val, (int, float)):
                value = val
                break

        # Tarih aciklamasi
        tarih_str = self._get_date_description(start_date, end_date)

        # Scorecard formatinda dondur
        output = []
        output.append("")
        output.append("=" * 40)
        output.append(f"  {metric_name.upper()}")
        output.append(f"  {tarih_str}")
        output.append("=" * 40)
        output.append("")
        output.append(f"  {self._format_number(value)}")
        output.append("")
        output.append("=" * 40)

        self.last_dataframe = None
        return "\n".join(output)

    def _handle_category_metric(self, analysis: Dict) -> str:
        """Kategori bazli metrik sorgusu - analiz edilmis"""
        start_date, end_date = analysis["date_range"]
        category = analysis["category"]
        metric = analysis["metric"] or "screenPageViews"
        metric_name = analysis["metric_name"] or "Sayfa Goruntuleme"

        # GA4'ten veri cek - kategori icin vcat1 dimension'i kullan
        df = self.client.run_query(
            dimensions=[],
            metrics=[metric],
            start_date=start_date,
            end_date=end_date,
            filters={"vcat1": category},  # GA4'te kategori dimension'i vcat1
            return_type="list"
        )

        if not df:
            return f"'{category}' kategorisi icin veri bulunamadi."

        # Degeri al
        value = 0
        for key, val in df[0].items():
            if isinstance(val, (int, float)):
                value = val
                break

        # Tarih aciklamasi
        tarih_str = self._get_date_description(start_date, end_date)

        # Scorecard formatinda dondur
        output = []
        output.append("")
        output.append("=" * 50)
        output.append(f"  {category.upper()} KATEGORISI")
        output.append(f"  {tarih_str}")
        output.append("=" * 50)
        output.append("")
        output.append(f"  {metric_name}: {self._format_number(value)}")
        output.append("")
        output.append("=" * 50)

        self.last_dataframe = None
        return "\n".join(output)

    def _get_date_description(self, start_date: str, end_date: str) -> str:
        """Tarih araliginin aciklamasini dondur"""
        if start_date == "yesterday" and end_date == "yesterday":
            return "Dun"
        elif start_date == "today" and end_date == "today":
            return "Bugun"
        elif start_date == "7daysAgo":
            return "Son 7 Gun"
        elif start_date == "30daysAgo":
            return "Son 30 Gun"
        elif start_date == end_date:
            # Spesifik tarih
            try:
                date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                return date_obj.strftime("%d %B %Y").replace("January", "Ocak").replace("February", "Subat").replace("March", "Mart").replace("April", "Nisan").replace("May", "Mayis").replace("June", "Haziran").replace("July", "Temmuz").replace("August", "Agustos").replace("September", "Eylul").replace("October", "Ekim").replace("November", "Kasim").replace("December", "Aralik")
            except:
                return start_date
        else:
            return f"{start_date} - {end_date}"

    def process_query(self, query: str) -> str:
        """Kullanici sorgusunu isle"""
        query = query.strip()

        # Disambiguation bekliyor mu?
        if self.context["pending_disambiguation"]:
            return self._handle_disambiguation(query)

        # Hizli komut mu?
        if query in self.quick_commands:
            _, handler = self.quick_commands[query]
            return handler()

        # Cikis komutlari
        if query.lower() in ["cikis", "exit", "quit", "q"]:
            return "EXIT"

        # Yardim
        if query.lower() in ["yardim", "help", "?"]:
            return self._show_help()

        # YENI: Sorguyu analiz et ve akilli isleme yap
        analysis = self._analyze_query(query)

        # Analiz basarili olduysa, analiz edilmis sorguyu isle
        if analysis["query_type"] in ["person_metric", "simple_metric", "category_metric"]:
            result = self._handle_analyzed_query(query, analysis)
            if result:
                return result

        # ONCE filtreleri kontrol et - filtre varsa dinamik sorgu kullan
        # Bu sayede "spor kategorisi" gibi sorgular sadece spor verisini getirir
        filters = self._extract_filters(query)
        if filters:
            result = self._try_dynamic_query(query)
            if result:
                return result

        # Intent'i bul (analiz basarisiz olduysa veya complex query ise)
        query_lower = query.lower()
        for intent_name, intent_data in self.intents.items():
            for pattern in intent_data["patterns"]:
                if re.search(pattern, query_lower):
                    return intent_data["handler"](query)

        # Bilinmeyen
        return self._handle_unknown(query)

    def _handle_disambiguation(self, selection: str) -> str:
        """
        Kullanicinin disambiguation secimini isle

        Args:
            selection: Kullanici girisi (numara veya kod)

        Returns:
            Sorgu sonucu veya hata mesaji
        """
        pending = self.context["pending_disambiguation"]

        if not pending:
            return "Bekleyen secim yok."

        # Iptal mi?
        if selection.lower() in ["iptal", "cancel", "vazgec"]:
            self.context["pending_disambiguation"] = None
            return "Secim iptal edildi."

        # Secimi coz
        matches = pending["matches"]
        original_query = pending["original_query"]
        match_type = pending["type"]  # "editor" veya "author"

        # Matcher sec
        if match_type == "editor":
            matcher = self.editor_matcher
            dimension = "veditor"
            title_prefix = "Editor"
        else:
            matcher = self.author_matcher
            dimension = "vauthor"
            title_prefix = "Yazar"

        # Secimi cozumle
        resolved = matcher.resolve_disambiguation(selection, matches)

        if not resolved:
            return f"Gecersiz secim. Lutfen 1-{len(matches)} arasi bir numara veya direkt kod girin."

        # Context'i temizle
        self.context["pending_disambiguation"] = None

        # Tarih araligini orijinal sorgudan al
        start_date, end_date = self._extract_date_range(original_query)
        limit = self._extract_limit(original_query)

        # Sorguyu calistir
        df = self.client.run_query(
            dimensions=[dimension, "pagePath", "pageTitle"],
            metrics=["screenPageViews", "totalUsers", "sessions"],
            start_date=start_date,
            end_date=end_date,
            filters={dimension: resolved},
            order_by="screenPageViews",
            order_desc=True,
            limit=limit
        )

        return self._format_dataframe(df, f"{title_prefix}: {resolved}")

    def _show_help(self) -> str:
        """Yardim mesaji"""
        output = []
        output.append("\n" + "="*60)
        output.append("  GA4 CHATBOT - YARDIM")
        output.append("="*60)

        output.append("\nANA MENU (0-9):")
        output.append("-"*40)
        for cmd in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            if cmd in self.quick_commands:
                desc, _ = self.quick_commands[cmd]
                output.append(f"  [{cmd}]  {desc}")

        output.append("\nEK RAPORLAR (11-19):")
        output.append("-"*40)
        for cmd in ["11", "12", "13", "14", "15", "16", "17", "18", "19"]:
            if cmd in self.quick_commands:
                desc, _ = self.quick_commands[cmd]
                output.append(f"  [{cmd}] {desc}")

        output.append("\nORNEK SORULAR:")
        output.append("-"*40)
        output.append("  - Dunun en cok okunan 20 haberi")
        output.append("  - Son 7 gunun trafik kaynaklari")
        output.append("  - Spor kategorisi nasil performans gosteriyor")
        output.append("  - Hangi yazarlar en cok okunuyor")
        output.append("  - Video haberler nasil gidiyor")
        output.append("  - Populer etiketler neler")
        output.append("  - Mobil mi desktop mu daha cok")
        output.append("  - Chrome mu Safari mi")
        output.append("  - Yeni kullanicilar mi eski mi fazla")
        output.append("  - Su an kac kisi var")

        output.append("\nEDITOR/YAZAR ARAMA:")
        output.append("-"*40)
        output.append("  Isim ile arama yapabilirsiniz:")
        output.append("  - Editor cemile gelgec performansi")
        output.append("  - Yazar ahmet yilmaz haberleri")
        output.append("  - Cemile editoru nasil gidiyor")
        output.append("  Birden fazla esleme varsa secim yapmaniz istenecek.")

        output.append("\nTARIH SECENEKLERI:")
        output.append("-"*40)
        output.append("  bugun, dun, son 7 gun, son 30 gun, son 3 ay")

        output.append("\nKOMUTLAR:")
        output.append("-"*40)
        output.append("  yardim, help, ?  - Bu mesaji goster")
        output.append("  cikis, exit, q   - Programdan cik")

        return "\n".join(output)

    def run(self):
        """Chatbot'u calistir"""
        print("\n" + "="*50)
        print("  GA4 ANALYTICS CHATBOT")
        print("  Hürriyet - Vatan Analytics")
        print("="*50)
        print("\nMerhaba! Size analytics verileri hakkinda")
        print("yardimci olabilirim.")
        print("\nYardim icin 'yardim' yazin veya hizli erisim")
        print("icin 0-9 arasi bir numara girin.")
        print("-"*50)

        while True:
            try:
                query = input("\n> ").strip()

                if not query:
                    continue

                result = self.process_query(query)

                if result == "EXIT":
                    print("\nGorüsmek üzere!")
                    break

                print(result)

            except KeyboardInterrupt:
                print("\n\nGorüsmek üzere!")
                break
            except Exception as e:
                print(f"\nHata olustu: {str(e)}")
                print("Lutfen tekrar deneyin.")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    chatbot = GA4Chatbot()
    chatbot.run()
