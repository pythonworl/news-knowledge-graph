from fastapi import FastAPI, HTTPException, Query
from typing import List
from models import (
    ArticleRequest, 
    RescanRequest, 
    Person, 
    PersonDetail, 
    DirectRelationship
)
from scraper import get_article_urls_from_page, scrape_article
from extractor import extract_knowledge
from graph_store import graph_db

app = FastAPI(title="News to People Knowledge Graph API")

@app.post("/articles")
async def add_article(request: ArticleRequest):
    """
    Submit a single article by URL.
    Fetches it, parses it, extracts knowledge, and merges into the graph.
    """
    try:
        article_data = await scrape_article(request.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to scrape article: {e}")
        
    if not article_data.get("text"):
        raise HTTPException(status_code=400, detail="Could not extract text from article")
        
    extraction = extract_knowledge(article_data["text"], request.url)
    graph_db.merge_extraction(extraction)
    
    return {"message": "Article processed and merged", "entities_extracted": len(extraction.people), "relationships_extracted": len(extraction.relationships)}


@app.post("/rescan")
async def rescan_topic(request: RescanRequest):
    """
    Re-crawl the latest pages of the TechCrunch OpenAI topic listing.
    """
    base_url = "https://techcrunch.com/tag/openai/"
    
    all_article_urls = []
    
    for page in range(1, request.pages + 1):
        if page == 1:
            page_url = base_url
        else:
            page_url = f"{base_url}page/{page}/"
            
        try:
            urls = await get_article_urls_from_page(page_url)
            all_article_urls.extend(urls)
        except Exception as e:
            print(f"Failed to scrape page {page_url}: {e}")
            
    # Deduplicate URLs
    all_article_urls = list(set(all_article_urls))
    
    results = []
    for url in all_article_urls:
        try:
            article_data = await scrape_article(url)
            extraction = extract_knowledge(article_data["text"], url)
            graph_db.merge_extraction(extraction)
            results.append({"url": url, "status": "success"})
        except Exception as e:
            results.append({"url": url, "status": "failed", "error": str(e)})
            
    return {
        "message": f"Rescanned {request.pages} pages",
        "articles_processed": len(all_article_urls),
        "results": results
    }


@app.get("/people", response_model=List[Person])
async def list_people(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)):
    """
    List all people in the knowledge graph.
    """
    skip = (page - 1) * size
    return graph_db.get_people(skip=skip, limit=size)


@app.get("/people/{person_id}", response_model=PersonDetail)
async def get_person_details(person_id: str):
    """
    Get details for one person by id, including their direct relationships.
    """
    person = graph_db.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
        
    rels = graph_db.get_direct_relationships(person_id)
    
    direct_rels = []
    for r in rels:
        # Determine the target from the perspective of the requested person
        if r.source == person_id:
            direction_target = r.target
            rel_type = f"-> {r.type} ->"
        else:
            direction_target = r.source
            rel_type = f"<- {r.type} <-"
            
        direct_rels.append(DirectRelationship(
            type=rel_type,
            target_id=direction_target,
            explanation=r.explanation,
            provenance=r.provenance
        ))
        
    return PersonDetail(
        id=person.id,
        name=person.name,
        relationships=direct_rels
    )
