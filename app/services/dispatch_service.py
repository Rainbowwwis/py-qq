"""就近调度服务：候选救护员筛选与排序。

骨架阶段用球面距离（Haversine）+ 简单加权排序，后续可替换为
地图服务（高德/腾讯位置服务）的路径规划距离与真实通行时间。
"""

import math

from ..extensions import db
from ..models import RescuerProfile, VerifyStatus


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """两点间球面距离（公里）。"""
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return 2 * radius * math.asin(math.sqrt(a))


def find_candidates(
    latitude: float,
    longitude: float,
    limit: int = 5,
    max_radius_km: float | None = None,
) -> list[dict]:
    """筛选在线、已认证、且在服务半径内的救护员，按距离优先、评分次之排序。"""

    profiles = (
        db.session.query(RescuerProfile)
        .filter(
            RescuerProfile.online.is_(True),
            RescuerProfile.verify_status == VerifyStatus.APPROVED,
            RescuerProfile.latitude.isnot(None),
            RescuerProfile.longitude.isnot(None),
        )
        .all()
    )

    candidates = []
    for profile in profiles:
        distance = haversine_km(latitude, longitude, profile.latitude, profile.longitude)
        radius = max_radius_km if max_radius_km is not None else profile.service_radius_km
        if distance > radius:
            continue
        candidates.append(
            {
                'rescuer_id': profile.user_id,
                'name': profile.user.name if profile.user else '',
                'cert_type': profile.cert_type,
                'distance_km': round(distance, 2),
                'rating': profile.rating,
                'finished_orders': profile.finished_orders,
                # 综合分：距离越近越好，评分越高越好（后续可加入历史接单速度）
                'score': profile.rating - distance * 0.5,
            }
        )

    candidates.sort(key=lambda item: item['score'], reverse=True)
    return candidates[:limit]
