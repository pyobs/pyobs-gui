# Plan: preserve typed structured-config choices and show their labels

Status: implemented; release and deployment pending.
Repos: pyobs-gui, pyobs-core.
Issue: [#211](https://github.com/pyobs/pyobs-gui/issues/211).
Shared contract and rollout: [core plan](../../pyobs-core/specs/plans/2026-10-14-typed-config-choices.md).
Companion: [portal plan](../../pyobs-portal/specs/plans/2026-10-14-typed-config-choices.md).

## Verified cause and intended behavior

`pyobs_gui/structuredconfigwidget.py::_build_editor` uses `QComboBox.addItems`,
`currentText`, and `setCurrentText` for enum choices. Its numeric spin boxes already
return numbers. Core currently stringifies Pydantic Literal values before the GUI
sees them, so a GUI-only cast is not sufficient.

With the coordinated core change, a synthetic choice `16416` can display
`Detector A` and submit integer `16416`. Labels come from capability metadata;
the widget remains generic and consumes no provider-specific label tables.

## Implementation checklist

- [x] Feature-detect optional typed `choices` records on `ConfigFieldSchema`,
      retaining compatibility with existing core versions and legacy string `options`.
- [x] Prefer `schema.choices` when present. Populate each combo entry with its display
      label and keep its original scalar value in an authoritative Python-side list
      indexed by combo index. Qt user data is also viable if tests establish exact
      scalar preservation; do not rely on QVariant's implicit conversions.
- [x] Get the selected value from that typed collection, never `currentText`. Use
      index-based change notifications so entries with identical labels remain distinct.
- [x] Set defaults/state/reset selection by scalar identity: bool differs from number,
      strings differ from numbers, and numerical int/float equality follows the shared
      JSON contract. Never match by display label or use `str(value)` as identity.
- [x] Preserve duplicate labels, `"1"` versus `1`, `True` versus `1`, and string codes
      such as `"001"`. Do not globally parse numeric-looking strings.
- [x] Define invalid/missing selection behavior explicitly: if a received value is not
      in the domain, preserve it with a visibly marked synthetic entry until the user
      chooses a legal value. Never silently retain the previous selection or choose the
      first entry. An empty domain needs a preserved raw value or a disabled editor;
      getting index -1 must not accidentally return the last allowed option.
- [x] Keep default fallback only for genuinely absent values. A received `None` for a
      non-null choice is a preserved invalid value, not a first-choice substitution.
      General nullable editor support is outside this fix.
- [x] With `choices=None`, render legacy `options` as string-valued choices as before.
      A numeric state value against a string-only legacy domain must remain visible
      as unsupported/unknown rather than being guessed into a type. Document that
      upgrading the producer is necessary for the numeric Literal fix.
- [x] Preserve descriptions, expert visibility, permissions, nested editors, apply/reset
      flow and incoming-state dirty suppression. Test payloads through the existing
      `_apply_config` proxy path. Avoid broad dirty-state or hidden-field refactoring.

## Tests and acceptance

Extend `tests/test_structuredconfigwidget.py` (confirm existing test helpers before
adding fixtures), exercising real Qt widgets with the existing headless test setup:

- [x] Typed integer/float/bool/string choices retain exact Python types on initial
      render, selection, state refresh, reset and apply. An unchanged numeric state
      must not become dirty solely because a combo returns text.
- [x] Labels render correctly, including the Unicode choice label. Duplicate labels and
      mixed typed values select by identity and trigger change handling by index.
- [x] Nested `main.detector` payload reaches the mocked `IStructuredConfig.set_config` as
      an integer; rejection/server validation behavior remains intact.
- [x] Plain integer/float editors still return numbers; old string-only capabilities
      still work. Partial/missing labels use raw display fallbacks from core.
- [x] Unknown value, None, empty options, invalid default, and invalid current index
      do not silently overwrite configuration with the first or last option.
- [ ] Run the affected Qt suite and repository lint/type checks. Against candidate
      installed core and model-provider versions, load a real representative configuration,
      change a numeric choice and a numeric scalar, Apply, observe published state, then Reset.
      Confirm no hardware operation beyond the explicitly authorized test environment.

## Deployment constraints

For the full typed-choice fix, the new core must be installed in the GUI environment and in the module's environment;
update standalone bundles as well as normal Python installations. Old core decoders ignore
unknown `choices`, and old `options: list[str]` decoding cannot recover numerical types.
New GUI + old producer is therefore only legacy-compatible, not a complete fix. Old
GUI + new producer continues to render string options and retains its old bug.

Readable labels additionally require the model provider to publish the shared
`x-pyobs-choices` metadata and the module to republish capabilities after restart.
Test typed choices without labels too, so the numeric fix can ship independently of
label deployment. Implementation and automated regression checks are complete; release and deployment remain pending.

## Implementation verification (2026-10-15)

- Full GUI suite: 311 passed. Structured-config regressions pass with both the
  installed legacy core and the candidate typed-choice core.
- Ruff and Pyrefly pass; changed Python files pass Black. Repository-wide Black
  reports existing differences in generated UI files and unrelated widgets.
- Candidate provider → core XML → Qt checks preserve numeric values and labels,
  including unlabeled bitmask combinations. No hardware operation was performed.
