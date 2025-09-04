from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Boolean
from sqlalchemy.orm import relationship

from .db import Base

# 新增：用户表（不影响你现有逻辑）
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 反向关系：一个用户有多条日志
    dives = relationship("DiveLog", back_populates="user", cascade="all, delete-orphan")


# ====== 下面是你原来的 DiveLog；我把常见字段都列出来了（含气瓶压力）======
# 如果你的字段与这里不同，请用你自己的字段，**不要删改你的字段**，
# 只需在末尾保留我标注的 user_id 和 user 两行即可。
class DiveLog(Base):
    __tablename__ = "divelogs"
    id = Column(Integer, primary_key=True, index=True)

    # —— 你原来的字段：保持不变（举例，含气瓶压力等常见字段；如与你不同，以你的为准）——
    date = Column(String(50), nullable=True)                   # 潜水日期（或使用 Date）
    country = Column(String(100), nullable=True)               # 国家
    site = Column(String(200), nullable=True)                  # 潜点
    entry_time = Column(String(20), nullable=True)             # 下水时间（可选）
    exit_time = Column(String(20), nullable=True)              # 出水时间（可选）
    bottom_time = Column(String(20), nullable=True)            # 底时，或分钟数
    max_depth = Column(String(20), nullable=True)              # 最大深度
    avg_depth = Column(String(20), nullable=True)              # 平均深度（可选）
    water_temp = Column(String(20), nullable=True)             # 水温
    visibility = Column(String(50), nullable=True)             # 能见度
    weather = Column(String(50), nullable=True)                # 天气
    current = Column(String(50), nullable=True)                # 流速/流况
    # —— 气瓶压力（你提到的“气瓶压力”已包含在内）——
    cylinder_pressure_start = Column(String(20), nullable=True)  # 起始气压（bar/psi）
    cylinder_pressure_end = Column(String(20), nullable=True)    # 结束气压（bar/psi）
    gas = Column(String(50), nullable=True)                    # 气体（Air/Nitrox…）
    tank_type = Column(String(50), nullable=True)              # 气瓶类型/容量
    weight = Column(String(20), nullable=True)                 # 配重
    suit = Column(String(50), nullable=True)                   # 潜衣类型
    computer = Column(String(100), nullable=True)              # 电脑/型号
    buddy = Column(String(100), nullable=True)                 # 搭档
    guide = Column(String(100), nullable=True)                 # 向导
    operator = Column(String(200), nullable=True)              # 俱乐部/船宿
    notes = Column(Text, nullable=True)                        # 备注/见闻
    rating = Column(String(10), nullable=True)                 # 评分
    # 你可能还有的其他列……全部保留即可
    # —— 结束 你原有字段 ——


    # 新增：把日志绑定到用户（**唯一必须新增的两行**）
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    user = relationship("User", back_populates="dives")
