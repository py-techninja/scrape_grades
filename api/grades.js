const puppeteer = require('puppeteer');

async function loginAndScrapeGrades() {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  try {
    await page.goto('https://sis-portal.uom.gr/login');
    await page.type('#username', 'dai18173');
    await page.type('#password', 'zei7!vo6');
    await page.click('#loginButton');
    await page.waitForNavigation();

    await page.goto('https://sis-portal.uom.gr/student/grades/list_diploma');
    await page.waitForSelector('tr.odd, tr.even');

    const grades = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('tr.odd, tr.even')).map(row => {
        const cols = row.querySelectorAll('td');
        return {
          course_code: cols[0].getAttribute('title'),
          course_name: cols[1].getAttribute('title'),
          grade: cols[2].getAttribute('title'),
          semester: cols[3].getAttribute('title')
        };
      });
    });

    return grades;
  } catch (error) {
    console.error('An error occurred:', error);
    return { error: 'An error occurred while scraping grades' };
  } finally {
    await browser.close();
  }
}

module.exports = async (req, res) => {
  try {
    const grades = await loginAndScrapeGrades();
    res.status(200).json(grades);
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
};