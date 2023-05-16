from argparse import ArgumentParser
from typing import List, Optional, Sequence
import requests
import json as json_module
import xml.etree.ElementTree as element_tree


class UnhandledException(Exception):
    pass


def rss_parser(
        xml: str,
        limit: Optional[int] = None,
        json: bool = False,
) -> List[str]:

    if limit is not None and limit <= 0:
        raise UnhandledException("Limit must be greater than zero")

    root_xml = element_tree.fromstring(xml)
    result_list = []
    if json:
        result_list.append(get_json_output(root_xml, limit))
    else:
        result_list = get_standard_output(root_xml, limit)
    return result_list


def get_standard_output(rss_root, limit) -> List[str]:
    channels = rss_root.findall("channel")
    rss_list = []
    for channel in channels:
        rss_list.extend(get_standard_channel(channel))
        items = channel.findall("item")
        counter = 0
        if limit is None or limit >= len(items):
            limit = len(items)
        for item in items:
            if counter < limit:
                rss_list.extend(get_standard_item(item))
            counter += 1
    return rss_list


def get_standard_channel(channel) -> List[str]:
    rss_list = []
    if channel.find('title') is not None:
        rss_list.append(f"Feed: {channel.find('title').text}")
    if channel.find('link') is not None:
        rss_list.append(f"Link: {channel.find('link').text}")
    if channel.find('lastBuildDate') is not None:
        rss_list.append(f"Last Build Date: {channel.find('lastBuildDate').text}")
    if channel.find('pubDate') is not None:
        rss_list.append(f"Publish Date: {channel.find('pubDate').text}")
    if channel.find('language') is not None:
        rss_list.append(f"Language: {channel.find('language').text}")
    if channel.find('category') is not None:
        rss_list.append(f"Categories: {channel.find('category').text}")
    if channel.find('managinEditor') is not None:
        rss_list.append(f"Editor: {channel.find('managinEditor').text}")
    if channel.find('description') is not None:
        rss_list.append(f"Description: {channel.find('description').text}\n")
    return rss_list


def get_standard_item(item) -> List[str]:
    rss_list = []
    if item.find('title') is not None:
        rss_list.append(f"Title: {item.find('title').text}")
    if item.find('author') is not None:
        rss_list.append(f"Author: {item.find('author').text}")
    if item.find('pubDate') is not None:
        rss_list.append(f"Published: {item.find('pubDate').text}")
    if item.find('link') is not None:
        rss_list.append(f"Link: {item.find('link').text}")
    if item.find('category') is not None:
        rss_list.append(f"Categories: {item.find('category').text}")
    if item.find('description') is not None:
        rss_list.append(f"\n{item.find('description').text}\n")
    return rss_list


def get_json_output(rss_soup, limit) -> str:
    channels = rss_soup.findall("channel")
    data = {}
    for channel in channels:
        data.update(get_json_channel(channel))
        items = channel.findall("item")
        item_counter = 0
        if limit is None or limit >= len(items):
            limit = len(items)
        item_list = []
        for item in items:
            if item_counter < limit:
                item_list.append(get_json_item(item))
            item_counter += 1
        data["items"] = item_list
    json_formatted_str = json_module.dumps(data, indent=2)
    return json_formatted_str


def get_json_channel(channel) -> dict:
    data = {}
    if channel.find('title') is not None:
        data["title"] = channel.find('title').text
    if channel.find('link') is not None:
        data["link"] = channel.find('link').text
    if channel.find('lastBuildDate') is not None:
        data["lastBuildDate"] = channel.find('lastBuildDate').text
    if channel.find('pubDate') is not None:
        data["pubDate"] = channel.find('pubDate').text
    if channel.find('language') is not None:
        data["language"] = channel.find('language').text
    if channel.find('category') is not None:
        data["category"] = channel.find('category').text
    if channel.find('managinEditor') is not None:
        data["managinEditor"] = channel.find('managinEditor').text
    if channel.find('description') is not None:
        data["description"] = channel.find('description').text
    return data


def get_json_item(item) -> dict:
    data = {}
    if item.find('title') is not None:
        data["title"] = item.find('title').text
    if item.find('author') is not None:
        data["author"] = item.find('author').text
    if item.find('pubDate') is not None:
        data["pubDate"] = item.find('pubDate').text
    if item.find('link') is not None:
        data["link"] = item.find('link').text
    if item.find('category') is not None:
        data["category"] = item.find('category').text
    if item.find('description') is not None:
        data["description"] = item.find('description').text
    return data


def main(argv: Optional[Sequence] = None):
    """
    The main function of your task.
    """
    parser = ArgumentParser(
        prog="rss_reader",
        description="Pure Python command-line RSS reader.",
    )
    parser.add_argument("source", help="RSS URL", type=str, nargs="?")
    parser.add_argument(
        "--json", help="Print result as JSON in stdout", action="store_true"
    )
    parser.add_argument(
        "--limit", help="Limit news topics if this parameter provided", type=int
    )

    args = parser.parse_args(argv)
    xml = requests.get(args.source).text
    try:
        print("\n".join(rss_parser(xml, args.limit, args.json)))
        return 0
    except Exception as e:
        raise UnhandledException(e)


if __name__ == "__main__":
    main()