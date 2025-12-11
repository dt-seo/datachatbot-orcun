# -*- coding: utf-8 -*-
"""
Fuzzy Matcher - Editor/Yazar ve Dimension/Metric eslemesi
GA4 verisindeki kodlu isimleri kullanici dostu isimlere esler

Kullanim:
    from fuzzy_matcher import EditorMatcher, DimensionMetricMatcher

    # Editor esleme
    editor_matcher = EditorMatcher(ga4_client)
    result = editor_matcher.find_editor("cemile gelgec")

    # Dimension/Metric esleme
    dm_matcher = DimensionMetricMatcher()
    dim = dm_matcher.find_dimension("goruntuleme")
    metric = dm_matcher.find_metric("kac kisi")
"""

import re
from typing import Dict, List, Optional, Tuple, Union
from difflib import SequenceMatcher


# =============================================================================
# TURKCE ALIAS TANIMLARI - Gunluk dil karsiliklari
# =============================================================================

# Dimension Alias'lari - Kullanicinin yazabilecegi tum varyasyonlar
DIMENSION_ALIASES = {
    # ===== SAYFA/ICERIK =====
    "pagePath": [
        "sayfa", "sayfa yolu", "url", "link", "adres", "path",
        "hangi sayfa", "hangi sayfalar", "sayfalar", "icerik",
        "haber", "haberler", "yazi", "yazilar", "makale"
    ],
    "pageTitle": [
        "baslik", "sayfa basligi", "haber basligi", "title",
        "basliklar", "hangi baslik", "ne basligi"
    ],
    "landingPage": [
        "giris sayfasi", "landing", "ilk sayfa", "giris",
        "nereden girdi", "hangi sayfadan girdi", "baslangic sayfasi"
    ],
    "exitPage": [
        "cikis sayfasi", "son sayfa", "cikis", "nereden cikti",
        "hangi sayfadan cikti", "terk ettigi sayfa"
    ],
    "hostname": [
        "site", "domain", "alan adi", "host", "website"
    ],

    # ===== TARIH/ZAMAN =====
    "date": [
        "tarih", "gun", "hangi gun", "ne zaman", "tarihler"
    ],
    "dateHour": [
        "tarih saat", "gun saat", "hangi saatte"
    ],
    "hour": [
        "saat", "hangi saat", "saatler", "saatlik", "kacta"
    ],
    "dayOfWeek": [
        "haftanin gunu", "hangi gun", "gun", "pazartesi", "sali",
        "carsamba", "persembe", "cuma", "cumartesi", "pazar"
    ],
    "month": [
        "ay", "hangi ay", "aylar", "aylik"
    ],
    "week": [
        "hafta", "hangi hafta", "haftalar", "haftalik"
    ],
    "year": [
        "yil", "hangi yil", "yillar", "yillik"
    ],

    # ===== TRAFIK KAYNAKLARI =====
    "sessionDefaultChannelGroup": [
        "kanal", "kanal grubu", "trafik kanali", "nereden geldi",
        "nereden geliyor", "kaynak kanal", "trafik", "channel",
        "organic", "direct", "social", "referral"
    ],
    "source": [
        "kaynak", "trafik kaynagi", "nereden", "hangi kaynak",
        "google", "facebook", "twitter", "instagram"
    ],
    "medium": [
        "ortam", "medium", "trafik ortami", "organik", "cpc", "referans"
    ],
    "sourceMedium": [
        "kaynak ortam", "kaynak/ortam", "source medium"
    ],
    "campaignName": [
        "kampanya", "kampanya adi", "hangi kampanya", "reklam kampanyasi"
    ],

    # ===== CIHAZ/TEKNOLOJI =====
    "deviceCategory": [
        "cihaz", "cihaz turu", "mobil", "desktop", "tablet",
        "hangi cihaz", "telefon", "bilgisayar", "mobil mi desktop mu",
        "cihaz dagilimi", "cihazlar"
    ],
    "browser": [
        "tarayici", "browser", "chrome", "safari", "firefox", "edge",
        "hangi tarayici", "tarayicilar"
    ],
    "operatingSystem": [
        "isletim sistemi", "os", "windows", "mac", "ios", "android",
        "hangi isletim sistemi", "sistem"
    ],
    "screenResolution": [
        "ekran cozunurlugu", "cozunurluk", "resolution", "ekran boyutu"
    ],
    "mobileDeviceBranding": [
        "telefon markasi", "marka", "samsung", "apple", "xiaomi", "huawei"
    ],

    # ===== KONUM =====
    "country": [
        "ulke", "hangi ulke", "ulkeler", "turkiye", "nereden geliyor konum"
    ],
    "city": [
        "sehir", "hangi sehir", "sehirler", "il", "istanbul", "ankara", "izmir"
    ],
    "region": [
        "bolge", "hangi bolge", "bolgeler"
    ],
    "continent": [
        "kita", "hangi kita", "kitalar", "avrupa", "asya"
    ],

    # ===== KULLANICI =====
    "newVsReturning": [
        "yeni kullanici", "geri donen", "yeni mi eski mi",
        "yeni ziyaretci", "tekrar gelen", "sadik kullanici",
        "ilk kez gelen", "daha once gelmis mi"
    ],
    "userAgeBracket": [
        "yas", "yas grubu", "yas araligi", "kac yasinda", "demografik"
    ],
    "userGender": [
        "cinsiyet", "kadin", "erkek", "gender"
    ],

    # ===== EVENT =====
    "eventName": [
        "event", "olay", "etkinlik", "event adi", "hangi event"
    ],

    # ===== CUSTOM DIMENSIONS (Haber sitesi icin) =====
    "vcat1": [
        "kategori", "ana kategori", "haber kategorisi", "bolum",
        "hangi kategori", "kategoriler", "spor", "ekonomi", "gundem", "magazin"
    ],
    "vcat2": [
        "alt kategori", "ikinci kategori", "alt bolum"
    ],
    "veditor": [
        "editor", "editoru", "editorler", "hangi editor",
        "kim hazirladi", "kim girdi", "editor performansi"
    ],
    "vauthor": [
        "yazar", "yazari", "yazarlar", "hangi yazar", "kim yazdi",
        "kose yazari", "muhabir", "yazar performansi"
    ],
    "vnewstype": [
        "haber tipi", "haber turu", "icerik tipi", "video", "galeri",
        "foto galeri", "normal haber", "canli yayin"
    ],
    "vpagetype": [
        "sayfa tipi", "sayfa turu", "anasayfa", "detay sayfa", "liste sayfa"
    ],
    "vtag": [
        "etiket", "tag", "etiketler", "hangi etiket", "konu"
    ],
    "publisheddate": [
        "yayin tarihi", "yayinlanma tarihi", "haber tarihi", "ne zaman yayinlandi"
    ],
    "vnewsid": [
        "haber id", "icerik id", "news id", "haber numarasi"
    ],
}

# Metric Alias'lari
METRIC_ALIASES = {
    # ===== TEMEL METRIKLER =====
    "screenPageViews": [
        "goruntuleme", "sayfa goruntulemesi", "pageview", "pv",
        "kac goruntuleme", "kac kez goruntulendi", "izlenme",
        "okunma", "kac okundu", "kac kisi okudu", "hit",
        "tiklama", "kac tiklandi", "goruntulenme sayisi"
    ],
    "totalUsers": [
        "kullanici", "kullanici sayisi", "kac kullanici", "kac kisi",
        "ziyaretci", "ziyaretci sayisi", "user", "users",
        "kac kisi girdi", "kac kisi geldi", "unique"
    ],
    "sessions": [
        "oturum", "session", "oturum sayisi", "kac oturum",
        "ziyaret", "ziyaret sayisi", "kac ziyaret"
    ],
    "newUsers": [
        "yeni kullanici", "yeni ziyaretci", "ilk kez gelen",
        "kac yeni kullanici", "yeni kisi"
    ],
    "activeUsers": [
        "aktif kullanici", "aktif kisi", "active user"
    ],

    # ===== ENGAGEMENT METRIKLERI =====
    "bounceRate": [
        "hemen cikma", "bounce rate", "bounce", "hemen cikma orani",
        "tek sayfa", "direkt cikis", "hemen terk"
    ],
    "engagementRate": [
        "etkilesim orani", "engagement", "baglilik", "ilgi orani"
    ],
    "averageSessionDuration": [
        "ortalama sure", "oturum suresi", "kac dakika", "ne kadar kaldi",
        "site suresi", "kalma suresi", "duration", "zaman gecirdi"
    ],
    "userEngagementDuration": [
        "kullanici suresi", "aktif sure", "gecirilen sure"
    ],
    "engagedSessions": [
        "aktif oturum", "ilgili oturum", "engaged session"
    ],
    "sessionsPerUser": [
        "kullanici basi oturum", "oturum/kullanici", "kac kez geldi"
    ],
    "screenPageViewsPerSession": [
        "oturum basi goruntuleme", "sayfa/oturum", "kac sayfa gezdi"
    ],

    # ===== GIRIS/CIKIS =====
    "entrances": [
        "giris", "giris sayisi", "kac giris", "nereden girdi"
    ],
    "exits": [
        "cikis", "cikis sayisi", "kac cikis", "nereden cikti"
    ],

    # ===== EVENT METRIKLERI =====
    "eventCount": [
        "event sayisi", "olay sayisi", "kac event", "toplam event"
    ],
    "conversions": [
        "donusum", "conversion", "hedef", "kac donusum"
    ],

    # ===== CUSTOM METRICS (Haber sitesi icin) =====
    "averageDuration": [
        "okuma suresi", "ortalama okuma", "kac saniye okudu",
        "haber okuma suresi", "ne kadar okudu"
    ],
    "maxScroll": [
        "scroll", "kaydirma", "ne kadar kaydirdi", "asagi indi mi",
        "sayfa sonu", "sonuna kadar okudu mu"
    ],
}


class DimensionMetricMatcher:
    """Turkce gunluk dil ile dimension/metric eslemesi yapar"""

    def __init__(self):
        """Matcher'i baslat ve alias index'lerini olustur"""
        self._dimension_index: Dict[str, str] = {}
        self._metric_index: Dict[str, str] = {}
        self._build_indexes()

    def _build_indexes(self):
        """Alias'lardan hizli arama indexi olustur"""
        # Dimension index
        for api_name, aliases in DIMENSION_ALIASES.items():
            # API ismini de ekle
            self._dimension_index[api_name.lower()] = api_name
            self._dimension_index[api_name.lower().replace("_", " ")] = api_name
            # Tum alias'lari ekle
            for alias in aliases:
                self._dimension_index[alias.lower()] = api_name

        # Metric index
        for api_name, aliases in METRIC_ALIASES.items():
            self._metric_index[api_name.lower()] = api_name
            self._metric_index[api_name.lower().replace("_", " ")] = api_name
            for alias in aliases:
                self._metric_index[alias.lower()] = api_name

    def _normalize_query(self, query: str) -> str:
        """Sorguyu normalize et (kucuk harf, fazla bosluk temizle)"""
        query = query.lower().strip()
        query = re.sub(r"\s+", " ", query)
        # Turkce karakterleri koru
        return query

    def _similarity_score(self, str1: str, str2: str) -> float:
        """Iki string arasindaki benzerlik skoru"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    def find_dimension(self, query: str, threshold: float = 0.6) -> Optional[Dict]:
        """
        Turkce sorgudan dimension bul

        Args:
            query: Kullanici sorgusu (ör: "hangi cihaz", "kategoriler")
            threshold: Minimum benzerlik skoru

        Returns:
            {"api_name": "deviceCategory", "score": 0.95, "matched_alias": "cihaz"}
            veya None
        """
        query = self._normalize_query(query)

        # 1. Tam esleme kontrolu
        if query in self._dimension_index:
            return {
                "api_name": self._dimension_index[query],
                "score": 1.0,
                "matched_alias": query,
                "match_type": "exact"
            }

        # 2. Icerik kontrolu (query bir alias'in icinde mi?)
        best_match = None
        best_score = 0

        for alias, api_name in self._dimension_index.items():
            # Alias query'yi icerir mi veya query alias'i icerir mi?
            if query in alias or alias in query:
                # Uzunluk oranina gore skor
                score = min(len(query), len(alias)) / max(len(query), len(alias))
                score = max(score, 0.7)  # Minimum 0.7

                if score > best_score:
                    best_score = score
                    best_match = {
                        "api_name": api_name,
                        "score": score,
                        "matched_alias": alias,
                        "match_type": "contains"
                    }

        # 3. Fuzzy esleme
        if best_score < threshold:
            for alias, api_name in self._dimension_index.items():
                score = self._similarity_score(query, alias)
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = {
                        "api_name": api_name,
                        "score": score,
                        "matched_alias": alias,
                        "match_type": "fuzzy"
                    }

        return best_match if best_score >= threshold else None

    def find_metric(self, query: str, threshold: float = 0.6) -> Optional[Dict]:
        """
        Turkce sorgudan metric bul

        Args:
            query: Kullanici sorgusu (ör: "kac kisi", "goruntuleme")
            threshold: Minimum benzerlik skoru

        Returns:
            {"api_name": "totalUsers", "score": 0.95, "matched_alias": "kac kisi"}
            veya None
        """
        query = self._normalize_query(query)

        # 1. Tam esleme
        if query in self._metric_index:
            return {
                "api_name": self._metric_index[query],
                "score": 1.0,
                "matched_alias": query,
                "match_type": "exact"
            }

        # 2. Icerik kontrolu
        best_match = None
        best_score = 0

        for alias, api_name in self._metric_index.items():
            if query in alias or alias in query:
                score = min(len(query), len(alias)) / max(len(query), len(alias))
                score = max(score, 0.7)

                if score > best_score:
                    best_score = score
                    best_match = {
                        "api_name": api_name,
                        "score": score,
                        "matched_alias": alias,
                        "match_type": "contains"
                    }

        # 3. Fuzzy esleme
        if best_score < threshold:
            for alias, api_name in self._metric_index.items():
                score = self._similarity_score(query, alias)
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = {
                        "api_name": api_name,
                        "score": score,
                        "matched_alias": alias,
                        "match_type": "fuzzy"
                    }

        return best_match if best_score >= threshold else None

    def extract_dimensions_from_query(self, query: str) -> List[Dict]:
        """
        Bir cümleden tüm dimension'lari cikar

        Args:
            query: "editör cansu hangi kategoride kac goruntuleme almis"

        Returns:
            [{"api_name": "veditor", ...}, {"api_name": "vcat1", ...}]
        """
        query = self._normalize_query(query)
        found = []
        found_apis = set()

        # Her alias'i kontrol et
        for alias, api_name in self._dimension_index.items():
            if len(alias) >= 3 and alias in query and api_name not in found_apis:
                found.append({
                    "api_name": api_name,
                    "score": 0.9,
                    "matched_alias": alias,
                    "match_type": "extract"
                })
                found_apis.add(api_name)

        return found

    def extract_metrics_from_query(self, query: str) -> List[Dict]:
        """
        Bir cümleden tüm metric'leri cikar

        Args:
            query: "kac kullanici geldi ve kac goruntuleme aldi"

        Returns:
            [{"api_name": "totalUsers", ...}, {"api_name": "screenPageViews", ...}]
        """
        query = self._normalize_query(query)
        found = []
        found_apis = set()

        for alias, api_name in self._metric_index.items():
            if len(alias) >= 3 and alias in query and api_name not in found_apis:
                found.append({
                    "api_name": api_name,
                    "score": 0.9,
                    "matched_alias": alias,
                    "match_type": "extract"
                })
                found_apis.add(api_name)

        return found

    def parse_query(self, query: str) -> Dict:
        """
        Sorguyu tam olarak parse et - dimension, metric ve filtreleri cikar

        Args:
            query: "editor cansu kategorisi spor olan haberler kac goruntuleme almis"

        Returns:
            {
                "dimensions": [...],
                "metrics": [...],
                "potential_filters": {"veditor": "cansu", "vcat1": "spor"},
                "raw_query": "..."
            }
        """
        dimensions = self.extract_dimensions_from_query(query)
        metrics = self.extract_metrics_from_query(query)

        # Potansiyel filtreler (basit keyword extraction)
        filters = {}

        # Kategori filtresi
        kategori_match = re.search(
            r"kategori[si]*\s+(\w+)|(\w+)\s+kategorisi",
            query.lower()
        )
        if kategori_match:
            filters["vcat1"] = kategori_match.group(1) or kategori_match.group(2)

        return {
            "dimensions": dimensions,
            "metrics": metrics,
            "potential_filters": filters,
            "raw_query": query
        }

    def suggest_for_query(self, query: str, top_n: int = 3) -> Dict:
        """
        Sorgu icin dimension ve metric onerileri sun

        Args:
            query: Kullanici sorgusu
            top_n: Her kategori icin maksimum oneri sayisi

        Returns:
            {
                "suggested_dimensions": [...],
                "suggested_metrics": [...],
                "confidence": "high" | "medium" | "low"
            }
        """
        dims = self.extract_dimensions_from_query(query)
        mets = self.extract_metrics_from_query(query)

        # Eger hicbir sey bulunamazsa, sorguyu kelime kelime dene
        if not dims and not mets:
            words = query.lower().split()
            for word in words:
                if len(word) >= 3:
                    dim = self.find_dimension(word, threshold=0.5)
                    if dim and dim["api_name"] not in [d["api_name"] for d in dims]:
                        dims.append(dim)

                    met = self.find_metric(word, threshold=0.5)
                    if met and met["api_name"] not in [m["api_name"] for m in mets]:
                        mets.append(met)

        # Confidence hesapla
        total_found = len(dims) + len(mets)
        if total_found >= 2:
            confidence = "high"
        elif total_found == 1:
            confidence = "medium"
        else:
            confidence = "low"

        return {
            "suggested_dimensions": dims[:top_n],
            "suggested_metrics": mets[:top_n],
            "confidence": confidence
        }


class EditorMatcher:
    """Editor ve yazar isimlerini fuzzy matching ile esler - CSV dosyasindan gercek isimlerle"""

    # Site marka eslesmesi
    SITE_BRAND_MAP = {
        "hurriyet": "hurriyet",
        "vatan": "vatan",
        "milliyet": "milliyet",
        "posta": "posta",
        "cnn": "cnn",
        "fanatik": "fanatik",
        "kanald": "kanald",
        "ign": "ign",
        "mashable": "mashable",
    }

    # Turkce karakter donusumu
    TURKISH_CHAR_MAP = {
        'ç': 'c', 'Ç': 'c',
        'ğ': 'g', 'Ğ': 'g',
        'ı': 'i', 'İ': 'i', 'I': 'i',
        'ö': 'o', 'Ö': 'o',
        'ş': 's', 'Ş': 's',
        'ü': 'u', 'Ü': 'u',
    }

    def __init__(self, ga4_client):
        """
        EditorMatcher'i baslat

        Args:
            ga4_client: GA4Client instance
        """
        self.client = ga4_client
        self._editor_cache: Dict[str, List[str]] = {}
        self._editor_list: List[str] = []
        self._name_to_user_map: Dict[str, str] = {}  # Gercek isim -> username (normalized)
        self._name_to_user_map_original: Dict[str, str] = {}  # Gercek isim -> username (original)
        self._user_to_name_map: Dict[str, str] = {}  # Username -> gercek isim
        self._dot_variation_map: Dict[str, str] = {}  # Noktasiz kod -> orijinal kod (o.yenilmez icin)
        self._last_fetch_date: str = None
        self._csv_loaded: bool = False

    def _normalize_turkish(self, text: str) -> str:
        """Turkce karakterleri ASCII'ye donustur"""
        result = text.lower()
        for tr_char, ascii_char in self.TURKISH_CHAR_MAP.items():
            result = result.replace(tr_char, ascii_char)
        return result

    def _load_csv_mapping(self):
        """CSV dosyasindan editor listesini yukle"""
        if self._csv_loaded:
            return

        import os
        import pandas as pd

        # CSV dosyasinin yolu
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, "editorlist.csv")

        if not os.path.exists(csv_path):
            print(f"[UYARI] editorlist.csv bulunamadi: {csv_path}")
            return

        try:
            df = pd.read_csv(csv_path, encoding='utf-8-sig')

            # Marka bazli filtreleme
            brand_key = getattr(self.client, 'brand_key', None)

            for _, row in df.iterrows():
                name = str(row.get('name', '')).strip()
                user = str(row.get('user', '')).strip()
                site = str(row.get('site', '')).strip().lower()

                if not name or not user or name == 'nan' or user == 'nan':
                    continue

                # Marka filtresi (opsiyonel - tum markalari da kabul edebiliriz)
                # Simdilik tum markalari yukluyoruz, sorgu sirasinda filtrelenebilir

                # Isim -> username mapping (normalized - Turkce karakterler ASCII'ye)
                name_normalized = self._normalize_turkish(name)
                user_lower = user.lower()

                # Tam isim mapping (normalized)
                if name_normalized not in self._name_to_user_map:
                    self._name_to_user_map[name_normalized] = user

                # Sadece ad (ilk kelime - normalized)
                first_name = name_normalized.split()[0] if name_normalized else ""
                if first_name and first_name not in self._name_to_user_map:
                    self._name_to_user_map[first_name] = user

                # Sadece soyad (son kelime - normalized)
                if len(name_normalized.split()) > 1:
                    last_name = name_normalized.split()[-1]
                    # Soyad zaten varsa override etme (cakisma olabilir)
                    if last_name not in self._name_to_user_map:
                        self._name_to_user_map[last_name] = user

                # Username -> isim mapping (orijinal isim sakla)
                self._user_to_name_map[user_lower] = name

                # Nokta varyasyonlari icin mapping ekle
                # GA4'teki noktali kodlar (o.yenilmez) CSV'deki noktasiz kodlarla (oyenilmez) eslessin
                # veya tersi: CSV'de noktali varsa GA4'te noktasiz olabilir

                # Eger username'de nokta varsa, noktasiz versiyonunu da ekle
                if '.' in user_lower:
                    without_dot = user_lower.replace('.', '')
                    self._dot_variation_map[without_dot] = user_lower  # noktasiz -> noktali
                    self._user_to_name_map[without_dot] = name  # noktasiz icin de isim ekle
                else:
                    # Noktasiz username icin potansiyel noktali varyasyonlari olustur
                    # Ornek: oyenilmez -> o.yenilmez, sdinc -> s.dinc
                    # Tek harf + geri kalan pattern'i varsa noktali versiyon olustur
                    if len(user_lower) > 1:
                        dotted = user_lower[0] + '.' + user_lower[1:]
                        self._dot_variation_map[dotted] = user_lower  # noktali -> noktasiz

            self._csv_loaded = True
            print(f"[OK] CSV'den {len(self._name_to_user_map)} isim-kullanici eslesmesi yuklendi")

        except Exception as e:
            print(f"[HATA] CSV yuklenemedi: {str(e)}")

    def _fetch_editors(self, force_refresh: bool = False) -> List[str]:
        """
        GA4'ten editor listesini cek ve CSV ile birlestir

        Args:
            force_refresh: Cache'i yoksay ve yeniden cek

        Returns:
            Editor kodlari listesi
        """
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")

        # CSV mapping'i yukle
        self._load_csv_mapping()

        # Cache gecerli mi?
        if not force_refresh and self._editor_list and self._last_fetch_date == today:
            return self._editor_list

        # GA4'ten cek (son 30 gun)
        try:
            df = self.client.run_query(
                dimensions=["editor"],
                metrics=["screenPageViews"],
                start_date="30daysAgo",
                end_date="yesterday",
                order_by="screenPageViews",
                order_desc=True,
                limit=1000
            )

            if df is not None and not df.empty:
                # Turkce kolon adi
                col_name = "Editor" if "Editor" in df.columns else "Editör" if "Editör" in df.columns else df.columns[0]
                self._editor_list = df[col_name].dropna().unique().tolist()

                # Bos ve (not set) degerleri filtrele
                self._editor_list = [
                    e for e in self._editor_list
                    if e and e.strip() and e != "(not set)"
                ]

                self._last_fetch_date = today
                print(f"[OK] {len(self._editor_list)} editor yuklendi")

        except Exception as e:
            print(f"[HATA] Editor listesi cekilemedi: {str(e)}")

        return self._editor_list

    def get_real_name(self, username: str) -> Optional[str]:
        """
        Username'den gercek ismi al

        Nokta varyasyonlarini da destekler:
        - o.yenilmez -> oyenilmez (CSV'de oyenilmez varsa)
        - s.dinc -> sdinc (CSV'de sdinc varsa)
        - oyenilmez -> o.yenilmez (GA4'te noktasiz ama CSV'de noktali)
        """
        self._load_csv_mapping()
        username_lower = username.lower()

        # 1. Direkt esleme
        if username_lower in self._user_to_name_map:
            return self._user_to_name_map[username_lower]

        # 2. Nokta varyasyonu dene (o.yenilmez -> oyenilmez)
        if '.' in username_lower:
            without_dot = username_lower.replace('.', '')
            if without_dot in self._user_to_name_map:
                return self._user_to_name_map[without_dot]

        # 3. dot_variation_map'ten bak (her iki yonde de)
        if username_lower in self._dot_variation_map:
            mapped = self._dot_variation_map[username_lower]
            if mapped in self._user_to_name_map:
                return self._user_to_name_map[mapped]

        # 4. Tek harf + nokta + geri kalan pattern dene (oyenilmez -> o.yenilmez)
        if '.' not in username_lower and len(username_lower) > 1:
            dotted = username_lower[0] + '.' + username_lower[1:]
            if dotted in self._user_to_name_map:
                return self._user_to_name_map[dotted]

        return None

    def get_username(self, real_name: str) -> Optional[str]:
        """Gercek isimden username'i al"""
        self._load_csv_mapping()
        return self._name_to_user_map.get(real_name.lower())

    def _parse_editor_code(self, code: str) -> Dict[str, str]:
        """
        Editor kodunu parcalara ayir

        Ornekler:
            "c.gelgec" -> {"initial": "c", "surname": "gelgec"}
            "cemile.gelgec" -> {"name": "cemile", "surname": "gelgec"}
            "cansu.akalp" -> {"name": "cansu", "surname": "akalp"}
            "edagdelen" -> {"full": "edagdelen"}

        Args:
            code: Editor kodu

        Returns:
            Parcalanmis isim dict'i
        """
        code = code.lower().strip()

        # Nokta ile ayrilmis mi?
        if "." in code:
            parts = code.split(".")
            if len(parts) == 2:
                first, second = parts
                # Ilk kisim tek harf mi (baş harf)?
                if len(first) == 1:
                    return {"initial": first, "surname": second}
                else:
                    return {"name": first, "surname": second}

        # Alt cizgi ile ayrilmis mi?
        if "_" in code:
            parts = code.split("_")
            if len(parts) == 2:
                return {"name": parts[0], "surname": parts[1]}

        # Tek parca
        return {"full": code}

    def _parse_query(self, query: str) -> Dict[str, str]:
        """
        Kullanici sorgusunu parcala

        Ornekler:
            "cemile gelgec" -> {"name": "cemile", "surname": "gelgec"}
            "cemile" -> {"name": "cemile"}
            "gelgec" -> {"surname_or_name": "gelgec"}

        Args:
            query: Kullanici sorgusu

        Returns:
            Parcalanmis sorgu dict'i
        """
        query = query.lower().strip()
        parts = query.split()

        if len(parts) >= 2:
            return {"name": parts[0], "surname": " ".join(parts[1:])}
        elif len(parts) == 1:
            return {"name_or_surname": parts[0]}

        return {}

    def _similarity_score(self, str1: str, str2: str) -> float:
        """
        Iki string arasindaki benzerlik skoru (0-1)

        Args:
            str1: Birinci string
            str2: Ikinci string

        Returns:
            Benzerlik skoru (0-1)
        """
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    def _match_score(self, code: str, query_parts: Dict) -> Tuple[float, str]:
        """
        Bir editor kodu ile sorgu arasindaki esleme skorunu hesapla

        Args:
            code: Editor kodu
            query_parts: Parcalanmis sorgu

        Returns:
            (skor, aciklama) tuple'i
        """
        code_parts = self._parse_editor_code(code)
        score = 0.0
        reason = ""

        # Tam isim + soyisim sorgusu
        if "name" in query_parts and "surname" in query_parts:
            q_name = query_parts["name"]
            q_surname = query_parts["surname"]

            # Kod: bas harf + soyisim (c.gelgec)
            if "initial" in code_parts and "surname" in code_parts:
                initial_match = code_parts["initial"] == q_name[0]
                surname_sim = self._similarity_score(code_parts["surname"], q_surname)

                if initial_match and surname_sim > 0.7:
                    score = 0.5 + (surname_sim * 0.5)  # Max 1.0
                    reason = f"Bas harf ({code_parts['initial']}) + soyisim eslesti"

            # Kod: tam isim + soyisim (cemile.gelgec)
            elif "name" in code_parts and "surname" in code_parts:
                name_sim = self._similarity_score(code_parts["name"], q_name)
                surname_sim = self._similarity_score(code_parts["surname"], q_surname)

                if name_sim > 0.7 and surname_sim > 0.7:
                    score = (name_sim + surname_sim) / 2
                    reason = "Tam isim ve soyisim eslesti"

            # Kod: tek parca (edagdelen)
            elif "full" in code_parts:
                full_code = code_parts["full"]
                # Isim veya soyisim iceriyor mu?
                if q_name in full_code or q_surname in full_code:
                    score = 0.6
                    reason = "Isim/soyisim kod icinde bulundu"
                else:
                    # Birlesik kontrol (cemilegelgec gibi)
                    combined = q_name + q_surname
                    combined_sim = self._similarity_score(full_code, combined)
                    if combined_sim > 0.6:
                        score = combined_sim * 0.8
                        reason = "Birlesik isim eslesti"

        # Sadece isim veya soyisim sorgusu
        elif "name_or_surname" in query_parts:
            q_term = query_parts["name_or_surname"]

            # Bas harf + soyisim formati kontrolu (c.gelgec gibi)
            if "initial" in code_parts and "surname" in code_parts:
                # Sorgu terimi bas harfle mi basliyor?
                if code_parts["initial"] == q_term[0]:
                    # Potansiyel esleme
                    score = 0.6
                    reason = f"Bas harf ({code_parts['initial']}) eslesti - olasi esleme"

            # Tam isim eslesmesi
            if "name" in code_parts:
                name_sim = self._similarity_score(code_parts["name"], q_term)
                if name_sim > 0.7:
                    score = max(score, name_sim)
                    reason = "Isim eslesti"

            if "surname" in code_parts:
                surname_sim = self._similarity_score(code_parts["surname"], q_term)
                if surname_sim > 0.7:
                    score = max(score, surname_sim)
                    reason = "Soyisim eslesti"

            # Tek parca kod
            if "full" in code_parts:
                full_sim = self._similarity_score(code_parts["full"], q_term)
                if full_sim > 0.6:
                    score = max(score, full_sim)
                    reason = "Kod benzerligi"
                # Icerik kontrolu
                elif q_term in code_parts["full"]:
                    score = max(score, 0.65)
                    reason = "Terim kodda bulundu"

        return score, reason

    def find_editor(
        self,
        query: str,
        threshold: float = 0.5,
        max_results: int = 5
    ) -> Dict:
        """
        Kullanici sorgusuna en uygun editor(ler)i bul

        Args:
            query: Kullanici sorgusu (ör: "cemile gelgec", "cemile", "c.gelgec")
            threshold: Minimum esleme skoru (0-1)
            max_results: Maksimum sonuc sayisi

        Returns:
            {
                "status": "single" | "multiple" | "not_found",
                "matches": [{"code": "c.gelgec", "score": 0.95, "reason": "..."}],
                "message": "Kullaniciya gosterilecek mesaj"
            }
        """
        # CSV mapping'i yukle (oncelikli kaynak)
        self._load_csv_mapping()

        # ONCE CSV'den gercek isim -> username eslesmesini kontrol et
        # Sorguyu normalize et (Turkce karaktersiz arama icin)
        query_normalized = self._normalize_turkish(query.strip())
        if query_normalized in self._name_to_user_map:
            username = self._name_to_user_map[query_normalized]
            real_name = self._user_to_name_map.get(username.lower(), query)
            return {
                "status": "single",
                "matches": [{"code": username, "score": 1.0, "reason": f"CSV eslesmesi ({real_name})"}],
                "message": f"Editor bulundu: {username} ({real_name})"
            }

        query_lower = query.lower().strip()

        # Editor listesini al
        editors = self._fetch_editors()

        if not editors:
            return {
                "status": "error",
                "matches": [],
                "message": "Editor listesi alinamadi. Lutfen daha sonra tekrar deneyin."
            }

        # Sorguyu dogrudan eslestirmeyi dene
        if query_lower in [e.lower() for e in editors]:
            exact = next(e for e in editors if e.lower() == query_lower)
            return {
                "status": "single",
                "matches": [{"code": exact, "score": 1.0, "reason": "Tam esleme"}],
                "message": f"Editor bulundu: {exact}"
            }

        # Dot variation kontrolu (o.yenilmez -> oyenilmez veya tersi)
        # GA4'teki kod CSV'de farkli formatta olabilir
        if '.' in query_lower:
            without_dot = query_lower.replace('.', '')
            if without_dot in [e.lower() for e in editors]:
                exact = next(e for e in editors if e.lower() == without_dot)
                return {
                    "status": "single",
                    "matches": [{"code": exact, "score": 1.0, "reason": "Nokta varyasyonu eslesmesi"}],
                    "message": f"Editor bulundu: {exact}"
                }
        elif len(query_lower) > 1:
            dotted = query_lower[0] + '.' + query_lower[1:]
            if dotted in [e.lower() for e in editors]:
                exact = next(e for e in editors if e.lower() == dotted)
                return {
                    "status": "single",
                    "matches": [{"code": exact, "score": 1.0, "reason": "Nokta varyasyonu eslesmesi"}],
                    "message": f"Editor bulundu: {exact}"
                }

        # Sorguyu parcala
        query_parts = self._parse_query(query)

        if not query_parts:
            return {
                "status": "not_found",
                "matches": [],
                "message": "Gecersiz sorgu. Lutfen bir isim veya soyisim girin."
            }

        # Tum editorleri skorla
        scored = []
        for editor in editors:
            score, reason = self._match_score(editor, query_parts)
            if score >= threshold:
                scored.append({
                    "code": editor,
                    "score": round(score, 3),
                    "reason": reason
                })

        # Skora gore sirala
        scored.sort(key=lambda x: x["score"], reverse=True)

        # Sonuclari sinirla
        scored = scored[:max_results]

        # Sonuc durumunu belirle
        if not scored:
            return {
                "status": "not_found",
                "matches": [],
                "message": f"'{query}' icin eslesen editor bulunamadi."
            }

        # Tek sonuc ve yuksek skor
        if len(scored) == 1 or (scored[0]["score"] > 0.85 and
                                (len(scored) == 1 or scored[0]["score"] - scored[1]["score"] > 0.15)):
            return {
                "status": "single",
                "matches": [scored[0]],
                "message": f"Editor bulundu: {scored[0]['code']}"
            }

        # Birden fazla sonuc - disambiguation gerekli
        options = "\n".join([
            f"  [{i+1}] {m['code']} (benzerlik: %{int(m['score']*100)})"
            for i, m in enumerate(scored)
        ])

        return {
            "status": "multiple",
            "matches": scored,
            "message": f"'{query}' icin birden fazla esleme bulundu:\n{options}\n\nHangisini kullanmak istediginizi belirtin (numara veya tam kod)."
        }

    def resolve_disambiguation(
        self,
        selection: str,
        previous_matches: List[Dict]
    ) -> Optional[str]:
        """
        Kullanicinin disambiguasyon secimini coz

        Args:
            selection: Kullanici secimi ("1", "2" veya editor kodu)
            previous_matches: Onceki find_editor sonucundaki matches listesi

        Returns:
            Secilen editor kodu veya None
        """
        selection = selection.strip()

        # Numara mi?
        if selection.isdigit():
            idx = int(selection) - 1
            if 0 <= idx < len(previous_matches):
                return previous_matches[idx]["code"]

        # Dogrudan kod mu?
        for match in previous_matches:
            if selection.lower() == match["code"].lower():
                return match["code"]

        return None


class AuthorMatcher(EditorMatcher):
    """Yazar isimlerini fuzzy matching ile esler (Editor matcher'in vauthor versiyonu)"""

    def _fetch_editors(self, force_refresh: bool = False) -> List[str]:
        """
        GA4'ten yazar listesini cek ve cache'le
        """
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")

        if not force_refresh and self._editor_list and self._last_fetch_date == today:
            return self._editor_list

        try:
            df = self.client.run_query(
                dimensions=["vauthor"],
                metrics=["screenPageViews"],
                start_date="30daysAgo",
                end_date="yesterday",
                order_by="screenPageViews",
                order_desc=True,
                limit=1000
            )

            if df is not None and not df.empty:
                col_name = "Yazar" if "Yazar" in df.columns else df.columns[0]
                self._editor_list = df[col_name].dropna().unique().tolist()

                self._editor_list = [
                    e for e in self._editor_list
                    if e and e.strip() and e != "(not set)"
                ]

                self._last_fetch_date = today
                print(f"[OK] {len(self._editor_list)} yazar yuklendi")

        except Exception as e:
            print(f"[HATA] Yazar listesi cekilemedi: {str(e)}")

        return self._editor_list


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("FUZZY MATCHER TEST")
    print("=" * 60)

    # ===========================================
    # 1. DIMENSION/METRIC MATCHER TESTLERI
    # ===========================================
    print("\n" + "=" * 60)
    print("DIMENSION/METRIC MATCHER TESTLERI")
    print("=" * 60)

    dm_matcher = DimensionMetricMatcher()

    # Dimension testleri
    print("\n--- Dimension Esleme Testleri ---\n")
    dim_tests = [
        "cihaz",
        "mobil mi desktop mu",
        "hangi kategoride",
        "editör",
        "nereden geliyor",
        "hangi sehirden",
        "tarayici",
        "yeni kullanici mi"
    ]

    for query in dim_tests:
        result = dm_matcher.find_dimension(query)
        if result:
            print(f"  '{query}' -> {result['api_name']} (skor: {result['score']:.2f}, tip: {result['match_type']})")
        else:
            print(f"  '{query}' -> Bulunamadi")

    # Metric testleri
    print("\n--- Metric Esleme Testleri ---\n")
    metric_tests = [
        "goruntuleme",
        "kac kisi",
        "oturum sayisi",
        "hemen cikma",
        "ne kadar kaldi",
        "tiklama"
    ]

    for query in metric_tests:
        result = dm_matcher.find_metric(query)
        if result:
            print(f"  '{query}' -> {result['api_name']} (skor: {result['score']:.2f}, tip: {result['match_type']})")
        else:
            print(f"  '{query}' -> Bulunamadi")

    # Tam sorgu parse testleri
    print("\n--- Tam Sorgu Parse Testleri ---\n")
    full_queries = [
        "editor cansu dun kac goruntuleme almis",
        "spor kategorisinde kac kullanici var",
        "mobilden gelen trafik ne kadar",
        "istanbul sehirinden kac kisi geldi",
        "hangi tarayicidan daha cok giris var"
    ]

    for query in full_queries:
        result = dm_matcher.suggest_for_query(query)
        print(f"\nSorgu: '{query}'")
        print(f"  Guven: {result['confidence']}")
        if result['suggested_dimensions']:
            dims = [d['api_name'] for d in result['suggested_dimensions']]
            print(f"  Dimensions: {dims}")
        if result['suggested_metrics']:
            mets = [m['api_name'] for m in result['suggested_metrics']]
            print(f"  Metrics: {mets}")

    # ===========================================
    # 2. EDITOR MATCHER TESTLERI
    # ===========================================
    print("\n" + "=" * 60)
    print("EDITOR MATCHER TESTLERI")
    print("=" * 60)

    # Test icin mock data
    class MockGA4Client:
        def run_query(self, **kwargs):
            import pandas as pd
            editors = [
                "c.gelgec", "cemile.yilmaz", "edagdelen", "oozturk",
                "b.arica", "mgoren", "cansu.akalp", "ercan.sarikaya",
                "azizk", "a.kara", "ahmet.kara", "c.yilmaz"
            ]
            return pd.DataFrame({"Editor": editors, "screenPageViews": range(len(editors))})

    mock_client = MockGA4Client()
    editor_matcher = EditorMatcher(mock_client)

    editor_tests = [
        "cemile gelgec",
        "cemile",
        "cansu akalp",
        "ercan",
        "ahmet kara",
        "a.kara",
        "xyz123"
    ]

    print("\n--- Editor Esleme Testleri ---\n")

    for query in editor_tests:
        print(f"Sorgu: '{query}'")
        result = editor_matcher.find_editor(query)
        print(f"  Durum: {result['status']}")
        if result['matches']:
            for m in result['matches'][:3]:
                print(f"    - {m['code']}: {m['score']} ({m['reason']})")
        print()

    print("\n" + "=" * 60)
    print("TESTLER TAMAMLANDI")
    print("=" * 60)
