# find "data/mods" -name '*.json' -type f -print0 y| xargs -0 -n1 sh -c '
#      tmp=$(mktemp)
#      jq -f tools/convert_run_eoc_selector.jq "$1" > "$tmp" && mv "$tmp" "$1"
#    ' sh

def transform_selector:
  if (type == "object"
      and has("run_eoc_selector")
      and (.run_eoc_selector | type == "array")
      and (.run_eoc_selector[0] | type == "string")
      and has("names")
      and has("keys")
      and has("descriptions"))
    then
. as $source
| $source
| {
    run_eoc_selector:
      [ range(0; .run_eoc_selector | length) as $i
      | {
          eocs: [ .run_eoc_selector[$i] ],
          name: .names[$i],
          key: .keys[$i],
          description: .descriptions[$i]
        }
        + ( if $source.variables != null then { variables: $source.variables } else {} end )
      ]
  }
  + ($source | del(.run_eoc_selector, .names, .keys, .descriptions, .variables))
  else
    .
  end;

walk(transform_selector)