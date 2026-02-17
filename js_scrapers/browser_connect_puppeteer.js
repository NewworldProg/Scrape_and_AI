const puppeteer = require('puppeteer-core');

// function for scraping
// uses puppeteer
// connects to existing Chrome instance via remote debugging port
// scrapes currently open page (first tab)
async function scrapeWithBrowserConnect() {
    console.log('🔗 PUPPETEER BROWSER CONNECT SCRAPER');
    console.log('=====================================');
    console.log('📋 Instructions:');
    console.log('1. Start Chrome with: chrome.exe --remote-debugging-port=9222');
    console.log('2. Open any website in first browser tab');
    console.log('3. Run this script');
    console.log();
    // variable to hold browser instance
    let browser;
    try {
        // log connecting message
        console.log('🔗 connecting to Chrome on port 9222...');

        // Connecting to existing Chrome browser
        browser = await puppeteer.connect({
            browserURL: 'http://127.0.0.1:9222',
            defaultViewport: null
        });
        // log it
        console.log('✅ Successfully connected to Chrome!');

        // Get all open tabs/pages
        const pages = await browser.pages();
        console.log(`📄 Found ${pages.length} open tabs`);

        // Use the first available tab
        let page = pages[0];

        // Log all available tabs for debugging
        for (let i = 0; i < pages.length; i++) {
            const pageUrl = pages[i].url();
            const pageTitle = await pages[i].title().catch(() => '');
            console.log(`📄 Tab ${i}: ${pageTitle} - ${pageUrl}`);
        }

        // Use first tab
        if (page) {
            console.log(`✅ Using first available tab`);
        } else {
            throw new Error('No tabs available to scrape');
        }

        // Check current page URL and title
        const currentUrl = page.url();
        const pageTitle = await page.title();
        console.log(`📄 Current page: ${pageTitle}`);
        console.log(`🔗 URL: ${currentUrl}`);

        // Simulate short human actions to allow the page to fully load
        console.log('🎭 Simulating short human actions...');
        await page.evaluate(() => {
            window.scrollTo(0, 100);
        });
        await new Promise(resolve => setTimeout(resolve, 1000));

        await page.evaluate(() => {
            window.scrollTo(0, 0);
        });
        await new Promise(resolve => setTimeout(resolve, 500));

        // inside variable content get full HTML of the page
        const content = await page.content();
        console.log(`📊 HTML length: ${content.length} characters`);

        // Save HTML to data folder
        const fs = require('fs');
        const path = require('path');
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `browser_scrape_${timestamp}.html`;
        const dataDir = path.join(__dirname, '..', 'data', 'data_raw');
        const fullPath = path.join(dataDir, filename);

        // Create data_raw folder if it doesn't exist
        if (!fs.existsSync(dataDir)) {
            fs.mkdirSync(dataDir, { recursive: true });
        }

        fs.writeFileSync(fullPath, content);
        console.log(`💾 HTML saved to: data/data_raw/${filename}`);

        // File saved successfully - parser will be called separately by n8n workflow
        console.log('💾 HTML saved - parser will run separately');

        // log content analysis
        const hasContent = content.length > 1000;
        console.log(`🔍 Contains content: ${hasContent ? 'YES' : 'NO'}`);

        if (hasContent) {
            console.log('✅ SUCCESS! Page scraped!');

            // Estimated word count (rough estimate)
            const wordCount = content.split(/\s+/).length;
            console.log(`📊 Estimated ${wordCount} words in HTML`);

            return true;
        } else {
            console.log('⚠️ Page is empty or failed to load properly.');
            return false;
        }

    } catch (error) {
        console.log(`❌ Error: ${error.message}`);
        return false;
    } finally {
        // dont close the browser, just disconnect
        if (browser) {
            console.log('🔗 Browser remains open');
        }
    }
}
// Main function to run the scraper
async function main() {
    try {
        const success = await scrapeWithBrowserConnect();
        // if success log success message
        if (success) {
            console.log('\n🎉 SUCCESS! Scraper worked!');
            process.exit(0);
            // else log failed message
        } else {
            console.log('\n💔 Failed');
            process.exit(1);
        }
    } catch (error) {
        console.log(`💥 CRITICAL ERROR: ${error.message}`);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}