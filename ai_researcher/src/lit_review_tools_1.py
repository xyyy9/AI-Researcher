import requests
import re

# Define the OpenAlex paper search endpoint URL
openalex_url = 'https://api.openalex.org/works'

def KeywordQuery(keyword):
    ## retrieve papers based on keywords
    query_params = {
        'search': keyword,
        'per-page': 20,  # Limit to 20 results like in the original code
    }
    response = requests.get(openalex_url, params=query_params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

def PaperQuery(paper_id):
    ## retrieve similar papers (OpenAlex doesn't have recommendations like S2, so we fetch paper details)
    response = requests.get(f"https://api.openalex.org/works/{paper_id}")
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

def PaperDetails(paper_id):
    ## get paper details based on paper id
    response = requests.get(f"https://api.openalex.org/works/{paper_id}")
    
    if response.status_code == 200:
        data = response.json()
        # Map fields to match the original request
        paper_details = {
            'title': data.get('title'),
            'year': data.get('publication_year'),
            'citationCount': data.get('cited_by_count'),
            'abstract': data.get('abstract'),
            # OpenAlex does not have tldr, leaving it as None
            'tldr': None,
            'id': data.get('id')
        }
        return paper_details
    else:
        return None
    
def reconstruct_abstract(abstract_inverted_index):
    """Reconstructs the abstract from the inverted index format."""
    if not abstract_inverted_index:
        return ""
    
    # Create a list with None placeholders for all words
    max_position = max([max(positions) for positions in abstract_inverted_index.values()])
    abstract_words = [None] * (max_position + 1)
    
    # Fill in the words in their correct positions
    for word, positions in abstract_inverted_index.items():
        for pos in positions:
            abstract_words[pos] = word
    
    # Join the words to form the original abstract, filtering out None
    return ' '.join([word for word in abstract_words if word is not None])

def GetAbstract(paper_id):
    ## get the abstract of a paper based on paper id
    paper_details = PaperDetails(paper_id)
    
    if paper_details is not None:
        return paper_details["abstract"]
    else:
        return None

def GetCitationCount(paper_id):
    ## get the citation count of a paper based on paper id
    paper_details = PaperDetails(paper_id)
    
    if paper_details is not None:
        return int(paper_details["citationCount"])
    else:
        return None

def GetCitations(paper_id):
    ## OpenAlex doesn't have citations listed directly like S2
    paper_details = PaperDetails(paper_id)
    
    if paper_details is not None:
        return paper_details.get('referenced_works', [])
    else:
        return None

def GetReferences(paper_id):
    ## get the reference list of a paper based on paper id
    paper_details = PaperDetails(paper_id)
    references = paper_details.get('referenced_works', [])
    
    ## get details of each reference, keep first 20 to save API requests
    detailed_references = [PaperDetails(ref.split('/')[-1]) for ref in references[:20]]
    
    if paper_details is not None:
        return detailed_references
    else:
        return None

def paper_filter(paper_lst):
    ## filter out papers based on more lenient heuristics
    filtered_lst = []
    for paper in paper_lst:
        # Extract the paper ID from the OpenAlex 'id' URL and store it as 'paperId'
        paper["paperId"] = paper.get("id", "").split('/')[-1]  # Extracts the paper ID from the URL
        
        # Get the abstract in inverted index format if available
        abstract_inverted_index = paper.get("abstract_inverted_index", None)
        
        # Reconstruct the abstract and store it in the paper dictionary
        paper["abstract"] = reconstruct_abstract(abstract_inverted_index) if abstract_inverted_index else ""
        
        # Debug: Print each paper's title and reconstructed abstract (or note if missing)
        title = paper.get("title", "")
        abstract = paper["abstract"]

        # Allow papers without abstracts, and filter based on title and abstract length
        if title and abstract and len(abstract.split()) > 50:
            # Optional: Keep filtering based on keywords in title
            if "survey" in title.lower() or "review" in title.lower() or "position paper" in title.lower():
                continue  # Skip these types of papers
            filtered_lst.append(paper)
    
    print(f"Filtered {len(filtered_lst)} papers from {len(paper_lst)} total.")  # Debug: Show how many papers are kept
    return filtered_lst




def dedup_paper_bank(sorted_paper_bank):
    idx_to_remove = []

    for i in reversed(range(len(sorted_paper_bank))):
        for j in range(i):
            if sorted_paper_bank[i]["id"].strip() == sorted_paper_bank[j]["id"].strip():
                idx_to_remove.append(i)
                break
            if ''.join(sorted_paper_bank[i]["title"].lower().split()) == ''.join(sorted_paper_bank[j]["title"].lower().split()):
                idx_to_remove.append(i)
                break
            if sorted_paper_bank[i]["abstract"] == sorted_paper_bank[j]["abstract"]:
                idx_to_remove.append(i)
                break
    
    deduped_paper_bank = [paper for i, paper in enumerate(sorted_paper_bank) if i not in idx_to_remove]
    return deduped_paper_bank

def parse_and_execute(output):
    ## parse gpt4 output and execute corresponding functions
    if output.startswith("KeywordQuery"):
        match = re.match(r'KeywordQuery\("([^"]+)"\)', output)
        keyword = match.group(1) if match else None
        if keyword:
            response = KeywordQuery(keyword)
            if 'meta' in response and response['meta']['count'] == 0:
                return None
            if response is not None:
                paper_lst = response["results"]
                return paper_filter(paper_lst)
    elif output.startswith("PaperQuery"):
        match = re.match(r'PaperQuery\("([^"]+)"\)', output)
        paper_id = match.group(1) if match else None
        if paper_id:
            response = PaperQuery(paper_id)
            return response
    elif output.startswith("GetAbstract"):
        match = re.match(r'GetAbstract\("([^"]+)"\)', output)
        paper_id = match.group(1) if match else None
        if paper_id:
            return GetAbstract(paper_id)
    elif output.startswith("GetCitationCount"):
        match = re.match(r'GetCitationCount\("([^"]+)"\)', output)
        paper_id = match.group(1) if match else None
        if paper_id:
            return GetCitationCount(paper_id)
    elif output.startswith("GetCitations"):
        match = re.match(r'GetCitations\("([^"]+)"\)', output)
        paper_id = match.group(1) if match else None
        if paper_id:
            return GetCitations(paper_id)
    elif output.startswith("GetReferences"):
        match = re.match(r'GetReferences\("([^"]+)"\)', output)
        paper_id = match.group(1) if match else None
        if paper_id:
            return GetReferences(paper_id)
    
    return None

def format_papers_for_printing(paper_lst, include_abstract=True, include_score=True, include_id=True):
    ## convert a list of papers to a string for printing or as part of a prompt 
    output_str = ""
    for paper in paper_lst:
        if include_id:
            output_str += "paperId: " + paper["id"].split('/')[-1] + "\n"
        output_str += "title: " + paper["title"].strip() + "\n"
        if include_abstract and "abstract" in paper and paper["abstract"]:
            output_str += "abstract: " + paper["abstract"].strip() + "\n"
        if include_score and "relevance_score" in paper:
            output_str += "relevance score: " + str(paper["relevance_score"]) + "\n"
        output_str += "\n"

    return output_str

def print_top_papers_from_paper_bank(paper_bank, top_k=10):
    # Sort the paper objects by 'relevance_score'
    top_papers = sorted(paper_bank.values(), key=lambda x: x.get('relevance_score', 0), reverse=True)[:top_k]
    
    # Print the top papers
    for paper in top_papers:
        print(f"paperId: {paper['paperId']}")
        print(f"title: {paper['title']}")
        print(f"relevance score: {paper.get('relevance_score', 'N/A')}")
        print(f"abstract: {paper['abstract'][:100]}...")
        print("\n")


if __name__ == "__main__":
    ## some unit tests
    # Call the function and check the filtering process
    paper_bank = KeywordQuery("language model mathematical reasoning")
    if paper_bank and 'results' in paper_bank:
        filtered_papers = paper_filter(paper_bank['results'])
        print(f"Filtered papers: {len(filtered_papers)}")
    else:
        print("No papers found.")
