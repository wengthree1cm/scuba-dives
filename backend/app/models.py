from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from sqlalchemy.sql import func
from .db import Base  # 按你项目里数据库模块的相对导入保持不变

class DiveLog(Base):
    __tablename__ = "dive_logs"

    id = Column(Integer, primary_key=True, index=True)

    # ====== 保留的“必需信息”列 ======
    # 日期时间
    dive_time = Column(DateTime, nullable=False, index=True)
    # 个人潜水编号
    dive_number = Column(Integer, nullable=False, index=True)
    # 国家（前端做下拉，本列就是字符串）
    country = Column(String(100), nullable=False, index=True)
    # 地理区域/地点（城市/海域/岛）
    location = Column(String(255), nullable=False, index=True)
    # 潜点名（自由输入）
    site_name = Column(String(255), nullable=False, index=True)
    # 同伴签名/姓名
    buddy = Column(String(255), nullable=True)

    # 最大深度（米）
    max_depth_m = Column(Float, nullable=False, default=0.0)
    # 水下时间（分钟）
    bottom_time_min = Column(Integer, nullable=False, default=0)

    # 气瓶压力（单位你在前端标注 bar 或 psi）
    air_start = Column(Integer, nullable=True)  # 起始压力
    air_end = Column(Integer, nullable=True)    # 结束压力

    # 备注
    notes = Column(Text, nullable=True)

    # 审计字段
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

# 索引（按检索习惯）
Index("idx_dive_time_desc", DiveLog.dive_time.desc())
Index("idx_dive_number", DiveLog.dive_number)
Index("idx_country", DiveLog.country)
Index("idx_location", DiveLog.location)
Index("idx_site_name", DiveLog.site_name)
