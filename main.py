import asyncio
from playwright.async_api import async_playwright
from nyc_rules.rule_scraper import RuleScraper # type: ignore
from nyc_rules.openai_processor import OpenAIProcessor # type: ignore

# Constants
KEYWORD = "clean energy"

async def main():
    async with async_playwright() as playwright:
        # Initialize Playwright-based RuleScraper
        scraper = RuleScraper(playwright, headless=False)  
        await scraper.setup_browser()

        # Initialize Processor
        processor = OpenAIProcessor()  # ✅ Ensure processor is initialized

        try:
            print(f"🔍 Searching rules for: {KEYWORD}")
            rule_pages = await scraper.search_rules(KEYWORD)  # Now async
            
            if not rule_pages:
                print("❌ No rule pages found.")
                return

            print(f"✅ Found {len(rule_pages)} rule pages.")
            [print(f"Rule Page {i}: {page}") for i, page in enumerate(rule_pages, start=1)]

            # Download PDFs in async fashion
            downloaded_pdfs = {
                await scraper.download_pdf(pdf_link)  
                for rule_page in rule_pages
                if (pdf_link := await scraper.extract_pdf_link(rule_page))
            }

            downloaded_pdfs.discard(None)  # Remove failed downloads
            
            if not downloaded_pdfs:
                print("❌ No PDFs downloaded.")
                return

            for pdf_path in downloaded_pdfs:
                print(f"📄 Processing PDF: {pdf_path}")
                text = await scraper.extract_text_from_pdf(pdf_path)
                
                if not text.strip():
                    print(f"⚠️ No extractable text in {pdf_path}")
                    continue

                # ✅ Remove `await` because `chunk_text()` returns a list
                chunks = processor.chunk_text(text)  
                if not chunks:
                    print(f"⚠️ No valid text chunks found in {pdf_path}")
                    continue

                # ✅ Remove `await` for `analyze_text_chunk()` if it's also synchronous
                results = [
                    processor.analyze_text_chunk(chunk)  
                    for i, chunk in enumerate(chunks, start=1)
                    if chunk.strip()  # Skip empty chunks
                ]

                print(f"📝 Results for {pdf_path}:")
                [print(f"\nChunk {i}:\n{result}\n{'-'*60}") for i, result in enumerate(results, start=1)]

        finally:
            await scraper.close()  # Proper cleanup

# Run the async function
try:
    asyncio.run(main())
except Exception as e:
    print(f"❌ Unexpected error: {e}")
