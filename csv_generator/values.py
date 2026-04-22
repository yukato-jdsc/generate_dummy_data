from __future__ import annotations

import random
from datetime import date, datetime

from faker import Faker

from .config import COMPANY_WORDS


def clip(value: str, max_length: int | None) -> str:
    """文字列を列定義の最大長に収める。"""
    if max_length is None:
        return value
    return value[:max_length]


def ymd(value: date) -> str:
    """日付を `YYYY/MM/DD` 形式へ変換する。"""
    return value.strftime("%Y/%m/%d")


def hms(hour: int, minute: int, second: int = 0) -> str:
    """時刻要素を `HH:MM:SS` 形式へ変換する。"""
    return f"{hour:02d}:{minute:02d}:{second:02d}"


def ymd_dash(value: date) -> str:
    """日付を `YYYY-MM-DD` 形式へ変換する。"""
    return value.strftime("%Y-%m-%d")


def ymdhms_millis(value: datetime) -> str:
    """日時をミリ秒付き `YYYY-MM-DDTHH:MM:SS.mmm` 形式へ変換する。"""
    return value.strftime("%Y-%m-%dT%H:%M:%S.") + f"{value.microsecond // 1000:03d}"


def ymdhm(value: datetime) -> str:
    """日時を分単位の `YYYY/MM/DD HH:MM` 形式へ変換する。"""
    return value.strftime("%Y/%m/%d %H:%M")


class ValueFactory:
    """ダミーデータ生成で再利用する文字列・コード・名称の共通生成器。"""

    def __init__(self, seed: int) -> None:
        self.random = random.Random(seed)
        self.faker = Faker("ja_JP")
        self.faker.seed_instance(seed)

    def number_string(self, width: int, number: int) -> str:
        """数値を固定長のゼロ埋め文字列へ変換する。"""
        return f"{number:0{width}d}"[-width:]

    def code(self, prefix: str, number: int, width: int = 8) -> str:
        """接頭辞付きの業務コード風文字列を生成する。"""
        return f"{prefix}{self.number_string(width, number)}"

    def sequential_id(self, index: int) -> str:
        """数値連番の `id` を1始まりの文字列で返す。"""
        return str(index + 1)

    def compass_id(self, index: int) -> str:
        """営業決裁CSV向けの業務コード風 `id` を返す。"""
        return self.code("CM", index + 1, 10)

    def katakana_word(self, index: int) -> str:
        words = ["ソフト", "モバイル", "リンク", "プラン", "サービス", "ネット", "ビジネス", "テック"]
        return words[index % len(words)]

    def english_word(self, index: int) -> str:
        words = ["Mobile", "Business", "Cloud", "Link", "Smart", "Edge", "Network", "Store"]
        return words[index % len(words)]

    def company_name(self, index: int) -> str:
        return f"株式会社{self.katakana_word(index)}{COMPANY_WORDS[index % len(COMPANY_WORDS)]}"

    def company_short_name(self, index: int) -> str:
        return f"{self.katakana_word(index)}{COMPANY_WORDS[index % len(COMPANY_WORDS)]}"

    def person_name(self) -> str:
        """日本語の氏名をスペースなしで返す。"""
        return self.faker.name().replace(" ", "")

    def person_name_kana(self, index: int) -> str:
        names = ["サトウタロウ", "スズキハナコ", "タナカイチロウ", "イノウエミホ", "ヤマモトケン"]
        return names[index % len(names)]

    def phone(self, area: str, number: int) -> str:
        """市外局番を考慮した電話番号風文字列を生成する。"""
        suffix = self.number_string(8, number)
        return f"{area}-{suffix[:4]}-{suffix[4:]}"

    def postal_code(self, number: int) -> str:
        """郵便番号風の文字列を生成する。"""
        digits = self.number_string(7, number)
        return f"{digits[:3]}-{digits[3:]}"

    def decimal_value(self, index: int, modulo: int = 9, minimum: int = 0) -> str:
        """DECIMAL列向けの簡易な数値文字列を返す。"""
        return str(minimum + (index % modulo))

    def bool_flag(self, index: int, true_every: int = 2) -> str:
        """一定周期で `t` と `f` を返す。"""
        return "t" if index % true_every == 0 else "f"

    def employee_id(self, index: int) -> str:
        """営業担当者向けの社員番号風文字列を返す。"""
        return self.number_string(7, 1_100_000 + index)

    def email(self, index: int) -> str:
        """共有用メールアドレス向けの文字列を返す。"""
        return f"shared{index % 1000:03d}@example.jp"
