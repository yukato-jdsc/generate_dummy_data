from __future__ import annotations

import random
from datetime import timedelta
from pathlib import Path

from .config import (
    BASE_DATE,
    CAMPAIGN_PREFIXES,
    CAMPAIGN_SUFFIXES,
    COLORS,
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
from .values import ValueFactory, clip, hms, ymd


class CsvGenerator:
    """各CSVの行データを生成し、必要に応じてファイルへ出力する。"""

    def __init__(self, specs: dict[str, list[ColumnSpec]], seed: int, counts: dict[str, int]) -> None:
        self.specs = specs
        self.seed = seed
        self.counts = counts
        self.values = ValueFactory(seed)
        self.diff_sample_size = counts["agency_diff"]

    def campaign_rows(self) -> list[list[str]]:
        """キャンペーンCSVの全行をメモリ上で生成する。"""
        rows = []
        for index in range(self.counts["campaign"]):
            start = BASE_DATE - timedelta(days=index % 180)
            end = start + timedelta(days=90 + (index % 180))
            name = self._campaign_name(index)
            context = {
                "campaign_id": self.values.code("CP", index + 1, 10),
                "campaign_name": name,
                "description": f"{name}のテスト投入用データ",
                "effective_start_date": ymd(start),
                "effective_end_date": ymd(end),
                "old_flag": "" if index % 5 else "1",
            }
            rows.append(self._row_from_context(self.specs["campaign"], context))
        return rows

    def _campaign_name(self, index: int) -> str:
        """キャンペーン名テンプレートをインデックスから組み立てる。"""
        return f"{CAMPAIGN_PREFIXES[index % len(CAMPAIGN_PREFIXES)]}{CAMPAIGN_SUFFIXES[index % len(CAMPAIGN_SUFFIXES)]}"

    def write_agency_files(self, output_dir: Path) -> None:
        """取次店の全量CSVと差分CSVを同時に出力する。"""
        headers = [column.name for column in self.specs["agency"]]
        sampled: list[list[str]] = []
        sampler = random.Random(self.seed)
        handle, writer = open_csv_writer(output_dir / OUTPUT_FILES["agency_all"])
        try:
            writer.writerow(headers)
            for index in range(self.counts["agency_all"]):
                row = self.agency_row(index)
                writer.writerow(row)
                self._update_reservoir(sampled, row, index, sampler)
        finally:
            handle.close()
        sampled.sort(key=lambda row: row[0])
        write_csv(output_dir / OUTPUT_FILES["agency_diff"], headers, sampled)

    def _update_reservoir(
        self,
        sampled: list[list[str]],
        row: list[str],
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

    def agency_row(self, index: int) -> list[str]:
        """取次店1行ぶんの文脈を組み立て、列順に並べた値へ変換する。"""
        context = {}
        context.update(self._agency_base_context(index))
        context.update(self._agency_category_context(index))
        context.update(self._agency_address_context(index))
        context.update(self._agency_contact_context(index))
        context.update(self._agency_organization_context(index))
        context.update(self._agency_operation_context(index))
        context.update(self._agency_billing_context(index))
        context.update(self._agency_misc_context(index))
        return [
            clip(self.resolve_agency_value(column, context, index), column.max_length)
            for column in self.specs["agency"]
        ]

    def _agency_base_context(self, index: int) -> dict[str, str]:
        """取次店の識別子・有効期間などの基本属性を生成する。"""
        start = BASE_DATE - timedelta(days=index % 720)
        end = start + timedelta(days=365 if index % 9 else 180)
        primary_index = (index // 10) + 1
        aggregated_index = (index // 5) + 1
        return {
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
            rows.append(
                [clip(self.resolve_product_value(column, context, index), column.max_length) for column in self.specs["product"]]
            )
        return rows

    def _product_context(self, index: int) -> dict[str, str]:
        """商品1行ぶんの主要属性をテンプレートから組み立てる。"""
        template = PRODUCT_TEMPLATES[index % len(PRODUCT_TEMPLATES)]
        color_name, color_abbr = COLORS[index % len(COLORS)]
        start = BASE_DATE - timedelta(days=index % 400)
        end = start + timedelta(days=730)
        return {
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

    def _row_from_context(self, columns: list[ColumnSpec], context: dict[str, str]) -> list[str]:
        """列定義順に文脈値を並べ替え、最大長を適用した1行へ変換する。"""
        return [clip(context[column.name], column.max_length) for column in columns]
