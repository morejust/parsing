import re

def merge_tags(html_tags_offsets):
    merged = []
    done_offsets = []
    for t1 in html_tags_offsets:
        if t1[0] in done_offsets:
            continue
        tags_with_same_offset = [t for o, t in html_tags_offsets if o == t1[0]]
        new_tag = "".join(tags_with_same_offset)
        merged.append((t1[0], new_tag))  
        done_offsets.append(t1[0])
    return merged

def unescape_xml_tags(text):
    # TODO: implement proper XML tags replace 
    # html_string = re.sub("&#?\w+;", "'", html_string)
    text = re.sub('&#8217;', "'", text)
    text = re.sub('&#160;', " ", text)
    text = re.sub('&#8230;', "…", text)
    return text
    

def extract_tags(html_string):
    html_string = unescape_xml_tags(html_string)
    
    raw_text = ""
    length_of_cutted_tokens = 0
    end_of_prev_token = 0
    html_tags_offsets = []
    for match in re.finditer('<.*?>', html_string):
        s, e, g = match.start(), match.end(), match.group()

        token = html_string[s: e]
        raw_text += html_string[end_of_prev_token: s] + ' '
        # TODO: save tags as dict: {'offset': , 'content': , 'type': 'html'}
        html_tags_offsets.append((len(raw_text), g))

        end_of_prev_token = match.end()
        length_of_cutted_tokens += len(token)

    html_tags_offsets = merge_tags(html_tags_offsets)

    return (html_tags_offsets, raw_text)


def insert_tags(html_tags_offsets, raw_text):
    text_with_html = raw_text
    for offset, tag_text in sorted(html_tags_offsets, key=lambda x: -x[0]):
        # -1 -> remove space that was added above
        text_with_html = text_with_html[:offset - 1] + tag_text + text_with_html[offset:]
    return text_with_html