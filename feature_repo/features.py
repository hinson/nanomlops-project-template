from datetime import timedelta

from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32, Int64

# 定义实体 (Entity)，例如用户 ID
driver = Entity(name="driver", join_keys=["driver_id"])

# 定义数据源 (此处示例为 Parquet 文件，实际生产通常连接数据仓库或 DVC 管理的文件)
driver_stats_source = FileSource(
    name="driver_hourly_stats_source",
    path="/home/jovyan/work/data/driver_stats.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
)

# 定义特征视图 (Feature View)
driver_hourly_stats_view = FeatureView(
    name="driver_hourly_stats",
    entities=[driver],
    ttl=timedelta(days=1),
    schema=[
        Field(name="conv_rate", dtype=Float32),
        Field(name="acc_rate", dtype=Float32),
        Field(name="avg_daily_trips", dtype=Int64),
    ],
    online=True,
    source=driver_stats_source,
    tags={"team": "driver_performance"},
)
