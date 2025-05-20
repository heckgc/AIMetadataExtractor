import asyncio
import sys
from playwright.async_api import async_playwright


async def run():
    try:
        print("Launching browser...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            print("Navigating to app...")
            await page.goto("http://127.0.0.1:50001/")
            print("Uploading image...")
            await page.set_input_files("input[type='file']", "tests/test_image.png")
            print("Waiting for 'prompt' box...")
            await page.wait_for_selector("text=prompt", timeout=5000)
            print("Waiting for 'workflow' box...")
            await page.wait_for_selector("text=workflow", timeout=5000)
            assert await page.is_visible("text=prompt"), "'prompt' box not visible!"
            assert await page.is_visible("text=workflow"), "'workflow' box not visible!"
            print("✅ UI test passed: Both 'prompt' and 'workflow' boxes are visible.")
            await browser.close()
    except Exception as e:
        print(f"❌ UI test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run())
