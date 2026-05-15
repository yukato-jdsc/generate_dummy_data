
-- DROP PROCEDURE public.sp_detect_diff(text, text, text, text);

CREATE OR REPLACE PROCEDURE public.sp_detect_diff(IN p_tmp_table text, IN p_base_table text, IN p_primary_keys text, IN p_diff_columns text)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
    v_diff_table TEXT := 'tmp_diff_' || regexp_replace(p_base_table, '^tmp_base_', '');
    v_pk_array TEXT[];
    v_diff_array TEXT[];
    v_all_columns TEXT[];
    v_insert_sql TEXT;
    v_update_sql TEXT;
    v_delete_sql TEXT;
    v_pk_join TEXT;
    v_diff_condition TEXT;
    v_column_list TEXT;
    v_column_list_with_t TEXT;
    i INTEGER;
BEGIN
    -- カンマ区切り文字列を配列に変換（空白をトリム）
    v_pk_array := string_to_array(regexp_replace(p_primary_keys, '\s+', '', 'g'), ',');
    
    -- 全カラムリストを取得
    SELECT array_agg(column_name::TEXT ORDER BY ordinal_position)
    INTO v_all_columns
    FROM information_schema.columns
    WHERE table_name = p_tmp_table
      AND column_name NOT IN ('diff_type', 'diff_at');

    -- 差分判定対象カラムを決定する。未指定時は主キー以外の全カラムを使う。
    IF p_diff_columns IS NULL OR btrim(p_diff_columns) = '' THEN
        SELECT array_agg(column_name ORDER BY column_position)
        INTO v_diff_array
        FROM (
            SELECT column_name, column_position
            FROM unnest(v_all_columns) WITH ORDINALITY AS cols(column_name, column_position)
            WHERE column_name <> ALL(v_pk_array)
        ) filtered_columns;
    ELSE
        v_diff_array := string_to_array(regexp_replace(p_diff_columns, '\s+', '', 'g'), ',');
    END IF;
    
    -- カラムリスト文字列生成
    v_column_list := array_to_string(v_all_columns, ', ');
    v_column_list_with_t := array_to_string(
        ARRAY(SELECT 't.' || unnest FROM unnest(v_all_columns)),
        ', '
    );
    
    -- ベーステーブルが存在しない場合は全レコードをINSERTとして扱う
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = p_base_table
    ) THEN
        RAISE NOTICE 'Base table % does not exist. Treating all records as INSERT.', p_base_table;
        
        v_insert_sql := format(
            'INSERT INTO %I (%s, diff_type) SELECT %s, ''I'' FROM %I',
            v_diff_table,
            v_column_list,
            v_column_list,
            p_tmp_table
        );
        
        EXECUTE v_insert_sql;
        RAISE NOTICE 'Diff detection completed for table: % (initial load)', p_base_table;
        RETURN;
    END IF;
    
    -- プライマリキー結合条件生成
    v_pk_join := '';
    FOR i IN 1..array_length(v_pk_array, 1) LOOP
        IF v_pk_join <> '' THEN
            v_pk_join := v_pk_join || ' AND ';
        END IF;
        v_pk_join := v_pk_join || 'd.' || v_pk_array[i] || ' = t.' || v_pk_array[i];
    END LOOP;
    
    -- 差分検出条件生成 (IS DISTINCT FROM使用)
    v_diff_condition := '';
    IF array_length(v_diff_array, 1) IS NOT NULL THEN
        FOR i IN 1..array_length(v_diff_array, 1) LOOP
            IF v_diff_condition <> '' THEN
                v_diff_condition := v_diff_condition || ' OR ';
            END IF;
            v_diff_condition := v_diff_condition || 'd.' || v_diff_array[i] || ' IS DISTINCT FROM t.' || v_diff_array[i];
        END LOOP;
    END IF;
    
    -- ===========================
    -- 1. INSERT (新規レコード検出)
    -- ===========================
    v_insert_sql := format(
        'INSERT INTO %I (%s, diff_type) ' ||
        'SELECT %s, ''I'' ' ||
        'FROM %I t ' ||
        'LEFT JOIN %I d ON %s ' ||
        'WHERE d.%I IS NULL',
        v_diff_table,
        v_column_list,
        v_column_list_with_t,
        p_tmp_table,
        p_base_table,
        v_pk_join,
        v_pk_array[1]
    );
    
    RAISE NOTICE 'Executing INSERT SQL: %', v_insert_sql;
    EXECUTE v_insert_sql;
    
    -- ===========================
    -- 2. UPDATE (変更レコード検出)
    -- ===========================
    IF v_diff_condition <> '' THEN
        v_update_sql := format(
            'INSERT INTO %I (%s, diff_type) ' ||
            'SELECT %s, ''U'' ' ||
            'FROM %I t ' ||
            'JOIN %I d ON %s ' ||
            'WHERE %s',
            v_diff_table,
            v_column_list,
            v_column_list_with_t,
            p_tmp_table,
            p_base_table,
            v_pk_join,
            v_diff_condition
        );
        
        RAISE NOTICE 'Executing UPDATE SQL: %', v_update_sql;
        EXECUTE v_update_sql;
    ELSE
        RAISE NOTICE 'No diff columns configured for %. Skipping UPDATE detection.', p_base_table;
    END IF;
    
    -- ===========================
    -- 3. DELETE (削除レコード検出)
    -- ===========================
    v_delete_sql := format(
        'INSERT INTO %I (%s, diff_type) ' ||
        'SELECT %s, ''D'' ' ||
        'FROM %I d ' ||
        'LEFT JOIN %I t ON %s ' ||
        'WHERE t.%I IS NULL',
        v_diff_table,
        v_column_list,
        array_to_string(
            ARRAY(SELECT 'd.' || unnest FROM unnest(v_all_columns)),
            ', '
        ),
        p_base_table,
        p_tmp_table,
        v_pk_join,
        v_pk_array[1]
    );
    
    RAISE NOTICE 'Executing DELETE SQL: %', v_delete_sql;
    EXECUTE v_delete_sql;
    
    RAISE NOTICE 'Diff detection completed for table: %', p_base_table;
END;
$procedure$
;
