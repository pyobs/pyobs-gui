"""Work around a Nuitka/astropy incompatibility that breaks unit-string parsing in the
compiled standalone binary (see specs/plans/gui-widget-plugins-and-packaging.md).

astropy.units.format.generic builds its PLY grammar by having ``astropy.extern.ply.yacc``/
``lex`` walk the call stack with ``sys._getframe()`` to auto-discover the ``tokens``/``p_*``/
``t_*`` local variables defined inside ``Generic._parser``/``Generic._lexer``. Nuitka-compiled
function frames don't populate ``f_locals`` the way CPython's interpreted frames do, so that
walk finds no grammar and the very first ``import astropy.units`` (pulled in unconditionally by
pyobs-core's ``pyobs.utils.enums``) crashes with ``YaccError: Unable to build parser``. This is a
real, unresolved upstream limitation as of 2026-07, not a pyobs bug:
https://github.com/astropy/astropy/issues/15069
https://github.com/Nuitka/Nuitka/issues/2313

Fix: patch ``astropy.extern.ply.yacc.get_caller_module_dict``/``...lex.get_caller_module_dict``
(the two functions actually doing the broken frame walk) so that whenever the walk comes back
without a ``tokens`` entry, they fall back to a namespace we rebuild here from the same grammar
(copied verbatim from astropy.units.format.generic), handed to PLY in a way that doesn't need
frame introspection at all.

This has to patch at the ``astropy.extern.ply`` level, not by importing
``astropy.units.format.generic`` and monkeypatching ``Generic`` directly, because of a
bootstrapping deadlock: merely importing ``astropy.units.core``/``astropy.units.format.generic``
runs ``astropy/units/__init__.py``, which (via ``astropy.units.astrophys``, defining physical
constants) *already* triggers the broken parser during that very import -- before a class-level
patch could ever be installed. Patching ``get_caller_module_dict`` needs only
``astropy.extern.ply``, which has no dependency on ``astropy.units`` at all, so it's safe to
install before anything touches ``astropy.units``. The vendored grammar's own reference to
``astropy.units.core.Unit``/``CompositeUnit``/``Generic`` is resolved lazily, only when the
fallback actually fires -- by then we're already being called from inside
``Generic._parser``/``_lexer``'s own call chain, so those names are guaranteed importable.

Scoped to the generic unit format only -- the one format pyobs_gui is known to hit
unconditionally at startup. astropy's cds/ogip/vounit formats and astropy.coordinates.angles use
the same PLY pattern and would need the identical treatment if/when they're actually exercised in
the compiled binary.

Two caveats learned the hard way (pyobs-gui issue #151):

- **The patch must be a strict no-op under a regular interpreter.** The wrapper functions below
  add one stack frame, which shifts astropy's frame-level bookkeeping: ``astropy.utils.parsing``
  calls ``get_caller_module_dict(2)`` directly, and its own ``_patch_ply_module`` wrapper adds two
  more levels, so the extra frame makes the walk land on astropy's parsing wrapper instead of the
  grammar-defining frame -- the fallback fired on plain CPython and corrupted unit/coordinate
  parsing when running from source ("Invalid coordinates" in the Telescope widget, astropy units
  failing to import). Therefore the patched functions step one level deeper (``levels + 1``) to
  restore the original frame targeting, and ``patch_generic_unit_parser`` only installs at all
  when running under Nuitka (``"__compiled__" in globals()``); otherwise it returns immediately.
- **The vendored grammar must be a *registered* module.** PLY validates p-functions with
  ``inspect.getmodule()``/``getsourcefile()``, which resolve the function's ``__module__`` through
  ``sys.modules`` and want a real source file. ``_build_generic_grammar_namespace`` therefore
  registers the namespace under its name and materializes its ``__file__`` stub; without that the
  parser rebuild dies with "Unable to build parser" (``TypeError ... got NoneType``).

Must run before ``astropy.units`` is imported anywhere, i.e. as the first thing in
``pyobs_gui/__init__.py``.
"""

from __future__ import annotations

import re
import sys
import tempfile
import types
from fractions import Fraction
from pathlib import Path
from typing import Any

_generic_ns_cache: dict[str, types.ModuleType] = {}


def _build_generic_grammar_namespace() -> types.ModuleType:
    """Rebuild astropy.units.format.generic's PLY grammar as a plain namespace object.

    Only called lazily, from inside the ``get_caller_module_dict`` fallback below -- by that
    point ``astropy.units.core``/``astropy.units.format.generic`` are already far enough along
    to import from (see module docstring).
    """
    from astropy.units.core import CompositeUnit, Unit
    from astropy.units.format.generic import Generic

    cls = Generic
    tokens = cls._tokens

    # astropy.utils.parsing wants to write a generated tab-file cache next to __file__'s
    # directory. In a frozen binary, astropy/units/format/ isn't a real directory on disk (it's
    # compiled into the binary), so point this at a writable scratch directory instead --
    # writing there is harmless best-effort caching, not required for parsing to work.
    stub_dir = Path(tempfile.gettempdir()) / "pyobs_gui_astropy_ply_stub"
    stub_dir.mkdir(parents=True, exist_ok=True)

    # Typed as Any, not types.ModuleType: every t_*/p_* attribute below is bolted on
    # dynamically for PLY's benefit, which a real ModuleType's static shape can't express.
    ns: Any = types.ModuleType("_pyobs_gui_generic_grammar")
    ns.__file__ = str(stub_dir / "generic.py")
    ns.tokens = tokens

    # Register the namespace under its own name and materialize its __file__ so PLY's
    # grammar validation can resolve it: ParserReflect.get_pfunctions() calls
    # inspect.getmodule() on every p_* function (which looks the function's __module__ up
    # in sys.modules), and validate_pfunctions() calls inspect.getsourcefile() on the
    # result -- both need a real, registered module or the rebuild dies with
    # "Unable to build parser" / "TypeError: ... got NoneType".
    sys.modules.setdefault(ns.__name__, ns)
    (stub_dir / "generic.py").write_text(
        "# pyobs-gui: vendored astropy.units.format.generic PLY grammar (Nuitka workaround).\n",
        encoding="utf-8",
    )

    ns.t_COMMA = r"\,"
    ns.t_PRODUCT = "[*.]"
    ns.t_DIVISION = "/"
    ns.t_POWER = r"\^|(\*\*)"
    ns.t_OPEN_PAREN = r"\("
    ns.t_CLOSE_PAREN = r"\)"

    def t_UFLOAT(t):
        r"((\d+\.?\d*)|(\.\d+))([eE][+-]?\d+)?"
        if not re.search(r"[eE\.]", t.value):
            t.type = "UINT"
            t.value = int(t.value)
        elif t.value.endswith("."):
            t.type = "UINT"
            t.value = int(t.value[:-1])
        else:
            t.value = float(t.value)
        return t

    def t_UINT(t):
        r"\d+"
        t.value = int(t.value)
        return t

    def t_SIGN(t):
        r"[+-](?=\d)"
        t.value = int(t.value + "1")
        return t

    def t_FUNCNAME(t):
        r"((sqrt)|(ln)|(exp)|(log)|(mag)|(dB)|(dex))(?=\ *\()"
        return t

    def t_UNIT(t):
        r"[^\s\d+\-\./\*\^\(\)\,]+"
        t.value = cls._get_unit(t)
        return t

    ns.t_ignore = " "

    def t_error(t):
        raise ValueError(f"Invalid character at col {t.lexpos}")

    ns.t_UFLOAT = t_UFLOAT
    ns.t_UINT = t_UINT
    ns.t_SIGN = t_SIGN
    ns.t_FUNCNAME = t_FUNCNAME
    ns.t_UNIT = t_UNIT
    ns.t_error = t_error

    def p_main(p):
        """
        main : unit
             | structured_unit
             | structured_subunit
        """
        if isinstance(p[1], tuple):
            p[0] = p[1][0]
        else:
            p[0] = p[1]

    def p_structured_subunit(p):
        """
        structured_subunit : OPEN_PAREN structured_unit CLOSE_PAREN
        """
        p[0] = (p[2],)

    def p_structured_unit(p):
        """
        structured_unit : subunit COMMA
                        | subunit COMMA subunit
        """
        from astropy.units.structured import StructuredUnit

        inputs = (p[1],) if len(p) == 3 else (p[1], p[3])
        units = ()
        for subunit in inputs:
            if isinstance(subunit, tuple):
                units += subunit
            elif isinstance(subunit, StructuredUnit):
                units += subunit.values()
            else:
                units += (subunit,)

        p[0] = StructuredUnit(units)

    def p_subunit(p):
        """
        subunit : unit
                | structured_unit
                | structured_subunit
        """
        p[0] = p[1]

    def p_unit(p):
        """
        unit : product_of_units
             | factor product_of_units
             | factor PRODUCT product_of_units
             | division_product_of_units
             | factor division_product_of_units
             | factor PRODUCT division_product_of_units
             | inverse_unit
             | factor inverse_unit
             | factor PRODUCT inverse_unit
             | factor
        """
        if len(p) == 2:
            p[0] = Unit(p[1])
        elif len(p) == 3:
            p[0] = CompositeUnit(p[1] * p[2].scale, p[2].bases, p[2].powers)
        elif len(p) == 4:
            p[0] = CompositeUnit(p[1] * p[3].scale, p[3].bases, p[3].powers)

    def p_division_product_of_units(p):
        """
        division_product_of_units : division_product_of_units DIVISION product_of_units
                                  | product_of_units
        """
        if len(p) == 4:
            p[0] = Unit(p[1] / p[3])
        else:
            p[0] = p[1]

    def p_inverse_unit(p):
        """
        inverse_unit : DIVISION unit_expression
        """
        p[0] = p[2] ** -1

    def p_factor(p):
        """
        factor : factor_fits
               | factor_float
               | factor_int
        """
        p[0] = p[1]

    def p_factor_float(p):
        """
        factor_float : signed_float
                     | signed_float UINT signed_int
                     | signed_float UINT POWER numeric_power
        """
        if cls.name == "fits":
            raise ValueError("Numeric factor not supported by FITS")
        if len(p) == 4:
            p[0] = p[1] * p[2] ** float(p[3])
        elif len(p) == 5:
            p[0] = p[1] * p[2] ** float(p[4])
        elif len(p) == 2:
            p[0] = p[1]

    def p_factor_int(p):
        """
        factor_int : UINT
                   | UINT signed_int
                   | UINT POWER numeric_power
                   | UINT UINT signed_int
                   | UINT UINT POWER numeric_power
        """
        if cls.name == "fits":
            raise ValueError("Numeric factor not supported by FITS")
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = p[1] ** float(p[2])
        elif len(p) == 4:
            if isinstance(p[2], int):
                p[0] = p[1] * p[2] ** float(p[3])
            else:
                p[0] = p[1] ** float(p[3])
        elif len(p) == 5:
            p[0] = p[1] * p[2] ** p[4]

    def p_factor_fits(p):
        """
        factor_fits : UINT POWER OPEN_PAREN signed_int CLOSE_PAREN
                    | UINT POWER OPEN_PAREN UINT CLOSE_PAREN
                    | UINT POWER signed_int
                    | UINT POWER UINT
                    | UINT SIGN UINT
                    | UINT OPEN_PAREN signed_int CLOSE_PAREN
        """
        if p[1] != 10:
            if cls.name == "fits":
                raise ValueError("Base must be 10")
            else:
                return
        if len(p) == 4:
            if p[2] in ("**", "^"):
                p[0] = 10 ** p[3]
            else:
                p[0] = 10 ** (p[2] * p[3])
        elif len(p) == 5:
            p[0] = 10 ** p[3]
        elif len(p) == 6:
            p[0] = 10 ** p[4]

    def p_product_of_units(p):
        """
        product_of_units : unit_expression PRODUCT product_of_units
                         | unit_expression product_of_units
                         | unit_expression
        """
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = p[1] * p[2]
        else:
            p[0] = p[1] * p[3]

    def p_unit_expression(p):
        """
        unit_expression : function
                        | unit_with_power
                        | OPEN_PAREN product_of_units CLOSE_PAREN
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[2]

    def p_unit_with_power(p):
        """
        unit_with_power : UNIT POWER numeric_power
                        | UNIT numeric_power
                        | UNIT
        """
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = p[1] ** p[2]
        else:
            p[0] = p[1] ** p[3]

    def p_numeric_power(p):
        """
        numeric_power : sign UINT
                      | OPEN_PAREN paren_expr CLOSE_PAREN
        """
        if len(p) == 3:
            p[0] = p[1] * p[2]
        elif len(p) == 4:
            p[0] = p[2]

    def p_paren_expr(p):
        """
        paren_expr : sign UINT
                   | signed_float
                   | frac
        """
        if len(p) == 3:
            p[0] = p[1] * p[2]
        else:
            p[0] = p[1]

    def p_frac(p):
        """
        frac : sign UINT DIVISION sign UINT
        """
        p[0] = Fraction(p[1] * p[2], p[4] * p[5])

    def p_sign(p):
        """
        sign : SIGN
             |
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = 1

    def p_signed_int(p):
        """
        signed_int : SIGN UINT
        """
        p[0] = p[1] * p[2]

    def p_signed_float(p):
        """
        signed_float : sign UINT
                     | sign UFLOAT
        """
        p[0] = p[1] * p[2]

    def p_function(p):
        """
        function : FUNCNAME OPEN_PAREN main CLOSE_PAREN
        """
        if p[1] == "sqrt":
            p[0] = p[3] ** 0.5
            return
        elif p[1] in ("mag", "dB", "dex"):
            function_unit = cls._validate_unit(p[1])
            if callable(function_unit):
                p[0] = function_unit(p[3])
                return

        raise ValueError(f"'{p[1]}' is not a recognized function")

    def p_error(p):
        raise ValueError()

    ns.p_main = p_main
    ns.p_structured_subunit = p_structured_subunit
    ns.p_structured_unit = p_structured_unit
    ns.p_subunit = p_subunit
    ns.p_unit = p_unit
    ns.p_division_product_of_units = p_division_product_of_units
    ns.p_inverse_unit = p_inverse_unit
    ns.p_factor = p_factor
    ns.p_factor_float = p_factor_float
    ns.p_factor_int = p_factor_int
    ns.p_factor_fits = p_factor_fits
    ns.p_product_of_units = p_product_of_units
    ns.p_unit_expression = p_unit_expression
    ns.p_unit_with_power = p_unit_with_power
    ns.p_numeric_power = p_numeric_power
    ns.p_paren_expr = p_paren_expr
    ns.p_frac = p_frac
    ns.p_sign = p_sign
    ns.p_signed_int = p_signed_int
    ns.p_signed_float = p_signed_float
    ns.p_function = p_function
    ns.p_error = p_error

    return ns


def _namespace_pdict(ns: types.ModuleType) -> dict[str, Any]:
    return {k: getattr(ns, k) for k in dir(ns)}


def patch_generic_unit_parser(*, compiled: bool | None = None) -> None:
    """Patch astropy.extern.ply's frame-walking helpers to fall back to our vendored grammar.

    Only intended for the Nuitka-compiled standalone binary. Under a regular interpreter the
    original frame walk always finds the grammar, and installing the wrapper would *shift* the
    walk by one stack frame and break astropy's parsing (see module docstring / pyobs-gui issue
    #151), so unless ``compiled`` is true this is a strict no-op.

    Pass ``compiled`` as ``"__compiled__" in globals()`` evaluated in the entry package
    (``pyobs_gui/__init__.py``), which is guaranteed to be compiled in the binary. When left as
    None the marker is checked in this module's own globals instead.
    """
    if compiled is None:
        compiled = "__compiled__" in globals()
    if not compiled:
        return

    from astropy.extern.ply import lex as ply_lex
    from astropy.extern.ply import yacc as ply_yacc

    original_yacc_dict = ply_yacc.get_caller_module_dict
    original_lex_dict = ply_lex.get_caller_module_dict

    def _fallback_pdict(pdict: dict[str, Any] | None) -> dict[str, Any]:
        # Only the *generic unit* format's grammar is vendored here. astropy's other PLY
        # grammars (angle/cds/ogip/vounit) would need the identical treatment, and feeding
        # them the generic grammar would silently parse with the wrong productions (that is
        # exactly how the binary's coordinate parsing broke: the angle parser got the unit
        # grammar). For any other grammar return the broken-locals pdict unchanged so the
        # build fails loudly instead of corrupting results.
        if pdict is not None and pdict.get("__name__") != "astropy.units.format.generic":
            return dict(pdict)
        # Keep whatever the real (possibly broken-locals) pdict already has -- __file__/
        # __package__/__name__ are module globals and come through fine even on a compiled
        # frame -- and only supplement the missing tokens/p_*/t_* grammar entries. Replacing
        # __file__ wholesale would point astropy's tab-file bookkeeping at the wrong directory.
        if "ns" not in _generic_ns_cache:
            _generic_ns_cache["ns"] = _build_generic_grammar_namespace()
        merged = dict(pdict) if pdict else {}
        merged.update(_namespace_pdict(_generic_ns_cache["ns"]))
        return merged

    def patched_yacc_dict(levels: int) -> dict[str, Any]:
        try:
            # Our wrapper adds one frame compared with the unpatched call chain (the original
            # walk is now called from here instead of directly from astropy's parsing.yacc /
            # _patch_ply_module wrapper), so step one level deeper to land on the same frame
            # the original walk would have inspected. Without this the fallback fires under
            # plain CPython and astropy's parsing breaks (pyobs-gui issue #151).
            pdict = original_yacc_dict(levels + 1)
        except Exception:
            return _fallback_pdict(None)
        if "tokens" not in pdict:
            return _fallback_pdict(pdict)
        return pdict

    def patched_lex_dict(levels: int) -> dict[str, Any]:
        try:
            pdict = original_lex_dict(levels + 1)
        except Exception:
            return _fallback_pdict(None)
        if "tokens" not in pdict:
            return _fallback_pdict(pdict)
        return pdict

    ply_yacc.get_caller_module_dict = patched_yacc_dict
    ply_lex.get_caller_module_dict = patched_lex_dict
