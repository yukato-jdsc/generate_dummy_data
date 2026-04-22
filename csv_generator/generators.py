from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

from .config import (
    AGENCY_ALL_KEEP_COLUMNS,
    BASE_DATE,
    BFS_KEEP_COLUMNS,
    CAMPAIGN_PREFIXES,
    CAMPAIGN_SUFFIXES,
    COLORS,
    COMPASS_APPROVAL_TYPES,
    COMPASS_APPROVER_LAYERS,
    COMPASS_BILLING_FORMS,
    COMPASS_CORP_KINDS,
    COMPASS_SALES_CHANNELS,
    COMPASS_SERVICE_TYPES,
    COMPANY_CATEGORY_NAMES,
    DEPARTMENTS,
    OPERATION_PERMISSION_NAMES,
    OUTPUT_FILES,
    POSITIONS,
    PREFECTURES,
    PRODUCT_TEMPLATES,
    ColumnSpec,
)
from .io import open_csv_writer, write_csv
from .size_control import RowSizeAdjuster, build_row_size_profile, target_row_size_bytes
from .values import ValueFactory, clip, hms, ymd, ymd_dash, ymdhm, ymdhms_millis


class CsvGenerator:
    """各CSVの行データを生成し、必要に応じてファイルへ出力する。"""

    def __init__(self, specs: dict[str, list[ColumnSpec]], seed: int, counts: dict[str, int]) -> None:
        self.specs = specs
        self.seed = seed
        self.counts = counts
        self.values = ValueFactory(seed)
        self.diff_sample_size = counts["agency_diff"]
        self.row_adjusters = self._build_row_adjusters()

    def _build_row_adjusters(self) -> dict[str, RowSizeAdjuster]:
        """出力種別ごとのサイズ調整器を初期化する。"""
        return {
            "campaign": self._build_row_adjuster("campaign", "campaign", {"id"}),
            "agency_all": self._build_row_adjuster("agency_all", "agency", AGENCY_ALL_KEEP_COLUMNS),
            "agency_diff": self._build_row_adjuster("agency_diff", "agency", {"id", "agent_code"}),
            "compass": self._build_row_adjuster("compass", "compass", {"id"}),
            "product": self._build_row_adjuster("product", "product", {"id"}),
            "bfs_all": self._build_row_adjuster("bfs_all", "bfs", BFS_KEEP_COLUMNS),
            "bfs_diff": self._build_row_adjuster("bfs_diff", "bfs", BFS_KEEP_COLUMNS),
        }

    def _build_row_adjuster(
        self,
        output_key: str,
        spec_key: str,
        keep_columns: set[str] | None = None,
    ) -> RowSizeAdjuster:
        """単一CSV向けのサイズ調整器を構築する。"""
        columns = self.specs[spec_key]
        return RowSizeAdjuster(
            columns,
            target_row_size_bytes(columns, output_key, self.counts[output_key]),
            build_row_size_profile(columns, output_key, keep_columns=keep_columns),
        )

    def campaign_rows(self) -> list[list[str]]:
        """キャンペーンCSVの全行をメモリ上で生成する。"""
        rows = []
        for index in range(self.counts["campaign"]):
            start = BASE_DATE - timedelta(days=index % 180)
            end = start + timedelta(days=90 + (index % 180))
            name = self._campaign_name(index)
            context = {
                "id": self.values.sequential_id(index),
                "campaign_id": self.values.code("CP", index + 1, 10),
                "campaign_name": name,
                "description": f"{name}のテスト投入用データ",
                "effective_start_date": ymd(start),
                "effective_end_date": ymd(end),
                "old_flag": "" if index % 5 else "1",
            }
            rows.append(self._fit_row("campaign", self._row_from_context(self.specs["campaign"], context)))
        return rows

    def _campaign_name(self, index: int) -> str:
        """キャンペーン名テンプレートをインデックスから組み立てる。"""
        return f"{CAMPAIGN_PREFIXES[index % len(CAMPAIGN_PREFIXES)]}{CAMPAIGN_SUFFIXES[index % len(CAMPAIGN_SUFFIXES)]}"

    def write_agency_files(self, output_dir: Path) -> None:
        """取次店の全量CSVと差分CSVを同時に出力する。"""
        headers = self._header_labels("agency")
        sampled: list[tuple[int, dict[str, str]]] = []
        sampler = random.Random(self.seed)
        handle, writer = open_csv_writer(output_dir / OUTPUT_FILES["agency_all"])
        try:
            writer.writerow(headers)
            for index in range(self.counts["agency_all"]):
                context = self.agency_context(index)
                writer.writerow(self._fit_row("agency_all", self._agency_row(context, index)))
                self._update_reservoir(sampled, (index, context), index, sampler)
        finally:
            handle.close()
        sampled.sort(key=lambda item: item[1]["agent_code"])
        diff_rows = [
            self._fit_row("agency_diff", self._agency_row(context, index))
            for index, context in sampled
        ]
        write_csv(output_dir / OUTPUT_FILES["agency_diff"], headers, diff_rows)

    def _header_labels(self, spec_key: str) -> list[str]:
        """指定した仕様キーのヘッダー表示名一覧を返す。"""
        return [column.header_label for column in self.specs[spec_key]]

    def write_compass_file(self, output_dir: Path) -> None:
        """営業決裁CSVを逐次書き出しする。"""
        headers = self._header_labels("compass")
        handle, writer = open_csv_writer(output_dir / OUTPUT_FILES["compass"])
        try:
            writer.writerow(headers)
            for index in range(self.counts["compass"]):
                writer.writerow(self._fit_row("compass", self._compass_row(self._compass_context(index), index)))
        finally:
            handle.close()

    def _update_reservoir(
        self,
        sampled: list[tuple[int, dict[str, str]]],
        row: tuple[int, dict[str, str]],
        index: int,
        sampler: random.Random,
    ) -> None:
        """差分CSV用に、全量行から固定件数をリザーバサンプリングする。"""
        if len(sampled) < self.diff_sample_size:
            sampled.append(row)
            return
        choice = sampler.randint(0, index)
        if choice < self.diff_sample_size:
            sampled[choice] = row

    def agency_context(self, index: int) -> dict[str, str]:
        """取次店1行ぶんの文脈を組み立てる。"""
        context = {}
        context.update(self._agency_base_context(index))
        context.update(self._agency_category_context(index))
        context.update(self._agency_address_context(index))
        context.update(self._agency_contact_context(index))
        context.update(self._agency_organization_context(index))
        context.update(self._agency_operation_context(index))
        context.update(self._agency_billing_context(index))
        context.update(self._agency_misc_context(index))
        return context

    def agency_row(self, index: int) -> list[str]:
        """取次店1行ぶんを全量CSV向けのサイズで生成する。"""
        context = self.agency_context(index)
        return self._fit_row("agency_all", self._agency_row(context, index))

    def _agency_base_context(self, index: int) -> dict[str, str]:
        """取次店の識別子・有効期間などの基本属性を生成する。"""
        start = BASE_DATE - timedelta(days=index % 720)
        end = start + timedelta(days=365 if index % 9 else 180)
        primary_index = (index // 10) + 1
        aggregated_index = (index // 5) + 1
        return {
            "id": self.values.sequential_id(index),
            "agent_code": self.values.code("AG", index + 1, 10),
            "valid_start_date": ymd(start),
            "valid_end_date": ymd(end),
            "common_store_code": self.values.code("ST", index + 1, 8),
            "chkdigit_common_store_cd": self.values.code("9", index + 1, 10),
            "logistics_agent_code": self.values.code("LG", index + 1, 8),
            "chkdigit_agent_cd": self.values.code("8", index + 1, 10),
            "front_desk_code": self.values.code("FD", index + 1, 8),
            "primary_agent_code": self.values.code("PA", primary_index, 8),
            "chkdigit_primary_agent_cd": self.values.code("7", primary_index, 10),
            "aggregated_primary_agent_code": self.values.code("AP", primary_index, 8),
            "chkdigit_collected_primary_agent_cd": self.values.code("6", primary_index, 10),
            "aggregated_agent_code": self.values.code("AA", aggregated_index, 8),
            "chkdigit_aggregated_agent_cd": self.values.code("5", aggregated_index, 10),
            "store_unique_code": self.values.code("SU", index + 1, 12),
            "operating_store_corporate_code": self.values.code("OC", (index // 7) + 1, 10),
            "business_start_date": ymd(start - timedelta(days=30)),
            "business_end_date": ymd(end),
            "backup_date": ymd(BASE_DATE),
        }

    def _agency_category_context(self, index: int) -> dict[str, str]:
        """取次店の分類・権限・区分系の属性を生成する。"""
        company_category = str((index % 3) + 1)
        operation_permission = str((index % 3) + 1)
        direct_flag = str(index % 2)
        return {
            "company_category": company_category,
            "company_category_official_name": COMPANY_CATEGORY_NAMES[int(company_category) - 1],
            "store_type_code": str((index % 4) + 1),
            "store_registration_settings_ptn_cd": str((index % 3) + 1),
            "agency_small_category_id": str((index % 10) + 1),
            "order_to_order_small_category_code": self.values.code("OS", (index % 12) + 1, 4),
            "order_to_order_medium_category_id": str((index % 8) + 1),
            "order_to_order_small_category_full_name": "法人販売",
            "order_to_order_small_category_half_width_kn": "ﾎｳｼﾞﾝﾊﾝﾊﾞｲ",
            "order_to_order_small_category_english_name": "Corporate Sales",
            "order_to_order_medium_category_code": self.values.code("OM", (index % 8) + 1, 2),
            "order_to_order_large_category_id": str((index % 5) + 1),
            "order_to_order_medium_category_full_name": "営業店",
            "order_to_order_medium_category_half_width_kn": "ｴｲｷﾞｮｳﾃﾝ",
            "order_to_order_medium_category_english_name": "Sales Office",
            "order_to_order_large_category_code": self.values.code("OL", (index % 5) + 1, 2),
            "order_to_order_large_category_full_name": "代理店",
            "order_to_order_large_category_half_width_kn": "ﾀﾞｲﾘﾃﾝ",
            "order_to_order_large_category_english_name": "Agency",
            "wholesale_channel": str((index % 4) + 1),
            "corporate_channel": str((index % 3) + 1),
            "direct_store_determination_flg": direct_flag,
            "direct_store_determination_flg_nm": "直営" if direct_flag == "1" else "代理店",
            "ginie_permission_code": str((index % 4) + 1),
            "ginie_permission_code_nm": "一般",
            "operation_permission": operation_permission,
            "operation_permission_official_name": OPERATION_PERMISSION_NAMES[int(operation_permission) - 1],
            "commission_calculation_category": str((index % 4) + 1),
            "commission_calculation_category_nm": "標準計算",
            "corporate_dealer_type": str((index % 3) + 1),
            "corporate_dealer_type_nm": "法人取扱店",
            "service_fee_payment_ptn": str((index % 3) + 1),
            "service_fee_payment_ptn_nm": "月次支払",
            "maintenance_agency_category": str((index % 2) + 1),
            "maintenance_agency_category_nm": "通常保守",
            "not_eligible_for_recurring_fee_kbn": str(index % 2),
            "not_eligible_for_recurring_fee_kbn_nm": "対象外" if index % 2 else "対象",
            "partial_delivery_category": str((index % 2) + 1),
            "partial_delivery_category__official_name_": "分割あり" if index % 2 else "分割なし",
            "performance_management_category": str((index % 2) + 1),
            "performance_management_category__official_name_": "管理対象",
            "goal_management_category": str((index % 2) + 1),
            "goal_management_category__official_name_": "目標管理対象",
            "statistical_shop_category": str((index % 2) + 1),
            "statistical_shop_category_nm": "集計対象",
            "arpu_manager_category": str((index % 3) + 1),
            "mvno_category": str((index % 3) + 1),
            "mvno_category_official_name": "標準MVNO",
            "mvno_attribute": str((index % 2) + 1),
            "mvno_attribute_official_name": "通常属性",
        }

    def _agency_address_context(self, index: int) -> dict[str, str]:
        """都道府県や住所関連の属性を生成する。"""
        pref = PREFECTURES[index % len(PREFECTURES)]
        return {
            **pref,
            "agent_postal_code": self.values.postal_code(1000000 + index),
            "additional_address": f"{pref['chome_kanji']}{(index % 9) + 1}番地",
            "okinawa_category": "1" if pref["prefecture_kanji"] == "沖縄県" else "0",
            "okinawa_category_official_name": "沖縄" if pref["prefecture_kanji"] == "沖縄県" else "本土",
            "old_region_code": self.values.code("OR", (index % 12) + 1, 4),
        }

    def _agency_contact_context(self, index: int) -> dict[str, str]:
        """名称・担当者・電話番号などの連絡先系属性を生成する。"""
        pref = PREFECTURES[index % len(PREFECTURES)]
        company_name = self.values.company_name(index)
        company_short = self.values.company_short_name(index)
        person_name_kana = self.values.person_name_kana(index)
        return {
            "aggregator_official_name": company_name,
            "aggregator_abbreviation": clip(company_short, 20),
            "aggregator_name_katakana": person_name_kana + self.values.katakana_word(index),
            "aggregator_store_name_in_english": f"{self.values.english_word(index)} {self.values.english_word(index + 1)}",
            "registered_corporate_name": company_name,
            "representative_name": self.values.person_name(),
            "department_name_of_person_in_charge": DEPARTMENTS[index % len(DEPARTMENTS)],
            "name_of_person_in_charge": self.values.person_name(),
            "position_of_person_in_charge": POSITIONS[index % len(POSITIONS)],
            "agent_tel_no": self.values.phone(pref["phone_area"], 10000000 + index),
            "agent_fax_no": self.values.phone(pref["phone_area"], 20000000 + index),
            "registration_business_tel_no": self.values.phone(pref["phone_area"], 30000000 + index),
            "registration_business_tel_no_2": self.values.phone(pref["phone_area"], 40000000 + index),
            "registration_business_fax_no": self.values.phone(pref["phone_area"], 50000000 + index),
            "broadcast_fax_no": self.values.phone(pref["phone_area"], 60000000 + index),
            "shop_name__kana_": self.values.katakana_word(index) + "ショップ",
            "corporate_name": company_name,
            "manager_name": self.values.person_name(),
            "corporate_my_number": self.values.number_string(13, 10_000_000_000 + index),
        }

    def _agency_organization_context(self, index: int) -> dict[str, str]:
        """組織・実績集計・ルート系の属性を生成する。"""
        pref = PREFECTURES[index % len(PREFECTURES)]
        start = BASE_DATE - timedelta(days=index % 720)
        end = start + timedelta(days=365 if index % 9 else 180)
        return {
            "registered_business_department_code": self.values.code("BD", (index % 50) + 1, 6),
            "organization_id__right_1_digit_": str(index % 10),
            "organization_name": f"{pref['prefecture_kanji']}{DEPARTMENTS[index % len(DEPARTMENTS)]}",
            "hierarchy": str((index % 4) + 1),
            "supervisor_organization_code": self.values.code("SO", (index % 80) + 1, 8),
            "supervisor_organization_code__right_1_digit_": str((index + 1) % 10),
            "manager_employee_number": self.values.code("EM", index + 1, 10),
            "approval_form_number": self.values.code("APV", index + 1, 8),
            "commission_calculation_end_date": ymd(end),
            "shop_outsourcing_dt": ymd(start - timedelta(days=5)),
            "order_start_date": ymd(start),
            "order_stop_date": ymd(end - timedelta(days=30)),
            "route_code": self.values.code("RT", (index % 20) + 1, 4),
            "route_code__official_name_": "標準ルート",
            "performance_computing_department_code": self.values.code("PD", (index % 20) + 1, 6),
            "performance_computing_department_code_nm": "実績集計部門",
            "performance_computing_staff_code": self.values.code("PS", (index % 200) + 1, 6),
            "performance_computing_channel_cd": self.values.code("PC", (index % 10) + 1, 4),
            "performance_computing_channel_l_cd_nm": "法人チャネル",
            "channel_code": self.values.code("CH", (index % 10) + 1, 4),
            "channel_code_nm": "直販",
            "allocation_department_code": self.values.code("AD", (index % 20) + 1, 6),
            "allocation_code": self.values.code("AL", (index % 30) + 1, 4),
            "allocation_official_name": "標準割当",
            "arpu_headquarters": self.values.code("HQ", (index % 8) + 1, 2),
        }

    def _agency_operation_context(self, index: int) -> dict[str, str]:
        """WMSや通知フラグなど運用系の属性を生成する。"""
        return {
            "wms_packing_slip_format": str((index % 3) + 1),
            "wms_packing_slip_format_nm": "標準",
            "wms_main_slip_format": str((index % 3) + 1),
            "wms_main_invoice_format_nm": "標準",
            "wms_main_invoice_amount_printing_flg": str(index % 2),
            "wms_main_invoice_amount_printing_flg_nm": "印字あり" if index % 2 else "印字なし",
            "wms_main_transmission_destination_flg": str(index % 2),
            "wms_main_transmission_destination_flg_nm": "店舗" if index % 2 else "本部",
            "application_form_original_collection_notification": str(index % 2),
            "application_form_original_collection_notification_nm": "通知あり" if index % 2 else "通知なし",
            "application_form_original_not_collected_lst": str(index % 2),
            "application_form_original_not_collected_lst_nm": "対象あり" if index % 2 else "対象なし",
            "application_form_original_return_address": str(index % 2),
            "application_form_original_return_address_nm": "店舗" if index % 2 else "本部",
            "store_performance_report_sending_address": str(index % 2),
            "store_performance_report_sending_address_nm": "本部" if index % 2 else "店舗",
            "promotional_item_shipping_flag": str(index % 2),
            "promotional_item_shipping_flag_nm": "出荷あり" if index % 2 else "出荷なし",
        }

    def _agency_billing_context(self, index: int) -> dict[str, str]:
        """請求・運営店・グループ管理系の属性を生成する。"""
        return {
            "cd_for_recipient_sys": self.values.code("RC", index + 1, 8),
            "company_cd_for_recipient_sys": self.values.code("CC", (index // 3) + 1, 8),
            "pre_business_transfer_agent_cd": self.values.code("PB", max(1, index), 8),
            "chkdigit_pre_business_transfer_agent_cd": self.values.code("4", max(1, index), 10),
            "step_primary_distributor_code": self.values.code("SP", (index // 10) + 1, 8),
            "willcom_code": self.values.code("WC", index + 1, 8),
            "jenesys_primary_distributor_cd": self.values.code("JP", (index // 10) + 1, 8),
            "eaccess_code": self.values.code("EA", index + 1, 8),
            "billing_flag": str(index % 2),
            "operating_store_flag": str((index + 1) % 2),
            "operating_store_code": self.values.code("OP", (index // 6) + 1, 8),
            "chkdigit_operating_store_cd": self.values.code("3", (index // 6) + 1, 10),
            "affiliated_store_survey_approval_number": self.values.code("SV", index + 1, 8),
            "billing_payment_summary_flag": str(index % 2),
            "billing_payment_summary_code": self.values.code("BP", (index // 4) + 1, 8),
            "chkdigit_billing_payment_summary_cd": self.values.code("2", (index // 4) + 1, 10),
            "shop_classification_code": self.values.code("SC", (index % 10) + 1, 4),
            "logistics_channel_cd": self.values.code("LC", (index % 6) + 1, 2),
            "sub_store_owner_flag": str(index % 2),
            "store_owner_code": self.values.code("OW", (index // 3) + 1, 8),
            "chkdigit_store_owner_cd": self.values.code("1", (index // 3) + 1, 10),
            "group_management_flag": str(index % 2),
            "group_master_code": self.values.code("GM", (index // 12) + 1, 8),
        }

    def _agency_misc_context(self, index: int) -> dict[str, str]:
        """他の文脈に属しづらい補助属性を生成する。"""
        return {
            "sales_statistics_summary_key": self.values.code("SS", index + 1, 10),
        }

    def resolve_agency_value(self, column: ColumnSpec, context: dict[str, str], index: int) -> str:
        """明示値が無い列に対し、列名規則から妥当な既定値を補完する。"""
        if column.name in context:
            return context[column.name]
        name = column.name
        if column.data_type.startswith("DECIMAL"):
            return self.values.decimal_value(index, modulo=9, minimum=1)
        if name.endswith("_date") or name.endswith("_dt"):
            return ymd(BASE_DATE - timedelta(days=index % 365))
        if name.endswith("_time"):
            return hms((index * 3) % 24, (index * 7) % 60)
        if "tel_no" in name or "fax_no" in name:
            pref = PREFECTURES[index % len(PREFECTURES)]
            return self.values.phone(pref["phone_area"], 70000000 + index)
        if "postal_code" in name:
            return self.values.postal_code(2000000 + index)
        if "english" in name:
            return f"{self.values.english_word(index)} {self.values.english_word(index + 1)}"
        if "kana" in name or "kn" in name:
            return self.values.katakana_word(index) + self.values.katakana_word(index + 1)
        if name.endswith("_name") or "official_name" in name or name.endswith("_nm") or "kanji" in name:
            return f"サンプル{index % 50:02d}"
        if "code" in name or name.endswith("_cd") or name.endswith("_id") or name.endswith("_number"):
            return self.values.code("X", index + 1, 8)
        return f"VAL{index % 1000}"

    def product_rows(self) -> list[list[str]]:
        """商品CSVの全行をメモリ上で生成する。"""
        rows = []
        for index in range(self.counts["product"]):
            context = self._product_context(index)
            rows.append(self._fit_row("product", self._product_row(context, index)))
        return rows

    def compass_rows(self) -> list[list[str]]:
        """営業決裁CSVの全行をメモリ上で生成する。"""
        rows = []
        for index in range(self.counts["compass"]):
            rows.append(self._fit_row("compass", self._compass_row(self._compass_context(index), index)))
        return rows

    def _product_row(self, context: dict[str, str], index: int) -> list[str]:
        """商品文脈を列順の行へ変換する。"""
        return [clip(self.resolve_product_value(column, context, index), column.max_length) for column in self.specs["product"]]

    def _agency_row(self, context: dict[str, str], index: int) -> list[str]:
        """取次店文脈を列順の行へ変換する。"""
        return [clip(self.resolve_agency_value(column, context, index), column.max_length) for column in self.specs["agency"]]

    def _compass_row(self, context: dict[str, str], index: int) -> list[str]:
        """営業決裁文脈を列順の行へ変換する。"""
        return [clip(self.resolve_compass_value(column, context, index), column.max_length) for column in self.specs["compass"]]

    def _compass_context(self, index: int) -> dict[str, str]:
        """営業決裁1行ぶんの主要属性を組み立てる。"""
        created_at = datetime(2025, 1, 1, 9, 0, 0) + timedelta(hours=index * 7)
        approval_at = created_at + timedelta(days=(index % 5) + 1, minutes=30)
        execution_date = BASE_DATE + timedelta(days=index % 90)
        expiration_date = execution_date + timedelta(days=180)
        company_name = self.values.company_name(index)
        person_name = self.values.person_name()
        contact_name = self.values.person_name()
        approval_number = f"LS{1_000_000 + index:07d}"
        project_name = f"{company_name}向けモバイル提案{index % 50 + 1}"
        line_count = 10 + (index % 120)
        sales_amount = 500_000 + (index % 500) * 25_000
        contribution = int(sales_amount * 0.18)
        operating_profit = int(sales_amount * 0.12)
        incentive = int(sales_amount * 0.03)
        agency_code = self.values.code("AG", (index % 5000) + 1, 10)
        shared_email_1 = self.values.email(index)
        shared_email_2 = self.values.email(index + 1)
        shared_email_3 = self.values.email(index + 2)
        project_summary = (
            f"案件名: {project_name}\n"
            f"提案回線数: {line_count}回線\n"
            f"希望開始日: {ymd_dash(execution_date)}\n"
            f"提案条件: 法人向け標準プランをベースに個別調整を実施"
        )
        return {
            "id": self.values.compass_id(index),
            "approval_number": approval_number,
            "approval_subject": f"{company_name}向け営業決裁 {index % 30 + 1}",
            "status": "承認",
            "date_and_time_of_application": ymdhms_millis(created_at),
            "approval_type": COMPASS_APPROVAL_TYPES[index % len(COMPASS_APPROVAL_TYPES)],
            "mobile_type": self.values.bool_flag(index, 2),
            "voice_type": self.values.bool_flag(index + 1, 5),
            "voice_otoku_hikari_type": self.values.bool_flag(index + 2, 9),
            "id_data_type": self.values.bool_flag(index + 3, 4),
            "is_ni_product_type": self.values.bool_flag(index + 4, 6),
            "phs_type": "f",
            "common_discounts_etc": self.values.bool_flag(index + 5, 3),
            "common_corporate_consolidated_billing": self.values.bool_flag(index + 6, 4),
            "common_test_lines": self.values.bool_flag(index + 7, 8),
            "mobile_approval_pattern_a": self.values.bool_flag(index + 8, 2),
            "mobile_approval_pattern_c": self.values.bool_flag(index + 9, 5),
            "mobile_approval_pattern_e": self.values.bool_flag(index + 10, 7),
            "mobile_incentive_adjustment_increase": self.values.bool_flag(index + 11, 6),
            "mobile_resale_or_rental_companies": self.values.bool_flag(index + 12, 4),
            "mobile_deposits_joint_guarantees_credit_relaxation": self.values.bool_flag(index + 13, 9),
            "common_qa_review_cases": self.values.bool_flag(index + 14, 5),
            "special_debt_collection": self.values.bool_flag(index + 15, 11),
            "construction_industry_law": self.values.bool_flag(index + 16, 13),
            "agency_code_change": self.values.bool_flag(index + 17, 10),
            "refund_fee_reduction": self.values.bool_flag(index + 18, 6),
            "agency_contract": self.values.bool_flag(index + 19, 4),
            "reseller_contract": self.values.bool_flag(index + 20, 7),
            "other_type": self.values.bool_flag(index + 21, 15),
            "originators_name": person_name,
            "originators_phone_number": self.values.phone("03", 10_000_000 + index),
            "affiliated_org_address_list": f"{DEPARTMENTS[index % len(DEPARTMENTS)]}/法人営業統括/営業1課",
            "source_aggregation_sheet_info": self.values.code("a7s", index + 1, 12),
            "aggregation_number": str(20_250_000_000_000 + index),
            "scheduled_execution_date": ymd_dash(execution_date),
            "approval_document_period_months": str(12 + (index % 36)),
            "credit_alert": "有" if index % 4 == 0 else "無",
            "whether_credit_review": "有" if index % 5 == 0 else "無",
            "credit_review_request_name_compass": f"CR{execution_date:%Y%m%d}{index % 1000:03d}" if index % 5 == 0 else "",
            "credit_review_request_name_bfs": f"BFS{execution_date:%Y%m%d}{index % 1000:03d}" if index % 8 == 0 else "",
            "whether_legal_pre_review_conducted": "有" if index % 6 == 0 else "無",
            "legal_pre_review_request_number": f"LG{index:06d}" if index % 6 == 0 else "",
            "re_approval_draft_flag": "有" if index % 9 == 0 else "無",
            "service_type": COMPASS_SERVICE_TYPES[index % len(COMPASS_SERVICE_TYPES)],
            "sales_channel": COMPASS_SALES_CHANNELS[index % len(COMPASS_SALES_CHANNELS)],
            "legal_personal_classification": COMPASS_CORP_KINDS[index % len(COMPASS_CORP_KINDS)],
            "billing_form": COMPASS_BILLING_FORMS[index % len(COMPASS_BILLING_FORMS)],
            "agency_collaboration_conditions": "設定なし" if index % 2 == 0 else "代理店決裁基準内",
            "borderline_payment_amount": "代理店決裁基準で定めた水際金額範囲内",
            "pre_approval_flag": "無" if index % 10 else "有",
            "name_of_approved_person": self.values.person_name(),
            "reason_for_post_approval": "契約開始希望日が直近であり、先行承認のうえ事後起案となったため",
            "approver": self.values.code("0057F", index + 1, 10),
            "applicant": self.values.code("0055H", index + 1, 10),
            "orgl_route_proposers_duties": "本務",
            "orgl_route_sales_duties": "本務",
            "sales_representatives_list": f"{DEPARTMENTS[index % len(DEPARTMENTS)]}/法人営業第{index % 5 + 1}部",
            "comprehensive_approval": self.values.bool_flag(index + 22, 8),
            "group_comprehensive_approval": self.values.bool_flag(index + 23, 11),
            "used_in_other_projects": self.values.bool_flag(index + 24, 9),
            "contact_name": contact_name,
            "contact_phone_number": self.values.phone("070", 12_000_000 + index),
            "pre_confirmation": "有" if index % 4 == 0 else "無",
            "pre_approval_consultation_name": f"事前相談{index % 40 + 1}",
            "project_name": project_name,
            "project_id": self.values.code("0065H", index + 1, 10),
            "company_name": company_name,
            "uniform_company_code": self.values.code("UC", index + 1, 8),
            "tsr_rating": str(50 + (index % 40)),
            "number_of_lines": str(line_count),
            "contract_period_months": str(12 + (index % 24)),
            "contract_start_date": ymd_dash(execution_date),
            "number_of_lines_attended_opening": str(index % 10),
            "activation_installation_fee": "無料" if index % 3 == 0 else "有料",
            "free_installation_and_additional_service_fee": "無料" if index % 4 == 0 else "有料",
            "free_installation_fee": "開通工事費支援",
            "banner_installation_fee_additional_services": str(3_000 + (index % 10) * 500),
            "cost_1": str(10_000 + (index % 12) * 2_000),
            "cost_monthly_per_yen1": "月額値引き",
            "cost_lump_sum_per_yen1": str(1_000 + (index % 8) * 300),
            "cost_monthly_per_yen2": str(5_000 + (index % 10) * 700),
            "cost_lump_sum_per_yen2": "事務手数料減免",
            "cost_monthly_per_yen3": str(800 + (index % 6) * 200),
            "cost_lump_sum_per_yen3": str(3_000 + (index % 5) * 400),
            "proposal_type": "追加新規" if index % 2 == 0 else "機種変更",
            "project_summary_1_summary": project_summary,
            "project_summary_2_summary": "価格条件、保守体制、請求運用、開始スケジュールを関係部門と調整済み。",
            "other": str(line_count + 20),
            "expected_number_of_lines_maximum": str(line_count + 20),
            "applicable_platform_discount_rate_percent": str(5 + (index % 20)),
            "channel": COMPASS_SALES_CHANNELS[index % len(COMPASS_SALES_CHANNELS)],
            "exemption_deduction": "有" if index % 3 == 0 else "無",
            "exemption_amount_yen": str(50_000 + (index % 30) * 5_000 if index % 3 == 0 else 0),
            "sales_yen": str(sales_amount),
            "variable_operating_profit_yen": str(int(sales_amount * 0.25)),
            "variable_operating_profit_margin_percent": str(25),
            "operating_contribution_margin_yen": str(contribution),
            "operating_contribution_margin_margin_percent": str(18),
            "operating_profit_yen": str(operating_profit),
            "operating_profit_margin_percent": str(12),
            "voice_sales_contribution_margin_yen": str(int(sales_amount * 0.04)),
            "voice_sales_contribution_margin_margin_percent": str(4),
            "id_data_approval_base_profit_yen": str(int(sales_amount * 0.03)),
            "id_data_approval_base_profit_margin_percent": str(3),
            "is_ni_product_sales_approval_base_profit_yen": str(int(sales_amount * 0.02)),
            "is_ni_product_sales_approval_base_profit_margin_percent": str(2),
            "mobile_sales_contribution_margin_yen": str(int(sales_amount * 0.14)),
            "mobile_sales_contribution_margin_margin_percent": str(14),
            "agency_information_manual_input_flag": self.values.bool_flag(index + 25, 6),
            "agency_name_reference": self.values.company_name(index + 20),
            "agency_name_estimate": self.values.company_name(index + 30),
            "agency_code": agency_code,
            "commission_rate_percent_incent": str(3 + (index % 8)),
            "incentive_amount_yen": str(incentive),
            "reason_for_collaboration": "対応エリアおよび保守体制の要件を満たすため" if index % 2 else "",
            "automatic_renewal": "有" if index % 2 == 0 else "無",
            "sbm_line_count_upper": str(line_count),
            "sbm_line_count_lower": str(max(1, line_count - 8)),
            "mobile_ym_line_count_upper": str(index % 25),
            "mobile_ym_line_count_lower": str(max(0, (index % 25) - 3)),
            "total_external_expenses_purchases_yen": str(int(sales_amount * 0.35)),
            "voice_otoku_hikari_phone_sales_contribution_margin_yen": str(int(sales_amount * 0.01)),
            "voice_otoku_hikari_phone_sales_contribution_margin_rate_percent": "1",
            "deduction_adjustment_refund_recovery_amount_yen": str(30_000 + (index % 10) * 1_000 if index % 3 == 0 else 0),
            "total_external_expenses_yen": str(int(sales_amount * 0.28)),
            "applicable_period": f"{execution_date:%Y/%m} - {(execution_date + timedelta(days=180)):%Y/%m}",
            "payment_date": f"{(execution_date + timedelta(days=30)):%Y/%m}",
            "total_sales_amount_yen": str(sales_amount + 120_000),
            "invoice_reissue": "無",
            "related_approvals_compass": approval_number,
            "approval_request_number_other_than_compass": f"RNG{index:06d}",
            "solution_sales_management_system_quote_number": str(20_260_000 + index),
            "asset_db_number": self.values.code("AST", index + 1, 8),
            "agency_application_number": self.values.code("APN", index + 1, 8),
            "agency_application_number_sd_wf": self.values.code("SDW", index + 1, 8),
            "notes": f"案件{index % 100 + 1}の補足。先方要望に応じて社内確認済み。",
            "viewability": "全社員に開示",
            "additions_changes": "回線数、初期費用、保守条件を更新",
            "inputter": self.values.person_name(),
            "input_date": ymdhms_millis(created_at),
            "contractual_condition_1": "開始希望日までに契約条件確認が完了していること",
            "contractual_condition_2": "与信確認結果に重大懸念がないこと",
            "create_sub_approval_from_flow_flag": self.values.bool_flag(index + 26, 9),
            "private_flag": "f",
            "approval_date": ymdhms_millis(approval_at),
            "business_category": "モバイル",
            "expiration_date": ymd_dash(expiration_date),
            "additional_information_field": "営業判断メモおよび事前相談結果を記載",
            "based_proposal_approval": f"PR{index:06d}" if index % 5 == 0 else "",
            "approval_content": "【共通】値引きなど",
            "approval_route_criteria": "営業担当者情報から申請者・同意者・承認者をセット",
            "supplier_credit": "f",
            "valid_flg": "t",
            "record_id_formula": self.values.code("a1IJ2", index + 1, 10),
            "creator_id": self.values.code("0057F", index + 1, 10),
            "creation_date": ymdhms_millis(created_at - timedelta(days=2)),
            "deleted_flg": "f",
            "last_updated_by_id": self.values.code("0057F", index + 5, 10),
            "last_updated_date": ymdhms_millis(approval_at + timedelta(days=1)),
            "last_reference_date": ymdhms_millis(approval_at + timedelta(days=2)),
            "last_viewed_date": ymdhms_millis(approval_at + timedelta(days=3)),
            "owner_id": self.values.code("0057F", index + 3, 10),
            "record_type_id": self.values.code("012J2", index + 1, 10),
            "systemmodstamp": ymdhms_millis(approval_at + timedelta(days=1, hours=2)),
            "estimate_sheet_number": f"SN{created_at:%Y%m%d}{index % 100000:05d}",
            "summit_data_migration_flag": self.values.bool_flag(index + 27, 20),
            "credit_review_request_name_compass_presence_absence": "t" if index % 5 == 0 else "f",
            "estimate_sheet_presence_absence": "有" if index % 2 == 0 else "無",
            "product_pre_consultation": "有" if index % 4 == 0 else "無",
            "mobile_p2p_consultation_approval_conditions": "粗利率、契約期間、回線数の条件を満たすこと",
            "pre_consultation_approval_conditions": "部門長の事前確認を得ていること",
            "summary_supplement_applicant_only": "申請者メモ: 導入スケジュールに余裕がないため早期判断希望",
            "approval_date_and_time_unixtime": str(int(approval_at.timestamp())),
            "comment_1": "営業部一次確認済み",
            "comment_2": "法務確認不要" if index % 6 else "法務確認済み",
            "comment_3": "与信確認結果反映済み",
            "comment_4": "試算条件の差分を確認済み",
            "comment_5": "関係部門へ共有済み",
            "shared_email_address_1": shared_email_1,
            "shared_email_address_2": shared_email_2,
            "shared_email_address_3": shared_email_3,
            "proposers_common_employee_id": self.values.employee_id(index),
            "proposers_dept": DEPARTMENTS[index % len(DEPARTMENTS)],
            "proposal_dept_org_code_headquarters": self.values.code("HB", index + 1, 5),
            "proposal_dept_org_general_affairs_dept": self.values.code("TB", index + 1, 5),
            "proposal_dept_org_code_dept": self.values.code("DP", index + 1, 5),
            "applicants_group_name": "申請者グループ",
            "applicants_user_id": self.values.employee_id(index + 10),
            "applicants_user_name": person_name,
            "consenters_group_name": "同意者グループ",
            "consenters_user_id": self.values.employee_id(index + 20),
            "consenters_user_name": self.values.person_name(),
            "approvers_layer": COMPASS_APPROVER_LAYERS[index % len(COMPASS_APPROVER_LAYERS)],
            "approvers_group_name": "承認者グループ",
            "approvers_user_id": self.values.employee_id(index + 30),
            "approvers_user_name": self.values.person_name(),
            "last_processing_date_and_time": ymdhms_millis(approval_at + timedelta(hours=3)),
            "approval_history": "",
        }

    def _product_context(self, index: int) -> dict[str, str]:
        """商品1行ぶんの主要属性をテンプレートから組み立てる。"""
        template = PRODUCT_TEMPLATES[index % len(PRODUCT_TEMPLATES)]
        color_name, color_abbr = COLORS[index % len(COLORS)]
        start = BASE_DATE - timedelta(days=index % 400)
        end = start + timedelta(days=730)
        return {
            "id": self.values.sequential_id(index),
            "product_code": self.values.code("PRD", index + 1, 10),
            "validity_start_date": ymd(start),
            "validity_start_time": hms(9, index % 60),
            "validity_end_date": ymd(end),
            "validity_end_time": hms(18, index % 60),
            "area_code": PREFECTURES[index % len(PREFECTURES)]["area_code"],
            "product_official_name": f"{template[1]} {100 + (index % 900)}",
            "product_name_in_kana": f"{self.values.katakana_word(index)}モデル",
            "product_name_in_english": f"{template[1]} {100 + (index % 900)}",
            "product_abbreviation": clip(template[1].replace(' ', ''), 20),
            "product_subcategory_id": str((index % 10) + 1),
            "product_subcategory_official_name": template[0],
            "product_subcategory_kana": self.values.katakana_word(index),
            "product_subcategory_english_name": template[0],
            "product_small_category_id": str((index % 10) + 11),
            "product_small_category_official_name": template[0],
            "product_small_category_kana": self.values.katakana_word(index + 1),
            "product_small_category_english_name": template[0],
            "product_middle_category_id": str((index % 6) + 21),
            "product_middle_category_official_name": template[2],
            "product_middle_category_kana": self.values.katakana_word(index + 2),
            "product_middle_category_english_name": template[2],
            "product_major_category_id": str((index % 4) + 31),
            "product_major_category_official_name": template[3],
            "product_major_category_kana": self.values.katakana_word(index + 3),
            "product_major_category_english_name": template[3],
            "individual_management_type_code": str((index % 3) + 1),
            "manufacturer_id": str((index % 8) + 1),
            "manufacturer_official_name": f"{template[1]}メーカー",
            "manufacturer_name_in_kana": self.values.katakana_word(index + 4),
            "manufacturer_name_in_english": f"{template[1]} Inc",
            "brand_id": str((index % 8) + 101),
            "brand_official_name": template[1],
            "brand_code": self.values.code("BR", (index % 8) + 1, 4),
            "brand_name_in_kana": self.values.katakana_word(index + 5),
            "brand_abbreviation": clip(template[1].replace(' ', ''), 12),
            "brand_name_in_english": template[1],
            "jan_code": self.values.number_string(13, 49_000_000_0000 + index),
            "product_color_official_name": color_name,
            "product_color_abbreviation": color_abbr,
            "standard_color_id": str((index % len(COLORS)) + 1),
            "standard_color_official_name": color_name,
            "standard_color_name_in_kana": self.values.katakana_word(index + 6),
            "standard_color_name_in_english": color_name,
            "model_code": self.values.code("MD", index + 1, 8),
            "model_official_name": f"{template[1]}-{100 + (index % 900)}",
            "fee_payment_stop_date": ymd(end - timedelta(days=30)),
            "mvno_identification_id": str((index % 5) + 1),
            "mvno_identification_abbreviation_2": f"MV{(index % 5) + 1}",
            "sales_start_date": ymd(start + timedelta(days=14)),
            "sales_end_date": ymd(end - timedelta(days=14)),
            "additional_purchase_validity_start_date": ymd(start + timedelta(days=30)),
            "additional_purchase_validity_end_date": ymd(end - timedelta(days=90)),
            "cic_product_code": self.values.code("CIC", index + 1, 8),
            "non_essential_flag": str(index % 2),
            "service_generation_id": str((index % 4) + 1),
            "service_generation_official_name": "5G" if index % 2 == 0 else "4G",
            "capacity": template[5],
            "installment_review_limit_chk_target_flg": str(index % 2),
            "opt_installment_sales_applicable_flg": str((index + 1) % 2),
            "opt_installment_sales_applicable_from": ymd(start + timedelta(days=7)),
            "sales_price": str(template[6] + (index % 10) * 1000),
            "device_category": str((index % 5) + 1),
            "device_category_official_name": template[4],
            "major_category": str((index % 4) + 1),
            "major_category_official_name": template[3],
            "middle_category": str((index % 6) + 1),
            "middle_category_official_name": template[2],
            "minor_category": str((index % 10) + 1),
            "minor_category_official_name": template[0],
            "feature_flag": str(index % 2),
            "bundle_plan_identification_id": str((index % 5) + 1),
            "bundle_plan_nm": "法人基本プラン",
            "charge_amount": str(1000 + (index % 20) * 100),
            "uni_universal_usage_fee": "3",
            "validity_period": str(24 + (index % 12)),
            "logistics_product_code": self.values.code("LP", index + 1, 8),
            "quantity_amount_classification": str((index % 3) + 1),
            "product_tax_classification_code": str((index % 2) + 1),
            "logistics_product_tax_classification": "課税",
            "logistics_base_unit_quantity": "1",
            "standard_quantity": "1",
            "shipping_quantity": "1",
            "individual_box_size_length": str(10 + (index % 10)),
            "individual_box_size_width": str(7 + (index % 6)),
            "individual_box_size_height": str(2 + (index % 5)),
            "paper_packaging_material_weight": str(20 + (index % 10)),
            "plastic_packaging_material_weight": str(10 + (index % 5)),
            "product_weight": str(120 + (index % 80)),
            "number_of_pallets": str((index % 3) + 1),
            "packaging_specifications_etc": "標準梱包",
            "mrp_administrator_code": self.values.code("MR", (index % 20) + 1, 6),
            "conversion_representative_flag": str(index % 2),
            "product_type_for_inspection_cd": str((index % 4) + 1),
            "product_type_for_inspection_nm": "通常検品",
            "model_id": str(index + 1),
            "imsi_type": str((index % 3) + 1),
            "imsi_type_official_name": "標準IMSI",
        }

    def resolve_product_value(self, column: ColumnSpec, context: dict[str, str], index: int) -> str:
        """商品列の明示値が無い場合に、列名規則から既定値を補完する。"""
        if column.name in context:
            return context[column.name]
        if column.data_type.startswith("DECIMAL"):
            return self.values.decimal_value(index, modulo=9, minimum=1)
        if column.name.endswith("_date"):
            return ymd(BASE_DATE - timedelta(days=index % 300))
        if column.name.endswith("_time"):
            return hms((index * 5) % 24, (index * 11) % 60)
        if "english" in column.name:
            return f"{self.values.english_word(index)} {self.values.english_word(index + 1)}"
        if "kana" in column.name:
            return self.values.katakana_word(index) + self.values.katakana_word(index + 1)
        if "name" in column.name or column.name.endswith("_nm"):
            return f"商品サンプル{index % 100:02d}"
        if "code" in column.name or column.name.endswith("_id"):
            return self.values.code("P", index + 1, 8)
        return f"VAL{index % 1000}"

    def resolve_compass_value(self, column: ColumnSpec, context: dict[str, str], index: int) -> str:
        """営業決裁列の明示値が無い場合に、列名規則から既定値を補完する。"""
        if column.name in context:
            return context[column.name]
        name = column.name
        if column.data_type.startswith("DECIMAL"):
            return str(1 + (index % 50))
        if name.endswith("_flag") or name.endswith("_flg") or name.endswith("_type"):
            return self.values.bool_flag(index)
        if "unixtime" in name:
            return str(1_700_000_000 + index)
        if "date_and_time" in name or name.endswith("_date") and column.max_length == 23:
            base = datetime(2025, 1, 1, 9, 0, 0) + timedelta(hours=index)
            return ymdhms_millis(base)
        if name.endswith("_date"):
            return ymd_dash(BASE_DATE + timedelta(days=index % 180))
        if "email" in name:
            return self.values.email(index)
        if "phone" in name or "tel" in name or "fax" in name:
            return self.values.phone("03", 13_000_000 + index)
        if "name" in name or "subject" in name or "content" in name or "summary" in name or "notes" in name:
            return f"営業決裁サンプル{index % 100:02d}"
        if "code" in name or name.endswith("_id") or "number" in name:
            return self.values.code("CP", index + 1, 8)
        return f"VAL{index % 1000}"

    def _row_from_context(self, columns: list[ColumnSpec], context: dict[str, str]) -> list[str]:
        """列定義順に文脈値を並べ替え、最大長を適用した1行へ変換する。"""
        return [clip(context[column.name], column.max_length) for column in columns]

    def _fit_row(self, output_key: str, row: list[str]) -> list[str]:
        """出力種別ごとの目標サイズへ行を調整する。"""
        return self.row_adjusters[output_key].fit(row)

    def write_bfs_files(self, output_dir: Path) -> None:
        """BFSエントリCSVの全量版と差分版を逐次書き出す。"""
        headers = self._header_labels("bfs")
        self._write_bfs_file(output_dir / OUTPUT_FILES["bfs_all"], headers, "bfs_all", "all")
        self._write_bfs_file(output_dir / OUTPUT_FILES["bfs_diff"], headers, "bfs_diff", "diff")

    def _write_bfs_file(self, path: Path, headers: list[str], output_key: str, variant: str) -> None:
        """BFSエントリCSVを1ファイルずつ逐次出力する。"""
        handle, writer = open_csv_writer(path)
        try:
            writer.writerow(headers)
            for index in range(self.counts[output_key]):
                context = self._bfs_context(index, variant)
                writer.writerow(self._fit_row(output_key, self._bfs_row(context, index)))
        finally:
            handle.close()

    def _bfs_row(self, context: dict[str, str], index: int) -> list[str]:
        """BFS文脈を列順の行へ変換する。"""
        return [clip(self.resolve_bfs_value(column, context, index), column.max_length) for column in self.specs["bfs"]]

    def _bfs_context(self, index: int, variant: str) -> dict[str, str]:
        """BFS 1行ぶんの主要属性を組み立てる。"""
        base_index = index if variant == "all" else 2_000_000 + index
        created_at = datetime(2025, 12, 1, 9, 0) + timedelta(hours=base_index % 240, minutes=(base_index * 7) % 60)
        updated_at = created_at + timedelta(minutes=30)
        application_date = BASE_DATE - timedelta(days=base_index % 21)
        activation_date = application_date + timedelta(days=(base_index % 5) + 1)
        delivery_date = application_date + timedelta(days=(base_index % 10) + 2)
        approval_date = application_date + timedelta(days=(base_index % 7) + 1)
        rental_start_date = activation_date
        rental_end_date = rental_start_date + timedelta(days=365)
        company_name = self.values.company_name(base_index)
        agency_name = self.values.company_name(base_index + 17)
        contractor_name = company_name
        billing_name = company_name
        contact_person_name = self.values.person_name()
        contact_person_kana = self.values.person_name_kana(base_index)
        salesperson_name = self.values.person_name()
        salesperson_code = self.values.employee_id(base_index)
        agency_code = self.values.code("AGT", base_index + 1, 6)
        entry_number = f"EN{BASE_DATE:%Y%m%d}{self.values.number_string(6, base_index + 1)}"
        approval_numbers = [self.values.code("LS", base_index + i + 1, 7) for i in range(5)]
        plan_names = [
            "基本プラン",
            "データプラン",
            "音声プラン",
            "業務標準プラン",
            "セキュリティオプション",
            "端末補償プラン",
            "位置情報サービス",
            "クラウド連携プラン",
            "留守番電話サービス",
            "国際ローミング",
            "大容量データプラン",
            "テザリングオプション",
        ]
        op_categories = ["音声", "通信", "セキュリティ", "その他"]
        op_items = ["VoLTE", "データ通信", "端末補償", "国際ローミング"]
        percentage_op_categories = ["通信", "音声", "クラウド", "位置情報"]
        percentage_op_items = ["高速データ通信", "通話定額", "クラウドストレージ", "GPS位置情報"]
        share_options = ["50:50", "60:40", "70:30", "80:20"]
        other_options = [
            "初期設定サポート",
            "現場利用想定",
            "導入後フォロー",
            "請求運用確認",
            "与信確認済み",
            "保守条件調整済み",
            "契約更新条件確認済み",
            "関連部門合意済み",
        ]
        context: dict[str, str] = {
            "base_index": str(base_index),
            "variant": variant,
            "id": self.values.sequential_id(index),
            "entry_number": entry_number,
            "subject": f"{company_name}向けBFSエントリ {base_index % 500 + 1}",
            "creation_category": "新規" if base_index % 3 == 0 else "変更" if base_index % 3 == 1 else "追加",
            "order_type": ["新規契約", "変更契約", "追加契約"][base_index % 3],
            "application_form_linkage": "連携済" if base_index % 4 else "未連携",
            "special_contract_separate_output": "無" if base_index % 2 == 0 else "有",
            "notification_target": "対象" if base_index % 5 else "対象外",
            "activation_status": "開通済" if base_index % 2 == 0 else "未開通",
            "activation_date": ymd(activation_date),
            "incomplete_request_type": ["新規", "変更", "追加"][base_index % 3],
            "source_entry_type": "コピー元" if base_index % 4 == 0 else "試算",
            "salesperson_code": salesperson_code,
            "salesperson": salesperson_name,
            "agency_code": agency_code,
            "affiliated_agency": agency_name,
            "carrier_type": ["SoftBank", "Y!mobile", "LINEMO"][base_index % 3],
            "business_operator_category": "法人",
            "application_form_number": self.values.code("AP", base_index + 1, 10),
            "contract_type": ["レンタル", "売切", "リース"][base_index % 3],
            "expected_delivery_date": ymd(delivery_date),
            "application_date": ymd(application_date),
            "ipad_customer_type": ["法人", "一般", "教育"][base_index % 3],
            "billing_method": ["請求書", "口座振替", "クレジットカード"][base_index % 3],
            "number_of_payments": ["一括", "12回", "24回"][base_index % 3],
            "billing_category": ["毎月請求", "一括請求"][base_index % 2],
            "call_charge_combined_type": ["なし", "あり"][base_index % 2],
            "accessory_purchase": ["無", "有"][base_index % 2],
            "accessory_fee_payment_method": ["請求書", "口座振替", "クレジットカード"][base_index % 3],
            "accessory_fee_billing_category": ["毎月請求", "一括請求"][base_index % 2],
            "accessory_fee_combined_type": ["なし", "あり"][base_index % 2],
            "change_target": ["新規", "追加", "変更"][base_index % 3],
            "reception_category": "通常受付",
            "web_order_number": self.values.code("WO", base_index + 1, 10),
            "billing_discount_change": ["無", "有"][base_index % 2],
            "entry_creator_id": self.values.employee_id(base_index + 100),
            "entry_creation_date_and_time": ymdhm(created_at),
            "entry_updater_id": self.values.employee_id(base_index + 200),
            "entry_update_date_and_time": ymdhm(updated_at),
            "sfa_number": self.values.code("SFA", base_index + 1, 9),
            "sfa_project_name": f"{company_name}向けSFA案件{base_index % 300 + 1}",
            "unified_company_code": self.values.code("UC", base_index + 1, 8),
            "company_name": company_name,
            "sales_approval_subject": f"{company_name}向け営業決裁 {base_index % 80 + 1}",
            "sales_approval_number": self.values.code("LS", base_index + 1, 9),
            "distributor_code": self.values.code("DST", base_index + 1, 6),
            "consolidated_book_number": self.values.code("BK", base_index + 1, 10),
            "estimate_book_number": self.values.code("TS", base_index + 1, 10),
            "easy_estimate_number": self.values.code("QT", base_index + 1, 10),
            "relative_contract_management_number": self.values.code("CT", base_index + 1, 10),
            "agency_code_1": agency_code,
            "agency_name": agency_name,
            "sales_representative_1": salesperson_name,
            "telephone_number": self.values.phone("03", 10_000_000 + base_index),
            "department_name": DEPARTMENTS[base_index % len(DEPARTMENTS)],
            "identity_verification_implementer_code": self.values.code("IV", base_index + 1, 6),
            "receptionist_code": self.values.code("RC", base_index + 1, 6),
            "applicant_name": contact_person_name,
            "department_name_1": DEPARTMENTS[(base_index + 1) % len(DEPARTMENTS)],
            "common_employee_number": self.values.employee_id(base_index + 300),
            "credit_application_number": self.values.code("CR", base_index + 1, 8),
            "credit_response_number": self.values.code("CRR", base_index + 1, 8),
            "contractor_number": self.values.number_string(10, 3_450_000_000 + base_index),
            "contractor_type": "法人",
            "corporate_status_position": "前",
            "corporate_status": "株式会社",
            "contractor_name": contractor_name,
            "contractor_name_katakana": f"カブシキガイシャ{self.values.katakana_word(base_index)}{self.values.katakana_word(base_index + 1)}",
            "corporate_type": "通常法人",
            "deemed_corporate_approval_number": self.values.code("DC", base_index + 1, 10),
            "contact_person_name": contact_person_name,
            "contact_person_name_katakana": contact_person_kana,
            "contact_person_department": DEPARTMENTS[(base_index + 2) % len(DEPARTMENTS)],
            "contract_change_confirmation_check": "済" if base_index % 2 == 0 else "未",
            "contractor_name_change_comment": "" if base_index % 4 else "契約者名変更はなし。",
            "billing_number": self.values.number_string(10, 4_560_000_000 + base_index),
            "corporate_entity_position_1": "前",
            "corporate_entity_1": "株式会社",
            "billing_name": billing_name,
            "billing_name_katakana": f"カブシキガイシャ{self.values.katakana_word(base_index + 2)}{self.values.katakana_word(base_index + 3)}",
            "billing_department_name": f"{company_name}営業部",
            "contact_person": contact_person_name,
            "payment_method": ["金融機関窓口払込", "クレジットカード", "預金口座振替"][base_index % 3],
            "invoice_type": ["通常", "明細", "請求書"][base_index % 3],
            "invoice_delivery": ["送付", "なし", "表示"][base_index % 3],
            "last_4_digits": self.values.number_string(4, 1000 + (base_index % 9000)),
            "billing_group_information": "標準請求グループ",
            "installment_payment_allowance_number": self.values.code("IP", base_index + 1, 8),
            "agency": "代行業者なし" if base_index % 2 == 0 else "三井住友ファクター",
            "corporate_multiple_line_discount": ["無", "有"][base_index % 2],
            "discount_rate": str(5 + (base_index % 10)),
            "discount_amount": str(1_000 + (base_index % 20) * 500),
            "number_of_discount_months": str(12 + (base_index % 12)),
            "fee_type": str((base_index % 3) + 1),
            "bulk_invoice_discount": ["無", "有"][base_index % 2],
            "discount_rate_1": str(10 + (base_index % 10)),
            "discount_amount_1": str(2_000 + (base_index % 20) * 500),
            "number_of_discount_months_1": str(6 + (base_index % 12)),
            "fee_type_1": str((base_index % 3) + 1),
            "number_s_corporate_multiple_line_discount": ["無", "有"][base_index % 2],
            "discount_rate_2": str(12 + (base_index % 8)),
            "discount_amount_2": str(3_000 + (base_index % 20) * 600),
            "number_of_discount_months_2": str(6 + (base_index % 10)),
            "fee_type_2": str((base_index % 3) + 1),
            "s_number_large_call_discount": ["無", "有"][base_index % 2],
            "discount_rate_3": str(15 + (base_index % 5)),
            "discount_amount_3": str(4_000 + (base_index % 20) * 700),
            "number_of_discount_months_3": str(6 + (base_index % 8)),
            "fee_type_3": str((base_index % 3) + 1),
            "share": share_options[base_index % len(share_options)],
            "discount_rate_4": str(20 + (base_index % 5)),
            "discount_amount_4": str(5_000 + (base_index % 20) * 700),
            "number_of_discount_months_4": str(6 + (base_index % 8)),
            "fee_type_4": str((base_index % 3) + 1),
            "billing_address_shipping_address_category": "請求先住所",
            "shipping_address": f"{company_name} 御中",
            "invoice_customization": "無" if base_index % 2 == 0 else "有",
            "billing_address_category": "契約者住所",
            "shipping_address_1": f"{company_name} 御中",
            "invoice_customization_1": "無" if base_index % 2 == 0 else "有",
            "special_agreement_start_date": ymd(approval_date),
            "special_agreement_period": f"{12 + (base_index % 24)}ヶ月",
            "contract_period_in_months": str(12 + (base_index % 36)),
            "period_after_automatic_renewal": f"{12 + (base_index % 24)}ヶ月",
            "initial_rental_period": f"{12 + (base_index % 12)}ヶ月",
            "used_rental_start_date": ymd(rental_start_date),
            "used_rental_end_date": ymd(rental_end_date),
            "maximum_number_of_lines_applicable_to_the_special_agreement": str(99 + (base_index % 20)),
            "number_of_lines": str(50 + (base_index % 100)),
            "warehouse_type": "標準",
            "request_for_incomplete_report_creation": ["無", "有"][base_index % 2],
            "gisun_registration_not_possible": ["無", "有"][base_index % 7 == 0],
            "replacement_type": ["新規", "追加", "変更"][base_index % 3],
            "inventory_type": "標準",
            "sales_office": ["東京営業所", "大阪営業所", "名古屋営業所", "福岡営業所"][base_index % 4],
            "declaration_details": "導入用途、契約条件、運用体制を確認済み。",
            "usim_type": ["nanoSIM", "eSIM", "microSIM"][base_index % 3],
            "other_usim_types": "" if base_index % 2 == 0 else "標準",
            "quantity": str(1 + (base_index % 10)),
            "wo_specific_usim": ["無", "有"][base_index % 2],
            "estimate_template_version": f"Ver{4 + (base_index % 3)}.{base_index % 10}",
            "approval_date": ymd(approval_date),
            "original_estimate_number": self.values.code("TS", base_index + 1, 10),
            "copy_entry_number": entry_number if base_index % 5 == 0 else "",
            "minimum_number_of_lines": str(1 + (base_index % 10)),
            "device_binding_amount": str(10_000 + (base_index % 20) * 500),
            "device_binding_period": str(12 + (base_index % 12)),
            "international_rm_discount_specification": ["無", "有"][base_index % 2],
            "international_rm_discount_specification_discount_rate": str(5 + (base_index % 10)),
            "additional_information": f"{company_name}向けのBFSエントリ。契約条件と請求条件を確認済み。",
            "channel": ["直販", "代理店"][base_index % 2],
            "estimated_status": ["承認済", "作成中", "差戻し"][base_index % 3],
            "rental_used_start_date": ymd(rental_start_date),
            "rental_used_period_months": str(12 + (base_index % 12)),
        }
        for approval_index, approval_number in enumerate(approval_numbers, start=1):
            context[f"approval_number_{approval_index}"] = approval_number
        for stakeholder_index in range(1, 11):
            context[f"stakeholder_{stakeholder_index}"] = (
                f"{self.values.company_name(base_index + stakeholder_index)}／{self.values.person_name()}"
            )
        for plan_index, plan_name in enumerate(plan_names, start=1):
            if plan_index <= 6:
                context[f"plan_binding_{plan_index}"] = plan_name
            else:
                context[f"plan_restriction_{plan_index}"] = plan_name
        percentage_plan_ratios = ("60", "40", "30", "20")
        for ratio_index, ratio in enumerate(percentage_plan_ratios, start=1):
            context[f"percentage_plan_{ratio_index}"] = plan_names[ratio_index - 1]
            context[f"plan_ratio_{ratio_index}"] = ratio
        for op_index, op_category in enumerate(op_categories, start=1):
            context[f"required_op_category_{op_index}"] = op_category
            context[f"required_op_{op_index}"] = op_items[op_index - 1]
            context[f"percentage_op_category_{op_index}"] = percentage_op_categories[op_index - 1]
            context[f"percentage_op_{op_index}"] = percentage_op_items[op_index - 1]
            context[f"op_ratio_{op_index}"] = ("50", "30", "15", "5")[op_index - 1]
        for other_index, other_option in enumerate(other_options, start=1):
            context[f"other_options_{other_index}"] = other_option
        return context

    def resolve_bfs_value(self, column: ColumnSpec, context: dict[str, str], index: int) -> str:
        """BFS列の明示値が無い場合に、列名規則から既定値を補完する。"""
        if column.name in context:
            return context[column.name]
        name = column.name
        base_index = int(context["base_index"])
        if column.data_type.startswith("DECIMAL"):
            return str(1 + (base_index % 99))
        if "date_and_time" in name:
            return ymdhm(datetime(2025, 12, 1, 9, 0) + timedelta(hours=base_index % 240))
        if name.endswith("_date"):
            return ymd(BASE_DATE - timedelta(days=base_index % 365))
        if "kana" in name or "katakana" in name:
            return f"カタカナ{base_index % 100:02d}"
        if "phone" in name or "tel" in name or "fax" in name:
            return self.values.phone("03", 20_000_000 + base_index)
        if name in {"application_form_linkage", "special_contract_separate_output", "notification_target", "activation_status"}:
            return ["連携済", "無", "対象", "開通済"][base_index % 4]
        if name in {"creation_category", "order_type", "incomplete_request_type", "change_target", "replacement_type"}:
            return ["新規", "変更", "追加"][base_index % 3]
        if name in {"carrier_type"}:
            return ["SoftBank", "Y!mobile", "LINEMO"][base_index % 3]
        if name in {"business_operator_category", "contractor_type", "corporate_type"}:
            return ["法人", "個人", "みなし法人"][base_index % 3]
        if name in {"billing_method", "accessory_fee_payment_method", "payment_method"}:
            return ["請求書", "口座振替", "クレジットカード"][base_index % 3]
        if name in {"billing_category", "accessory_fee_billing_category"}:
            return ["毎月請求", "一括請求"][base_index % 2]
        if name in {"call_charge_combined_type", "accessory_fee_combined_type"}:
            return ["なし", "あり"][base_index % 2]
        if name in {"contract_type"}:
            return ["レンタル", "売切", "リース"][base_index % 3]
        if name in {"ipad_customer_type"}:
            return ["法人", "一般", "教育"][base_index % 3]
        if name in {"invoice_type", "invoice_delivery"}:
            return ["通常", "明細", "送付", "表示"][base_index % 4]
        if name in {"channel"}:
            return ["直販", "代理店"][base_index % 2]
        if name in {"estimated_status"}:
            return ["承認済", "作成中", "差戻し"][base_index % 3]
        if name in {"warehouse_type", "inventory_type"}:
            return "標準"
        if name in {"request_for_incomplete_report_creation", "gisun_registration_not_possible", "wo_specific_usim"}:
            return ["無", "有"][base_index % 2]
        if name in {"usim_type"}:
            return ["nanoSIM", "eSIM", "microSIM"][base_index % 3]
        if name in {"sales_office"}:
            return ["東京営業所", "大阪営業所", "名古屋営業所", "福岡営業所"][base_index % 4]
        if name in {"billing_address_shipping_address_category", "billing_address_category"}:
            return ["請求先住所", "契約者住所"][base_index % 2]
        if name in {"corporate_status_position"}:
            return ["前", "後"][base_index % 2]
        if name in {"corporate_status"}:
            return ["株式会社", "有限会社"][base_index % 2]
        if name in {"contract_change_confirmation_check"}:
            return ["済", "未"][base_index % 2]
        if name in {"corporate_multiple_line_discount", "bulk_invoice_discount", "number_s_corporate_multiple_line_discount", "s_number_large_call_discount"}:
            return ["無", "有"][base_index % 2]
        if name.startswith("fee_type"):
            return str((base_index % 3) + 1)
        if name.endswith("_ratio") or name.endswith("_rate") or "ratio" in name or "rate" in name:
            return str(5 + (base_index % 80))
        if "comment" in name or "details" in name or "description" in name or "summary" in name or "information" in name or "conditions" in name or "options" in name or "binding" in name or "history" in name:
            return f"{name}に関する補足{base_index % 100:02d}"
        if "number" in name or name.endswith("_id") or "code" in name or "book" in name or "sheet" in name:
            return self.values.code("BFS", base_index + 1, 10)
        if "name" in name:
            return f"BFSサンプル{base_index % 100:02d}"
        return f"VAL{base_index % 1000}"
