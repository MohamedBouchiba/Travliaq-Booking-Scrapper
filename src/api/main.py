from fastapi import FastAPI
from src.api.routes import search, details

app = FastAPI(
    title="Travliaq Booking Scraper API",
    description="API de scraping Booking.com pour hotels",
    version="1.0.0"
)

app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(details.router, prefix="/api/v1", tags=["details"])

@app.get("/")
async def root():
    return {
        "service": "Travliaq Booking Scraper API",
        "version": "1.0.0",
        "endpoints": ["/api/v1/search_hotels", "/api/v1/hotel_details"]
    }
