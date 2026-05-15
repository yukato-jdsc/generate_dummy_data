-- DROP PROCEDURE public.sp_merge_to_base(text, text, text, text);

CREATE OR REPLACE PROCEDURE public.sp_merge_to_base(IN p_tmp_table text, IN p_base_table text, IN p_diff_table text, IN p_primary_keys text)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
    v_pk_array TEXT[];
    v_pk_join TEXT;
    v_update_set TEXT;
    v_column_list TEXT;
    v_all_columns TEXT[];
    v_sql TEXT;
    i INTEGER;
BEGIN
    -- カンマ区切り文字列を配列に変換
    v_pk_array := string_to_array(regexp_replace(p_primary_keys, '\s+', '', 'g'), ',');
    
    -- ベーステーブルが存在しない場合は作成（初回実行時）
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = p_base_table
    ) THEN
        RAISE NOTICE 'Base table % does not exist. Creating from tmp table.', p_base_table;
        
        -- tmpテーブルからベーステーブルを作成
        v_sql := format(
            'CREATE TABLE %I AS SELECT * FROM %I',
            p_base_table,
            p_tmp_table
        );
        EXECUTE v_sql;
        
        -- プライマリキーを追加
        v_sql := format(
            'ALTER TABLE %I ADD PRIMARY KEY (%s)',
            p_base_table,
            p_primary_keys
        );
        EXECUTE v_sql;
        
        RAISE NOTICE 'Base table % created successfully.', p_base_table;
        RETURN;
    END IF;
    
    -- 全カラムリストを取得（diff_typeを除く）
    SELECT array_agg(column_name::TEXT ORDER BY ordinal_position)
    INTO v_all_columns
    FROM information_schema.columns
    WHERE table_name = p_base_table
      AND column_name != 'diff_type';
    
    v_column_list := array_to_string(v_all_columns, ', ');
    
    -- プライマリキー結合条件生成
    v_pk_join := '';
    FOR i IN 1..array_length(v_pk_array, 1) LOOP
        IF v_pk_join <> '' THEN
            v_pk_join := v_pk_join || ' AND ';
        END IF;
        v_pk_join := v_pk_join || 'b.' || v_pk_array[i] || ' = d.' || v_pk_array[i];
    END LOOP;
    
    -- UPDATE用のSET句生成（プライマリキー以外のカラム）
    v_update_set := '';
    FOR i IN 1..array_length(v_all_columns, 1) LOOP
        -- プライマリキーは除外
        IF NOT (v_all_columns[i] = ANY(v_pk_array)) THEN
            IF v_update_set <> '' THEN
                v_update_set := v_update_set || ', ';
            END IF;
            v_update_set := v_update_set || v_all_columns[i] || ' = d.' || v_all_columns[i];
        END IF;
    END LOOP;
    
    -- ===========================
    -- 1. INSERT（新規レコード）
    -- ===========================
    v_sql := format(
        'INSERT INTO %I (%s) SELECT %s FROM %I WHERE diff_type = ''I''',
        p_base_table,
        v_column_list,
        v_column_list,
        p_diff_table
    );
    
    RAISE NOTICE 'Executing INSERT: %', v_sql;
    EXECUTE v_sql;
    
    -- ===========================
    -- 2. UPDATE（変更レコード）
    -- ===========================
    IF v_update_set <> '' THEN
        v_sql := format(
            'UPDATE %I b SET %s FROM %I d WHERE %s AND d.diff_type = ''U''',
            p_base_table,
            v_update_set,
            p_diff_table,
            v_pk_join
        );
        
        RAISE NOTICE 'Executing UPDATE: %', v_sql;
        EXECUTE v_sql;
    END IF;
    
    -- ===========================
    -- 3. DELETE（削除レコード）
    -- ===========================
    v_sql := format(
        'DELETE FROM %I b USING %I d WHERE %s AND d.diff_type = ''D''',
        p_base_table,
        p_diff_table,
        v_pk_join
    );
    
    RAISE NOTICE 'Executing DELETE: %', v_sql;
    EXECUTE v_sql;
    
    RAISE NOTICE 'Merge to base table % completed successfully.', p_base_table;
END;
$procedure$
;
