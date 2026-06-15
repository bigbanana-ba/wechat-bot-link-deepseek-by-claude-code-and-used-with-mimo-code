#!/usr/bin/env node
// Edge 浏览器网页抓取工具 - 使用您 Edge 已有登录态
const EDGE_PATH = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const USER_DATA_DIR = process.env.TEMP + '\\edge_cdp_profile';
const url = process.argv[2] || 'https://www.bing.com';

async function main() {
    const puppeteer = require('puppeteer-core');
    const browser = await puppeteer.launch({
        executablePath: EDGE_PATH,
        userDataDir: USER_DATA_DIR,
        headless: false, // 有头模式避免被检测
        args: [
            '--no-sandbox', '--disable-setuid-sandbox',
            '--disable-dev-shm-usage', '--disable-gpu',
        ],
    });
    try {
        const page = await browser.newPage();
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0');
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
        const title = await page.title();
        const bodyText = await page.evaluate(() => {
            document.querySelectorAll('script,style,noscript,svg,header,footer,nav').forEach(s => s.remove());
            const main = document.querySelector('main, article, .content, #content, .main, .result, #results') || document.body;
            return main.innerText || '';
        });
        const result = { url, title, text: bodyText.substring(0, 8000) };
        process.stdout.write(JSON.stringify(result));
    } finally {
        await browser.close();
    }
}
main().catch(err => { process.stderr.write('Error: ' + err.message); process.exit(1); });
