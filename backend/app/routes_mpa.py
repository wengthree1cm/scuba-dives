# backend/app/routes_mpa.py
from fastapi import APIRouter, Query, HTTPException
from fastapi.concurrency import run_in_threadpool
from functools import lru_cache
import os, json, httpx
from shapely.geometry import shape, Point

router = APIRouter(prefix="/api", tags=["mpa"])

MPA_GEOJSON_URL = os.getenv("MPA_GEOJSON_URL")  # 在 Render 环境变量里设置
LOCAL_FALLBACK = "backend/data/mpa.geojson"     # 可选：项目内的备份

@lru_cache(maxsize=1)
def _load_mpa():
    # 优先 URL 拉取；失败用本地
    if MPA_GEOJSON_URL:
        try:
            r = httpx.get(MPA_GEOJSON_URL, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception:
            pass
    if os.path.exists(LOCAL_FALLBACK):
        with open(LOCAL_FALLBACK, "r", encoding="utf-8") as f:
            return json.load(f)
    raise RuntimeError("MPA GeoJSON not found")

def _point_in_polygons(lon: float, lat: float, gj: dict):
    pt = Point(lon, lat)
    hits = []
    for feat in gj.get("features", []):
        try:
            geom = shape(feat["geometry"])
            if geom.contains(pt):
                props = feat.get("properties", {})
                hits.append({
                    "name": props.get("name") or props.get("NAME") or "Protected Area",
                    "category": props.get("category") or props.get("IUCN_CAT"),
                    "id": props.get("id") or props.get("WDPAID")
                })
        except Exception:
            continue
    return hits

@router.get("/mpa-alert")
async def mpa_alert(lat: float = Query(..., ge=-90, le=90),
                    lon: float = Query(..., ge=-180, le=180)):
    try:
        gj = _load_mpa()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"mpa_load_error: {e}")

    # shapely 计算可能稍重，放线程池
    hits = await run_in_threadpool(_point_in_polygons, lon, lat, gj)
    return {"ok": True, "count": len(hits), "areas": hits}
