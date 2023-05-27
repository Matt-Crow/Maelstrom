from abc import ABC, abstractmethod
from maelstrom.campaign.area import Area
from maelstrom.campaign.campaign import Campaign
from maelstrom.campaign.level import Level
from maelstrom.io.files import read_json_file
from maelstrom.io.folders import all_files_in

class AbstractCampaignLoader(ABC):
    """Loads campaigns from an external resource."""

    @abstractmethod
    def get(self, name: str) -> Campaign:
        """
        returns the Campaign with the given name, or None if no such Campaign 
        exists
        """
        pass

    @abstractmethod
    def get_all(self) -> 'list[Campaign]':
        """returns all available Campaigns"""
        pass

class InMemoryCampaignLoader(AbstractCampaignLoader):
    """Stores Campaigns in-memeory."""

    def __init__(self, campaigns: 'list[Campaign]' = []):
        """Creates a new CampaignLoader which can provide the given Campaigns."""
        self._campaigns = {campaign.name: campaign for campaign in campaigns}
    
    def get(self, name: str) -> Campaign:
        return self._campaigns.get(name)
    
    def get_all(self) -> 'list[Campaign]':
        return list(self._campaigns.values())
    
class JsonFolderCampaignLoader(AbstractCampaignLoader):
    """Loads campaigns from a folder containing JSON files"""

    def __init__(self):
        self._campaigns = dict()
        self._all_loaded = False
    
    def get(self, name: str) -> Campaign:
        if not name in self._campaigns:
            self._load_file(name)
        return self._campaigns.get(name)
    
    def get_all(self) -> 'list[Campaign]':
        if not self._all_loaded:
            self._load_all_files()
        return list(self._campaigns.values())
    
    def _load_file(self, name: str):
        self._add_campaign_from_path(f'data/campaigns/{name}.json')
    
    def _load_all_files(self):
        all_files = all_files_in('data/campaigns')
        for file in all_files:
            self._add_campaign_from_path(file)
        self._all_loaded = True
        
    def _add_campaign_from_path(self, path: str):
        as_json = read_json_file(path)
        as_json["areas"] = [self._load_area(area) for area in as_json["areas"]]
        campaign = Campaign(**as_json)
        self._campaigns[campaign.name] = campaign

    def _load_area(self, as_json: dict) -> Area:
        as_json['levels'] = [self._load_level(level) for level in as_json['levels']]
        return Area(**as_json)
    
    def _load_level(self, as_json: dict) -> Level:
        return Level(**as_json)


def make_default_campaign_loader() -> AbstractCampaignLoader:
    """Creates the default campaign loader used by the program."""
    return JsonFolderCampaignLoader()