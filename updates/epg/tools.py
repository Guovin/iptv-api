import gzip
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime
from xml.dom import minidom


def write_to_xml(programmes, path):
    root = ET.Element('tv', attrib={'date': datetime.now().strftime("%Y%m%d%H%M%S +0800")})
    for channel_id, data in programmes.items():
        channel_elem = ET.SubElement(root, 'channel', attrib={"id": channel_id})
        display_name_elem = ET.SubElement(channel_elem, 'display-name', attrib={"lang": "zh"})
        display_name_elem.text = channel_id
        for prog in data:
            prog.set('channel', channel_id)
            root.append(prog)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(minidom.parseString(ET.tostring(root, 'utf-8')).toprettyxml(indent='\t', newl='\n'))


def compress_to_gz(input_path, output_path):
    with open(input_path, 'rb') as f_in:
        with gzip.open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
