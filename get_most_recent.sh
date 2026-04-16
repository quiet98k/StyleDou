#!/usr/bin/env bash

set -euo pipefail

checkpoint_dir=${1:-}
output_dir=${2:-most_recent_model}

if [[ -z "$checkpoint_dir" ]]; then
	echo "Usage: $0 <checkpoint_dir> [output_dir]" >&2
	exit 1
fi

if [[ ! -d "$checkpoint_dir" ]]; then
	echo "Checkpoint directory not found: $checkpoint_dir" >&2
	exit 1
fi

latest_ckpt() {
	local prefix=$1
	local latest

	latest=$(find "$checkpoint_dir" -maxdepth 1 -type f -name "${prefix}*.ckpt" | sort -V | tail -n 1)
	if [[ -z "$latest" ]]; then
		echo "Missing checkpoint matching ${prefix}*.ckpt in $checkpoint_dir" >&2
		exit 1
	fi
	printf '%s\n' "$latest"
}

latest_ckpt_optional() {
	local prefix=$1
	local latest

	latest=$(find "$checkpoint_dir" -maxdepth 1 -type f -name "${prefix}*.ckpt" | sort -V | tail -n 1)
	printf '%s\n' "$latest"
}

landlord_path=$(latest_ckpt landlord_weights_)
landlord_up_path=$(latest_ckpt landlord_up_weights_)
landlord_down_path=$(latest_ckpt landlord_down_weights_)
style_landlord_path=$(latest_ckpt_optional style_landlord_weights_)
style_landlord_up_path=$(latest_ckpt_optional style_landlord_up_weights_)
style_landlord_down_path=$(latest_ckpt_optional style_landlord_down_weights_)

printf '%s\n' "$landlord_path" "$landlord_up_path" "$landlord_down_path"
[[ -n "$style_landlord_path" ]] && printf '%s\n' "$style_landlord_path" "$style_landlord_up_path" "$style_landlord_down_path"

mkdir -p "$output_dir"

cp "$landlord_path" "$output_dir/landlord.ckpt"
cp "$landlord_up_path" "$output_dir/landlord_up.ckpt"
cp "$landlord_down_path" "$output_dir/landlord_down.ckpt"
if [[ -n "$style_landlord_path" ]]; then
	cp "$style_landlord_path" "$output_dir/style_landlord.ckpt"
	cp "$style_landlord_up_path" "$output_dir/style_landlord_up.ckpt"
	cp "$style_landlord_down_path" "$output_dir/style_landlord_down.ckpt"
fi
