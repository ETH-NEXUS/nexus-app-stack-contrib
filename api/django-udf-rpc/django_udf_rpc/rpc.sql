CREATE OR REPLACE FUNCTION constant.select_function_return_table(function TEXT, parameters TEXT[]) RETURNS TABLE(
  id TEXT,
  column_name TEXT,
  column_type TEXT,
  column_number INT4
) AS $$
  SELECT t.column_name AS id, t.column_name, t.column_type::REGTYPE::TEXT, t.column_number
    FROM pg_proc AS p
      CROSS JOIN unnest(proargnames, proargmodes, proallargtypes)
        WITH ORDINALITY AS t(column_name, arg_mode, column_type, column_number)
    WHERE p.oid = (
      SELECT f.oid
        FROM (
          SELECT a.oid, (
                SELECT array_agg(t.arg_name)
                  FROM pg_proc AS b
                    CROSS JOIN unnest(proargnames, proargmodes) AS t(arg_name, arg_mode)
                  WHERE b.oid = a.oid
                    AND t.arg_mode = 'i'
                  GROUP BY b.oid
              ) AS arg_names
            FROM pg_proc AS a
              WHERE a.proname = function
        ) AS f
        WHERE
          CASE
            WHEN array_length(parameters, 1) IS NULL THEN arg_names IS null
            ELSE f.arg_names = parameters
          END
      )
      AND t.arg_mode = 't'
    ORDER BY t.column_number
$$ LANGUAGE SQL STABLE;

GRANT EXECUTE ON FUNCTION constant.select_function_return_table TO constant_external;
