# main.py
from googlesearch import search, SearchResult



def main():
    term = "Who is the director of malla reddy engineering college"
    num_results = 10
    advanced = True
    
    # Perform the search
    results = search(term, num_results=num_results, advanced=advanced)
    
    # Print the results
    for result in results:
        if isinstance(result, SearchResult):
            print(f"URL: {result.url}")
            print(f"Title: {result.title}")
            print(f"Description: {result.description}\n")
        else:
            print(f"URL: {result}\n")

if __name__ == "__main__":
    main()
