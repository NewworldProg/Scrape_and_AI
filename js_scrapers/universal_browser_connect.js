/**
 * Universal Browser Connect Script for Multiple Browsers
 * Supports Chrome, CamoufoxBrowser, Firefox, Edge, Brave
 */

const puppeteer = require('puppeteer-core');
const { spawn } = require('child_process');
const path = require('path');
const https = require('https');
const http = require('http');

// Browser configuration from environment or arguments
const DEBUG_PORT = process.env.BROWSER_DEBUG_PORT || process.argv[2] || 9222;
const BROWSER_TYPE = process.env.BROWSER_TYPE || process.argv[3] || 'chrome';

// Simple HTTP GET function
function httpGet(url) {
    return new Promise((resolve, reject) => {
        const client = url.startsWith('https') ? https : http;
        client.get(url, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve(JSON.parse(data)));
        }).on('error', reject);
    });
}

console.log(`🌐 Starting universal browser scraper...`);
console.log(`🔌 Target: ${BROWSER_TYPE} on port ${DEBUG_PORT}`);

async function connectToBrowser() {
    try {
        console.log(`🔌 Connecting to ${BROWSER_TYPE} browser on port ${DEBUG_PORT}...`);

        // Get browser WebSocket endpoint
        const version = await httpGet(`http://localhost:${DEBUG_PORT}/json/version`);

        if (!version.webSocketDebuggerUrl) {
            throw new Error('Browser WebSocket URL not found');
        }

        console.log(`🎯 Connecting to browser at: ${version.webSocketDebuggerUrl}`);

        const browser = await puppeteer.connect({
            browserWSEndpoint: version.webSocketDebuggerUrl,
            defaultViewport: null,
            ignoreHTTPSErrors: true
        });

        console.log(`✅ Successfully connected to ${BROWSER_TYPE}!`);
        return browser;

    } catch (error) {
        console.error(`❌ Failed to connect to ${BROWSER_TYPE} on port ${DEBUG_PORT}:`, error.message);
        console.error(`💡 Make sure ${BROWSER_TYPE} is running with --remote-debugging-port=${DEBUG_PORT}`);
        throw error;
    }
}

async function findUpworkTab(browser) {
    console.log(`🔍 Looking for available tabs...`);

    const pages = await browser.pages();
    console.log(`📑 Found ${pages.length} open tabs`);

    // Use the first available tab (no longer preferring Upwork)
    if (pages.length > 0) {
        const page = pages[0];
        try {
            const url = page.url();
            const title = await page.title();
            console.log(`📌 Using first available tab: "${title}" - ${url}`);
            return page;
        } catch (error) {
            console.log(`⚠️  Could not access first tab: ${error.message}`);
        }
    }

    throw new Error('No accessible tabs found');
}

async function scrapeUpworkJobs(page) {
    console.log(`🚀 Starting Upwork job scraping...`);

    try {
        // Wait for page to be ready
        // Wait for page load
        await new Promise(resolve => setTimeout(resolve, 3000));

        // Get page content
        const content = await page.content();
        console.log(`📄 Page content length: ${content.length} characters`);

        // Save scraped content
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `browser_scrape_${timestamp}.html`;
        const fs = require('fs');
        const dataDir = path.join(__dirname, '..', 'data');

        // Ensure data directory exists
        if (!fs.existsSync(dataDir)) {
            fs.mkdirSync(dataDir, { recursive: true });
        }

        const filepath = path.join(dataDir, filename);
        fs.writeFileSync(filepath, content);

        console.log(`💾 Scraped content saved to: ${filename}`);

        // Call Python parser
        console.log(`🐍 Calling Python parser...`);
        const pythonCommand = 'E:/Repoi/UpworkNotif/venv/Scripts/python.exe';
        const parserScript = path.join(__dirname, '..', 'scripts', 'data_parser.py');

        const pythonProcess = spawn(pythonCommand, [parserScript, '--input', filepath, '--import-db'], {
            cwd: path.join(__dirname, '..'),
            stdio: 'inherit'
        });

        pythonProcess.on('close', (code) => {
            if (code === 0) {
                console.log(`✅ Python parser completed successfully`);
            } else {
                console.error(`❌ Python parser failed with code ${code}`);
            }
        });

        return {
            success: true,
            filename: filename,
            contentLength: content.length,
            browserType: BROWSER_TYPE,
            debugPort: DEBUG_PORT
        };

    } catch (error) {
        console.error(`❌ Error during scraping: ${error.message}`);
        throw error;
    }
}

async function main() {
    let browser = null;

    try {
        browser = await connectToBrowser();
        const page = await findUpworkTab(browser);
        const result = await scrapeUpworkJobs(page);

        console.log(`🎉 Scraping completed successfully!`);
        console.log(`📊 Result:`, JSON.stringify(result, null, 2));

    } catch (error) {
        console.error(`💥 Scraping failed: ${error.message}`);
        process.exit(1);

    } finally {
        if (browser) {
            try {
                await browser.disconnect();
                console.log(`🔌 Disconnected from ${BROWSER_TYPE}`);
            } catch (error) {
                console.log(`⚠️  Error disconnecting: ${error.message}`);
            }
        }
    }
}

// Handle process termination
process.on('SIGINT', () => {
    console.log('\n🛑 Received SIGINT, shutting down gracefully...');
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n🛑 Received SIGTERM, shutting down gracefully...');
    process.exit(0);
});

// Start the scraping process
main().catch(error => {
    console.error(`💥 Fatal error: ${error.message}`);
    process.exit(1);
});