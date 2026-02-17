const puppeteer = require('puppeteer-core'); // var for puppeteer-core
const fs = require('fs'); // var for filesystem
const path = require('path'); //var for path operations

// Chat Scraper using Puppeteer
// Connects to existing Chrome instance via remote debugging port 9223
// Scrapes chat/messages from currently open page
async function scrapeChatWithBrowserConnect() {
    console.log('PUPPETEER CHAT SCRAPER');
    console.log('======================');
    console.log('Instructions:');
    console.log('1. Chrome should be running on port 9223 for chat');
    console.log('2. Navigate to your chat/messages page');
    console.log('3. This script will scrape the chat content');
    console.log();

    // variable to hold puppeteer connection to browser
    let browser;
    try {
        console.log('Connecting to Chrome on port 9223...');

        // Connect to existing Chrome browser on chat port
        // 1. await function to start using puppeteer library and connect function
        // 2. pupetteer connect built in function to connect to given url of running browser
        browser = await puppeteer.connect({
            browserURL: 'http://127.0.0.1:9223',
            defaultViewport: null
        });
        // 2. log it
        console.log('Successfully connected to Chrome chat instance!');

        // inside variable like pages
        // 1. await function to to start using puppeteer library and pages function
        // 2. get all open tabs/pages
        const pages = await browser.pages();
        console.log(`Found ${pages.length} open tabs`);

        // Look for first tab that looks like chat/messages
        let page = pages[0];
        let chatPage = null;

        for (let i = 0; i < pages.length; i++) {
            const pageUrl = pages[i].url();
            const pageTitle = await pages[i].title().catch(() => '');
            console.log(`Tab ${i}: ${pageTitle} - ${pageUrl}`);

            // Look for chat-related URLs
            if (pageUrl.includes('messages') ||
                pageUrl.includes('chat') ||
                pageUrl.includes('upwork.com/messages') ||
                pageTitle.toLowerCase().includes('message') ||
                pageTitle.toLowerCase().includes('chat')) {
                chatPage = pages[i];
                console.log(`Found chat tab: ${pageTitle}`);
                break;
            }
        }

        // Use chat page if found, otherwise use first page
        if (chatPage) {
            page = chatPage;
        } else {
            console.log('No specific chat page found, using first tab');
        }

        // Get page info
        const url = page.url();
        const title = await page.title().catch(() => 'Unknown Title');

        console.log('Current page URL:', url);
        console.log('Current page title:', title);

        // Wait for page to be fully loaded
        try {
            await page.waitForLoadState?.('networkidle') ||
                await page.waitForSelector('body', { timeout: 5000 });
        } catch (e) {
            console.log('Page might still be loading, continuing...');
        }

        // Get page content
        console.log('Extracting page content...');

        // inside variable put data from main scraping 
        // contnent function from puppeteer library to get full HTML
        const htmlContent = await page.content();

        // Try to extract chat messages using various selectors
        let messages = [];

        try {
            // Common chat message selectors
            const messageSelectors = [
                '[data-test*="message"]',
                '.message',
                '.chat-message',
                '[class*="message"]',
                '[class*="Message"]',
                '.conversation-message',
                '[data-test*="conversation"]'
            ];
            // try each selector until we find messages
            for (const selector of messageSelectors) {
                const elements = await page.$$(selector);
                if (elements.length > 0) {
                    console.log(`Found ${elements.length} messages with selector: ${selector}`);

                    for (const element of elements) {
                        try {
                            const text = await element.innerText();
                            if (text && text.trim()) {
                                messages.push({
                                    text: text.trim(),
                                    selector: selector,
                                    timestamp: new Date().toISOString()
                                });
                            }
                        } catch (e) {
                            // Skip elements that can't be read
                        }
                    }
                    break; // Use first working selector
                }
            }
        } catch (e) {
            console.log('Error extracting messages:', e.message);
        }

        // Create timestamp for filename
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('.')[0];

        // Save raw HTML
        // inside variable put path for data file
        const dataDir = path.join(__dirname, '..', 'data');
        if (!fs.existsSync(dataDir)) {
            fs.mkdirSync(dataDir, { recursive: true });
        }
        // name file with timestamp
        // inside variable put chat raw filename + timestamp + .html
        const htmlFilename = `chat_raw_${timestamp}.html`;
        // combine path and filename
        const htmlPath = path.join(dataDir, htmlFilename);
        // write file to path and content
        fs.writeFileSync(htmlPath, htmlContent, 'utf8');

        // Create result object
        const result = {
            success: true,
            timestamp: new Date().toISOString(),
            url: url,
            title: title,
            platform: detectPlatform(url),
            messages_count: messages.length,
            html_file: htmlFilename,
            html_path: htmlPath,
            messages: messages.slice(0, 10), // Include first 10 messages in result
            session_id: generateSessionId(url, title)
        };

        // Save result as JSON
        const jsonFilename = `chat_result_${timestamp}.json`;
        const jsonPath = path.join(dataDir, jsonFilename);
        fs.writeFileSync(jsonPath, JSON.stringify(result, null, 2), 'utf8');

        console.log('Chat scraping completed successfully!');
        console.log(`HTML saved: ${htmlPath}`);
        console.log(`Result saved: ${jsonPath}`);
        console.log(`Found ${messages.length} messages`);

        // Output result for n8n
        console.log(JSON.stringify(result));

        return result;
        // error handling
    } catch (error) {
        console.error('Error during chat scraping:', error.message);

        const errorResult = {
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        };

        console.log(JSON.stringify(errorResult));
        return errorResult;

    } finally {
        // Don't close browser - let it stay open for user
        if (browser) {
            try {
                await browser.disconnect();
                console.log('Disconnected from browser (browser stays open)');
            } catch (e) {
                console.log('Error disconnecting:', e.message);
            }
        }
    }
}

// Helper function to detect platform from URL
function detectPlatform(url) {
    if (url.includes('upwork.com')) return 'upwork';
    if (url.includes('linkedin.com')) return 'linkedin';
    if (url.includes('discord.com')) return 'discord';
    if (url.includes('teams.microsoft.com')) return 'teams';
    if (url.includes('slack.com')) return 'slack';
    if (url.includes('telegram.org')) return 'telegram';
    return 'unknown';
}

// Helper function to generate session ID
function generateSessionId(url, title) {
    const platform = detectPlatform(url);
    const timestamp = new Date().toISOString().split('T')[0];
    const hash = Math.random().toString(36).substring(2, 8);
    return `${platform}_${timestamp}_${hash}`;
}

// Run the scraper
if (require.main === module) {
    scrapeChatWithBrowserConnect()
        .then(() => {
            console.log('Chat scraper finished');
            process.exit(0);
        })
        .catch((error) => {
            console.error('Chat scraper failed:', error);
            process.exit(1);
        });
}

module.exports = { scrapeChatWithBrowserConnect };