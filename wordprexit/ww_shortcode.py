import re
import html2text



def do_ww(tag_atts, tag_contents):
    tag_contents = tag_contents.replace('<p>', '')
    tag_contents = tag_contents.replace('</p>', '')
    tag_contents = tag_contents.replace('<br>', '\n')
    tag_contents = tag_contents.replace('<br />', '\n')

    ww_item_symb = []
    ww_item_text = []
    ww_item_count = 0
    for l in tag_contents.strip().splitlines():
        match = re.search(r'^(\S)\s+(.*)', l)
        if match:
            ww_item_count += 1
            ww_item_symb.append(match.group(1))
            ww_item_text.append(match.group(2).strip())
        elif ww_item_count > 0:
            ww_item_text[ww_item_count - 1] = ww_item_text[
                ww_item_count - 1] + ' ' + l.strip()

    OUTPUTS = {
        '+': '{{% wwitem "+" %}}',
        '-': '{{% wwitem "-" %}}',
        '=': '{{% wwitem "=" %}}',
    }

    h = html2text.HTML2Text()
    tag_contents = ''
    for i in range(ww_item_count):
        tag_contents = tag_contents + OUTPUTS.get(
            ww_item_symb[i],
            '{{% wwitem unknown %}}') + h.handle(ww_item_text[i]).strip() + '{{% /wwitem %}}\n'

    return '{{% ww %}}\n' + tag_contents + '{{% /ww %}}\n'


TAGS_WE_CAN_PARSE = {
    'ww': do_ww,
}


def replace_tags(match):
    tag_name = match.group(2)
    tag_atts = match.group(3)
    tag_contents = match.group(5)
    if tag_name in TAGS_WE_CAN_PARSE:
        tag_atts = parse_shortcode_atts(tag_atts)
        return TAGS_WE_CAN_PARSE[tag_name](tag_atts, tag_contents)


def parse_shortcode_atts(atts):
    pattern = r'(\w+)\s*=\s*"([^"]*)"(?:\s|$)|(\w+)\s*=\s*\'([^\']*)\'(?:\s|$)|(\w+)\s*=\s*([^\s\'"]+)(?:\s|$)|"([^"]*)"(?:\s|$)|(\S+)(?:\s|$)'
    return re.findall(pattern, atts)


def parse(post_body):
    """
    I stole this shortcode regex from Wordpress's source.  It is very confusing.
    """
    tagregexp = '|'.join([re.escape(t) for t in TAGS_WE_CAN_PARSE.keys()])
    pattern = re.compile(
        '\\[(\\[?)(' + tagregexp +
        ')\\b([^\\]\\/]*(?:\\/(?!\\])[^\\]\\/]*)*?)(?:(\\/)\\]|\\](?:([^\\[]*(?:\\[(?!\\/\\2\\])[^\\[]*)*)\\[\\/\\2\\])?)(\\]?)'
    )
    return re.sub(pattern, replace_tags, post_body)
