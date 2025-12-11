# -*- coding: utf-8 -*-
"""
Google Analytics 4 - Dimension ve Metric Mapping Dosyası
Tüm standart GA4 API dimension ve metrikleri Türkçe açıklamalarıyla

Kullanım:
    from ga4_mappings import DIMENSIONS, METRICS, CUSTOM_DIMENSIONS, get_dimension_info, get_metric_info
"""

# =============================================================================
# DIMENSIONS (Boyutlar)
# =============================================================================
# Her dimension için:
# - api_name: GA4 API'deki teknik isim
# - tr_name: Türkçe görünen isim
# - description: Açıklama
# - category: Kategori grubu
# - weight: Kullanım sıklığı/öncelik (1-10, 10=çok kullanılır)
#
# Weight Açıklaması:
#   10: Çok sık kullanılır (temel metrikler)
#   8-9: Sık kullanılır (önemli analizler)
#   6-7: Orta sıklıkta (detaylı analizler)
#   4-5: Ara sıra kullanılır (spesifik analizler)
#   1-3: Nadiren kullanılır (ileri düzey analizler)

DIMENSIONS = {
    # -------------------------------------------------------------------------
    # USER (Kullanıcı) Dimensionları
    # -------------------------------------------------------------------------
    "userAgeBracket": {
        "api_name": "userAgeBracket",
        "tr_name": "Yaş Aralığı",
        "description": "Kullanıcının yaş aralığı (18-24, 25-34, vb.)",
        "category": "Kullanıcı",
        "weight": 5  # Demografik analiz için
    },
    "userGender": {
        "api_name": "userGender",
        "tr_name": "Cinsiyet",
        "description": "Kullanıcının cinsiyeti",
        "category": "Kullanıcı",
        "weight": 5  # Demografik analiz için
    },
    "newVsReturning": {
        "api_name": "newVsReturning",
        "tr_name": "Yeni/Geri Dönen",
        "description": "Kullanıcının yeni mi yoksa geri dönen mi olduğu",
        "category": "Kullanıcı",
        "weight": 8  # Kullanıcı sadakati analizi için önemli
    },
    "firstUserCampaignName": {
        "api_name": "firstUserCampaignName",
        "tr_name": "İlk Kampanya Adı",
        "description": "Kullanıcıyı ilk getiren kampanyanın adı",
        "category": "Kullanıcı",
        "weight": 4  # Kampanya analizi için
    },
    "firstUserMedium": {
        "api_name": "firstUserMedium",
        "tr_name": "İlk Ortam",
        "description": "Kullanıcıyı ilk getiren ortam (organic, cpc, vb.)",
        "category": "Kullanıcı",
        "weight": 5
    },
    "firstUserSource": {
        "api_name": "firstUserSource",
        "tr_name": "İlk Kaynak",
        "description": "Kullanıcıyı ilk getiren kaynak (google, facebook, vb.)",
        "category": "Kullanıcı",
        "weight": 5
    },
    "firstUserSourceMedium": {
        "api_name": "firstUserSourceMedium",
        "tr_name": "İlk Kaynak/Ortam",
        "description": "Kullanıcıyı ilk getiren kaynak ve ortam kombinasyonu",
        "category": "Kullanıcı",
        "weight": 4
    },
    "firstUserDefaultChannelGroup": {
        "api_name": "firstUserDefaultChannelGroup",
        "tr_name": "İlk Kanal Grubu",
        "description": "Kullanıcıyı ilk getiren varsayılan kanal grubu",
        "category": "Kullanıcı",
        "weight": 6
    },

    # -------------------------------------------------------------------------
    # SESSION (Oturum) Dimensionları
    # -------------------------------------------------------------------------
    "sessionCampaignName": {
        "api_name": "sessionCampaignName",
        "tr_name": "Oturum Kampanya Adı",
        "description": "Oturumu başlatan kampanyanın adı",
        "category": "Oturum",
        "weight": 5
    },
    "sessionMedium": {
        "api_name": "sessionMedium",
        "tr_name": "Oturum Ortamı",
        "description": "Oturumu başlatan ortam",
        "category": "Oturum",
        "weight": 7
    },
    "sessionSource": {
        "api_name": "sessionSource",
        "tr_name": "Oturum Kaynağı",
        "description": "Oturumu başlatan kaynak",
        "category": "Oturum",
        "weight": 7
    },
    "sessionSourceMedium": {
        "api_name": "sessionSourceMedium",
        "tr_name": "Oturum Kaynak/Ortam",
        "description": "Oturumu başlatan kaynak ve ortam kombinasyonu",
        "category": "Oturum",
        "weight": 6
    },
    "sessionDefaultChannelGroup": {
        "api_name": "sessionDefaultChannelGroup",
        "tr_name": "Kanal Grubu",
        "description": "Oturumun varsayılan kanal grubu (Organic Search, Direct, Social, vb.)",
        "category": "Oturum",
        "weight": 10
    },
    "sessionManualAdContent": {
        "api_name": "sessionManualAdContent",
        "tr_name": "Reklam İçeriği",
        "description": "UTM content parametresi",
        "category": "Oturum",
        "weight": 4
    },
    "sessionManualTerm": {
        "api_name": "sessionManualTerm",
        "tr_name": "Anahtar Kelime",
        "description": "UTM term parametresi",
        "category": "Oturum",
        "weight": 4
    },
    "sessionGoogleAdsAdGroupName": {
        "api_name": "sessionGoogleAdsAdGroupName",
        "tr_name": "Google Ads Reklam Grubu",
        "description": "Google Ads reklam grubu adı",
        "category": "Oturum",
        "weight": 4
    },
    "sessionGoogleAdsCampaignName": {
        "api_name": "sessionGoogleAdsCampaignName",
        "tr_name": "Google Ads Kampanya Adı",
        "description": "Google Ads kampanya adı",
        "category": "Oturum",
        "weight": 4
    },

    # -------------------------------------------------------------------------
    # TRAFFIC SOURCE (Trafik Kaynağı) Dimensionları
    # -------------------------------------------------------------------------
    "source": {
        "api_name": "source",
        "tr_name": "Kaynak",
        "description": "Trafik kaynağı (google, facebook, direct, vb.)",
        "category": "Trafik Kaynağı",
        "weight": 9
    },
    "medium": {
        "api_name": "medium",
        "tr_name": "Ortam",
        "description": "Trafik ortamı (organic, cpc, referral, vb.)",
        "category": "Trafik Kaynağı",
        "weight": 9
    },
    "sourceMedium": {
        "api_name": "sourceMedium",
        "tr_name": "Kaynak/Ortam",
        "description": "Kaynak ve ortam kombinasyonu",
        "category": "Trafik Kaynağı",
        "weight": 8
    },
    "sourcePlatform": {
        "api_name": "sourcePlatform",
        "tr_name": "Kaynak Platformu",
        "description": "Trafik kaynağı platformu",
        "category": "Trafik Kaynağı"
    },
    "defaultChannelGroup": {
        "api_name": "defaultChannelGroup",
        "tr_name": "Varsayılan Kanal Grubu",
        "description": "Varsayılan kanal grubu sınıflandırması",
        "category": "Trafik Kaynağı",
        "weight": 7
    },
    "campaignName": {
        "api_name": "campaignName",
        "tr_name": "Kampanya Adı",
        "description": "Pazarlama kampanyası adı",
        "category": "Trafik Kaynağı",
        "weight": 7
    },
    "campaignId": {
        "api_name": "campaignId",
        "tr_name": "Kampanya ID",
        "description": "Pazarlama kampanyası kimliği",
        "category": "Trafik Kaynağı",
        "weight": 4
    },
    "googleAdsAccountName": {
        "api_name": "googleAdsAccountName",
        "tr_name": "Google Ads Hesap Adı",
        "description": "Google Ads hesap adı",
        "category": "Trafik Kaynağı",
        "weight": 3
    },
    "googleAdsCampaignName": {
        "api_name": "googleAdsCampaignName",
        "tr_name": "Google Ads Kampanya",
        "description": "Google Ads kampanya adı",
        "category": "Trafik Kaynağı",
        "weight": 4
    },
    "googleAdsAdGroupName": {
        "api_name": "googleAdsAdGroupName",
        "tr_name": "Google Ads Reklam Grubu",
        "description": "Google Ads reklam grubu adı",
        "category": "Trafik Kaynağı",
        "weight": 4
    },
    "googleAdsKeyword": {
        "api_name": "googleAdsKeyword",
        "tr_name": "Google Ads Anahtar Kelime",
        "description": "Google Ads anahtar kelimesi",
        "category": "Trafik Kaynağı",
        "weight": 4
    },

    # -------------------------------------------------------------------------
    # PAGE / SCREEN (Sayfa/Ekran) Dimensionları
    # -------------------------------------------------------------------------
    "pagePath": {
        "api_name": "pagePath",
        "tr_name": "Sayfa Yolu",
        "description": "Sayfa URL yolu (domain hariç)",
        "category": "Sayfa",
        "weight": 10
    },
    "pagePathPlusQueryString": {
        "api_name": "pagePathPlusQueryString",
        "tr_name": "Sayfa Yolu + Query",
        "description": "Sayfa URL yolu ve query string",
        "category": "Sayfa",
        "weight": 4
    },
    "pageLocation": {
        "api_name": "pageLocation",
        "tr_name": "Sayfa URL",
        "description": "Tam sayfa URL'si",
        "category": "Sayfa",
        "weight": 6
    },
    "pageTitle": {
        "api_name": "pageTitle",
        "tr_name": "Sayfa Başlığı",
        "description": "Sayfa başlığı (title tag)",
        "category": "Sayfa",
        "weight": 9
    },
    "pageReferrer": {
        "api_name": "pageReferrer",
        "tr_name": "Referrer URL",
        "description": "Kullanıcının geldiği önceki sayfa URL'si",
        "category": "Sayfa",
        "weight": 5
    },
    "landingPage": {
        "api_name": "landingPage",
        "tr_name": "Giriş Sayfası",
        "description": "Oturumun başladığı ilk sayfa",
        "category": "Sayfa",
        "weight": 8
    },
    "landingPagePlusQueryString": {
        "api_name": "landingPagePlusQueryString",
        "tr_name": "Giriş Sayfası + Query",
        "description": "Giriş sayfası URL'si ve query string",
        "category": "Sayfa",
        "weight": 4
    },
    "exitPage": {
        "api_name": "exitPage",
        "tr_name": "Çıkış Sayfası",
        "description": "Oturumun bittiği son sayfa",
        "category": "Sayfa",
        "weight": 7
    },
    "contentGroup": {
        "api_name": "contentGroup",
        "tr_name": "İçerik Grubu",
        "description": "İçerik grubu sınıflandırması",
        "category": "Sayfa",
        "weight": 5
    },
    "contentId": {
        "api_name": "contentId",
        "tr_name": "İçerik ID",
        "description": "İçerik kimliği",
        "category": "Sayfa",
        "weight": 4
    },
    "contentType": {
        "api_name": "contentType",
        "tr_name": "İçerik Tipi",
        "description": "İçerik türü",
        "category": "Sayfa",
        "weight": 5
    },
    "unifiedPagePathScreen": {
        "api_name": "unifiedPagePathScreen",
        "tr_name": "Birleşik Sayfa Yolu",
        "description": "Web ve uygulama için birleşik sayfa/ekran yolu",
        "category": "Sayfa",
        "weight": 3
    },
    "unifiedPageScreen": {
        "api_name": "unifiedPageScreen",
        "tr_name": "Birleşik Sayfa/Ekran",
        "description": "Web ve uygulama için birleşik sayfa/ekran",
        "category": "Sayfa",
        "weight": 3
    },
    "hostname": {
        "api_name": "hostname",
        "tr_name": "Host Adı",
        "description": "Web sitesi host adı",
        "category": "Sayfa",
        "weight": 6
    },

    # -------------------------------------------------------------------------
    # DEVICE (Cihaz) Dimensionları
    # -------------------------------------------------------------------------
    "deviceCategory": {
        "api_name": "deviceCategory",
        "tr_name": "Cihaz Kategorisi",
        "description": "Cihaz türü (desktop, mobile, tablet)",
        "category": "Cihaz",
        "weight": 9
    },
    "deviceModel": {
        "api_name": "deviceModel",
        "tr_name": "Cihaz Modeli",
        "description": "Cihaz modeli (iPhone 12, Samsung Galaxy, vb.)",
        "category": "Cihaz",
        "weight": 5
    },
    "mobileDeviceBranding": {
        "api_name": "mobileDeviceBranding",
        "tr_name": "Mobil Cihaz Markası",
        "description": "Mobil cihaz üretici markası",
        "category": "Cihaz",
        "weight": 5
    },
    "mobileDeviceMarketingName": {
        "api_name": "mobileDeviceMarketingName",
        "tr_name": "Mobil Cihaz Adı",
        "description": "Mobil cihazın pazarlama adı",
        "category": "Cihaz",
        "weight": 4
    },
    "mobileDeviceModel": {
        "api_name": "mobileDeviceModel",
        "tr_name": "Mobil Cihaz Modeli",
        "description": "Mobil cihaz model kodu",
        "category": "Cihaz",
        "weight": 4
    },
    "screenResolution": {
        "api_name": "screenResolution",
        "tr_name": "Ekran Çözünürlüğü",
        "description": "Cihaz ekran çözünürlüğü",
        "category": "Cihaz",
        "weight": 5
    },
    "browser": {
        "api_name": "browser",
        "tr_name": "Tarayıcı",
        "description": "Web tarayıcısı adı",
        "category": "Cihaz",
        "weight": 7
    },
    "browserVersion": {
        "api_name": "browserVersion",
        "tr_name": "Tarayıcı Versiyonu",
        "description": "Web tarayıcısı sürümü",
        "category": "Cihaz",
        "weight": 4
    },
    "operatingSystem": {
        "api_name": "operatingSystem",
        "tr_name": "İşletim Sistemi",
        "description": "İşletim sistemi adı",
        "category": "Cihaz",
        "weight": 7
    },
    "operatingSystemVersion": {
        "api_name": "operatingSystemVersion",
        "tr_name": "İşletim Sistemi Versiyonu",
        "description": "İşletim sistemi sürümü",
        "category": "Cihaz",
        "weight": 4
    },
    "operatingSystemWithVersion": {
        "api_name": "operatingSystemWithVersion",
        "tr_name": "İşletim Sistemi (Versiyon)",
        "description": "İşletim sistemi ve sürümü birlikte",
        "category": "Cihaz",
        "weight": 4
    },
    "platform": {
        "api_name": "platform",
        "tr_name": "Platform",
        "description": "Platform türü (web, iOS, Android)",
        "category": "Cihaz",
        "weight": 5
    },
    "platformDeviceCategory": {
        "api_name": "platformDeviceCategory",
        "tr_name": "Platform Cihaz Kategorisi",
        "description": "Platform ve cihaz kategorisi kombinasyonu",
        "category": "Cihaz",
        "weight": 4
    },
    "language": {
        "api_name": "language",
        "tr_name": "Dil",
        "description": "Tarayıcı/cihaz dil ayarı",
        "category": "Cihaz",
        "weight": 6
    },

    # -------------------------------------------------------------------------
    # GEO (Coğrafi) Dimensionları
    # -------------------------------------------------------------------------
    "country": {
        "api_name": "country",
        "tr_name": "Ülke",
        "description": "Kullanıcının ülkesi",
        "category": "Coğrafi",
        "weight": 8
    },
    "countryId": {
        "api_name": "countryId",
        "tr_name": "Ülke ID",
        "description": "Ülke ISO kodu",
        "category": "Coğrafi",
        "weight": 3
    },
    "region": {
        "api_name": "region",
        "tr_name": "Bölge",
        "description": "Kullanıcının bölgesi/eyaleti",
        "category": "Coğrafi",
        "weight": 6
    },
    "city": {
        "api_name": "city",
        "tr_name": "Şehir",
        "description": "Kullanıcının şehri",
        "category": "Coğrafi",
        "weight": 8
    },
    "cityId": {
        "api_name": "cityId",
        "tr_name": "Şehir ID",
        "description": "Şehir kimlik kodu",
        "category": "Coğrafi",
        "weight": 3
    },
    "continent": {
        "api_name": "continent",
        "tr_name": "Kıta",
        "description": "Kullanıcının kıtası",
        "category": "Coğrafi",
        "weight": 5
    },
    "continentId": {
        "api_name": "continentId",
        "tr_name": "Kıta ID",
        "description": "Kıta kimlik kodu",
        "category": "Coğrafi",
        "weight": 2
    },
    "subContinent": {
        "api_name": "subContinent",
        "tr_name": "Alt Kıta",
        "description": "Alt kıta/bölge",
        "category": "Coğrafi",
        "weight": 4
    },

    # -------------------------------------------------------------------------
    # TIME (Zaman) Dimensionları
    # -------------------------------------------------------------------------
    "date": {
        "api_name": "date",
        "tr_name": "Tarih",
        "description": "Tarih (YYYYMMDD formatında)",
        "category": "Zaman",
        "weight": 10
    },
    "dateHour": {
        "api_name": "dateHour",
        "tr_name": "Tarih ve Saat",
        "description": "Tarih ve saat (YYYYMMDDHH formatında)",
        "category": "Zaman",
        "weight": 5
    },
    "dateHourMinute": {
        "api_name": "dateHourMinute",
        "tr_name": "Tarih Saat Dakika",
        "description": "Tarih, saat ve dakika",
        "category": "Zaman",
        "weight": 3
    },
    "day": {
        "api_name": "day",
        "tr_name": "Gün",
        "description": "Ayın günü (01-31)",
        "category": "Zaman",
        "weight": 5
    },
    "dayOfWeek": {
        "api_name": "dayOfWeek",
        "tr_name": "Haftanın Günü",
        "description": "Haftanın günü (0=Pazar, 6=Cumartesi)",
        "category": "Zaman",
        "weight": 7
    },
    "dayOfWeekName": {
        "api_name": "dayOfWeekName",
        "tr_name": "Gün Adı",
        "description": "Haftanın günü adı (Monday, Tuesday, vb.)",
        "category": "Zaman",
        "weight": 7
    },
    "hour": {
        "api_name": "hour",
        "tr_name": "Saat",
        "description": "Günün saati (00-23)",
        "category": "Zaman",
        "weight": 8
    },
    "minute": {
        "api_name": "minute",
        "tr_name": "Dakika",
        "description": "Saatin dakikası (00-59)",
        "category": "Zaman",
        "weight": 3
    },
    "month": {
        "api_name": "month",
        "tr_name": "Ay",
        "description": "Yılın ayı (01-12)",
        "category": "Zaman",
        "weight": 7
    },
    "week": {
        "api_name": "week",
        "tr_name": "Hafta",
        "description": "Yılın haftası (01-53)",
        "category": "Zaman",
        "weight": 7
    },
    "year": {
        "api_name": "year",
        "tr_name": "Yıl",
        "description": "Yıl (4 haneli)",
        "category": "Zaman",
        "weight": 6
    },
    "yearMonth": {
        "api_name": "yearMonth",
        "tr_name": "Yıl-Ay",
        "description": "Yıl ve ay (YYYYMM formatında)",
        "category": "Zaman",
        "weight": 5
    },
    "yearWeek": {
        "api_name": "yearWeek",
        "tr_name": "Yıl-Hafta",
        "description": "Yıl ve hafta",
        "category": "Zaman",
        "weight": 4
    },
    "isoWeek": {
        "api_name": "isoWeek",
        "tr_name": "ISO Hafta",
        "description": "ISO standardına göre hafta numarası",
        "category": "Zaman",
        "weight": 3
    },
    "isoYear": {
        "api_name": "isoYear",
        "tr_name": "ISO Yıl",
        "description": "ISO standardına göre yıl",
        "category": "Zaman",
        "weight": 3
    },
    "isoYearIsoWeek": {
        "api_name": "isoYearIsoWeek",
        "tr_name": "ISO Yıl-Hafta",
        "description": "ISO yıl ve hafta kombinasyonu",
        "category": "Zaman",
        "weight": 3
    },
    "nthDay": {
        "api_name": "nthDay",
        "tr_name": "N. Gün",
        "description": "Tarih aralığındaki gün sırası",
        "category": "Zaman",
        "weight": 3
    },
    "nthHour": {
        "api_name": "nthHour",
        "tr_name": "N. Saat",
        "description": "Tarih aralığındaki saat sırası",
        "category": "Zaman",
        "weight": 3
    },
    "nthMinute": {
        "api_name": "nthMinute",
        "tr_name": "N. Dakika",
        "description": "Tarih aralığındaki dakika sırası",
        "category": "Zaman",
        "weight": 2
    },
    "nthMonth": {
        "api_name": "nthMonth",
        "tr_name": "N. Ay",
        "description": "Tarih aralığındaki ay sırası",
        "category": "Zaman",
        "weight": 3
    },
    "nthWeek": {
        "api_name": "nthWeek",
        "tr_name": "N. Hafta",
        "description": "Tarih aralığındaki hafta sırası",
        "category": "Zaman",
        "weight": 3
    },
    "nthYear": {
        "api_name": "nthYear",
        "tr_name": "N. Yıl",
        "description": "Tarih aralığındaki yıl sırası",
        "category": "Zaman",
        "weight": 2
    },

    # -------------------------------------------------------------------------
    # EVENT (Etkinlik) Dimensionları
    # -------------------------------------------------------------------------
    "eventName": {
        "api_name": "eventName",
        "tr_name": "Etkinlik Adı",
        "description": "GA4 etkinlik adı (page_view, click, vb.)",
        "category": "Etkinlik",
        "weight": 7
    },
    "isConversionEvent": {
        "api_name": "isConversionEvent",
        "tr_name": "Dönüşüm Etkinliği mi",
        "description": "Etkinliğin dönüşüm olarak işaretlenip işaretlenmediği",
        "category": "Etkinlik",
        "weight": 4
    },

    # -------------------------------------------------------------------------
    # ECOMMERCE (E-Ticaret) Dimensionları
    # -------------------------------------------------------------------------
    "transactionId": {
        "api_name": "transactionId",
        "tr_name": "İşlem ID",
        "description": "E-ticaret işlem kimliği",
        "category": "E-Ticaret",
        "weight": 2
    },
    "itemId": {
        "api_name": "itemId",
        "tr_name": "Ürün ID",
        "description": "Ürün kimliği",
        "category": "E-Ticaret",
        "weight": 2
    },
    "itemName": {
        "api_name": "itemName",
        "tr_name": "Ürün Adı",
        "description": "Ürün adı",
        "category": "E-Ticaret",
        "weight": 2
    },
    "itemBrand": {
        "api_name": "itemBrand",
        "tr_name": "Ürün Markası",
        "description": "Ürün markası",
        "category": "E-Ticaret",
        "weight": 2
    },
    "itemCategory": {
        "api_name": "itemCategory",
        "tr_name": "Ürün Kategorisi",
        "description": "Ürün ana kategorisi",
        "category": "E-Ticaret",
        "weight": 2
    },
    "itemCategory2": {
        "api_name": "itemCategory2",
        "tr_name": "Ürün Kategorisi 2",
        "description": "Ürün ikinci seviye kategorisi",
        "category": "E-Ticaret",
        "weight": 1
    },
    "itemCategory3": {
        "api_name": "itemCategory3",
        "tr_name": "Ürün Kategorisi 3",
        "description": "Ürün üçüncü seviye kategorisi",
        "category": "E-Ticaret",
        "weight": 1
    },
    "itemCategory4": {
        "api_name": "itemCategory4",
        "tr_name": "Ürün Kategorisi 4",
        "description": "Ürün dördüncü seviye kategorisi",
        "category": "E-Ticaret",
        "weight": 1
    },
    "itemCategory5": {
        "api_name": "itemCategory5",
        "tr_name": "Ürün Kategorisi 5",
        "description": "Ürün beşinci seviye kategorisi",
        "category": "E-Ticaret",
        "weight": 1
    },
    "itemVariant": {
        "api_name": "itemVariant",
        "tr_name": "Ürün Varyantı",
        "description": "Ürün varyantı (renk, boyut, vb.)",
        "category": "E-Ticaret",
        "weight": 2
    },
    "itemListName": {
        "api_name": "itemListName",
        "tr_name": "Ürün Liste Adı",
        "description": "Ürünün gösterildiği liste adı",
        "category": "E-Ticaret",
        "weight": 2
    },
    "itemListId": {
        "api_name": "itemListId",
        "tr_name": "Ürün Liste ID",
        "description": "Ürünün gösterildiği liste kimliği",
        "category": "E-Ticaret",
        "weight": 1
    },
    "itemListPosition": {
        "api_name": "itemListPosition",
        "tr_name": "Ürün Liste Pozisyonu",
        "description": "Ürünün listedeki pozisyonu",
        "category": "E-Ticaret",
        "weight": 2
    },
    "itemPromotionCreativeName": {
        "api_name": "itemPromotionCreativeName",
        "tr_name": "Promosyon Kreatif Adı",
        "description": "Promosyon kreatif adı",
        "category": "E-Ticaret",
        "weight": 1
    },
    "itemPromotionId": {
        "api_name": "itemPromotionId",
        "tr_name": "Promosyon ID",
        "description": "Promosyon kimliği",
        "category": "E-Ticaret",
        "weight": 1
    },
    "itemPromotionName": {
        "api_name": "itemPromotionName",
        "tr_name": "Promosyon Adı",
        "description": "Promosyon adı",
        "category": "E-Ticaret",
        "weight": 2
    },
    "orderCoupon": {
        "api_name": "orderCoupon",
        "tr_name": "Sipariş Kuponu",
        "description": "Siparişte kullanılan kupon kodu",
        "category": "E-Ticaret",
        "weight": 1
    },
    "shippingTier": {
        "api_name": "shippingTier",
        "tr_name": "Kargo Türü",
        "description": "Kargo/teslimat türü",
        "category": "E-Ticaret",
        "weight": 1
    },

    # -------------------------------------------------------------------------
    # PUBLISHER (Yayıncı) Dimensionları
    # -------------------------------------------------------------------------
    "adFormat": {
        "api_name": "adFormat",
        "tr_name": "Reklam Formatı",
        "description": "Reklam formatı türü",
        "category": "Yayıncı",
        "weight": 3
    },
    "adSourceName": {
        "api_name": "adSourceName",
        "tr_name": "Reklam Kaynağı Adı",
        "description": "Reklam kaynağı adı",
        "category": "Yayıncı",
        "weight": 3
    },
    "adUnitName": {
        "api_name": "adUnitName",
        "tr_name": "Reklam Birimi Adı",
        "description": "Reklam birimi adı",
        "category": "Yayıncı",
        "weight": 3
    },

    # -------------------------------------------------------------------------
    # OTHER (Diğer) Dimensionları
    # -------------------------------------------------------------------------
    "audienceId": {
        "api_name": "audienceId",
        "tr_name": "Kitle ID",
        "description": "Kitle kimliği",
        "category": "Diğer",
        "weight": 2
    },
    "audienceName": {
        "api_name": "audienceName",
        "tr_name": "Kitle Adı",
        "description": "Kitle adı",
        "category": "Diğer",
        "weight": 3
    },
    "brandingInterest": {
        "api_name": "brandingInterest",
        "tr_name": "Marka İlgisi",
        "description": "Kullanıcının marka ilgi alanı",
        "category": "Diğer",
        "weight": 2
    },
    "fileExtension": {
        "api_name": "fileExtension",
        "tr_name": "Dosya Uzantısı",
        "description": "İndirilen dosya uzantısı",
        "category": "Diğer",
        "weight": 3
    },
    "fileName": {
        "api_name": "fileName",
        "tr_name": "Dosya Adı",
        "description": "İndirilen dosya adı",
        "category": "Diğer",
        "weight": 3
    },
    "fullPageUrl": {
        "api_name": "fullPageUrl",
        "tr_name": "Tam Sayfa URL",
        "description": "Protokol dahil tam URL",
        "category": "Diğer",
        "weight": 3
    },
    "linkClasses": {
        "api_name": "linkClasses",
        "tr_name": "Link CSS Sınıfları",
        "description": "Tıklanan linkin CSS sınıfları",
        "category": "Diğer",
        "weight": 2
    },
    "linkDomain": {
        "api_name": "linkDomain",
        "tr_name": "Link Domain",
        "description": "Tıklanan linkin domain'i",
        "category": "Diğer",
        "weight": 3
    },
    "linkId": {
        "api_name": "linkId",
        "tr_name": "Link ID",
        "description": "Tıklanan linkin HTML ID'si",
        "category": "Diğer",
        "weight": 2
    },
    "linkText": {
        "api_name": "linkText",
        "tr_name": "Link Metni",
        "description": "Tıklanan linkin metni",
        "category": "Diğer",
        "weight": 3
    },
    "linkUrl": {
        "api_name": "linkUrl",
        "tr_name": "Link URL",
        "description": "Tıklanan linkin URL'si",
        "category": "Diğer",
        "weight": 3
    },
    "outbound": {
        "api_name": "outbound",
        "tr_name": "Dış Link",
        "description": "Linkin dış site linki olup olmadığı",
        "category": "Diğer",
        "weight": 3
    },
    "percentScrolled": {
        "api_name": "percentScrolled",
        "tr_name": "Kaydırma Yüzdesi",
        "description": "Sayfanın kaydırılma yüzdesi",
        "category": "Diğer",
        "weight": 4
    },
    "searchTerm": {
        "api_name": "searchTerm",
        "tr_name": "Arama Terimi",
        "description": "Site içi arama terimi",
        "category": "Diğer",
        "weight": 6
    },
    "videoProvider": {
        "api_name": "videoProvider",
        "tr_name": "Video Sağlayıcı",
        "description": "Video sağlayıcı adı (YouTube, vb.)",
        "category": "Diğer",
        "weight": 3
    },
    "videoTitle": {
        "api_name": "videoTitle",
        "tr_name": "Video Başlığı",
        "description": "Video başlığı",
        "category": "Diğer",
        "weight": 4
    },
    "videoUrl": {
        "api_name": "videoUrl",
        "tr_name": "Video URL",
        "description": "Video URL'si",
        "category": "Diğer",
        "weight": 3
    },
    "virtualCurrencyName": {
        "api_name": "virtualCurrencyName",
        "tr_name": "Sanal Para Birimi",
        "description": "Oyun içi sanal para birimi adı",
        "category": "Diğer",
        "weight": 1
    },
    "visible": {
        "api_name": "visible",
        "tr_name": "Görünür",
        "description": "Öğenin görünür olup olmadığı",
        "category": "Diğer",
        "weight": 2
    },
    "streamId": {
        "api_name": "streamId",
        "tr_name": "Stream ID",
        "description": "Veri akışı kimliği",
        "category": "Diğer",
        "weight": 2
    },
    "streamName": {
        "api_name": "streamName",
        "tr_name": "Stream Adı",
        "description": "Veri akışı adı",
        "category": "Diğer",
        "weight": 2
    },
    "testDataFilterName": {
        "api_name": "testDataFilterName",
        "tr_name": "Test Filtresi Adı",
        "description": "Test veri filtresi adı",
        "category": "Diğer",
        "weight": 1
    },
    "sessionCampaignId": {
        "api_name": "sessionCampaignId",
        "tr_name": "Oturum Kampanya ID",
        "description": "Oturumu başlatan kampanya ID'si",
        "category": "Oturum",
        "weight": 4
    },
    "firstUserCampaignId": {
        "api_name": "firstUserCampaignId",
        "tr_name": "İlk Kampanya ID",
        "description": "Kullanıcıyı ilk getiren kampanya ID'si",
        "category": "Kullanıcı",
        "weight": 3
    },
}


# =============================================================================
# METRICS (Metrikler)
# =============================================================================

METRICS = {
    # -------------------------------------------------------------------------
    # USER (Kullanıcı) Metrikleri
    # -------------------------------------------------------------------------
    "totalUsers": {
        "api_name": "totalUsers",
        "tr_name": "Toplam Kullanıcı",
        "description": "Toplam benzersiz kullanıcı sayısı",
        "category": "Kullanıcı",
        "type": "integer",
        "weight": 10
    },
    "newUsers": {
        "api_name": "newUsers",
        "tr_name": "Yeni Kullanıcı",
        "description": "İlk kez gelen kullanıcı sayısı",
        "category": "Kullanıcı",
        "type": "integer",
        "weight": 9
    },
    "activeUsers": {
        "api_name": "activeUsers",
        "tr_name": "Aktif Kullanıcı",
        "description": "Aktif kullanıcı sayısı",
        "category": "Kullanıcı",
        "type": "integer",
        "weight": 9
    },
    "dauPerMau": {
        "api_name": "dauPerMau",
        "tr_name": "DAU/MAU Oranı",
        "description": "Günlük aktif kullanıcı / Aylık aktif kullanıcı oranı",
        "category": "Kullanıcı",
        "type": "float",
        "weight": 5
    },
    "dauPerWau": {
        "api_name": "dauPerWau",
        "tr_name": "DAU/WAU Oranı",
        "description": "Günlük aktif kullanıcı / Haftalık aktif kullanıcı oranı",
        "category": "Kullanıcı",
        "type": "float",
        "weight": 5
    },
    "wauPerMau": {
        "api_name": "wauPerMau",
        "tr_name": "WAU/MAU Oranı",
        "description": "Haftalık aktif kullanıcı / Aylık aktif kullanıcı oranı",
        "category": "Kullanıcı",
        "type": "float",
        "weight": 5
    },
    "userEngagementDuration": {
        "api_name": "userEngagementDuration",
        "tr_name": "Kullanıcı Etkileşim Süresi",
        "description": "Toplam kullanıcı etkileşim süresi (saniye)",
        "category": "Kullanıcı",
        "type": "float",
        "weight": 7
    },
    "engagedSessions": {
        "api_name": "engagedSessions",
        "tr_name": "Etkileşimli Oturumlar",
        "description": "10 saniyeden uzun veya dönüşüm içeren oturum sayısı",
        "category": "Kullanıcı",
        "type": "integer",
        "weight": 8
    },
    "engagementRate": {
        "api_name": "engagementRate",
        "tr_name": "Etkileşim Oranı",
        "description": "Etkileşimli oturum yüzdesi",
        "category": "Kullanıcı",
        "type": "percent",
        "weight": 8
    },
    "bounceRate": {
        "api_name": "bounceRate",
        "tr_name": "Hemen Çıkma Oranı",
        "description": "Tek sayfa oturumların yüzdesi",
        "category": "Kullanıcı",
        "type": "percent",
        "weight": 9
    },

    # -------------------------------------------------------------------------
    # SESSION (Oturum) Metrikleri
    # -------------------------------------------------------------------------
    "sessions": {
        "api_name": "sessions",
        "tr_name": "Oturum Sayısı",
        "description": "Toplam oturum sayısı",
        "category": "Oturum",
        "type": "integer",
        "weight": 10
    },
    "sessionsPerUser": {
        "api_name": "sessionsPerUser",
        "tr_name": "Kullanıcı Başına Oturum",
        "description": "Kullanıcı başına ortalama oturum sayısı",
        "category": "Oturum",
        "type": "float",
        "weight": 7
    },
    "averageSessionDuration": {
        "api_name": "averageSessionDuration",
        "tr_name": "Ortalama Oturum Süresi",
        "description": "Ortalama oturum süresi (saniye)",
        "category": "Oturum",
        "type": "duration",
        "weight": 9
    },
    "screenPageViewsPerSession": {
        "api_name": "screenPageViewsPerSession",
        "tr_name": "Oturum Başına Sayfa",
        "description": "Oturum başına ortalama sayfa görüntüleme",
        "category": "Oturum",
        "type": "float",
        "weight": 8
    },

    # -------------------------------------------------------------------------
    # PAGE / SCREEN (Sayfa/Ekran) Metrikleri
    # -------------------------------------------------------------------------
    "screenPageViews": {
        "api_name": "screenPageViews",
        "tr_name": "Sayfa Görüntüleme",
        "description": "Toplam sayfa görüntüleme sayısı",
        "category": "Sayfa",
        "type": "integer",
        "weight": 10
    },
    "screenPageViewsPerUser": {
        "api_name": "screenPageViewsPerUser",
        "tr_name": "Kullanıcı Başına Sayfa",
        "description": "Kullanıcı başına ortalama sayfa görüntüleme",
        "category": "Sayfa",
        "type": "float",
        "weight": 7
    },
    "entrances": {
        "api_name": "entrances",
        "tr_name": "Giriş Sayısı",
        "description": "Sayfaya giriş sayısı",
        "category": "Sayfa",
        "type": "integer",
        "weight": 7
    },
    "exits": {
        "api_name": "exits",
        "tr_name": "Çıkış Sayısı",
        "description": "Sayfadan çıkış sayısı",
        "category": "Sayfa",
        "type": "integer",
        "weight": 7
    },
    "viewsPerSession": {
        "api_name": "viewsPerSession",
        "tr_name": "Oturum Başına Görüntüleme",
        "description": "Oturum başına sayfa görüntüleme",
        "category": "Sayfa",
        "type": "float",
        "weight": 6
    },

    # -------------------------------------------------------------------------
    # EVENT (Etkinlik) Metrikleri
    # -------------------------------------------------------------------------
    "eventCount": {
        "api_name": "eventCount",
        "tr_name": "Etkinlik Sayısı",
        "description": "Toplam etkinlik sayısı",
        "category": "Etkinlik",
        "type": "integer",
        "weight": 7
    },
    "eventCountPerUser": {
        "api_name": "eventCountPerUser",
        "tr_name": "Kullanıcı Başına Etkinlik",
        "description": "Kullanıcı başına ortalama etkinlik sayısı",
        "category": "Etkinlik",
        "type": "float",
        "weight": 6
    },
    "eventValue": {
        "api_name": "eventValue",
        "tr_name": "Etkinlik Değeri",
        "description": "Etkinliklerin toplam değeri",
        "category": "Etkinlik",
        "type": "currency",
        "weight": 4
    },
    "eventsPerSession": {
        "api_name": "eventsPerSession",
        "tr_name": "Oturum Başına Etkinlik",
        "description": "Oturum başına ortalama etkinlik sayısı",
        "category": "Etkinlik",
        "type": "float",
        "weight": 6
    },

    # -------------------------------------------------------------------------
    # CONVERSION (Dönüşüm) Metrikleri
    # -------------------------------------------------------------------------
    "conversions": {
        "api_name": "conversions",
        "tr_name": "Dönüşüm Sayısı",
        "description": "Toplam dönüşüm sayısı",
        "category": "Dönüşüm",
        "type": "integer",
        "weight": 6
    },
    "sessionConversionRate": {
        "api_name": "sessionConversionRate",
        "tr_name": "Oturum Dönüşüm Oranı",
        "description": "Dönüşüm içeren oturum yüzdesi",
        "category": "Dönüşüm",
        "type": "percent",
        "weight": 6
    },
    "userConversionRate": {
        "api_name": "userConversionRate",
        "tr_name": "Kullanıcı Dönüşüm Oranı",
        "description": "Dönüşüm gerçekleştiren kullanıcı yüzdesi",
        "category": "Dönüşüm",
        "type": "percent",
        "weight": 6
    },

    # -------------------------------------------------------------------------
    # ECOMMERCE (E-Ticaret) Metrikleri
    # -------------------------------------------------------------------------
    "transactions": {
        "api_name": "transactions",
        "tr_name": "İşlem Sayısı",
        "description": "Toplam e-ticaret işlem sayısı",
        "category": "E-Ticaret",
        "type": "integer",
        "weight": 2
    },
    "ecommercePurchases": {
        "api_name": "ecommercePurchases",
        "tr_name": "Satın Alma Sayısı",
        "description": "Toplam satın alma sayısı",
        "category": "E-Ticaret",
        "type": "integer",
        "weight": 2
    },
    "purchaseRevenue": {
        "api_name": "purchaseRevenue",
        "tr_name": "Satın Alma Geliri",
        "description": "Satın almalardan elde edilen toplam gelir",
        "category": "E-Ticaret",
        "type": "currency",
        "weight": 2
    },
    "totalRevenue": {
        "api_name": "totalRevenue",
        "tr_name": "Toplam Gelir",
        "description": "Tüm kaynaklardan toplam gelir",
        "category": "E-Ticaret",
        "type": "currency",
        "weight": 3
    },
    "averageRevenuePerUser": {
        "api_name": "averageRevenuePerUser",
        "tr_name": "Kullanıcı Başına Gelir",
        "description": "Kullanıcı başına ortalama gelir (ARPU)",
        "category": "E-Ticaret",
        "type": "currency",
        "weight": 2
    },
    "averagePurchaseRevenue": {
        "api_name": "averagePurchaseRevenue",
        "tr_name": "Ortalama Satın Alma Geliri",
        "description": "Satın alma başına ortalama gelir",
        "category": "E-Ticaret",
        "type": "currency",
        "weight": 2
    },
    "averagePurchaseRevenuePerUser": {
        "api_name": "averagePurchaseRevenuePerUser",
        "tr_name": "Kullanıcı Başına Satın Alma Geliri",
        "description": "Kullanıcı başına ortalama satın alma geliri",
        "category": "E-Ticaret",
        "type": "currency",
        "weight": 2
    },
    "itemsViewed": {
        "api_name": "itemsViewed",
        "tr_name": "Görüntülenen Ürün",
        "description": "Görüntülenen ürün sayısı",
        "category": "E-Ticaret",
        "type": "integer",
        "weight": 2
    },
    "itemsAddedToCart": {
        "api_name": "itemsAddedToCart",
        "tr_name": "Sepete Eklenen",
        "description": "Sepete eklenen ürün sayısı",
        "category": "E-Ticaret",
        "type": "integer",
        "weight": 2
    },
    "itemsCheckedOut": {
        "api_name": "itemsCheckedOut",
        "tr_name": "Ödemeye Geçilen",
        "description": "Ödeme sürecine geçilen ürün sayısı",
        "category": "E-Ticaret",
        "type": "integer",
        "weight": 2
    },
    "itemsPurchased": {
        "api_name": "itemsPurchased",
        "tr_name": "Satın Alınan Ürün",
        "description": "Satın alınan ürün sayısı",
        "category": "E-Ticaret",
        "type": "integer",
        "weight": 2
    },
    "itemRevenue": {
        "api_name": "itemRevenue",
        "tr_name": "Ürün Geliri",
        "description": "Ürünlerden elde edilen gelir",
        "category": "E-Ticaret",
        "type": "currency",
        "weight": 2
    },
    "itemQuantity": {
        "api_name": "itemQuantity",
        "tr_name": "Ürün Adedi",
        "description": "Satın alınan ürün adedi",
        "category": "E-Ticaret",
        "type": "integer",
        "weight": 2
    },
    "cartToViewRate": {
        "api_name": "cartToViewRate",
        "tr_name": "Sepete Ekleme Oranı",
        "description": "Görüntülenen ürünlerin sepete eklenme oranı",
        "category": "E-Ticaret",
        "type": "percent",
        "weight": 2
    },
    "purchaseToViewRate": {
        "api_name": "purchaseToViewRate",
        "tr_name": "Satın Alma Oranı",
        "description": "Görüntülenen ürünlerin satın alınma oranı",
        "category": "E-Ticaret",
        "type": "percent",
        "weight": 2
    },
    "refundAmount": {
        "api_name": "refundAmount",
        "tr_name": "İade Tutarı",
        "description": "Toplam iade tutarı",
        "category": "E-Ticaret",
        "type": "currency",
        "weight": 1
    },
    "shippingAmount": {
        "api_name": "shippingAmount",
        "tr_name": "Kargo Tutarı",
        "description": "Toplam kargo tutarı",
        "category": "E-Ticaret",
        "type": "currency",
        "weight": 1
    },
    "taxAmount": {
        "api_name": "taxAmount",
        "tr_name": "Vergi Tutarı",
        "description": "Toplam vergi tutarı",
        "category": "E-Ticaret",
        "type": "currency",
        "weight": 1
    },
    "transactionsPerPurchaser": {
        "api_name": "transactionsPerPurchaser",
        "tr_name": "Alıcı Başına İşlem",
        "description": "Satın alan kullanıcı başına işlem sayısı",
        "category": "E-Ticaret",
        "type": "float",
        "weight": 2
    },

    # -------------------------------------------------------------------------
    # PUBLISHER (Yayıncı) Metrikleri
    # -------------------------------------------------------------------------
    "publisherAdClicks": {
        "api_name": "publisherAdClicks",
        "tr_name": "Reklam Tıklamaları",
        "description": "Yayıncı reklam tıklama sayısı",
        "category": "Yayıncı",
        "type": "integer",
        "weight": 4
    },
    "publisherAdImpressions": {
        "api_name": "publisherAdImpressions",
        "tr_name": "Reklam Gösterimleri",
        "description": "Yayıncı reklam gösterim sayısı",
        "category": "Yayıncı",
        "type": "integer",
        "weight": 4
    },
    "totalAdRevenue": {
        "api_name": "totalAdRevenue",
        "tr_name": "Toplam Reklam Geliri",
        "description": "Reklamlardan elde edilen toplam gelir",
        "category": "Yayıncı",
        "type": "currency",
        "weight": 4
    },

    # -------------------------------------------------------------------------
    # SCROLL (Kaydırma) Metrikleri
    # -------------------------------------------------------------------------
    "scrolledUsers": {
        "api_name": "scrolledUsers",
        "tr_name": "Kaydıran Kullanıcı",
        "description": "Sayfayı kaydıran kullanıcı sayısı",
        "category": "Etkileşim",
        "type": "integer",
        "weight": 6
    },

    # -------------------------------------------------------------------------
    # OTHER (Diğer) Metrikler
    # -------------------------------------------------------------------------
    "crashAffectedUsers": {
        "api_name": "crashAffectedUsers",
        "tr_name": "Çökme Yaşayan Kullanıcı",
        "description": "Uygulama çökmesi yaşayan kullanıcı sayısı",
        "category": "Teknik",
        "type": "integer",
        "weight": 3
    },
    "crashFreeUsersRate": {
        "api_name": "crashFreeUsersRate",
        "tr_name": "Çökmesiz Kullanıcı Oranı",
        "description": "Çökme yaşamayan kullanıcı yüzdesi",
        "category": "Teknik",
        "type": "percent",
        "weight": 3
    },
    "firstTimePurchasers": {
        "api_name": "firstTimePurchasers",
        "tr_name": "İlk Kez Satın Alanlar",
        "description": "İlk kez satın alma yapan kullanıcı sayısı",
        "category": "E-Ticaret",
        "type": "integer",
        "weight": 2
    },
    "firstTimePurchasersPerNewUser": {
        "api_name": "firstTimePurchasersPerNewUser",
        "tr_name": "Yeni Kullanıcı Başına İlk Satın Alma",
        "description": "Yeni kullanıcıların ilk satın alma oranı",
        "category": "E-Ticaret",
        "type": "float",
        "weight": 2
    },
    "totalPurchasers": {
        "api_name": "totalPurchasers",
        "tr_name": "Toplam Satın Alanlar",
        "description": "Satın alma yapan toplam kullanıcı sayısı",
        "category": "E-Ticaret",
        "type": "integer",
        "weight": 2
    },
    "organicGoogleSearchAveragePosition": {
        "api_name": "organicGoogleSearchAveragePosition",
        "tr_name": "Google Arama Pozisyonu",
        "description": "Google organik aramada ortalama pozisyon",
        "category": "SEO",
        "type": "float",
        "weight": 5
    },
    "organicGoogleSearchClicks": {
        "api_name": "organicGoogleSearchClicks",
        "tr_name": "Google Arama Tıklamaları",
        "description": "Google organik aramadan gelen tıklama sayısı",
        "category": "SEO",
        "type": "integer",
        "weight": 5
    },
    "organicGoogleSearchClickThroughRate": {
        "api_name": "organicGoogleSearchClickThroughRate",
        "tr_name": "Google Arama CTR",
        "description": "Google organik arama tıklama oranı",
        "category": "SEO",
        "type": "percent",
        "weight": 5
    },
    "organicGoogleSearchImpressions": {
        "api_name": "organicGoogleSearchImpressions",
        "tr_name": "Google Arama Gösterimleri",
        "description": "Google organik aramada gösterim sayısı",
        "category": "SEO",
        "type": "integer",
        "weight": 5
    },
}


# =============================================================================
# CUSTOM DIMENSIONS (Özel Boyutlar)
# =============================================================================
# Hürriyet/Vatan property'sine özel custom dimension'lar
# Bu kısım senin property'ne göre özelleştirilmiştir
# Yeni custom dimension eklemek için bu sözlüğe ekleme yapabilirsin

CUSTOM_DIMENSIONS = {
    # -------------------------------------------------------------------------
    # HÜRRIYET Custom Dimension'ları
    # -------------------------------------------------------------------------
    "hcat1": {
        "api_name": "customEvent:hcat1",
        "tr_name": "Ana Kategori",
        "description": "Haberin ana kategorisi (Spor, Ekonomi, Gündem, vb.)",
        "category": "İçerik",
        "scope": "event",
        "weight": 10
    },
    "hcat2": {
        "api_name": "customEvent:hcat2",
        "tr_name": "Alt Kategori",
        "description": "Haberin alt kategorisi",
        "category": "İçerik",
        "scope": "event",
        "weight": 8
    },
    "hcat3": {
        "api_name": "customEvent:hcat3",
        "tr_name": "Alt Kategori 3",
        "description": "Haberin üçüncü seviye kategorisi",
        "category": "İçerik",
        "scope": "event",
        "weight": 5
    },
    "hcat4": {
        "api_name": "customEvent:hcat4",
        "tr_name": "Alt Kategori 4",
        "description": "Haberin dördüncü seviye kategorisi",
        "category": "İçerik",
        "scope": "event",
        "weight": 3
    },
    "hnewsid": {
        "api_name": "customEvent:hnewsid",
        "tr_name": "Haber ID",
        "description": "Haberin benzersiz kimlik numarası",
        "category": "İçerik",
        "scope": "event",
        "weight": 7
    },
    "heditor": {
        "api_name": "customEvent:heditor",
        "tr_name": "Editör",
        "description": "Haberi yazan/düzenleyen editör",
        "category": "İçerik",
        "scope": "event",
        "weight": 10
    },
    "hauthor": {
        "api_name": "customEvent:hauthor",
        "tr_name": "Yazar",
        "description": "Haberin yazarı",
        "category": "İçerik",
        "scope": "event",
        "weight": 9
    },
    "hauthortype": {
        "api_name": "customEvent:hauthortype",
        "tr_name": "Yazar Tipi",
        "description": "Yazar türü (köşe yazarı, muhabir, vb.)",
        "category": "İçerik",
        "scope": "event",
        "weight": 6
    },
    "hpublisheddate": {
        "api_name": "customEvent:hpublisheddate",
        "tr_name": "Yayın Tarihi",
        "description": "Haberin yayınlanma tarihi (YYYYMMDD)",
        "category": "İçerik",
        "scope": "event",
        "weight": 7
    },
    "hnewstype": {
        "api_name": "customEvent:hnewstype",
        "tr_name": "Haber Tipi",
        "description": "Haber türü (haber, video, galeri, vb.)",
        "category": "İçerik",
        "scope": "event",
        "weight": 9
    },
    "htag": {
        "api_name": "customEvent:htag",
        "tr_name": "Etiket",
        "description": "Haberin etiketi/tag'i",
        "category": "İçerik",
        "scope": "event",
        "weight": 8
    },

    # -------------------------------------------------------------------------
    # VATAN Custom Dimension'ları
    # -------------------------------------------------------------------------
    "vcat1": {
        "api_name": "customEvent:vcat1",
        "tr_name": "Ana Kategori",
        "description": "Haberin ana kategorisi (Spor, Ekonomi, Gündem, vb.)",
        "category": "İçerik",
        "scope": "event",
        "weight": 10
    },
    "vcat2": {
        "api_name": "customEvent:vcat2",
        "tr_name": "Alt Kategori",
        "description": "Haberin alt kategorisi",
        "category": "İçerik",
        "scope": "event",
        "weight": 8
    },
    "vcat3": {
        "api_name": "customEvent:vcat3",
        "tr_name": "Alt Kategori 3",
        "description": "Haberin üçüncü seviye kategorisi",
        "category": "İçerik",
        "scope": "event",
        "weight": 5
    },
    "vcat4": {
        "api_name": "customEvent:vcat4",
        "tr_name": "Alt Kategori 4",
        "description": "Haberin dördüncü seviye kategorisi",
        "category": "İçerik",
        "scope": "event",
        "weight": 3
    },
    "vnewsid": {
        "api_name": "customEvent:vnewsid",
        "tr_name": "Haber ID",
        "description": "Haberin benzersiz kimlik numarası",
        "category": "İçerik",
        "scope": "event",
        "weight": 7
    },
    "veditor": {
        "api_name": "customEvent:veditor",
        "tr_name": "Editör",
        "description": "Haberi yazan/düzenleyen editör",
        "category": "İçerik",
        "scope": "event",
        "weight": 10
    },
    "vauthor": {
        "api_name": "customEvent:vauthor",
        "tr_name": "Yazar",
        "description": "Haberin yazarı",
        "category": "İçerik",
        "scope": "event",
        "weight": 9
    },
    "vauthortype": {
        "api_name": "customEvent:vauthortype",
        "tr_name": "Yazar Tipi",
        "description": "Yazar türü (köşe yazarı, muhabir, vb.)",
        "category": "İçerik",
        "scope": "event",
        "weight": 6
    },
    "vpublisheddate": {
        "api_name": "customEvent:vpublisheddate",
        "tr_name": "Yayın Tarihi",
        "description": "Haberin yayınlanma tarihi (YYYYMMDD)",
        "category": "İçerik",
        "scope": "event",
        "weight": 7
    },
    "vnewstype": {
        "api_name": "customEvent:vnewstype",
        "tr_name": "Haber Tipi",
        "description": "Haber türü (haber, video, galeri, vb.)",
        "category": "İçerik",
        "scope": "event",
        "weight": 9
    },
    "vpagetype": {
        "api_name": "customEvent:vpagetype",
        "tr_name": "Sayfa Tipi",
        "description": "Sayfa türü (anasayfa, detay, kategori, vb.)",
        "category": "İçerik",
        "scope": "event",
        "weight": 8
    },
    "vcontenttype": {
        "api_name": "customEvent:vcontenttype",
        "tr_name": "İçerik Tipi",
        "description": "İçerik türü (makale, video, galeri, canlı yayın, vb.)",
        "category": "İçerik",
        "scope": "event",
        "weight": 7
    },
    "vtag": {
        "api_name": "customEvent:vtag",
        "tr_name": "Etiket",
        "description": "Haberin etiketi/tag'i",
        "category": "İçerik",
        "scope": "event",
        "weight": 8
    },
    "vseotype": {
        "api_name": "customEvent:vseotype",
        "tr_name": "SEO Tipi",
        "description": "SEO optimizasyon türü",
        "category": "İçerik",
        "scope": "event",
        "weight": 5
    },
    "vsource": {
        "api_name": "customEvent:vsource",
        "tr_name": "Haber Kaynağı",
        "description": "Haberin kaynağı (ajans, özel haber, vb.)",
        "category": "İçerik",
        "scope": "event",
        "weight": 6
    },
    "vsubdom": {
        "api_name": "customEvent:vsubdom",
        "tr_name": "Alt Domain",
        "description": "Alt domain bilgisi",
        "category": "İçerik",
        "scope": "event",
        "weight": 4
    },

    # -------------------------------------------------------------------------
    # ETKİNLİK (Event) Custom Dimension'ları
    # -------------------------------------------------------------------------
    "event_category": {
        "api_name": "customEvent:event_category",
        "tr_name": "Etkinlik Kategorisi",
        "description": "Etkinlik kategorisi (UA uyumlu)",
        "category": "Etkinlik",
        "scope": "event",
        "weight": 5
    },
    "event_action": {
        "api_name": "customEvent:event_action",
        "tr_name": "Etkinlik Aksiyonu",
        "description": "Etkinlik aksiyonu (UA uyumlu)",
        "category": "Etkinlik",
        "scope": "event",
        "weight": 5
    },
    "event_label": {
        "api_name": "customEvent:event_label",
        "tr_name": "Etkinlik Etiketi",
        "description": "Etkinlik etiketi (UA uyumlu)",
        "category": "Etkinlik",
        "scope": "event",
        "weight": 5
    },

    # -------------------------------------------------------------------------
    # DİĞER Custom Dimension'lar
    # -------------------------------------------------------------------------
    "infinite": {
        "api_name": "customEvent:infinite",
        "tr_name": "Sonsuz Kaydırma",
        "description": "Sonsuz kaydırma durumu",
        "category": "Diğer",
        "scope": "event",
        "weight": 3
    },
    "g_skbid": {
        "api_name": "customEvent:g_skbid",
        "tr_name": "SKB ID",
        "description": "SKB kimlik numarası",
        "category": "Diğer",
        "scope": "event",
        "weight": 2
    },
}


# =============================================================================
# CUSTOM METRICS (Özel Metrikler)
# =============================================================================
# Property'ye özel custom metric'ler

CUSTOM_METRICS = {
    "averageDuration": {
        "api_name": "customEvent:averageDuration",
        "tr_name": "Ortalama Süre",
        "description": "Ortalama okuma/izleme süresi",
        "category": "Etkileşim",
        "type": "float",
        "weight": 8
    },
    "maxScroll": {
        "api_name": "customEvent:maxScroll",
        "tr_name": "Maksimum Kaydırma",
        "description": "Maksimum kaydırma yüzdesi",
        "category": "Etkileşim",
        "type": "float",
        "weight": 7
    },
    "r_Duration": {
        "api_name": "customEvent:r_Duration",
        "tr_name": "Okuma Süresi",
        "description": "Gerçek okuma süresi",
        "category": "Etkileşim",
        "type": "float",
        "weight": 8
    },
    "r_Scroll": {
        "api_name": "customEvent:r_Scroll",
        "tr_name": "Okuma Kaydırması",
        "description": "Okuma kaydırma yüzdesi",
        "category": "Etkileşim",
        "type": "float",
        "weight": 7
    },
}


# =============================================================================
# HELPER FUNCTIONS (Yardımcı Fonksiyonlar)
# =============================================================================

def get_dimension_info(api_name_or_tr_name: str) -> dict:
    """
    Dimension bilgisini API adı veya Türkçe adıyla getirir.

    Args:
        api_name_or_tr_name: API adı (ör: "sessionDefaultChannelGroup") veya Türkçe adı (ör: "Kanal Grubu")

    Returns:
        Dimension bilgi sözlüğü veya None
    """
    # Önce standart dimension'larda ara
    for key, value in DIMENSIONS.items():
        if key == api_name_or_tr_name or value["api_name"] == api_name_or_tr_name or value["tr_name"] == api_name_or_tr_name:
            return value

    # Custom dimension'larda ara
    for key, value in CUSTOM_DIMENSIONS.items():
        if key == api_name_or_tr_name or value["api_name"] == api_name_or_tr_name or value["tr_name"] == api_name_or_tr_name:
            return value

    return None


def get_metric_info(api_name_or_tr_name: str) -> dict:
    """
    Metric bilgisini API adı veya Türkçe adıyla getirir.

    Args:
        api_name_or_tr_name: API adı (ör: "screenPageViews") veya Türkçe adı (ör: "Sayfa Görüntüleme")

    Returns:
        Metric bilgi sözlüğü veya None
    """
    # Standart metric'lerde ara
    for key, value in METRICS.items():
        if key == api_name_or_tr_name or value["api_name"] == api_name_or_tr_name or value["tr_name"] == api_name_or_tr_name:
            return value

    # Custom metric'lerde ara
    for key, value in CUSTOM_METRICS.items():
        if key == api_name_or_tr_name or value["api_name"] == api_name_or_tr_name or value["tr_name"] == api_name_or_tr_name:
            return value

    return None


def get_api_name_from_tr(tr_name: str) -> str:
    """
    Türkçe isimden API adını bulur.

    Args:
        tr_name: Türkçe isim (ör: "Sayfa Görüntüleme")

    Returns:
        API adı (ör: "screenPageViews") veya None
    """
    # Dimension'larda ara
    for key, value in DIMENSIONS.items():
        if value["tr_name"].lower() == tr_name.lower():
            return value["api_name"]

    # Custom dimension'larda ara
    for key, value in CUSTOM_DIMENSIONS.items():
        if value["tr_name"].lower() == tr_name.lower():
            return value["api_name"]

    # Metric'lerde ara
    for key, value in METRICS.items():
        if value["tr_name"].lower() == tr_name.lower():
            return value["api_name"]

    # Custom metric'lerde ara
    for key, value in CUSTOM_METRICS.items():
        if value["tr_name"].lower() == tr_name.lower():
            return value["api_name"]

    return None


def get_tr_name_from_api(api_name: str) -> str:
    """
    API adından Türkçe ismi bulur.

    Args:
        api_name: API adı (ör: "screenPageViews")

    Returns:
        Türkçe isim (ör: "Sayfa Görüntüleme") veya orijinal API adı
    """
    # Custom event prefix'ini temizle
    clean_api_name = api_name.replace("customEvent:", "")

    # Dimension'larda ara
    for key, value in DIMENSIONS.items():
        if value["api_name"] == api_name or key == clean_api_name:
            return value["tr_name"]

    # Custom dimension'larda ara
    for key, value in CUSTOM_DIMENSIONS.items():
        if value["api_name"] == api_name or key == clean_api_name:
            return value["tr_name"]

    # Metric'lerde ara
    for key, value in METRICS.items():
        if value["api_name"] == api_name or key == clean_api_name:
            return value["tr_name"]

    # Custom metric'lerde ara
    for key, value in CUSTOM_METRICS.items():
        if value["api_name"] == api_name or key == clean_api_name:
            return value["tr_name"]

    return api_name  # Bulunamazsa orijinal adı döndür


def list_dimensions_by_category(category: str = None) -> list:
    """
    Kategoriye göre dimension listesi döndürür.

    Args:
        category: Kategori adı (None ise tümünü döndürür)

    Returns:
        Dimension listesi
    """
    result = []

    for key, value in DIMENSIONS.items():
        if category is None or value["category"] == category:
            result.append(value)

    for key, value in CUSTOM_DIMENSIONS.items():
        if category is None or value["category"] == category:
            result.append(value)

    return result


def list_metrics_by_category(category: str = None) -> list:
    """
    Kategoriye göre metric listesi döndürür.

    Args:
        category: Kategori adı (None ise tümünü döndürür)

    Returns:
        Metric listesi
    """
    result = []

    for key, value in METRICS.items():
        if category is None or value["category"] == category:
            result.append(value)

    for key, value in CUSTOM_METRICS.items():
        if category is None or value["category"] == category:
            result.append(value)

    return result


def get_all_categories() -> dict:
    """
    Tüm kategorileri ve içindeki dimension/metric sayılarını döndürür.

    Returns:
        Kategori sözlüğü
    """
    categories = {
        "dimensions": {},
        "metrics": {}
    }

    # Dimension kategorileri
    for key, value in DIMENSIONS.items():
        cat = value["category"]
        categories["dimensions"][cat] = categories["dimensions"].get(cat, 0) + 1

    for key, value in CUSTOM_DIMENSIONS.items():
        cat = value["category"]
        categories["dimensions"][cat] = categories["dimensions"].get(cat, 0) + 1

    # Metric kategorileri
    for key, value in METRICS.items():
        cat = value["category"]
        categories["metrics"][cat] = categories["metrics"].get(cat, 0) + 1

    for key, value in CUSTOM_METRICS.items():
        cat = value["category"]
        categories["metrics"][cat] = categories["metrics"].get(cat, 0) + 1

    return categories


def search_dimensions_and_metrics(query: str) -> dict:
    """
    Dimension ve metric'lerde arama yapar.

    Args:
        query: Arama terimi

    Returns:
        Eşleşen dimension ve metric'ler
    """
    query_lower = query.lower()
    results = {
        "dimensions": [],
        "metrics": []
    }

    # Dimension'larda ara
    for key, value in DIMENSIONS.items():
        if (query_lower in key.lower() or
            query_lower in value["tr_name"].lower() or
            query_lower in value["description"].lower()):
            results["dimensions"].append(value)

    # Custom dimension'larda ara
    for key, value in CUSTOM_DIMENSIONS.items():
        if (query_lower in key.lower() or
            query_lower in value["tr_name"].lower() or
            query_lower in value["description"].lower()):
            results["dimensions"].append(value)

    # Metric'lerde ara
    for key, value in METRICS.items():
        if (query_lower in key.lower() or
            query_lower in value["tr_name"].lower() or
            query_lower in value["description"].lower()):
            results["metrics"].append(value)

    # Custom metric'lerde ara
    for key, value in CUSTOM_METRICS.items():
        if (query_lower in key.lower() or
            query_lower in value["tr_name"].lower() or
            query_lower in value["description"].lower()):
            results["metrics"].append(value)

    return results


# =============================================================================
# WEIGHT (Ağırlık) TABANLI FONKSİYONLAR
# =============================================================================
# Weight değerlerine göre dimension ve metrikleri filtreleme ve sıralama


def get_top_dimensions(min_weight: int = 7, category: str = None, limit: int = None) -> list:
    """
    Yüksek ağırlıklı (önemli) dimension'ları döndürür.

    Args:
        min_weight: Minimum weight değeri (varsayılan: 7)
        category: Opsiyonel kategori filtresi
        limit: Maksimum sonuç sayısı (None = sınırsız)

    Returns:
        Weight değerine göre sıralı dimension listesi
    """
    result = []

    # Standart dimension'lar
    for key, value in DIMENSIONS.items():
        weight = value.get("weight", 5)  # Varsayılan weight: 5
        if weight >= min_weight:
            if category is None or value["category"] == category:
                result.append({**value, "key": key})

    # Custom dimension'lar
    for key, value in CUSTOM_DIMENSIONS.items():
        weight = value.get("weight", 5)
        if weight >= min_weight:
            if category is None or value["category"] == category:
                result.append({**value, "key": key})

    # Weight'e göre sırala (büyükten küçüğe)
    result.sort(key=lambda x: x.get("weight", 5), reverse=True)

    if limit:
        return result[:limit]
    return result


def get_top_metrics(min_weight: int = 7, category: str = None, limit: int = None) -> list:
    """
    Yüksek ağırlıklı (önemli) metrikleri döndürür.

    Args:
        min_weight: Minimum weight değeri (varsayılan: 7)
        category: Opsiyonel kategori filtresi
        limit: Maksimum sonuç sayısı (None = sınırsız)

    Returns:
        Weight değerine göre sıralı metric listesi
    """
    result = []

    # Standart metric'ler
    for key, value in METRICS.items():
        weight = value.get("weight", 5)
        if weight >= min_weight:
            if category is None or value["category"] == category:
                result.append({**value, "key": key})

    # Custom metric'ler
    for key, value in CUSTOM_METRICS.items():
        weight = value.get("weight", 5)
        if weight >= min_weight:
            if category is None or value["category"] == category:
                result.append({**value, "key": key})

    # Weight'e göre sırala
    result.sort(key=lambda x: x.get("weight", 5), reverse=True)

    if limit:
        return result[:limit]
    return result


def list_dimensions_by_weight(descending: bool = True) -> list:
    """
    Tüm dimension'ları weight değerine göre sıralı döndürür.

    Args:
        descending: True = büyükten küçüğe, False = küçükten büyüğe

    Returns:
        Sıralı dimension listesi
    """
    result = []

    for key, value in DIMENSIONS.items():
        result.append({**value, "key": key})

    for key, value in CUSTOM_DIMENSIONS.items():
        result.append({**value, "key": key})

    result.sort(key=lambda x: x.get("weight", 5), reverse=descending)
    return result


def list_metrics_by_weight(descending: bool = True) -> list:
    """
    Tüm metrikleri weight değerine göre sıralı döndürür.

    Args:
        descending: True = büyükten küçüğe, False = küçükten büyüğe

    Returns:
        Sıralı metric listesi
    """
    result = []

    for key, value in METRICS.items():
        result.append({**value, "key": key})

    for key, value in CUSTOM_METRICS.items():
        result.append({**value, "key": key})

    result.sort(key=lambda x: x.get("weight", 5), reverse=descending)
    return result


def get_weight_summary() -> dict:
    """
    Weight dağılımının özetini döndürür.

    Returns:
        Her weight seviyesindeki dimension/metric sayıları
    """
    summary = {
        "dimensions": {i: 0 for i in range(1, 11)},
        "metrics": {i: 0 for i in range(1, 11)}
    }

    # Dimension weight'leri
    for key, value in DIMENSIONS.items():
        w = value.get("weight", 5)
        summary["dimensions"][w] = summary["dimensions"].get(w, 0) + 1

    for key, value in CUSTOM_DIMENSIONS.items():
        w = value.get("weight", 5)
        summary["dimensions"][w] = summary["dimensions"].get(w, 0) + 1

    # Metric weight'leri
    for key, value in METRICS.items():
        w = value.get("weight", 5)
        summary["metrics"][w] = summary["metrics"].get(w, 0) + 1

    for key, value in CUSTOM_METRICS.items():
        w = value.get("weight", 5)
        summary["metrics"][w] = summary["metrics"].get(w, 0) + 1

    return summary


def get_recommended_for_analysis(analysis_type: str) -> dict:
    """
    Analiz tipine göre önerilen dimension ve metrikleri döndürür.

    Args:
        analysis_type: Analiz tipi
            - "traffic": Trafik analizi
            - "content": İçerik performansı
            - "audience": Kitle analizi
            - "acquisition": Kaynak analizi
            - "engagement": Etkileşim analizi

    Returns:
        Önerilen dimension ve metric'ler
    """
    recommendations = {
        "traffic": {
            "description": "Genel trafik analizi için önerilen metrikler",
            "dimensions": ["date", "hour", "dayOfWeek"],
            "metrics": ["totalUsers", "sessions", "screenPageViews", "bounceRate", "averageSessionDuration"]
        },
        "content": {
            "description": "İçerik performans analizi için önerilen metrikler",
            "dimensions": ["pagePath", "pageTitle", "customEvent:vcat1", "customEvent:veditor", "customEvent:vnewstype"],
            "metrics": ["screenPageViews", "totalUsers", "averageSessionDuration", "engagementRate"]
        },
        "audience": {
            "description": "Kitle analizi için önerilen metrikler",
            "dimensions": ["deviceCategory", "country", "city", "browser", "operatingSystem", "newVsReturning"],
            "metrics": ["totalUsers", "newUsers", "sessionsPerUser", "engagementRate"]
        },
        "acquisition": {
            "description": "Kaynak/Edinim analizi için önerilen metrikler",
            "dimensions": ["sessionDefaultChannelGroup", "source", "medium", "sourceMedium", "campaignName"],
            "metrics": ["totalUsers", "sessions", "bounceRate", "conversions"]
        },
        "engagement": {
            "description": "Etkileşim analizi için önerilen metrikler",
            "dimensions": ["pagePath", "eventName", "customEvent:vtag"],
            "metrics": ["engagementRate", "engagedSessions", "userEngagementDuration", "eventCount", "screenPageViewsPerSession"]
        }
    }

    if analysis_type.lower() in recommendations:
        return recommendations[analysis_type.lower()]
    else:
        return {
            "error": f"Bilinmeyen analiz tipi: {analysis_type}",
            "valid_types": list(recommendations.keys())
        }


def filter_by_weight_range(min_weight: int, max_weight: int, item_type: str = "all") -> dict:
    """
    Belirli weight aralığındaki dimension ve metrikleri döndürür.

    Args:
        min_weight: Minimum weight (dahil)
        max_weight: Maximum weight (dahil)
        item_type: "dimensions", "metrics" veya "all"

    Returns:
        Filtrelenmiş dimension ve metric'ler
    """
    result = {"dimensions": [], "metrics": []}

    if item_type in ["dimensions", "all"]:
        for key, value in DIMENSIONS.items():
            w = value.get("weight", 5)
            if min_weight <= w <= max_weight:
                result["dimensions"].append({**value, "key": key})

        for key, value in CUSTOM_DIMENSIONS.items():
            w = value.get("weight", 5)
            if min_weight <= w <= max_weight:
                result["dimensions"].append({**value, "key": key})

        result["dimensions"].sort(key=lambda x: x.get("weight", 5), reverse=True)

    if item_type in ["metrics", "all"]:
        for key, value in METRICS.items():
            w = value.get("weight", 5)
            if min_weight <= w <= max_weight:
                result["metrics"].append({**value, "key": key})

        for key, value in CUSTOM_METRICS.items():
            w = value.get("weight", 5)
            if min_weight <= w <= max_weight:
                result["metrics"].append({**value, "key": key})

        result["metrics"].sort(key=lambda x: x.get("weight", 5), reverse=True)

    return result


# =============================================================================
# QUICK REFERENCE (Hızlı Referans)
# =============================================================================
# Chatbot'un sık kullanacağı dimension/metric kombinasyonları

QUICK_QUERIES = {
    "genel_bakis": {
        "tr_name": "Genel Bakış",
        "description": "Temel trafik metrikleri",
        "dimensions": ["date"],
        "metrics": ["totalUsers", "sessions", "screenPageViews", "bounceRate", "averageSessionDuration"]
    },
    "trafik_kaynaklari": {
        "tr_name": "Trafik Kaynakları",
        "description": "Ziyaretçilerin nereden geldiği",
        "dimensions": ["sessionDefaultChannelGroup"],
        "metrics": ["totalUsers", "sessions", "screenPageViews", "bounceRate"]
    },
    "en_cok_okunanlar": {
        "tr_name": "En Çok Okunan Sayfalar",
        "description": "En çok görüntülenen sayfalar",
        "dimensions": ["pagePath", "pageTitle"],
        "metrics": ["screenPageViews", "totalUsers", "averageSessionDuration"]
    },
    "cihaz_dagilimi": {
        "tr_name": "Cihaz Dağılımı",
        "description": "Cihaz türüne göre dağılım",
        "dimensions": ["deviceCategory"],
        "metrics": ["totalUsers", "sessions", "screenPageViews", "bounceRate"]
    },
    "sehir_dagilimi": {
        "tr_name": "Şehir Dağılımı",
        "description": "Şehirlere göre trafik dağılımı",
        "dimensions": ["city"],
        "metrics": ["totalUsers", "sessions", "screenPageViews"]
    },
    "kategori_performansi": {
        "tr_name": "Kategori Performansı",
        "description": "Haber kategorilerine göre performans",
        "dimensions": ["customEvent:vcat1"],
        "metrics": ["screenPageViews", "totalUsers", "sessions"]
    },
    "editor_performansi": {
        "tr_name": "Editör Performansı",
        "description": "Editörlere göre performans",
        "dimensions": ["customEvent:veditor"],
        "metrics": ["screenPageViews", "totalUsers", "sessions"]
    },
    "saatlik_trafik": {
        "tr_name": "Saatlik Trafik",
        "description": "Saatlere göre trafik dağılımı",
        "dimensions": ["hour"],
        "metrics": ["totalUsers", "sessions", "screenPageViews"]
    },
    "gunluk_trafik": {
        "tr_name": "Günlük Trafik",
        "description": "Günlere göre trafik dağılımı",
        "dimensions": ["date"],
        "metrics": ["totalUsers", "sessions", "screenPageViews", "newUsers"]
    },
    "haber_tipi": {
        "tr_name": "Haber Tipi Performansı",
        "description": "Haber tipine göre performans",
        "dimensions": ["customEvent:vnewstype"],
        "metrics": ["screenPageViews", "totalUsers", "sessions"]
    }
}


if __name__ == "__main__":
    # Test
    print("=" * 60)
    print("GA4 MAPPING DOSYASI - TEST")
    print("=" * 60)

    print(f"\nToplam Standart Dimension: {len(DIMENSIONS)}")
    print(f"Toplam Custom Dimension: {len(CUSTOM_DIMENSIONS)}")
    print(f"Toplam Metric: {len(METRICS)}")
    print(f"Toplam Hızlı Sorgu: {len(QUICK_QUERIES)}")

    print("\n--- Kategoriler ---")
    categories = get_all_categories()
    print("Dimension Kategorileri:")
    for cat, count in categories["dimensions"].items():
        print(f"  - {cat}: {count}")

    print("\nMetric Kategorileri:")
    for cat, count in categories["metrics"].items():
        print(f"  - {cat}: {count}")

    print("\n--- Örnek Arama: 'sayfa' ---")
    results = search_dimensions_and_metrics("sayfa")
    print(f"Bulunan Dimension: {len(results['dimensions'])}")
    print(f"Bulunan Metric: {len(results['metrics'])}")

    print("\n--- Türkçe/API Dönüşüm Örneği ---")
    print(f"'screenPageViews' -> '{get_tr_name_from_api('screenPageViews')}'")
    print(f"'Sayfa Görüntüleme' -> '{get_api_name_from_tr('Sayfa Görüntüleme')}'")

    # Weight testleri
    print("\n" + "=" * 60)
    print("WEIGHT TABANLI FONKSİYONLAR - TEST")
    print("=" * 60)

    print("\n--- Weight Dağılımı Özeti ---")
    summary = get_weight_summary()
    print("Dimension Weight Dağılımı:")
    for w in range(10, 0, -1):
        count = summary["dimensions"][w]
        if count > 0:
            print(f"  Weight {w}: {count} adet")

    print("\nMetric Weight Dağılımı:")
    for w in range(10, 0, -1):
        count = summary["metrics"][w]
        if count > 0:
            print(f"  Weight {w}: {count} adet")

    print("\n--- En Önemli Dimensionlar (weight >= 9) ---")
    top_dims = get_top_dimensions(min_weight=9, limit=10)
    for dim in top_dims:
        print(f"  [{dim.get('weight')}] {dim['api_name']} - {dim['tr_name']}")

    print("\n--- En Önemli Metrikler (weight >= 9) ---")
    top_metrics = get_top_metrics(min_weight=9, limit=10)
    for m in top_metrics:
        print(f"  [{m.get('weight')}] {m['api_name']} - {m['tr_name']}")

    print("\n--- İçerik Analizi için Öneriler ---")
    content_rec = get_recommended_for_analysis("content")
    print(f"Açıklama: {content_rec['description']}")
    print(f"Dimensions: {', '.join(content_rec['dimensions'])}")
    print(f"Metrics: {', '.join(content_rec['metrics'])}")