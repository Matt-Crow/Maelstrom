from abc import ABC, abstractmethod
import json
from genericpath import isfile
from typing import Optional
from maelstrom.campaign import Area, Campaign, Level
from os import listdir
from os.path import join

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

class JsonFolderCampaignLoader(AbstractCampaignLoader):
    """Loads campaigns from a folder containing JSON files"""

    def __init__(self):
        self._campaigns: dict[str,Campaign] = dict()
        self._all_loaded = False
    
    def get(self, name: str) -> Optional[Campaign]:
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
        all_files = _all_files_in('data/campaigns')
        for file in all_files:
            self._add_campaign_from_path(file)
        self._all_loaded = True
        
    def _add_campaign_from_path(self, path: str):
        as_json = _read_json_file(path)
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

def _all_files_in(folder: str) -> 'list[str]':
    """gets a path to all files in the given folder - not recursive"""
    all_files_and_folders = [join(folder, f) for f in listdir(folder)]
    all_files = [f for f in all_files_and_folders if isfile(f)]
    return all_files

def _read_json_file(path: str) -> dict:
    """reads the given JSON file and returns its contents"""
    with open(path, mode='r') as file:
        contents = file.read()
    as_json = json.loads(contents)
    return as_json