from difflib import SequenceMatcher 

def find_longest_substring(s1, s2): 
    # returns: offset according s1, substring itself
    seqMatch = SequenceMatcher(None, s1, s2) 
    match = seqMatch.find_longest_match(0, len(s1), 0, len(s2)) 
    
    if match.size != 0:  # found something
        return (match.a, s1[match.a: match.a + match.size])
    return None, None

def extract_facts(post):
    text = post["text"]
    summary = post["summary"]
    result = []
    while True:
        offset, substring = find_longest_substring(text, summary)
        if offset is None:
            break
        if len(substring) < 50:
            break
            
        result.append({ "offset": offset, "content": substring })

        summary = summary.replace(substring, "")    
        if len(summary) < 70:
            break

    return result