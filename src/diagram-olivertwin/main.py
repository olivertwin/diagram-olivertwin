from typing import Any
from N2G import drawio_diagram  # type: ignore
import logging
import re
from ttp import ttp  # type: ignore


# logger
logger = logging.getLogger("logger:")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("log/connection.log", "a", encoding="UTF-8")
log_format = logging.Formatter("%(asctime)s � %(name)s � %(levelname)s � %(message)s", datefmt="%D-%H:%M:%S")
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)


def lldp_file_reader(lldp_file: str, parse_template: str) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    """Parsing raw output from a file using a template. In the output we get lists of hosts and lists of connects

    Args:
        (lldp_file: str, parse_template: str) - Path to file and path to ttp-template.

    Raises:
        ValueError: if unknown or empty parameters are passed

    Returns:
       tuple[list[str], list[str]] - remove the duplicates and get back two lists
    """
    device_list: list = []
    connections_list: list = []
    duplicate_device_list: list = []

    parser = ttp(data=lldp_file, template=parse_template)
    parser.parse()
    result = parser.result()[0][0]

    identity = set_id("asw-01")
    main_device = {"id": identity, "label": "asw-01", "style": "./l3_switch"}
    device_list.append(main_device)
    for connect in result:
        if "Interface " in connect.get("id_type"):
            identity = set_id(connect.get("destinationNodeID"))
            attribute = set_attr(connect.get("destinationLabel"), identity)
            connection = {
                "source": "asw-01",
                "target": connect.get("destinationNodeID"),
                "src_label": connect.get("sourceLabel"),
                "trgt_label": connect.get("destinationLabel"),
                "style": attribute,
            }

            device = {
                "id": identity,
                "label": connect.get("destinationNodeID"),
            }
            if device["id"] not in duplicate_device_list:
                duplicate_device_list.append(device["id"])
                device_list.append(device)
            connections_list.append(connection)
    return device_list, connections_list


def set_id(sysname) -> str:
    ident = re.findall(r"\w+-\d+", sysname)[0]
    if ident:
        return ident
    else:
        raise ValueError("no sysname param")


def set_attr(end_point: str, dev_id: str) -> str:
    compare_part = "endArrow=none;"
    edge = ""
    entry_point = ""
    exit_point = ""
    if end_point == "MEth0/0/0":
        edge = "edgeStyle=orthogonalEdgeStyle;rounded=0;"
        if "01" in dev_id:
            entry_point = "entryX=0;entryDx=0;entryY=0.5;entryDy=0;"
            exit_point = "exitX=0;exitY=0.25;exitDx=0;exitDy=0;"
        else:
            entry_point = "entryX=1;entryDx=0;entryY=0.5;entryDy=0;"
            exit_point = "exitX=1;exitY=0.25;exitDx=0;exitDy=0;"

    elif end_point == "GigabitEthernet0/0/0" and "rt-" in dev_id:
        edge = "edgeStyle=orthogonalEdgeStyle;rounded=0;"
        if "01" in dev_id:
            entry_point = "entryX=0;entryDx=0;entryY=0.5;entryDy=0;"
            exit_point = "exitX=0;exitY=0.5;exitDx=0;exitDy=0;"
        else:
            entry_point = "entryX=1;entryDx=0;entryY=0.5;entryDy=0;"
            exit_point = "exitX=1;exitY=0.5;exitDx=0;exitDy=0;"

    elif "0/0/1" in end_point:
        if "usg" in dev_id:
            entry_point = "entryX=0.75;entryDx=0;entryY=1;entryDy=0;"
            exit_point = "exitX=0.5;exitY=0;exitDx=0;exitDy=0;"
        elif "rt" in dev_id:
            entry_point = "entryX=0.75;entryDx=0;entryY=0;entryDy=0;"
            exit_point = "exitX=0.5;exitY=1;exitDx=0;exitDy=0;"

    elif "0/0/2" in end_point or ("0/0/0" in end_point and "usg" in dev_id):
        if "usg" in dev_id:
            entry_point = "entryX=0.5;entryDx=0;entryY=1;entryDy=0;"
            exit_point = "exitX=0.5;exitY=0;exitDx=0;exitDy=0;"
        elif "rt" in dev_id:
            entry_point = "entryX=0.5;entryDx=0;entryY=0;entryDy=0;"
            exit_point = "exitX=0.5;exitY=1;exitDx=0;exitDy=0;"

    elif "0/0/8" in end_point:
        edge = "edgeStyle=orthogonalEdgeStyle;rounded=0;"
        if "01" in dev_id:
            entry_point = "entryX=0;entryDx=0;entryY=0.25;entryDy=0;"
            exit_point = "exitX=0;exitY=0.75;exitDx=0;exitDy=0;"
        elif "02" in dev_id:
            entry_point = "entryX=1;entryDx=0;entryY=0.25;entryDy=0;"
            exit_point = "exitX=1;exitY=0.75;exitDx=0;exitDy=0;"

    elif "0/0/9" in end_point:
        edge = "dashed=1;"
        if "01" in dev_id:
            entry_point = "entryX=0;entryDx=0;entryY=0;entryDy=0;"
            exit_point = "exitX=0;exitY=0.75;exitDx=0;exitDy=0;"
        elif "02" in dev_id:
            entry_point = "entryX=1;entryDx=0;entryY=0;entryDy=0;"
            exit_point = "exitX=1;exitY=0.75;exitDx=0;exitDy=0;"
    else:
        exit_point = "exitX=0.5;exitY=1;exitDx=0;exitDy=0;"

    new_style = compare_part + entry_point + exit_point + edge
    return new_style


def diagram_from_file(
    raw_data_file: str = "./lldp.txt",
    template_file: str = "./lldp.ttp",
) -> None:
    devices, connections = lldp_file_reader(raw_data_file, template_file)
    simple_graph = {
        "node": devices,
        "links": connections,
    }
    logger.info("Process diagram-olivertwin...")
    new_device = "asw-01"
    diagram = drawio_diagram()
    diagram.from_dict(
        simple_graph,
        width=1000,
        height=800,
        diagram_name=f"{new_device}",
    )
    diagram.layout(algo="circle")
    logger.info("Drop diagram-olivertwin...")
    diagram.dump_file(filename=f"{new_device}.drawio", folder="./")
    logger.info("The task completes")


if __name__ == "__main__":
    logger.info("Start script...")
    path_to_file = "./lldp.txt"
    ttp_template = "./lldp.ttp"
    diagram_from_file(path_to_file, ttp_template)
