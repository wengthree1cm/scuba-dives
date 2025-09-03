# backend/app/routes_mpa.py
from fastapi import APIRouter, Query, HTTPException
from fastapi.concurrency import run_in_threadpool
from functools import lru_cache
from shapely.geometry import shape, Point
import os, httpx

router = APIRouter(prefix="/api", tags=["mpa"])

# 必填：在部署环境（Render、本地 .env）里设置 MPA_GEOJSON_URL=https://.../mpa.geojson
MPA_GEOJSON_URL = os.getenv("MPA_GEOJSON_URL")

if not MPA_GEOJSON_URL:
    # 启动时就报错更早暴露问题；也可以换成延迟检查
    raise RuntimeError("Environment variable MPA_GEOJSON_URL is not set.")

@lru_cache(maxsize=1)
def _load_mpa() -> dict:
    """
    仅从远程 URL 加载一次并缓存（进程级）。服务重启或代码变更后会重新加载。
    """
    try:
        with httpx.Client(timeout=httpx.Timeout(30.0)) as client:
            r = client.get(MPA_GEOJSON_URL)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        # 统一抛 500，由路由层转成 HTTPException
        raise RuntimeError(f"failed_to_fetch_mpa_from_url: {e}") from e

def _point_in_polygons(lon: float, lat: float, gj: dict):
    pt = Point(lon, lat)
    hits = []
    for feat in gj.get("features", []):
        try:
            geom = shape(feat["geometry"])
            if geom.contains(pt):
                props = feat.get("properties", {}) or {}
                hits.append({
                    "name": props.get("name") or props.get("NAME") or "Protected Area",
                    "category": props.get("category") or props.get("IUCN_CAT"),
                    "id": props.get("id") or props.get("WDPAID")
                })
        except Exception:
            # 跳过坏几何
            continue
    return hits

@router.get("/mpa-alert")
async def mpa_alert(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
):
    try:
        gj = _load_mpa()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # shapely 计算放线程池，避免阻塞事件循环
    hits = await run_in_threadpool(_point_in_polygons, lon, lat, gj)
    return {"ok": True, "count": len(hits), "areas": hits}
