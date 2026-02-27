#!/usr/bin/env bash
# Regenerate Pydantic models from the OpenAPI specs.
# Run this whenever the API specs are updated:
#   uv run scripts/generate_models.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

CODEGEN_ARGS=(
  --input-file-type openapi
  --output-model-type pydantic_v2.BaseModel
  --snake-case-field
  --target-python-version 3.12
  --use-field-description
)

HEADER="# Auto-generated from the NS OpenAPI spec. Do not edit manually.\n# To regenerate, run: uv run scripts/generate_models.sh\n"

generate() {
  local input="$1"
  local output="$2"
  echo "Generating $output from $input..."
  uv run datamodel-codegen "${CODEGEN_ARGS[@]}" --input "$input" --output "$output"
  printf "$HEADER" | cat - "$output" > "$output.tmp" && mv "$output.tmp" "$output"
}

generate \
  "$PROJECT_ROOT/api-definitions/disruptions-api.json" \
  "$PROJECT_ROOT/py_ns/models/disruptions.py"

generate \
  "$PROJECT_ROOT/api-definitions/reisinformatie-api.json" \
  "$PROJECT_ROOT/py_ns/models/travel.py"

generate \
  "$PROJECT_ROOT/api-definitions/nsapp-stations-api.json" \
  "$PROJECT_ROOT/py_ns/models/stations.py"

DISRUPTIONS="$PROJECT_ROOT/py_ns/models/disruptions.py"
TRAVEL="$PROJECT_ROOT/py_ns/models/travel.py"
STATIONS="$PROJECT_ROOT/py_ns/models/stations.py"

# Patch: use extra='ignore' instead of extra='forbid' on all models.
# A client library should not crash when the API adds or returns unexpected fields.
sed -i "s/extra='forbid'/extra='ignore'/g" "$DISRUPTIONS"
sed -i "s/extra='forbid'/extra='ignore'/g" "$TRAVEL"

# Patch: datamodel-codegen incorrectly applies discriminator to non-union fields
# when the OpenAPI spec has a `type` property. Remove the incorrect annotations.
sed -i "s/styles: Styles | None = Field(None, discriminator='type')/styles: Styles | None = None  # discriminator removed: Styles is not a union type/" "$TRAVEL"
sed -i "s/product: Product | None = Field(None, discriminator='product_type')/product: Product | None = None  # discriminator removed: Product is not a union type/" "$TRAVEL"

# Patch: Product (and ProductInterface) fields marked required in the spec but not
# always returned by the API. Make them optional to avoid ValidationErrors at runtime.
# The Product subclass re-declares these fields, so both classes need patching.
sed -i "s/notes: list\[list\[Note\]\]$/notes: list[list[Note]] | None = None  # patched: not always returned by the API/" "$TRAVEL"
sed -i "s/name_nes_properties: NesProperties = Field(\.\.\., alias='nameNesProperties')/name_nes_properties: NesProperties | None = Field(None, alias='nameNesProperties')  # patched: not always returned by the API/g" "$TRAVEL"
sed -i "s/product_type: str = Field(\.\.\., alias='productType')/product_type: str | None = Field(None, alias='productType')  # patched: not always returned by the API/" "$TRAVEL"
sed -i "s/product_type: Literal\['Product'\] = Field(\.\.\., alias='productType')/product_type: Literal['Product'] | None = Field(None, alias='productType')  # patched: not always returned by the API/" "$TRAVEL"

# Patch: RepresentationResponse meta fields — the spec declares dict[str, dict]
# but the API returns a flat dict (e.g. {"numberOfDisruptions": 3}).
sed -i "s/meta: dict\[str, dict\[str, Any\]\] | None = None/meta: dict[str, Any] | None = None  # patched: API returns flat dict, not nested/g" "$TRAVEL"

# Patch: Station fields marked required in the spec but not always returned
# when Station is embedded in journey/trip responses (only full station lookups
# return all fields).
sed -i "s/uic_code: str = Field(\.\.\., alias='UICCode')/uic_code: str | None = Field(None, alias='UICCode')  # patched: not always returned/" "$TRAVEL"
sed -i "s/station_type: str = Field(\.\.\., alias='stationType')/station_type: str | None = Field(None, alias='stationType')  # patched: not always returned/" "$TRAVEL"
sed -i "s/sporen: list\[Track\]$/sporen: list[Track] | None = None  # patched: not always returned/" "$TRAVEL"
sed -i "s/synoniemen: list\[str\]$/synoniemen: list[str] | None = None  # patched: not always returned/" "$TRAVEL"
sed -i "s/heeft_faciliteiten: bool = Field(\.\.\., alias='heeftFaciliteiten')/heeft_faciliteiten: bool | None = Field(None, alias='heeftFaciliteiten')  # patched: not always returned/" "$TRAVEL"
sed -i "s/heeft_vertrektijden: bool = Field(\.\.\., alias='heeftVertrektijden')/heeft_vertrektijden: bool | None = Field(None, alias='heeftVertrektijden')  # patched: not always returned/" "$TRAVEL"
sed -i "s/heeft_reisassistentie: bool = Field(\.\.\., alias='heeftReisassistentie')/heeft_reisassistentie: bool | None = Field(None, alias='heeftReisassistentie')  # patched: not always returned/" "$TRAVEL"

# Patch: use extra='ignore' instead of extra='forbid' on all stations models.
sed -i "s/extra='forbid'/extra='ignore'/g" "$STATIONS"

echo "Done."
