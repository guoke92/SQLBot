from decimal import Decimal

import pandas as pd

from apps.chat.models.chat_model import AxisObj


class DataFormat:
    @staticmethod
    def rows_to_markdown_table(
        fields: list,
        rows: list,
        *,
        max_rows: int = 5,
        title: str = "",
    ) -> str:
        """Render tabular rows as a markdown table for LLM prompts.

        Shared helper for chart/sample enrichment so protocol consumers don't each
        hand-roll table formatting (and so SQL-vs-API can stay uniform).
        """
        if not fields or not rows:
            return ""
        sample = rows[:max_rows]
        lines: list[str] = []
        if title:
            lines.append(title)
        lines.append("| " + " | ".join(str(f) for f in fields) + " |")
        lines.append("| " + " | ".join("---" for _ in fields) + " |")
        for row in sample:
            if not isinstance(row, dict):
                vals = ["" for _ in fields]
            else:
                vals = [
                    "" if row.get(f) is None else str(row.get(f))
                    for f in fields
                ]
            lines.append("| " + " | ".join(vals) + " |")
        return "\n".join(lines)

    @staticmethod
    def safe_convert_to_string(df):
        df_copy = df.copy()

        for col in df_copy.columns:
            # 使用map避免ambiguous truth value问题
            df_copy[col] = df_copy[col].map(
                # 关键：在数字字符串前添加零宽空格，阻止pandas的自动格式化
                lambda x: "" if pd.isna(x) else "\u200b" + str(x)
            )

        return df_copy

    @staticmethod
    def normalize_qualified_sql_column_keys(row: dict) -> dict:
        """Add unqualified keys for names like ``alias.column`` (Hive/MySQL return shape).

        Chart bindings use the bare column name (``table_name``) while drivers may return
        ``_u2.table_name``. Only adds ``short`` when absent to avoid clobbering real duplicates.
        """
        if not row:
            return row
        out = dict(row)
        for k, v in row.items():
            ks = str(k)
            if "." not in ks:
                continue
            short = ks.rsplit(".", 1)[-1]
            if short not in out:
                out[short] = v
        return out

    @staticmethod
    def normalize_qualified_sql_column_keys_in_object_array(obj_array: list) -> list:
        if not obj_array:
            return obj_array
        return [
            DataFormat.normalize_qualified_sql_column_keys(obj) if isinstance(obj, dict) else obj
            for obj in obj_array
        ]

    @staticmethod
    def resolve_result_field_name(value: str, fields: list | None) -> str:
        """Map a chart binding token onto the actual query-result field name.

        Chart ``value`` must match row keys on the FE. SQL drivers usually lower-case
        columns; REST/OpenAPI keep original (often camelCase). Do **not** force
        ``.lower()`` on chart values — resolve against the executed result fields:
        exact match first, then case-insensitive, then bare name after ``.``.
        When no fields are available, preserve the original token.
        """
        if value is None:
            return value
        token = str(value)
        if not token or not fields:
            return token

        field_names = [str(f) for f in fields if f is not None]
        if not field_names:
            return token
        if token in field_names:
            return token

        lower_map: dict[str, str] = {}
        bare_map: dict[str, str] = {}
        for name in field_names:
            low = name.lower()
            if low not in lower_map:
                lower_map[low] = name
            if "." in name:
                bare = name.rsplit(".", 1)[-1]
                bare_low = bare.lower()
                if bare_low not in bare_map:
                    bare_map[bare_low] = name

        hit = lower_map.get(token.lower())
        if hit is not None:
            return hit
        hit = bare_map.get(token.lower())
        if hit is not None:
            return hit
        return token

    @staticmethod
    def align_chart_bindings(chart: dict, fields: list | None) -> dict:
        """Rewrite chart column/axis binding values to match actual result field names.

        Mutates and returns ``chart``. Shared by the stream pipeline and any later
        re-bind path so SQL lower-case columns and REST camelCase keys both bind.
        """
        if not chart or not isinstance(chart, dict):
            return chart

        def _fix(val):
            if val is None:
                return val
            if isinstance(val, list):
                return [DataFormat.resolve_result_field_name(v, fields) if v else v for v in val]
            return DataFormat.resolve_result_field_name(val, fields)

        columns = chart.get("columns")
        if columns:
            for col in columns:
                if isinstance(col, dict) and col.get("value") is not None:
                    col["value"] = _fix(col.get("value"))

        axis = chart.get("axis")
        if isinstance(axis, dict):
            for key in ("x", "series"):
                item = axis.get(key)
                if isinstance(item, dict) and item.get("value") is not None:
                    item["value"] = _fix(item.get("value"))

            y_axis = axis.get("y")
            if isinstance(y_axis, list):
                for item in y_axis:
                    if isinstance(item, dict) and item.get("value") is not None:
                        item["value"] = _fix(item.get("value"))
            elif isinstance(y_axis, dict) and y_axis.get("value") is not None:
                y_axis["value"] = _fix(y_axis.get("value"))

            multi_quota = axis.get("multi-quota")
            if isinstance(multi_quota, dict) and multi_quota.get("value") is not None:
                multi_quota["value"] = _fix(multi_quota.get("value"))

        return chart

    @staticmethod
    def convert_large_numbers_in_object_array(obj_array, int_threshold=1e15, float_threshold=1e10):
        """处理对象数组，将每个对象中的大数字转换为字符串"""

        def format_float_without_scientific(value):
            """格式化浮点数，避免科学记数法"""
            if value == 0:
                return "0"
            formatted = str(Decimal(str(value)))
            if '.' in formatted:
                formatted = formatted.rstrip('0').rstrip('.')
            return formatted

        def process_object(obj):
            """处理单个对象"""
            if not isinstance(obj, dict):
                return obj

            processed_obj = {}
            for key, value in obj.items():
                if isinstance(value, (int, float)):
                    # 只转换大数字
                    if isinstance(value, int) and abs(value) >= int_threshold:
                        processed_obj[key] = str(value)
                    elif isinstance(value, float) and (abs(value) >= float_threshold or abs(value) < 1e-6):
                        processed_obj[key] = format_float_without_scientific(value)
                    else:
                        processed_obj[key] = value
                elif isinstance(value, dict):
                    # 处理嵌套对象
                    processed_obj[key] = process_object(value)
                elif isinstance(value, list):
                    # 处理对象中的数组
                    processed_obj[key] = [process_item(item) for item in value]
                else:
                    processed_obj[key] = value
            return processed_obj

        def process_item(item):
            """处理数组中的项目"""
            if isinstance(item, dict):
                return process_object(item)
            return item

        return [process_item(obj) for obj in obj_array]

    @staticmethod
    def convert_object_array_for_pandas(column_list: list, data_list: list):
        _fields_list = []
        for field_idx, field in enumerate(column_list):
            _fields_list.append(field.name)

        md_data = []
        for inner_data in data_list:
            _row = []
            for field_idx, field in enumerate(column_list):
                value = inner_data.get(field.value)
                _row.append(value)
            md_data.append(_row)
        return md_data, _fields_list

    @staticmethod
    def convert_data_fields_for_pandas(chart: dict, fields: list, data: list):
        _fields = {}
        if chart.get('columns'):
            for _column in chart.get('columns'):
                if _column:
                    _fields[_column.get('value')] = _column.get('name')
        if chart.get('axis'):
            if chart.get('axis').get('x'):
                _fields[chart.get('axis').get('x').get('value')] = chart.get('axis').get('x').get('name')
            if chart.get('axis').get('y'):
                # _fields[chart.get('axis').get('y').get('value')] = chart.get('axis').get('y').get('name')
                y_axis = chart.get('axis').get('y')
                if isinstance(y_axis, list):
                    # y轴是数组的情况（多指标字段）
                    for y_item in y_axis:
                        if isinstance(y_item, dict) and 'value' in y_item and 'name' in y_item:
                            _fields[y_item.get('value')] = y_item.get('name')
                elif isinstance(y_axis, dict):
                    # y轴是对象的情况（单指标字段）
                    if 'value' in y_axis and 'name' in y_axis:
                        _fields[y_axis.get('value')] = y_axis.get('name')
            if chart.get('axis').get('series'):
                _fields[chart.get('axis').get('series').get('value')] = chart.get('axis').get('series').get(
                    'name')
        _column_list = []
        for field in fields:
            _column_list.append(
                AxisObj(name=field if not _fields.get(field) else _fields.get(field), value=field))

        md_data, _fields_list = DataFormat.convert_object_array_for_pandas(_column_list, data)

        return md_data, _fields_list

    @staticmethod
    def format_pd_data(column_list: list, data_list: list, col_formats: dict = None):
        # 预处理数据并记录每列的格式类型
        # 格式类型：'text'（文本）、'number'（数字）、'default'（默认）
        _fields_list = []

        if col_formats is None:
            col_formats = {}
        for field_idx, field in enumerate(column_list):
            _fields_list.append(field.name)
            col_formats[field_idx] = 'default'  # 默认不特殊处理

        data = []

        for _data in data_list:
            _row = []
            for field_idx, field in enumerate(column_list):
                value = _data.get(field.value)
                if value is not None:
                    # 检查是否为数字且需要特殊处理
                    if isinstance(value, (int, float)):
                        # 整数且超过15位 → 转字符串并标记为文本列
                        if isinstance(value, int) and len(str(abs(value))) > 15:
                            value = str(value)
                            col_formats[field_idx] = 'text'
                        # 小数且超过15位有效数字 → 转字符串并标记为文本列
                        elif isinstance(value, float):
                            decimal_str = format(value, '.16f').rstrip('0').rstrip('.')
                            if len(decimal_str) > 15:
                                value = str(value)
                                col_formats[field_idx] = 'text'
                        # 其他数字列标记为数字格式（避免科学记数法）
                        elif col_formats[field_idx] != 'text':
                            col_formats[field_idx] = 'number'
                _row.append(value)
            data.append(_row)

        return data, _fields_list, col_formats