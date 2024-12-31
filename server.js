import express from 'express';
import bodyParser from 'body-parser';
import { promises as fs } from 'fs';
import * as theme from 'jsonresume-theme-even';
import puppeteer from 'puppeteer';
import { render } from 'resumed';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const port = 3005;

// Middleware to parse JSON bodies
app.use(bodyParser.json({ limit: '50mb' }));
app.use(express.static('public'));

// Serve the sample resume
app.get('/sample-resume', async (req, res) => {
    try {
        const resumeData = await fs.readFile('resume.json', 'utf-8');
        res.json(JSON.parse(resumeData));
    } catch (error) {
        res.status(500).json({ error: 'Failed to load sample resume' });
    }
});

// Serve the main page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// POST endpoint to generate CV
app.post('/generate-cv', async (req, res) => {
    try {
        const resume = req.body;
        
        // Generate HTML from resume data
        const html = await render(resume, theme);

        // Launch browser and create PDF
        const browser = await puppeteer.launch();
        const page = await browser.newPage();
        
        await page.setContent(html, { waitUntil: 'networkidle0' });
        
        // Generate PDF directly to response
        const pdf = await page.pdf({ 
            format: 'a4', 
            printBackground: true 
        });
        
        await browser.close();

        // Send PDF to client
        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader('Content-Disposition', 'attachment; filename=resume.pdf');
        res.send(pdf);

    } catch (error) {
        console.error('Error generating CV:', error);
        res.status(500).json({ error: 'Failed to generate CV' });
    }
});

app.listen(port, () => {
    console.log(`CV Generator API running at http://localhost:${port}`);
});
