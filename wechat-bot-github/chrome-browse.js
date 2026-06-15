#!/usr/bin/env node
// 连接已运行的 Chrome (CDP port 9222)，打开网页获取内容
const url = process.argv[2] || 'https://www.bing.com';
const CDP_PORT = 9222;

async function main() {
    const puppeteer = require('puppeteer-core');

    // 连接到已运行的 Chrome
    const browser = await puppeteer.connect({
        browserURL: `http://127.0.0.1:${CDP_PORT}`,
        defaultViewport: null,
    });

    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36');

    await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });

    const title = await page.title();
    const text = await page.evaluate(() => {
        document.querySelectorAll('script,style,noscript,svg').forEach(s => s.remove());
        const el = document.querySelector('main, article, .content, #content, .result, #results, .main') || document.body;
        return (el.innerText || '').substring(0, 8000);
    });

    process.stdout.write(JSON.stringify({ url, title, text }));

    await page.close();
    await browser.disconnect();
}

main().catch(err => {
    process.stderr.write('Error: ' + err.message);
    process.exit(1);
});
