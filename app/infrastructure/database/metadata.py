from app.domains.data_pipeline.infrastructure.models import DataPipelineBase
from app.domains.map_configs.infrastructure.models import MapConfigBase
from app.domains.market_data.infrastructure.models import MarketDataBase
from app.domains.profiles.infrastructure.models import ProfileBase
from app.domains.searches.infrastructure.models import SearchBase

# Collect all metadata from the bounded contexts
target_metadata = [
    DataPipelineBase.metadata,
    MapConfigBase.metadata,
    MarketDataBase.metadata,
    ProfileBase.metadata,
    SearchBase.metadata,
]
