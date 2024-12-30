prompt_keywords = r"""
You are a technical expert in generating keywords for searching Google Paptent Database for a given idea.
Return the list of comma seperated keywords for the following idea

**IDEA:** {topic}

**Note:**
1. Keywords should be comma seperated.
2. Do not add any comments except the keywords.
3. You can include most applicable synonymous technical terms for keywords.
"""

prompt_query = r"""
You are a technical expert in generating a effective query string for Google Patent Database Search 
for a given idea and also a set of keywords.
Return the list of comma seperated query string that can effectively return the list of best matched patents
from the patents.google.com patents database.

**IDEA:** {topic}

**Note:**
1. Query string should be comma seperated.
2. Do not add any comments except the query string.
3. At least three query string should be returned.
4. All keywords should be distributed in the complex queries.
5. You can use AND, OR, XOR, SAME, ADJ, NEAR, ), ( and more advance operator for generating query string.

**Output Format:**
((Wearable) AND (Noise Cancellation)),
((Wearable OR Mobile) AND (Noise (Cancellation OR Suppression))
"""