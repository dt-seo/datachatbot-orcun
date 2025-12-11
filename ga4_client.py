# -*- coding: utf-8 -*-
"""
Google Analytics 4 - API Client
GA4 API ile veri çekme işlemlerini yöneten modül

Kullanım:
    from ga4_client import GA4Client

    # Varsayılan marka (Hürriyet)
    client = GA4Client()

    # Belirli bir marka
    client = GA4Client(brand="vatan")

    data = client.run_query(
        dimensions=["date", "sessionDefaultChannelGroup"],
        metrics=["totalUsers", "sessions"],
        start_date="2024-01-01",
        end_date="2024-01-31"
    )
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union

# Marka Property ID'leri ve Custom Dimension Prefix'leri
BRAND_PROPERTIES = {
    "hurriyet": {
        "property_id": "297156524",
        "name": "Hürriyet",
        "domain": "hurriyet.com.tr",
        "prefix": "h",  # hcat1, hcat2, heditor, hauthor, vb.
        "custom_dimensions": {
            "cat1": "customEvent:hcat1",
            "cat2": "customEvent:hcat2",
            "cat3": "customEvent:hcat3",
            "cat4": "customEvent:hcat4",
            "newsid": "customEvent:hnewsid",
            "editor": "customEvent:heditor",
            "author": "customEvent:hauthor",
            "authortype": "customEvent:hauthortype",
            "publisheddate": "customEvent:hpublishdate",
            "newstype": "customEvent:hnewstype",
            "tag": "customEvent:htag",
        }
    },
    "vatan": {
        "property_id": "307364284",
        "name": "Vatan",
        "domain": "gazetevatan.com",
        "prefix": "v",  # vcat1, vcat2, veditor, vauthor, vb.
        "custom_dimensions": {
            "cat1": "customEvent:vcat1",
            "cat2": "customEvent:vcat2",
            "cat3": "customEvent:vcat3",
            "cat4": "customEvent:vcat4",
            "newsid": "customEvent:vnewsid",
            "editor": "customEvent:veditor",
            "author": "customEvent:vauthor",
            "authortype": "customEvent:vauthortype",
            "publisheddate": "customEvent:vpublishdate",
            "newstype": "customEvent:vnewstype",
            "tag": "customEvent:vtag",
        }
    },
    "cnnturk": {
        "property_id": "308285565",
        "name": "CNN Türk",
        "domain": "cnnturk.com",
        "prefix": "c",  # ccat1, ccat2, ceditor, cauthor, vb.
        "custom_dimensions": {
            "cat1": "customEvent:ccat1",
            "cat2": "customEvent:ccat2",
            "cat3": "customEvent:ccat3",
            "cat4": "customEvent:ccat4",
            "newsid": "customEvent:cnewsid",
            "editor": "customEvent:ceditor",
            "author": "customEvent:cauthor",
            "authortype": "customEvent:cauthortype",
            "publisheddate": "customEvent:cpublishdate",
            "newstype": "customEvent:cnewstype",
            "tag": "customEvent:ctag",
        }
    },
    "fanatik": {
        "property_id": "308104450",
        "name": "Fanatik",
        "domain": "fanatik.com.tr",
        "prefix": "f",  # fcat1, fcat2, feditor, fauthor, vb.
        "custom_dimensions": {
            "cat1": "customEvent:fcat1",
            "cat2": "customEvent:fcat2",
            "cat3": "customEvent:fcat3",
            "cat4": "customEvent:fcat4",
            "newsid": "customEvent:fnewsid",
            "editor": "customEvent:feditor",
            "author": "customEvent:fauthor",
            "authortype": "customEvent:fauthortype",
            "publisheddate": "customEvent:fpublishdate",
            "newstype": "customEvent:fnewstype",
            "tag": "customEvent:ftag",
        }
    },
    "kanald": {
        "property_id": "358179093",
        "name": "Kanal D",
        "domain": "kanald.com.tr",
        "prefix": "d",  # dcat1, dcat2, deditor, dauthor, vb.
        "custom_dimensions": {
            "cat1": "customEvent:dcat1",
            "cat2": "customEvent:dcat2",
            "cat3": "customEvent:dcat3",
            "cat4": "customEvent:dcat4",
            "newsid": "customEvent:dnewsid",
            "editor": "customEvent:deditor",
            "author": "customEvent:dauthor",
            "authortype": "customEvent:dauthortype",
            "publisheddate": "customEvent:dpublishdate",
            "newstype": "customEvent:dnewstype",
            "tag": "customEvent:dtag",
        }
    },
    "milliyet": {
        "property_id": "308126149",
        "name": "Milliyet",
        "domain": "milliyet.com.tr",
        "prefix": "m",  # mcat1, mcat2, meditor, mauthor, vb.
        "custom_dimensions": {
            "cat1": "customEvent:mcat1",
            "cat2": "customEvent:mcat2",
            "cat3": "customEvent:mcat3",
            "cat4": "customEvent:mcat4",
            "newsid": "customEvent:mnewsid",
            "editor": "customEvent:meditor",
            "author": "customEvent:mauthor",
            "authortype": "customEvent:mauthortype",
            "publisheddate": "customEvent:mpublishdate",
            "newstype": "customEvent:mnewstype",
            "tag": "customEvent:mtag",
        }
    },
    "posta": {
        "property_id": "308164369",
        "name": "Posta",
        "domain": "posta.com.tr",
        "prefix": "p",  # pcat1, pcat2, peditor, pauthor, vb.
        "custom_dimensions": {
            "cat1": "customEvent:pcat1",
            "cat2": "customEvent:pcat2",
            "cat3": "customEvent:pcat3",
            "cat4": "customEvent:pcat4",
            "newsid": "customEvent:pnewsid",
            "editor": "customEvent:peditor",
            "author": "customEvent:pauthor",
            "authortype": "customEvent:pauthortype",
            "publisheddate": "customEvent:ppublishdate",
            "newstype": "customEvent:pnewstype",
            "tag": "customEvent:ptag",
        }
    },
}
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.oauth2 import service_account
from google.analytics.data_v1beta.types import (
    DateRange,
    Metric,
    Dimension,
    FilterExpression,
    Filter,
    FilterExpressionList,
    RunReportRequest,
    OrderBy,
    MetricType
)

from ga4_mappings import (
    DIMENSIONS,
    METRICS,
    CUSTOM_DIMENSIONS,
    get_tr_name_from_api,
    get_api_name_from_tr,
    get_dimension_info,
    get_metric_info,
    QUICK_QUERIES
)


class GA4Client:
    """Google Analytics 4 API Client"""

    def __init__(
        self,
        credentials_path: str = None,
        property_id: str = None,
        brand: str = None
    ):
        """
        GA4 Client'ı başlatır.

        Args:
            credentials_path: Service account JSON dosyasının yolu
            property_id: GA4 Property ID (doğrudan belirtilirse brand yerine kullanılır)
            brand: Marka adı ("hurriyet", "vatan", vb.)
        """
        # Credentials
        self.credentials_path = credentials_path or self._find_credentials()

        # Marka ve Property ID belirleme
        if property_id:
            # Doğrudan property_id verilmişse kullan
            self.property_id = property_id
            self.brand_name = "Özel"
            self.brand_key = None
            self.custom_dims = {}
            self.prefix = ""
        elif brand and brand.lower() in BRAND_PROPERTIES:
            # Marka adı verilmişse
            brand_info = BRAND_PROPERTIES[brand.lower()]
            self.property_id = brand_info["property_id"]
            self.brand_name = brand_info["name"]
            self.brand_key = brand.lower()
            self.custom_dims = brand_info.get("custom_dimensions", {})
            self.prefix = brand_info.get("prefix", "")
        else:
            # Varsayılan: Hürriyet
            brand_info = BRAND_PROPERTIES["hurriyet"]
            self.property_id = brand_info["property_id"]
            self.brand_name = brand_info["name"]
            self.brand_key = "hurriyet"
            self.custom_dims = brand_info.get("custom_dimensions", {})
            self.prefix = brand_info.get("prefix", "h")

        # Client'ı başlat
        self._init_client()

    @staticmethod
    def get_available_brands() -> Dict:
        """Mevcut markaları döndürür"""
        return BRAND_PROPERTIES

    def switch_brand(self, brand: str) -> bool:
        """
        Aktif markayı değiştirir.

        Args:
            brand: Yeni marka adı

        Returns:
            Başarılı ise True
        """
        if brand.lower() in BRAND_PROPERTIES:
            brand_info = BRAND_PROPERTIES[brand.lower()]
            self.property_id = brand_info["property_id"]
            self.brand_name = brand_info["name"]
            self.brand_key = brand.lower()
            self.custom_dims = brand_info.get("custom_dimensions", {})
            self.prefix = brand_info.get("prefix", "")
            print(f"[OK] Marka degistirildi: {self.brand_name} (Property: {self.property_id}, Prefix: {self.prefix})")
            return True
        else:
            print(f"[HATA] Bilinmeyen marka: {brand}")
            print(f"Mevcut markalar: {', '.join(BRAND_PROPERTIES.keys())}")
            return False

    def get_custom_dimension(self, generic_name: str) -> str:
        """
        Jenerik custom dimension adını marka bazlı API adına çevirir.

        Args:
            generic_name: Jenerik ad (ör: "cat1", "editor", "author")

        Returns:
            Marka bazlı API adı (ör: "customEvent:hcat1" veya "customEvent:vcat1")
        """
        if generic_name in self.custom_dims:
            return self.custom_dims[generic_name]
        # Prefix ile dene
        return f"customEvent:{self.prefix}{generic_name}"

    def _find_credentials(self) -> str:
        """Credentials dosyasını bul"""
        # Önce aynı klasörde ara
        current_dir = os.path.dirname(os.path.abspath(__file__))
        for file in os.listdir(current_dir):
            if file.endswith('.json') and 'service' not in file.lower():
                # JSON dosyasını kontrol et
                try:
                    import json
                    with open(os.path.join(current_dir, file), 'r') as f:
                        data = json.load(f)
                        if data.get('type') == 'service_account':
                            return os.path.join(current_dir, file)
                except:
                    continue

        # Varsayılan konum
        return os.path.join(current_dir, "golden-imprint-441508-d8-765863a31f54.json")

    def _init_client(self):
        """API Client'ı başlat"""
        try:
            self.credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path
            )
            self.client = BetaAnalyticsDataClient(credentials=self.credentials)
            print(f"[OK] GA4 Client basariyla baslatildi - {self.brand_name} (Property: {self.property_id})")
        except Exception as e:
            raise Exception(f"GA4 Client başlatma hatası: {str(e)}")

    def _resolve_dimension_name(self, name: str) -> str:
        """
        Dimension adını API formatına çevirir.
        Hem Türkçe hem İngilizce isim kabul eder.
        Marka bazlı custom dimension'ları otomatik çözer.
        """
        # Zaten API formatındaysa
        if name in DIMENSIONS or name.startswith("customEvent:"):
            return name

        # Marka bazlı jenerik custom dimension mı? (cat1, editor, author, vb.)
        generic_custom_dims = ["cat1", "cat2", "cat3", "cat4", "newsid", "editor",
                               "author", "authortype", "publisheddate",
                               "newstype", "tag"]
        if name in generic_custom_dims:
            return self.get_custom_dimension(name)

        # Eski format (vcat1, veditor, vb.) - marka prefix'i ile çevir
        old_prefixes = ["v", "h"]  # Vatan ve Hürriyet
        for prefix in old_prefixes:
            if name.startswith(prefix) and name[1:] in generic_custom_dims:
                # Eski formatı yeni marka bazlı formata çevir
                generic_name = name[1:]  # vcat1 -> cat1
                return self.get_custom_dimension(generic_name)

        # Custom dimension kısaltması mı? (ga4_mappings'den)
        if name in CUSTOM_DIMENSIONS:
            # CUSTOM_DIMENSIONS'dan al ama marka prefix'ine göre dönüştür
            original_api = CUSTOM_DIMENSIONS[name]["api_name"]
            # customEvent:vcat1 -> customEvent:hcat1 veya tersi
            if original_api.startswith("customEvent:"):
                suffix = original_api.replace("customEvent:", "")
                # Prefix'i temizle ve yeni prefix ekle
                for prefix in old_prefixes:
                    if suffix.startswith(prefix):
                        generic = suffix[1:]  # vcat1 -> cat1
                        return self.get_custom_dimension(generic)
            return original_api

        # Türkçe isimden API adını bul
        api_name = get_api_name_from_tr(name)
        if api_name:
            return api_name

        # Bulunamazsa olduğu gibi döndür
        return name

    def _resolve_metric_name(self, name: str) -> str:
        """
        Metric adını API formatına çevirir.
        Hem Türkçe hem İngilizce isim kabul eder.
        """
        # Zaten API formatındaysa
        if name in METRICS:
            return name

        # Türkçe isimden API adını bul
        api_name = get_api_name_from_tr(name)
        if api_name:
            return api_name

        # Bulunamazsa olduğu gibi döndür
        return name

    def _parse_date(self, date_input: Union[str, datetime, int]) -> str:
        """
        Tarih girişini API formatına çevirir.

        Args:
            date_input: Tarih girişi
                - "today", "yesterday", "7daysAgo", "30daysAgo" gibi özel değerler
                - "2024-01-15" gibi tarih string'i
                - datetime objesi
                - -7 gibi negatif integer (bugünden X gün önce)

        Returns:
            API formatında tarih string'i
        """
        if isinstance(date_input, str):
            # Özel tarih değerleri
            special_dates = ["today", "yesterday", "7daysAgo", "30daysAgo", "90daysAgo", "365daysAgo"]
            if date_input in special_dates:
                return date_input

            # YYYY-MM-DD formatında mı?
            try:
                datetime.strptime(date_input, "%Y-%m-%d")
                return date_input
            except:
                pass

            # Türkçe özel değerler
            tr_special = {
                "bugün": "today",
                "dün": "yesterday",
                "son 7 gün": "7daysAgo",
                "son 30 gün": "30daysAgo",
                "son 90 gün": "90daysAgo",
                "son 1 yıl": "365daysAgo"
            }
            if date_input.lower() in tr_special:
                return tr_special[date_input.lower()]

        elif isinstance(date_input, datetime):
            return date_input.strftime("%Y-%m-%d")

        elif isinstance(date_input, int):
            # Negatif değer = X gün önce
            if date_input <= 0:
                target_date = datetime.now() + timedelta(days=date_input)
                return target_date.strftime("%Y-%m-%d")

        return str(date_input)

    def run_query(
        self,
        dimensions: List[str] = None,
        metrics: List[str] = None,
        start_date: Union[str, datetime, int] = "7daysAgo",
        end_date: Union[str, datetime, int] = "yesterday",
        filters: Dict = None,
        order_by: str = None,
        order_desc: bool = True,
        limit: int = 10000,
        return_type: str = "dataframe"
    ) -> Union[pd.DataFrame, List[Dict], Dict]:
        """
        GA4 API'den veri çeker.

        Args:
            dimensions: Dimension listesi (Türkçe veya API adı)
                Örnek: ["date", "Kanal Grubu"] veya ["date", "sessionDefaultChannelGroup"]
            metrics: Metric listesi (Türkçe veya API adı)
                Örnek: ["totalUsers", "Sayfa Görüntüleme"]
            start_date: Başlangıç tarihi
            end_date: Bitiş tarihi
            filters: Filtre sözlüğü
                Örnek: {"vcat1": "Spor"} veya {"sessionDefaultChannelGroup": "Organic Search"}
            order_by: Sıralama yapılacak metric/dimension
            order_desc: Azalan sıralama (True) veya artan (False)
            limit: Maksimum satır sayısı
            return_type: Dönüş tipi - "dataframe", "list", "raw"

        Returns:
            Sorgu sonuçları (belirtilen formatta)
        """
        # Varsayılan değerler
        dimensions = dimensions or ["date"]
        metrics = metrics or ["totalUsers", "sessions", "screenPageViews"]

        # İsimleri API formatına çevir
        resolved_dimensions = [self._resolve_dimension_name(d) for d in dimensions]
        resolved_metrics = [self._resolve_metric_name(m) for m in metrics]

        # Tarihleri parse et
        parsed_start = self._parse_date(start_date)
        parsed_end = self._parse_date(end_date)

        # Request oluştur
        request = {
            "property": f"properties/{self.property_id}",
            "date_ranges": [DateRange(start_date=parsed_start, end_date=parsed_end)],
            "dimensions": [Dimension(name=d) for d in resolved_dimensions],
            "metrics": [Metric(name=m) for m in resolved_metrics],
            "limit": limit
        }

        # Filtre ekle
        if filters:
            filter_expressions = []
            for field, value in filters.items():
                resolved_field = self._resolve_dimension_name(field)
                filter_expressions.append(
                    FilterExpression(
                        filter=Filter(
                            field_name=resolved_field,
                            string_filter=Filter.StringFilter(
                                value=value,
                                match_type=Filter.StringFilter.MatchType.EXACT
                            )
                        )
                    )
                )

            if len(filter_expressions) == 1:
                request["dimension_filter"] = filter_expressions[0]
            else:
                request["dimension_filter"] = FilterExpression(
                    and_group=FilterExpressionList(expressions=filter_expressions)
                )

        # Sıralama ekle
        if order_by:
            resolved_order = self._resolve_metric_name(order_by) if order_by in METRICS or get_metric_info(order_by) else self._resolve_dimension_name(order_by)

            # Metric mi dimension mı kontrol et
            if resolved_order in resolved_metrics:
                request["order_bys"] = [
                    OrderBy(
                        metric=OrderBy.MetricOrderBy(metric_name=resolved_order),
                        desc=order_desc
                    )
                ]
            else:
                request["order_bys"] = [
                    OrderBy(
                        dimension=OrderBy.DimensionOrderBy(dimension_name=resolved_order),
                        desc=order_desc
                    )
                ]

        # Veriyi çek (sayfalama ile)
        all_data = []
        offset = 0
        page_size = min(limit, 10000)

        while True:
            current_request = request.copy()
            current_request["offset"] = offset
            current_request["limit"] = page_size

            try:
                response = self.client.run_report(current_request)
            except Exception as e:
                raise Exception(f"GA4 API hatası: {str(e)}")

            if not response.rows:
                break

            # Yanıtı işle
            for row in response.rows:
                row_data = {}

                # Dimension değerleri
                for i, dim in enumerate(resolved_dimensions):
                    tr_name = get_tr_name_from_api(dim)
                    row_data[tr_name] = row.dimension_values[i].value

                # Metric değerleri
                for i, met in enumerate(resolved_metrics):
                    tr_name = get_tr_name_from_api(met)
                    value = row.metric_values[i].value

                    # Metric tipine göre dönüşüm
                    metric_info = get_metric_info(met)
                    if metric_info:
                        if metric_info.get("type") in ["integer"]:
                            value = int(value)
                        elif metric_info.get("type") in ["float", "percent", "currency", "duration"]:
                            value = float(value)

                    row_data[tr_name] = value

                all_data.append(row_data)

            # Son sayfa mı?
            if len(response.rows) < page_size or len(all_data) >= limit:
                break

            offset += page_size

        # Sonucu formatla
        if return_type == "dataframe":
            df = pd.DataFrame(all_data)
            return df
        elif return_type == "list":
            return all_data
        else:  # raw
            return {
                "data": all_data,
                "dimensions": resolved_dimensions,
                "metrics": resolved_metrics,
                "date_range": {"start": parsed_start, "end": parsed_end},
                "row_count": len(all_data)
            }

    def quick_query(
        self,
        query_name: str,
        start_date: Union[str, datetime, int] = "7daysAgo",
        end_date: Union[str, datetime, int] = "yesterday",
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Önceden tanımlanmış hızlı sorguları çalıştırır.

        Args:
            query_name: Sorgu adı (QUICK_QUERIES'den)
                - "genel_bakis"
                - "trafik_kaynaklari"
                - "en_cok_okunanlar"
                - "cihaz_dagilimi"
                - "sehir_dagilimi"
                - "kategori_performansi"
                - "editor_performansi"
                - "saatlik_trafik"
                - "gunluk_trafik"
                - "haber_tipi"
            start_date: Başlangıç tarihi
            end_date: Bitiş tarihi
            limit: Maksimum satır sayısı

        Returns:
            Sorgu sonuçları DataFrame olarak
        """
        if query_name not in QUICK_QUERIES:
            available = ", ".join(QUICK_QUERIES.keys())
            raise ValueError(f"Geçersiz sorgu adı: {query_name}. Mevcut sorgular: {available}")

        query = QUICK_QUERIES[query_name]

        return self.run_query(
            dimensions=query["dimensions"],
            metrics=query["metrics"],
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            order_by=query["metrics"][0],
            order_desc=True
        )

    def get_top_pages(
        self,
        start_date: Union[str, datetime, int] = "yesterday",
        end_date: Union[str, datetime, int] = "yesterday",
        limit: int = 10,
        category: str = None
    ) -> pd.DataFrame:
        """
        En çok görüntülenen sayfaları getirir.
        GA4 panelindeki gibi sadece pagePath bazında.

        Args:
            start_date: Başlangıç tarihi
            end_date: Bitiş tarihi
            limit: Kaç sayfa getirileceği
            category: Kategori filtresi (opsiyonel)

        Returns:
            En çok görüntülenen sayfalar
        """
        filters = {}
        if category:
            # Jenerik cat1 kullan - marka bazli cozulecek
            filters["cat1"] = category

        # GA4 panelindeki gibi: pagePath, screenPageViews, totalUsers, sessions
        return self.run_query(
            dimensions=["pagePath"],
            metrics=["screenPageViews", "totalUsers", "sessions"],
            start_date=start_date,
            end_date=end_date,
            filters=filters if filters else None,
            order_by="screenPageViews",
            order_desc=True,
            limit=limit
        )

    def get_traffic_sources(
        self,
        start_date: Union[str, datetime, int] = "7daysAgo",
        end_date: Union[str, datetime, int] = "yesterday"
    ) -> pd.DataFrame:
        """
        Trafik kaynaklarını getirir.

        Args:
            start_date: Başlangıç tarihi
            end_date: Bitiş tarihi

        Returns:
            Trafik kaynakları dağılımı
        """
        return self.run_query(
            dimensions=["sessionDefaultChannelGroup"],
            metrics=["totalUsers", "sessions", "screenPageViews", "bounceRate", "averageSessionDuration"],
            start_date=start_date,
            end_date=end_date,
            order_by="totalUsers",
            order_desc=True
        )

    def get_category_performance(
        self,
        start_date: Union[str, datetime, int] = "7daysAgo",
        end_date: Union[str, datetime, int] = "yesterday",
        limit: int = 20
    ) -> pd.DataFrame:
        """
        Kategori performansını getirir.

        Args:
            start_date: Başlangıç tarihi
            end_date: Bitiş tarihi
            limit: Maksimum kategori sayısı

        Returns:
            Kategori bazlı performans
        """
        # Jenerik "cat1" kullan - marka bazli cozulecek
        df = self.run_query(
            dimensions=["cat1"],
            metrics=["screenPageViews", "totalUsers", "sessions", "averageSessionDuration"],
            start_date=start_date,
            end_date=end_date,
            order_by="screenPageViews",
            order_desc=True,
            limit=limit
        )

        # Oturum suresi saniye cinsinden, dakikaya cevir ve birim ekle
        if "Ortalama Oturum Suresi" in df.columns:
            df["Ort. Oturum (dk)"] = (df["Ortalama Oturum Suresi"] / 60).round(2)
            df = df.drop(columns=["Ortalama Oturum Suresi"])

        return df

    def get_editor_performance(
        self,
        start_date: Union[str, datetime, int] = "7daysAgo",
        end_date: Union[str, datetime, int] = "yesterday",
        limit: int = 20
    ) -> pd.DataFrame:
        """
        Editör performansını getirir.

        Args:
            start_date: Başlangıç tarihi
            end_date: Bitiş tarihi
            limit: Maksimum editör sayısı

        Returns:
            Editör bazlı performans
        """
        # Jenerik "editor" kullan - marka bazli cozulecek
        return self.run_query(
            dimensions=["editor"],
            metrics=["screenPageViews", "totalUsers", "sessions"],
            start_date=start_date,
            end_date=end_date,
            order_by="screenPageViews",
            order_desc=True,
            limit=limit
        )

    def get_hourly_traffic(
        self,
        date: Union[str, datetime, int] = "yesterday"
    ) -> pd.DataFrame:
        """
        Saatlik trafik dağılımını getirir.

        Args:
            date: Tarih

        Returns:
            Saatlik trafik dağılımı
        """
        return self.run_query(
            dimensions=["hour"],
            metrics=["totalUsers", "sessions", "screenPageViews"],
            start_date=date,
            end_date=date,
            order_by="hour",
            order_desc=False
        )

    def get_device_breakdown(
        self,
        start_date: Union[str, datetime, int] = "7daysAgo",
        end_date: Union[str, datetime, int] = "yesterday"
    ) -> pd.DataFrame:
        """
        Cihaz dağılımını getirir.

        Args:
            start_date: Başlangıç tarihi
            end_date: Bitiş tarihi

        Returns:
            Cihaz kategorisi bazlı dağılım
        """
        return self.run_query(
            dimensions=["deviceCategory"],
            metrics=["totalUsers", "sessions", "screenPageViews"],
            start_date=start_date,
            end_date=end_date,
            order_by="totalUsers",
            order_desc=True
        )

    def get_city_breakdown(
        self,
        start_date: Union[str, datetime, int] = "7daysAgo",
        end_date: Union[str, datetime, int] = "yesterday",
        country: str = "Turkey",
        limit: int = 20
    ) -> pd.DataFrame:
        """
        Şehir dağılımını getirir.

        Args:
            start_date: Başlangıç tarihi
            end_date: Bitiş tarihi
            country: Ülke filtresi
            limit: Maksimum şehir sayısı

        Returns:
            Şehir bazlı dağılım
        """
        filters = {"country": country} if country else None

        return self.run_query(
            dimensions=["city"],
            metrics=["totalUsers", "sessions", "screenPageViews"],
            start_date=start_date,
            end_date=end_date,
            filters=filters,
            order_by="totalUsers",
            order_desc=True,
            limit=limit
        )

    def get_daily_trend(
        self,
        start_date: Union[str, datetime, int] = "30daysAgo",
        end_date: Union[str, datetime, int] = "yesterday"
    ) -> pd.DataFrame:
        """
        Günlük trafik trendini getirir.

        Args:
            start_date: Başlangıç tarihi
            end_date: Bitiş tarihi

        Returns:
            Günlük trafik trendi
        """
        df = self.run_query(
            dimensions=["date"],
            metrics=["totalUsers", "sessions", "screenPageViews", "newUsers"],
            start_date=start_date,
            end_date=end_date,
            order_by="date",
            order_desc=False
        )

        # Tarih formatını düzenle
        if "Tarih" in df.columns:
            df["Tarih"] = pd.to_datetime(df["Tarih"], format="%Y%m%d").dt.strftime("%Y-%m-%d")

        return df

    def compare_periods(
        self,
        metrics: List[str] = None,
        current_start: Union[str, datetime, int] = "7daysAgo",
        current_end: Union[str, datetime, int] = "yesterday",
        previous_start: Union[str, datetime, int] = "14daysAgo",
        previous_end: Union[str, datetime, int] = "8daysAgo"
    ) -> Dict:
        """
        İki dönemi karşılaştırır.

        Args:
            metrics: Karşılaştırılacak metrikler
            current_start: Mevcut dönem başlangıç
            current_end: Mevcut dönem bitiş
            previous_start: Önceki dönem başlangıç
            previous_end: Önceki dönem bitiş

        Returns:
            Karşılaştırma sonuçları
        """
        metrics = metrics or ["totalUsers", "sessions", "screenPageViews"]

        # Mevcut dönem
        current = self.run_query(
            dimensions=[],
            metrics=metrics,
            start_date=current_start,
            end_date=current_end,
            return_type="list"
        )

        # Önceki dönem
        previous = self.run_query(
            dimensions=[],
            metrics=metrics,
            start_date=previous_start,
            end_date=previous_end,
            return_type="list"
        )

        # Karşılaştırma hesapla
        comparison = {}
        if current and previous:
            current_data = current[0]
            previous_data = previous[0]

            for metric in metrics:
                tr_name = get_tr_name_from_api(metric)
                curr_val = current_data.get(tr_name, 0)
                prev_val = previous_data.get(tr_name, 0)

                if prev_val > 0:
                    change_pct = ((curr_val - prev_val) / prev_val) * 100
                else:
                    change_pct = 100 if curr_val > 0 else 0

                comparison[tr_name] = {
                    "current": curr_val,
                    "previous": prev_val,
                    "change": curr_val - prev_val,
                    "change_percent": round(change_pct, 2)
                }

        return comparison

    def get_realtime_summary(self) -> Dict:
        """
        Not: GA4 Data API'de gerçek zamanlı veri için ayrı bir endpoint var.
        Bu metot şimdilik bugünün verisini döndürür.

        Returns:
            Bugünün özet verileri
        """
        today_data = self.run_query(
            dimensions=[],
            metrics=["activeUsers", "sessions", "screenPageViews"],
            start_date="today",
            end_date="today",
            return_type="list"
        )

        if today_data:
            return today_data[0]
        return {}


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("GA4 CLIENT TEST")
    print("=" * 60)

    try:
        # Client oluştur
        client = GA4Client()

        # Test sorgusu
        print("\n--- Test: Son 7 günün trafik kaynakları ---")
        df = client.get_traffic_sources()
        print(df.head(10))

        print("\n--- Test: Dünün en çok okunan sayfaları ---")
        df = client.get_top_pages(limit=5)
        print(df)

        print("\n--- Test: Hızlı sorgu (genel_bakis) ---")
        df = client.quick_query("genel_bakis", start_date="7daysAgo", limit=10)
        print(df)

    except Exception as e:
        print(f"\n❌ Hata: {str(e)}")
        import traceback
        traceback.print_exc()
