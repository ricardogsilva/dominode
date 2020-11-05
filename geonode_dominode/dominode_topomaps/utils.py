import re
import typing
from pathlib import Path

from django.conf import settings


def find_sheet(
        series: int,
        version: str,
        sheet_index: str
) -> typing.Optional[typing.Dict[str, Path]]:
    pattern = settings.DOMINODE_PUBLISHED_TOPOMAPS['sheet_path_pattern']
    sheet_pattern = Path(
        pattern.format(
            series=series, version=version, sheet=sheet_index)
    )
    result = {}
    sheet_dir = sheet_pattern.parent
    if sheet_dir.is_dir():
        for item in sheet_pattern.parent.iterdir():
            re_obj = re.match(sheet_pattern.name, item.name)
            if re_obj is not None:
                size = re_obj.group('paper_size')
                result[size] = item
    return result or None