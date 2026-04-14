"""
API Routes — REST endpoints for the TTS Text Normalization Framework.
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.api.schemas import (
    GenerateRequest,
    NormalizeRequest,
    ValidateRequest,
    SimulateRequest,
    ExportRequest,
)
from app.core.category_engine import CategoryEngine
from app.export.exporter import Exporter

router = APIRouter(prefix="/api")
engine = CategoryEngine()
exporter = Exporter()


# ======================================================================
# Language & Category Discovery
# ======================================================================

@router.get("/languages")
async def list_languages():
    """List all available languages."""
    return {"languages": engine.get_languages()}


@router.get("/languages/{locale}/categories")
async def list_categories(locale: str):
    """List available categories for a language."""
    try:
        categories = engine.get_categories(locale)
        return {"locale": locale, "categories": categories}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ======================================================================
# Rule Generation
# ======================================================================

@router.post("/generate")
async def generate_rules(request: GenerateRequest):
    """Generate rules (regex + DFA + SSML) for a language + category."""
    try:
        result = engine.generate_rules(request.locale, request.category)
        return result
    except (FileNotFoundError, KeyError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Rule generation failed: {str(e)}"
        )


# ======================================================================
# Text Normalization
# ======================================================================

@router.post("/normalize")
async def normalize_text(request: NormalizeRequest):
    """Apply rules to normalize input text."""
    try:
        result = engine.normalize_text(request.locale, request.category, request.text)
        return result
    except (FileNotFoundError, KeyError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Normalization failed: {str(e)}"
        )


# ======================================================================
# Validation
# ======================================================================

@router.post("/validate")
async def validate_rules(request: ValidateRequest):
    """Validate rules against test cases."""
    try:
        result = engine.validate_rules(
            request.locale, request.category, request.custom_tests
        )
        return result
    except (FileNotFoundError, KeyError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Validation failed: {str(e)}"
        )


# ======================================================================
# DFA Simulation
# ======================================================================

@router.post("/dfa/simulate")
async def simulate_dfa(request: SimulateRequest):
    """Simulate DFA execution step-by-step for visualization."""
    try:
        result = engine.simulate_dfa(
            request.locale, request.category, request.input_string
        )
        return result
    except (FileNotFoundError, KeyError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"DFA simulation failed: {str(e)}"
        )


# ======================================================================
# Export
# ======================================================================

@router.get("/export/dfa")
async def export_dfa(locale: str = Query(...), category: str = Query(...)):
    """Export DFA as JSON file."""
    try:
        rules = engine.generate_rules(locale, category)
        content = exporter.export_dfa_json(rules["dfa"])
        return StreamingResponse(
            content,
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="dfa_{locale}_{category}.json"'
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/ssml")
async def export_ssml(locale: str = Query(...), category: str = Query(...)):
    """Export SSML template as XML file."""
    try:
        rules = engine.generate_rules(locale, category)
        content = exporter.export_ssml_xml(rules["ssml"], locale, category)
        return StreamingResponse(
            content,
            media_type="application/xml",
            headers={
                "Content-Disposition": f'attachment; filename="ssml_{locale}_{category}.xml"'
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/regex")
async def export_regex(locale: str = Query(...), category: str = Query(...)):
    """Export regex pattern as text file."""
    try:
        rules = engine.generate_rules(locale, category)
        content = exporter.export_regex_txt(rules["regex"], locale, category)
        return StreamingResponse(
            content,
            media_type="text/plain",
            headers={
                "Content-Disposition": f'attachment; filename="regex_{locale}_{category}.txt"'
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/bundle")
async def export_bundle(locale: str = Query(...), category: str = Query(...)):
    """Export full rule bundle as ZIP file."""
    try:
        rules = engine.generate_rules(locale, category)
        content = exporter.export_zip_bundle(rules, locale, category)
        return StreamingResponse(
            content,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="rules_{locale}_{category}.zip"'
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
