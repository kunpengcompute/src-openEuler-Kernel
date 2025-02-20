#!/bin/bash
set -eo pipefail

kernelver="$1"
rootdir="$2"
modules_file="$3"

[[ -n "$kernelver" && -n "$rootdir" && -n "$modules_file" ]] || {
    echo "Usage: $0 kernelver rootdir modules_file" >&2
    exit 1
}

depmod -b "${rootdir}" "${kernelver}"

modules_dep="${rootdir}/lib/modules/${kernelver}/modules.dep"
[[ -f "${modules_dep}" ]] || { echo "Error: ${modules_dep} not found" >&2; exit 1; }

user_modules=()
while IFS= read -r line; do
    user_modules+=("$line")
done < "$modules_file"

all_deps=()

for module_rel in "${user_modules[@]}"; do
  all_deps+=("${module_rel}.ko")
  module_line=$(grep -m1 -P "^(\\./)?${module_rel}\.ko:" "${modules_dep}" || true)
  
  if [[ -z "${module_line}" ]]; then
    echo "Warning: Module ${module_rel} not found" >&2
    continue
  fi

  deps_string="${module_line#*:}"
  read -ra deps <<< "${deps_string}"

  for dep in "${deps[@]}"; do
    all_deps+=("${dep}")
  done
done

if [[ ${#all_deps[@]} -gt 0 ]]; then
  printf "%s\n" "${all_deps[@]}" | sort -u
fi
