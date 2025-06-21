from functools import lru_cache
from urllib.parse import urlencode

NETBOX_URL: str = "https://demo.netbox.dev"


EXAMPLE_INPUT: dict[str, list[str]] = {
    "manufacturer": ["cisco"],
    "role": ["router", "core-switch", "access-switch"],
    "status": ["active", "offline"],
    "site": ["dm-akronsk", "dm-albany", "dm-camden"],
}

EXAMPLE_RESULT: list[tuple[str, int] | tuple[str, str]] = [
    ("manufacturer_id", 3),
    ("role_id", 1),
    ("role_id", 2),
    ("role_id", 4),
    ("status", "active"),
    ("status", "offline"),
    ("site_id", 2),
    ("site_id", 3),
    ("site_id", 6),
    ("brief", "true"),
    ("limit", 500),
]


@lru_cache
def _get_site_id(site_slug: str) -> int:
    """Stub for get site's id."""
    site_id = {
        "dm-akronsk": 2,
        "dm-albany": 3,
        "dm-binghamton": 4,
        "dm-buffalo": 5,
        "dm-camden": 6,
    }.get(site_slug)
    if site_id is None:
        raise ValueError(f"undefined site '{site_slug}'")
    return site_id


@lru_cache
def _get_device_role_id(device_role_slug: str) -> int:
    """Stub for get id role with slug."""
    device_role_id = {
        "router": 1,
        "core-switch": 2,
        "distribution-switch": 3,
        "access-switch": 4,
    }.get(device_role_slug)
    if device_role_id is None:
        raise ValueError(f"undefined devices role '{device_role_slug}'")
    return device_role_id


@lru_cache
def _get_manufacturer_id(manufacturer_slug: str) -> int:
    manufacturer_id = {
        "arista": 1,
        "cisco": 3,
        "juniper": 7,
    }.get(manufacturer_slug)
    if manufacturer_id is None:
        raise ValueError(f"неизвестный производитель '{manufacturer_slug}'")
    return manufacturer_id


def craft_nb_query(request_params: dict[str, list[str]]) -> list[tuple[str, str] | tuple[str, int]]:
    """Преобразование набора параметров в request params.

    Args:
        request_params (dict[str, str]): параметры запроса.
        ```python
        {
            "manufacturer": ["cisco"],
            "role": ["router"],
            "status": ["active", "offline"],
            "site": ["dm-akronsk", "dm-albany"],
        }
        ```

    Raises:
        ValueError: если переданы неизвестные или пустые параметры

    Returns:
        list[tuple[str, str | int]]: список кортежей из переданных параметров + brief и limit:
        ```python
        [
            ("manufacturer_id", 3),
            ("role", "router"),
            ("status", "active"),
            ("status", "offline"),
            ("site_id", 2),
            ("site_id", 3),
            ("brief", "true"),
            ("limit", 500),
        ]
        ```
    """
    if len(request_params) == 0:
        raise ValueError("don't get req parameters")

    q: list[tuple[str, str] | tuple[str, int]] = []
    for item_type, items in request_params.items():
        for item in items:
            if item_type == "name":
                new_name = "name_ie"
                new_id = item.lower()
            elif item_type == "status":
                new_name = "status"
                new_id = item
            elif item_type == "role":
                new_name = "role_id"
                new_id = _get_device_role_id(item)  # type: ignore
            elif item_type == "manufacturer":
                new_name = "manufacturer_id"
                new_id = _get_manufacturer_id(item)  # type: ignore
            elif item_type == "site":
                new_name = "site_id"
                new_id = _get_site_id(item)  # type: ignore
            else:
                raise ValueError("undefined parameter")
            q.append((new_name, new_id))
    q.append(("brief", "true"))
    q.append(("limit", 500))
    return q


if __name__ == "__main__":
    result = craft_nb_query(EXAMPLE_INPUT)
    assert result == EXAMPLE_RESULT, "func 'craft_nb_query' doesn't work"
    print(NETBOX_URL + "/api/dcim/devices/?" + urlencode(result))
