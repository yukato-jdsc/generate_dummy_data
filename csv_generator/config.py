from __future__ import annotations

from dataclasses import dataclass
from datetime import date


DEFAULT_SEED = 42
DEFAULT_COUNTS = {
    "campaign": 50,
    "agency_all": 1_000,
    "agency_diff": 53,
    "compass": 100,
    "product": 1_000,
    "bfs_all": 1_000,
    "bfs_diff": 100,
}
FULL_COUNTS = {
    "campaign": 1_612,
    "agency_all": 1_200_000,
    "agency_diff": 53,
    "compass": 160_000,
    "product": 122_802,
    "bfs_all": 2_000_000,
    "bfs_diff": 5_921,
}
SECTION_KEYS = {
    "(Mars)キャンペーン": "campaign",
    "(Mars)取次店": "agency",
    "(COMPASS)営業決裁": "compass",
    "(Mars)商品": "product",
    "(BFSエントリ)モバイル_エントリ情報": "bfs",
}
OUTPUT_FILES = {
    "campaign": "m_campaign_all.csv",
    "agency_all": "m_agency_all.csv",
    "agency_diff": "m_agency_diff.csv",
    "compass": "compass_sales_approval.csv",
    "product": "m_product_all.csv",
    "bfs_all": "bfs_entry_informations_all.csv",
    "bfs_diff": "bfs_entry_informations_diff.csv",
}
VALID_TARGETS = {"campaign", "agency", "compass", "product", "bfs"}
BASE_DATE = date(2026, 4, 21)
@dataclass(frozen=True)
class ColumnSpec:
    name: str
    header_label: str
    data_type: str
    max_length: int | None


PREFECTURES = [
    {
        "prefecture_code": "01",
        "prefecture_kanji": "北海道",
        "prefecture_kana": "ホッカイドウ",
        "area_code": "01",
        "area_official_name": "北海道",
        "area_english_code": "HK",
        "area_half_width_kana_name": "ﾎｯｶｲﾄﾞｳ",
        "area_english_name": "Hokkaido",
        "city_code": "01101",
        "city_kanji": "札幌市中央区",
        "city_kana": "サッポロシチュウオウク",
        "common_name_code": "011",
        "common_name_kanji": "大通",
        "common_name_kana": "オオドオリ",
        "chome_code": "001",
        "chome_kanji": "1丁目",
        "chome_kana": "イッチョウメ",
        "phone_area": "011",
    },
    {
        "prefecture_code": "04",
        "prefecture_kanji": "宮城県",
        "prefecture_kana": "ミヤギケン",
        "area_code": "02",
        "area_official_name": "東北",
        "area_english_code": "TH",
        "area_half_width_kana_name": "ﾄｳﾎｸ",
        "area_english_name": "Tohoku",
        "city_code": "04101",
        "city_kanji": "仙台市青葉区",
        "city_kana": "センダイシアオバク",
        "common_name_code": "041",
        "common_name_kanji": "一番町",
        "common_name_kana": "イチバンチョウ",
        "chome_code": "002",
        "chome_kanji": "2丁目",
        "chome_kana": "ニチョウメ",
        "phone_area": "022",
    },
    {
        "prefecture_code": "13",
        "prefecture_kanji": "東京都",
        "prefecture_kana": "トウキョウト",
        "area_code": "03",
        "area_official_name": "関東",
        "area_english_code": "KT",
        "area_half_width_kana_name": "ｶﾝﾄｳ",
        "area_english_name": "Kanto",
        "city_code": "13101",
        "city_kanji": "千代田区",
        "city_kana": "チヨダク",
        "common_name_code": "131",
        "common_name_kanji": "丸の内",
        "common_name_kana": "マルノウチ",
        "chome_code": "003",
        "chome_kanji": "3丁目",
        "chome_kana": "サンチョウメ",
        "phone_area": "03",
    },
    {
        "prefecture_code": "23",
        "prefecture_kanji": "愛知県",
        "prefecture_kana": "アイチケン",
        "area_code": "04",
        "area_official_name": "中部",
        "area_english_code": "CB",
        "area_half_width_kana_name": "ﾁｭｳﾌﾞ",
        "area_english_name": "Chubu",
        "city_code": "23101",
        "city_kanji": "名古屋市中区",
        "city_kana": "ナゴヤシナカク",
        "common_name_code": "231",
        "common_name_kanji": "栄",
        "common_name_kana": "サカエ",
        "chome_code": "004",
        "chome_kanji": "4丁目",
        "chome_kana": "ヨンチョウメ",
        "phone_area": "052",
    },
    {
        "prefecture_code": "27",
        "prefecture_kanji": "大阪府",
        "prefecture_kana": "オオサカフ",
        "area_code": "05",
        "area_official_name": "関西",
        "area_english_code": "KS",
        "area_half_width_kana_name": "ｶﾝｻｲ",
        "area_english_name": "Kansai",
        "city_code": "27127",
        "city_kanji": "大阪市北区",
        "city_kana": "オオサカシキタク",
        "common_name_code": "271",
        "common_name_kanji": "梅田",
        "common_name_kana": "ウメダ",
        "chome_code": "005",
        "chome_kanji": "5丁目",
        "chome_kana": "ゴチョウメ",
        "phone_area": "06",
    },
    {
        "prefecture_code": "34",
        "prefecture_kanji": "広島県",
        "prefecture_kana": "ヒロシマケン",
        "area_code": "06",
        "area_official_name": "中国",
        "area_english_code": "CG",
        "area_half_width_kana_name": "ﾁｭｳｺﾞｸ",
        "area_english_name": "Chugoku",
        "city_code": "34101",
        "city_kanji": "広島市中区",
        "city_kana": "ヒロシマシナカク",
        "common_name_code": "341",
        "common_name_kanji": "紙屋町",
        "common_name_kana": "カミヤチョウ",
        "chome_code": "006",
        "chome_kanji": "6丁目",
        "chome_kana": "ロクチョウメ",
        "phone_area": "082",
    },
    {
        "prefecture_code": "40",
        "prefecture_kanji": "福岡県",
        "prefecture_kana": "フクオカケン",
        "area_code": "07",
        "area_official_name": "九州",
        "area_english_code": "KY",
        "area_half_width_kana_name": "ｷｭｳｼｭｳ",
        "area_english_name": "Kyushu",
        "city_code": "40131",
        "city_kanji": "福岡市中央区",
        "city_kana": "フクオカシチュウオウク",
        "common_name_code": "401",
        "common_name_kanji": "天神",
        "common_name_kana": "テンジン",
        "chome_code": "007",
        "chome_kanji": "7丁目",
        "chome_kana": "ナナチョウメ",
        "phone_area": "092",
    },
]
COMPANY_WORDS = [
    "ソリューションズ",
    "商事",
    "通信",
    "ネットワーク",
    "情報システム",
    "データサービス",
    "モバイル",
    "テクノロジー",
    "カンパニー",
]
DEPARTMENTS = [
    "営業本部",
    "販売推進部",
    "法人営業部",
    "運営管理部",
    "店舗支援部",
    "業務企画部",
]
POSITIONS = ["部長", "課長", "主任", "担当", "マネージャー"]
CAMPAIGN_PREFIXES = [
    "春の",
    "法人向け",
    "新規契約",
    "端末更新",
    "回線増設",
    "年度末",
    "地域限定",
]
CAMPAIGN_SUFFIXES = [
    "応援キャンペーン",
    "優待施策",
    "割引プログラム",
    "導入支援",
    "更新特典",
]
PRODUCT_TEMPLATES = [
    ("スマートフォン", "SB Phone", "端末", "モバイル", "スマートフォン", "64GB", 72800),
    ("タブレット", "SB Tab", "端末", "モバイル", "タブレット", "128GB", 65800),
    ("モバイルルーター", "SB Air", "通信機器", "データ", "ルーター", "32GB", 19800),
    ("SIMカード", "SB SIM", "SIM", "回線", "SIM", "0GB", 3980),
    ("アクセサリ", "SB Accessory", "付属品", "物販", "アクセサリ", "N/A", 4800),
]
COMPASS_STATUSES = ["承認", "申請中", "差戻し", "再申請", "却下"]
COMPASS_APPROVAL_TYPES = [
    "提案・契約決裁(代理店協業含む)",
    "料金調整・現金返還・料金減免",
    "代理店契約",
    "再販契約",
]
COMPASS_SERVICE_TYPES = [
    "【モバイル】 その他サービス（モバイル）",
    "【モバイル】 データ通信",
    "【共通】 値引き・減免",
]
COMPASS_SALES_CHANNELS = ["直販", "代理店", "パートナー"]
COMPASS_CORP_KINDS = ["法人サービス", "個人", "官公庁"]
COMPASS_BILLING_FORMS = ["直請求", "代理店請求", "請求代行"]
COMPASS_APPROVER_LAYERS = ["部長承認", "統括承認", "本部長承認"]
COLORS = [
    ("ブラック", "BLK"),
    ("ホワイト", "WHT"),
    ("ネイビー", "NVY"),
    ("シルバー", "SLV"),
]
COMPANY_CATEGORY_NAMES = ["直販", "一次代理店", "二次代理店"]
OPERATION_PERMISSION_NAMES = ["閲覧", "編集", "管理"]
