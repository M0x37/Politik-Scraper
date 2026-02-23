class NewsWebsite {
    constructor() {
        this.newsData = null;
        this.init();
    }

    init() {
        this.loadNews();
        this.setupEventListeners();
        this.setupAutoRefresh();
    }

    setupEventListeners() {
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadNews());
        }
    }

    setupAutoRefresh() {
        // Alle 5 Minuten automatisch aktualisieren
        setInterval(() => this.loadNews(), 5 * 60 * 1000);
    }

    async loadNews() {
        const container = document.getElementById('newsContainer');
        const refreshBtn = document.getElementById('refreshBtn');
        
        // Lade-Animation anzeigen
        container.innerHTML = `
            <div class="loading">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Lade Nachrichten...</p>
            </div>
        `;
        
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Lade...';

        try {
            // Versuche zuerst die lokale JSON-Datei zu laden
            const response = await fetch('demo_news.json');
            
            if (response.ok) {
                const data = await response.json();
                this.newsData = data;
                this.displayNews(data);
            } else {
                // Fallback: Demo-Daten anzeigen
                this.showDemoNews();
            }
        } catch (error) {
            console.error('Fehler beim Laden der Nachrichten:', error);
            this.showDemoNews();
        } finally {
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Aktualisieren';
        }
    }

    displayNews(data) {
        const container = document.getElementById('newsContainer');
        
        if (!data.news || data.news.length === 0) {
            container.innerHTML = `
                <div class="error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Keine Nachrichten gefunden.</p>
                </div>
            `;
            return;
        }

        const newsHTML = data.news.map((news, index) => `
            <div class="news-item">
                <div class="news-header">
                    <h3 class="news-title">${this.escapeHtml(news.title)}</h3>
                    <button class="copy-btn" onclick="newsWebsite.copyNews(${index})" title="Kopieren">
                        <i class="fas fa-copy"></i>
                        <span>Kopieren</span>
                    </button>
                </div>
                <p class="news-summary">${this.escapeHtml(news.summary)}</p>
                <div class="news-meta">
                    <span class="news-source">${this.escapeHtml(news.source)}</span>
                    <span class="news-time">
                        <i class="fas fa-clock"></i>
                        ${this.formatDate(news.published)}
                    </span>
                </div>
            </div>
        `).join('');

        container.innerHTML = newsHTML;
    }

    showDemoNews() {
        const demoData = {
            date: new Date().toISOString(),
            news_count: 3,
            news: [
                {
                    title: "Demo: Bundesregierung beschließt neues Klimapaket",
                    summary: "Die Bundesregierung hat heute ein umfassendes Klimapaket verabschiedet, das ambitionierte Ziele für CO₂-Reduzierung bis 2030 festlegt.",
                    source: "Tagesschau Politik",
                    published: new Date().toISOString()
                },
                {
                    title: "Demo: EU-Sanktionen gegen Russland verlängert",
                    summary: "Die Europäische Union hat die Sanktionen gegen Russland um weitere sechs Monate verlängert und neue Maßnahmen beschlossen.",
                    source: "ZDF Politik",
                    published: new Date().toISOString()
                },
                {
                    title: "Demo: Koalitionsausschuss tagt über Steuerreform",
                    summary: "Im Koalitionsausschuss wird heute über eine umfassende Steuerreform beraten, die Entlastungen für Bürger und Unternehmen vorsieht.",
                    source: "ARD Politik",
                    published: new Date().toISOString()
                }
            ]
        };
        
        this.displayNews(demoData);
        
        // Hinweis anzeigen
        const container = document.getElementById('newsContainer');
        const demoNotice = document.createElement('div');
        demoNotice.className = 'error';
        demoNotice.style.marginBottom = '20px';
        demoNotice.innerHTML = `
            <i class="fas fa-info-circle"></i>
            <p><strong>Demo-Modus:</strong> Keine aktuellen Nachrichten gefunden. Dies sind Beispieldaten.</p>
        `;
        container.insertBefore(demoNotice, container.firstChild);
    }

    copyNews(index) {
        if (!this.newsData || !this.newsData.news || !this.newsData.news[index]) {
            return;
        }

        const news = this.newsData.news[index];
        const copyText = `${news.title}\n\n${news.summary}\n\nQuelle: ${news.source}`;
        
        // Versuche moderne Clipboard API
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(copyText).then(() => {
                this.showCopySuccess(index);
            }).catch(err => {
                console.error('Clipboard API fehlgeschlagen:', err);
                this.fallbackCopy(copyText, index);
            });
        } else {
            // Fallback für ältere Browser
            this.fallbackCopy(copyText, index);
        }
    }

    fallbackCopy(text, index) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.showCopySuccess(index);
        } catch (err) {
            console.error('Kopieren fehlgeschlagen:', err);
            alert('Kopieren fehlgeschlagen. Bitte manuell kopieren.');
        }
        
        document.body.removeChild(textArea);
    }

    showCopySuccess(index) {
        const button = document.querySelector(`.copy-btn:nth-child(${index + 1})`);
        if (button) {
            button.classList.add('copied');
            button.innerHTML = '<i class="fas fa-check"></i> <span>Kopiert!</span>';
            
            setTimeout(() => {
                button.classList.remove('copied');
                button.innerHTML = '<i class="fas fa-copy"></i> <span>Kopieren</span>';
            }, 2000);
        }
    }

    formatDate(dateString) {
        try {
            const date = new Date(dateString);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMs / 3600000);
            const diffDays = Math.floor(diffMs / 86400000);

            if (diffMins < 1) {
                return 'Gerade eben';
            } else if (diffMins < 60) {
                return `Vor ${diffMins} Minute${diffMins > 1 ? 'n' : ''}`;
            } else if (diffHours < 24) {
                return `Vor ${diffHours} Stunde${diffHours > 1 ? 'n' : ''}`;
            } else if (diffDays < 7) {
                return `Vor ${diffDays} Tag${diffDays > 1 ? 'en' : ''}`;
            } else {
                return date.toLocaleDateString('de-DE', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric'
                });
            }
        } catch (error) {
            return 'Unbekannt';
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Website initialisieren
const newsWebsite = new NewsWebsite();
