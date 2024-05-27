from googlesearch import search, SearchResult

def perform_search(term, num_results=10, advanced=True):
    """
    Perform a Google search for the given term and return the results.

    :param term: The search term
    :param num_results: Number of search results to return
    :param advanced: Whether to return detailed results
    :return: List of dictionaries containing search results
    """
    results = search(term, num_results=num_results, advanced=advanced)
    search_results = []
    for result in results:
        if isinstance(result, SearchResult):
            search_results.append({
                'url': result.url,
                'title': result.title,
                'description': result.description
            })
        else:
            search_results.append({'url': result})
    return search_results