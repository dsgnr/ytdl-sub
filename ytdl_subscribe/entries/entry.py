from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional

from sanitize_filename import sanitize

from ytdl_subscribe.validators.base.string_formatter_validators import StringFormatterValidator
from ytdl_subscribe.validators.config.overrides.overrides_validator import OverridesValidator


@dataclass
class PlaylistMetadata:
    playlist_index: int
    playlist_id: str
    playlist_extractor: str


class BaseEntry(ABC):
    def __init__(self, **kwargs):
        """
        Initialize the entry using ytdl metadata
        """
        self._kwargs = kwargs

    def kwargs_contains(self, key: str) -> bool:
        """Returns whether internal kwargs contains the specified key"""
        return key in self._kwargs

    def kwargs(self, key) -> Any:
        """Returns an internal kwarg value supplied from ytdl"""
        if not self.kwargs_contains(key):
            raise KeyError(f"Expected '{key}' in {self.__class__.__name__} but does not exist.")
        return self._kwargs[key]

    @property
    def uid(self) -> str:
        """Returns the entry's unique id"""
        return self.kwargs("id")

    @property
    def extractor(self) -> str:
        """
        :return: The ytdl extrator name
        """
        return self.kwargs("extractor")

    @property
    def playlist_metadata(self) -> Optional[PlaylistMetadata]:
        """
        Reserved for any child entry class that resides in a playlist.

        :return: Playlist metadata for this entry
        """
        return None

    def to_dict(self) -> Dict[str, str]:
        """Returns the entry's values as a dictionary"""
        return {
            "uid": self.uid,
            "extractor": self.extractor,
        }

    def apply_formatter(
        self,
        formatter: StringFormatterValidator,
        overrides: Optional[OverridesValidator] = None,
    ) -> str:
        """
        Perform a string format on the given format string, using the entry's dict for format
        values. The override dict will overwrite any values within the entry's dict.
        """
        entry_dict = self.to_dict()
        if overrides:
            entry_dict = dict(entry_dict, **overrides.dict_with_format_strings)

        return formatter.apply_formatter(variable_dict=entry_dict)


class Entry(BaseEntry):
    """
    Entry object to represent a single media object returned from yt-dlp.
    """

    @property
    def title(self) -> str:
        """Returns the entry's title"""
        return self.kwargs("title")

    @property
    def sanitized_title(self) -> str:
        """Returns the entry's sanitized title"""
        return sanitize(self.title)

    @property
    def ext(self) -> str:
        """Returns the entry's file extension"""
        return self.kwargs("ext")

    @property
    def upload_date(self) -> str:
        """Returns the entry's upload date"""
        return self.kwargs("upload_date")

    @property
    def upload_year(self) -> int:
        """Returns the entry's upload year"""
        return int(self.upload_date[:4])

    @property
    def upload_month_padded(self) -> str:
        """Returns the entry's upload month, padded"""
        return self.upload_date[4:6]

    @property
    def upload_day_padded(self) -> str:
        """Returns the entry's upload day, padded"""
        return self.upload_date[6:8]

    @property
    def upload_month(self) -> int:
        """Returns the entry's upload month as an int"""
        return int(self.upload_month_padded.lstrip("0"))

    @property
    def upload_day(self) -> int:
        """Returns the entry's upload month as an int"""
        return int(self.upload_day_padded.lstrip("0"))

    @property
    def upload_date_standardized(self) -> str:
        """
        :return: upload date as YYYY-MM-DD
        """
        return f"{self.upload_year}-{self.upload_month_padded}-{self.upload_day_padded}"

    @property
    def description(self) -> str:
        return self.kwargs("description")

    @property
    def thumbnail(self) -> str:
        """Returns the entry's thumbnail url"""
        return self.kwargs("thumbnail")

    @property
    def thumbnail_ext(self) -> str:
        """Returns the entry's thumbnail extension"""
        return self.thumbnail.split(".")[-1]

    @property
    def download_file_name(self) -> str:
        """Returns the entry's file name when downloaded locally"""
        return f"{self.uid}.{self.ext}"

    @property
    def download_thumbnail_name(self) -> str:
        """Returns the thumbnail's file name when downloaded locally TODO: unit test this"""
        return f"{self.uid}.{self.thumbnail_ext}"

    def file_path(self, relative_directory: str):
        """Returns the entry's file path with respect to the relative directory"""
        return str(Path(relative_directory) / self.download_file_name)

    def thumbnail_path(self, relative_directory: str):
        """Returns the entry's thumbnail path with respect to the relative directory"""
        return str(Path(relative_directory) / self.download_thumbnail_name)

    def to_dict(self) -> Dict:
        """Returns the entry's values as a dictionary"""
        return dict(
            super().to_dict(),
            **{
                "title": self.title,
                "sanitized_title": self.sanitized_title,
                "description": self.description,
                "ext": self.ext,
                "upload_date": self.upload_date,
                "upload_date_standardized": self.upload_date_standardized,
                "upload_year": self.upload_year,
                "upload_month": self.upload_month,
                "upload_month_padded": self.upload_month_padded,
                "upload_day": self.upload_day,
                "upload_day_padded": self.upload_day_padded,
                "thumbnail": self.thumbnail,
                "thumbnail_ext": self.thumbnail_ext,
            },
        )
